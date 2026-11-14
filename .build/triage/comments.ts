import { COMMENT_MARKER_PREFIX, KNOWN_SIBLING_INTEGRATIONS } from './config';
import { Analysis, DocLink, Evidence, Outcome } from './schemas';
import { sanitizeModelText } from './validate';
import { ChangelogLine, plainChangelogText } from './version';

export const AI_DISCLOSURE =
  '> :robot: **Automated AI response** - this comment was generated automatically and has not been reviewed by ' +
  'the maintainer. Please treat it as a suggestion, not a confirmed answer.';

/** Outcomes addressed to the reporter, where a 👍 means "solved" and the issue can be closed. */
export const REPORTER_RESOLVABLE: Outcome[] = ['docs_answer', 'fixed_in_newer_version', 'already_supported', 'duplicate', 'wrong_repo'];

export interface CommentContext {
  repo: string;
  sha: string;
  maintainer: string;
}

export function commentMarker(outcome: Outcome): string {
  return `${COMMENT_MARKER_PREFIX} outcome=${outcome} -->`;
}

export function parseCommentMarker(body: string): Outcome | null {
  const match = body.match(/<!-- ai-triage v1 outcome=([a-z_]+) -->/);
  return match ? (match[1] as Outcome) : null;
}

function footer(outcome: Outcome, maintainer: string): string {
  if (REPORTER_RESOLVABLE.includes(outcome)) {
    return '**Did this solve your issue?** React with :+1: to this comment and the issue will be closed, or :-1: if it didn\'t and it will be passed to the maintainer.';
  }
  if (outcome === 'needs_info') {
    return 'Please add the details above when you can. If this comment isn\'t relevant, react with :-1: and it will be passed straight to the maintainer.';
  }
  return `@${maintainer} - react with :+1: if this diagnosis is useful or :-1: if not. Reporters can react too; either way the maintainer will pick this up.`;
}

function permalink(ctx: CommentContext, evidence: Evidence): string {
  const range = evidence.start_line === evidence.end_line ? `L${evidence.start_line}` : `L${evidence.start_line}-L${evidence.end_line}`;
  return `https://github.com/${ctx.repo}/blob/${ctx.sha}/${evidence.file}#${range}`;
}

function renderEvidence(ctx: CommentContext, evidence: Evidence[]): string {
  return evidence
    .slice(0, 5)
    .map((item) => {
      const lines = item.quote.split('\n');
      const quote = lines.length > 15 ? [...lines.slice(0, 15), '# ...'].join('\n') : item.quote;
      return [`- [\`${item.file.replace(/^custom_components\/octopus_energy\//, '')}#L${item.start_line}\`](${permalink(ctx, item)}) - ${sanitizeModelText(item.why)}`, '', `  \`\`\`${item.file.endsWith('.py') ? 'python' : item.file.match(/\.ya?ml$/) ? 'yaml' : ''}`, ...quote.split('\n').map((line) => `  ${line}`), '  ```'].join('\n');
    })
    .join('\n');
}

/** The query as a ready-to-run `run_graphql_query` action call (Developer tools > Actions). */
function renderGraphqlAction(query: string): string {
  const body = query.replace(/`/g, '').trim().split('\n').map((line) => `      ${line}`);
  return [
    '  Run this from **Developer tools > Actions** (YAML mode), replacing the account id with yours:',
    '  ```yaml',
    '  action: octopus_energy.run_graphql_query',
    '  data:',
    '    account_id: "<your account id>"',
    '    query: |',
    ...body,
    '  ```',
    '  Please remove any personal details from the response before pasting it here.',
  ].join('\n');
}

function renderDocLinks(links: DocLink[]): string {
  return links.map((link) => `- ${link.url}\n  > ${sanitizeModelText(link.quote)}`).join('\n');
}

function wrap(outcome: Outcome, ctx: CommentContext, body: string[]): string {
  return [commentMarker(outcome), AI_DISCLOSURE, '', ...body.filter((part) => part !== null && part !== undefined), '', '---', footer(outcome, ctx.maintainer)].join('\n');
}

// Heading for the maintainer's technical summary (inside the collapsed section).
const HEADINGS: Partial<Record<Outcome, string>> = {
  root_cause: '**Possible root cause:**',
  implementation_notes: '**Implementation notes:**',
  already_supported: '**Existing support:**',
  needs_info: '**What the code shows so far:**',
  docs_answer: '**Answer:**',
  wrong_repo: '**Why this looks like another integration:**',
};

