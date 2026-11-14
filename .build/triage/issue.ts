import { readFileSync } from 'fs';
import { basename } from 'path';
import { GithubIssueSummary } from './github';
import { tokenize } from './text';

export interface GithubIssue {
  number: number;
  title: string;
  body: string;
  html_url: string;
  labels: string[];
  author: { login: string; type: string };
  createdAt?: string;
}

export function issueFromApi(raw: GithubIssueSummary): GithubIssue {
  return {
    createdAt: raw.created_at,
    number: raw.number,
    title: raw.title ?? '',
    body: raw.body ?? '',
    html_url: raw.html_url,
    labels: (raw.labels ?? []).map((label) => (typeof label === 'string' ? label : label.name)),
    author: { login: raw.user?.login ?? '', type: raw.user?.type ?? 'User' },
  };
}

export function loadIssueFromEvent(): GithubIssue {
  const eventPath = process.env.GITHUB_EVENT_PATH;
  if (!eventPath) {
    throw new Error('GITHUB_EVENT_PATH not set - this script must be run from a GitHub Actions `issues` event');
  }

  const event = JSON.parse(readFileSync(eventPath, 'utf-8'));
  if (!event.issue) {
    throw new Error('GitHub event payload did not contain an `issue`');
  }

  return issueFromApi(event.issue);
}

// Must match the checkbox label text in the "ai-triage-consent" field of every form under
// .github/ISSUE_TEMPLATE/. The checkbox is optional, not required, so reporters can decline AI
// processing of their issue (which may include logs/account details) and still get a human triage.
export const AI_TRIAGE_CONSENT_TEXT = 'processed by an AI assistant for automated triage';

// Only the bug form's consent text covers logs ("including any text or logs I provide"), so
// attachments are only ever downloaded for issues whose consent line says so.
const LOG_CONSENT_TEXT = 'text or logs';

function findConsentLine(body: string): string | undefined {
  return body.split('\n').find((line) => line.toLowerCase().includes(AI_TRIAGE_CONSENT_TEXT.toLowerCase()));
}

// GitHub issue forms render an unchecked box as "- [ ] <label>" and a checked one as "- [X] <label>".
// If the checkbox line can't be found at all (e.g. an issue predating this field), that's treated
// as no consent too - fail closed rather than assume permission that was never given.
export function hasAiTriageConsent(body: string): boolean {
  const consentLine = findConsentLine(body);
  return consentLine ? /^\s*-\s*\[[xX]\]/.test(consentLine) : false;
}

export function hasLogConsent(body: string): boolean {
  const consentLine = findConsentLine(body);
  return Boolean(consentLine && hasAiTriageConsent(body) && consentLine.toLowerCase().includes(LOG_CONSENT_TEXT));
}

// GitHub marks GitHub App/classic bot accounts (e.g. "github-actions[bot]", "dependabot[bot]")
// with `type: "Bot"`; the "[bot]" login suffix is checked too as a fallback for automation that
// posts through a regular user token without that type set.
export function isBotAuthor(author: GithubIssue['author']): boolean {
  return author.type === 'Bot' || author.login.toLowerCase().endsWith('[bot]');
}

/**
 * Builds a synthetic issue from a local file for manual testing - the file's contents become the
 * issue body, so the full pipeline can be exercised against real text without a live GitHub issue.
 */
export function loadIssueFromFile(
  filePath: string,
  options: { title?: string | null; label?: string | null; isBot?: boolean; consent?: boolean },
): GithubIssue {
  const fileBody = readFileSync(filePath, 'utf-8');
  // Defaults to no consent, matching a real issue form's unchecked-by-default checkbox.
  const body = options.consent
    ? `${fileBody}\n\n### AI Triage\n\n- [X] I consent to this issue, including any text or logs I provide, being ${AI_TRIAGE_CONSENT_TEXT}`
    : fileBody;

  return {
    number: 0,
    title: options.title ?? `Local test issue (${basename(filePath)})`,
    body,
    html_url: filePath,
    labels: options.label ? [options.label] : [],
    author: { login: options.isBot ? 'local-test[bot]' : 'local-test-user', type: options.isBot ? 'Bot' : 'User' },
  };
}

export interface ParsedIssue {
  /** Section key (see SECTION_KEYS) or a slug of an unknown heading, in original order. */
  sections: Array<{ key: string; heading: string; content: string }>;
  get(key: string): string;
}