// Used if the model leaves reporter_message empty, so the visible part is never just code.
const DEFAULT_REPORTER_MESSAGE: Partial<Record<Outcome, string>> = {
  root_cause: 'This looks like a problem in the integration itself rather than anything in your setup. The maintainer has been notified, and there is nothing you need to change for now.',
  implementation_notes: "Some notes on how this could be built have been added below for the maintainer. There's nothing you need to do for now.",
  needs_info: 'To work out what is going on, a few more details would help:',
};

export function buildAnalysisComment(analysis: Analysis, ctx: CommentContext, extraQuestions: string[] = []): string {
  const outcome = analysis.outcome;
  const asked = analysis.questions_for_reporter.slice(0, 2);
  const parts: string[] = [];

  // Visible: written for the reporter, in plain language.
  if (outcome === 'wrong_repo') {
    const sibling = KNOWN_SIBLING_INTEGRATIONS[analysis.other_integration];
    parts.push(
      sibling
        ? `This looks like it relates to **${sibling.name}**, which is a separate integration with its own repository: https://github.com/${sibling.repo}/issues`
        : "This doesn't look like it relates to this integration (Octopus Energy for UK Octopus Energy accounts), so it may need raising elsewhere.",
      '',
    );
  }
  parts.push(sanitizeModelText(analysis.reporter_message) || DEFAULT_REPORTER_MESSAGE[outcome] || '');
  const questions = [
    ...asked.map((q) => `- [ ] ${sanitizeModelText(q.ask)}${q.graphql_query?.trim() ? `\n${renderGraphqlAction(q.graphql_query)}` : ''}`),
    ...extraQuestions.map((q) => `- [ ] ${q}`),
  ];
  if (questions.length) parts.push('', '**Could you please provide:**', ...questions);
  if (analysis.doc_links.length) parts.push('', '**Documentation:**', renderDocLinks(analysis.doc_links));

  // Collapsed: technical detail for the maintainer.
  const details: string[] = [];
  const summary = sanitizeModelText(analysis.summary);
  const findings = analysis.new_findings.map(sanitizeModelText).filter(Boolean);
  const whys = asked.map((q) => sanitizeModelText(q.why)).filter(Boolean);
  if (summary) details.push('', HEADINGS[outcome] ? `${HEADINGS[outcome]} ${summary}` : summary);
  if (findings.length) details.push('', ...findings.map((f) => `- ${f}`));
  if (analysis.evidence.length) details.push('', '**Relevant code:**', renderEvidence(ctx, analysis.evidence));
  if (analysis.graphql_fields.length) details.push('', `**Candidate GraphQL field(s):** ${analysis.graphql_fields.map((f) => `\`${f}\``).join(', ')}`);
  if (analysis.suggested_fix && ['root_cause', 'implementation_notes'].includes(outcome)) details.push('', `**Suggested fix:** ${sanitizeModelText(analysis.suggested_fix)}`);
  if (whys.length) details.push('', '**Why these questions (in order):**', ...whys.map((why) => `- ${why}`));
  if (details.length) parts.push('', '<details><summary>Technical details for the maintainer</summary>', ...details, '', '</details>');

  return wrap(outcome, ctx, parts);
}

export function buildFixedInNewerVersionComment(reported: string, latest: string, lines: Array<ChangelogLine & { why: string }>, ctx: CommentContext): string {
  const entries = lines.map((line) => {
    const why = sanitizeModelText(line.why.replace(/\s*[([]?\bC\d+\b[)\]]?:?/g, '')); // never leak internal entry ids
    return `- **v${line.version}**: ${plainChangelogText(line.text)}${line.closes.length ? ` (${line.closes.map((n) => `#${n}`).join(', ')})` : ''}\n  _${why}_`;
  });
  return wrap('fixed_in_newer_version', ctx, [
    `You're on **v${reported}**, and this looks like it was fixed in a later release (latest is **v${latest}**):`,
    '',
    ...entries,
    '',
    `Please update to v${latest} and let us know if the problem persists. Release notes: https://github.com/${ctx.repo}/releases`,
  ]);
}

export function buildDuplicateComment(duplicate: { number: number; title: string; state: string }, why: string, ctx: CommentContext): string {
  return wrap('duplicate', ctx, [
    `This looks like a duplicate of #${duplicate.number} (${duplicate.state}): ${sanitizeModelText(why)}`,
    '',
    `If so, please follow #${duplicate.number} and add any extra details there.`,
  ]);
}