const SECTION_KEYS: Record<string, string> = {
  'describe the bug': 'description',
  'describe the feature': 'description',
  'reproduction steps': 'reproduction',
  'expected behaviour': 'expected',
  'use case': 'use_case',
  'tariff code': 'tariff',
  'integration version': 'integration_version',
  'home assistant version': 'ha_version',
  'fresh install?': 'fresh_install',
  'home assistant logs': 'logs',
  'provider name': 'provider', // "Unknown intelligent provider" form
};

// Form boilerplate (confirmations and the consent box) carries no information for triage.
const IGNORED_HEADINGS = new Set(['confirmation', 'ai triage']);

export function parseIssueForm(body: string): ParsedIssue {
  const sections: ParsedIssue['sections'] = [];
  const lines = (body ?? '').replace(/\r\n?/g, '\n').split('\n');
  let current: { key: string; heading: string; lines: string[] } | null = null;
  const preamble: string[] = [];

  const flush = () => {
    if (current) {
      const content = current.lines.join('\n').trim();
      if (!IGNORED_HEADINGS.has(current.heading.toLowerCase())) {
        sections.push({ key: current.key, heading: current.heading, content: content === '_No response_' ? '' : content });
      }
    }
  };

  for (const line of lines) {
    const heading = line.match(/^###\s+(.+?)\s*$/);
    if (heading) {
      flush();
      const text = heading[1];
      const key = SECTION_KEYS[text.toLowerCase()] ?? text.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
      current = { key, heading: text, lines: [] };
    } else if (current) {
      current.lines.push(line);
    } else {
      preamble.push(line);
    }
  }
  flush();

  const preambleText = preamble.join('\n').trim();
  if (preambleText) {
    // Not created from an issue form (or text before the first heading) - treat as the description.
    sections.unshift({ key: sections.length ? 'preamble' : 'description', heading: 'Description', content: preambleText });
  }

  return {
    sections,
    get: (key: string) => sections.filter((section) => section.key === key).map((section) => section.content).join('\n\n'),
  };
}

/**
 * Integration version from the form field, but only when the field contains nothing except a
 * version number - e.g. "Version 1.5.2 of Target Timeframes" (#1938) is a different integration's
 * version and must not trigger an "update to the latest version" comment.
 */
export function parseReportedVersion(fieldText: string): string | null {
  // Pre-releases are kept ("19.0.0-beta.4", "18.3.3 (beta)" -> "18.3.3-beta"): beta testers report
  // bugs too (#1714, #1725) and need pointing at the stable release.
  const match = fieldText.match(/v?(\d+\.\d+\.\d+)(?:\s*[-.(]?\s*(alpha|beta|rc|dev)\s*[.-]?\s*(\d+)?\s*\)?)?/i);
  if (!match) {
    return null;
  }
  const leftover = fieldText.replace(match[0], '').replace(/\bversion\b/gi, '').replace(/[^a-z]/gi, '');
  if (leftover.length) {
    return null;
  }
  const prerelease = match[2] ? `-${match[2].toLowerCase()}${match[3] ? `.${match[3]}` : ''}` : '';
  return `${match[1]}${prerelease}`;
}

// Words that say nothing about which part of the integration is affected. A title made only of
// these (plus versions) can't be found by duplicate search or understood from the issue list.
const GENERIC_TITLE_WORDS = new Set(
  (
    'bug report reports issue issues problem problems error errors message messages warning warnings help please fix fixed broken break breaks breaking ' +
    'working work works stopped stop stops failed failing fails failure failures fail wrong incorrect odd strange weird question request feature suggests suggestion ' +
    'octopus energy integration integrations intergration component custom home assistant homeassistant core hass update updated updating upgrade upgraded upgrading ' +
    'version latest new log logs logged detected occurred happening happens after since when anymore longer still ' +
    'data setup install installation support entity entities sensor sensors'
  ).split(/\s+/),
);

/**
 * True when the title has fewer than two distinctive words, e.g. "Bug report rt", "Octopus
 * intergration broken", "Error message when updating to v19.0.1 which suggests a bug" (#1838).
 */
export function isGenericTitle(title: string): boolean {
  const distinctive = new Set(
    tokenize(title.replace(/\bv?\d+(\.\d+)+(-[\w.]+)?\b/g, ' ')).filter((t) => !GENERIC_TITLE_WORDS.has(t) && !t.includes('_') && !/^v?\d/.test(t)),
  );
  return distinctive.size < 2;
}
