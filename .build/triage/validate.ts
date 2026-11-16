import { parse, visit } from 'graphql';
import { BLUEPRINTS_REPO_PREFIX, SOURCE_REPO_PREFIX } from './config';
import { DocSection, normalizeDocUrl, sectionContainsQuote } from './docs';
import { CodeIndex } from './retrieval';
import { DocLink, Evidence } from './schemas';
import { normalizeWhitespace } from './text';

const MIN_QUOTE_CHARS = 10;

function normalizeFile(file: string): string {
  const cleaned = file.trim().replace(/^\.?\//, '').split('\\').join('/');
  return cleaned.startsWith('custom_components/') || cleaned.startsWith(`${BLUEPRINTS_REPO_PREFIX}/`) ? cleaned : `${SOURCE_REPO_PREFIX}/${cleaned}`;
}

function stripLinePrefixes(quote: string): string {
  return quote
    .split('\n')
    .map((line) => line.replace(/^\s*L\d+:\s?/, ''))
    .join('\n');
}

/**
 * Finds the quoted lines in the file (blank lines ignored), preferring the occurrence nearest the
 * claimed line. The first and last quoted lines may be partial; lines in between must match.
 */
function findQuote(fileLines: string[], quote: string, near: number): { start: number; end: number } | null {
  const wanted = quote.split('\n').map(normalizeWhitespace).filter(Boolean);
  const lines = fileLines.map((text, index) => ({ text: normalizeWhitespace(text), index })).filter((line) => line.text);
  const last = wanted.length - 1;
  let best: { start: number; end: number } | null = null;
  for (let i = 0; i + last < lines.length; i++) {
    const matches = wanted.every((text, k) => (k === 0 || k === last ? lines[i + k].text.includes(text) : lines[i + k].text === text));
    if (matches && (!best || Math.abs(lines[i].index - near) < Math.abs(best.start - near))) {
      best = { start: lines[i].index, end: lines[i + last].index };
    }
  }
  return best;
}

/**
 * Keeps only evidence whose quote really appears in the named file. Only files from the indexed
 * source tree are accepted (so no path traversal), and if the quote is found at different lines
 * than claimed, the line numbers are corrected rather than the evidence dropped.
 */
export function validateEvidence(evidence: Evidence[], code: CodeIndex): { valid: Evidence[]; rejected: string[] } {
  const valid: Evidence[] = [];
  const rejected: string[] = [];

  for (const item of evidence ?? []) {
    const file = normalizeFile(item.file ?? '');
    const source = code.files.get(file);
    const quote = stripLinePrefixes(item.quote ?? '');
    const match = source && normalizeWhitespace(quote).length >= MIN_QUOTE_CHARS ? findQuote(source.lines, quote, (item.start_line || 1) - 1) : null;
    if (!source) {
      rejected.push(`evidence file not found: ${item.file}`);
    } else if (normalizeWhitespace(quote).length < MIN_QUOTE_CHARS) {
      rejected.push(`evidence quote too short in ${file}`);
    } else if (!match) {
      rejected.push(`evidence quote not found in ${file}`);
    } else {
      valid.push({ ...item, file, start_line: match.start + 1, end_line: match.end + 1, quote: source.lines.slice(match.start, match.end + 1).join('\n') });
    }
  }

  return { valid, rejected };
}

/** Links must be one of the doc sections the model was shown, and the quote must be in it. */
export function validateDocLinks(links: DocLink[], shown: DocSection[]): { valid: DocLink[]; rejected: string[] } {
  const byUrl = new Map(shown.map((section) => [normalizeDocUrl(section.url), section]));
  const valid: DocLink[] = [];
  const rejected: string[] = [];
  for (const link of links ?? []) {
    const url = normalizeDocUrl(link.url ?? '');
    const section = byUrl.get(url);
    if (!section) {
      rejected.push(`doc link not in provided sections: ${link.url}`);
    } else if (!sectionContainsQuote(section, link.quote ?? '')) {
      rejected.push(`doc quote not found in ${url}`);
    } else if (!valid.some((v) => v.url === section.url)) {
      valid.push({ url: section.url, quote: normalizeWhitespace(link.quote) });
    }
  }
  return { valid, rejected };
}

export function validateGraphqlFields(fields: string[], validFields: Set<string>): string[] {
  return Array.from(new Set((fields ?? []).map((field) => field.trim()).filter((field) => validFields.has(field))));
}

export function quoteInText(quote: string, text: string): boolean {
  const normalizedQuote = normalizeWhitespace(quote ?? '').toLowerCase();
  return normalizedQuote.length >= 5 && normalizeWhitespace(text).toLowerCase().includes(normalizedQuote);
}

const ALLOWED_URL = /^https:\/\/(github\.com\/BottlecapDave\/|bottlecapdave\.github\.io\/|([a-z0-9-]+\.)?octopus\.energy\/|(www\.)?home-assistant\.io\/)/i;

/**
 * Model prose is posted publicly, so: no HTML (which also stops it forging the hidden feedback
 * marker), no @mentions (no pinging arbitrary users), and no links outside a small allowlist
 * (no attacker-chosen URLs even if an injection slipped past screening).
 */
export function sanitizeModelText(text: string): string {
  return (
    (text ?? '')
      .replace(/<!--|-->/g, '')
      // GitHub renders nothing inside `code spans` (no HTML, links or mentions), so they're left
      // as-is - escaping there would show a literal "&lt;".
      .split(/(`[^`\n]*`)/)
      .map((part, index) =>
        index % 2 === 1
          ? part
          : part
              .replace(/</g, '&lt;')
              .replace(/(^|[^\w`])@([A-Za-z0-9][A-Za-z0-9-]*)/g, '$1`@$2`')
              .replace(/https?:\/\/[^\s)\]>"']+/gi, (url) => (ALLOWED_URL.test(url) ? url : '[link removed]')),
      )
      .join('')
      .trim()
  );
}

// Fields whose values identify the reporter, their property or their devices. Matched against the
// fields a query selects (what comes back), not its arguments (what the reporter supplies).
const IDENTIFYING_FIELD = /^(id|number|accountNumber|mpan|mprn|serialNumber|serial|meterSerialNumber|deviceId|krakenflexDeviceId|address|addressLine\d*|postcode|postCode|name|fullName|givenName|familyName|firstName|lastName|email|phone|phoneNumber|mobile|dateOfBirth|billingName|billingAddress\w*)$/i;

/**
 * A query the reporter may be asked to run must parse, be read-only, select no identifying fields,
 * and only use field names the integration already uses (or the fetched schema contains), so the
 * model can't invent fields. Returns why it's rejected, or null if it's fine.
 */
export function graphqlQueryProblem(query: string, knownFields: Set<string>): string | null {
  let document;
  try {
    document = parse(query);
  } catch (error) {
    return `does not parse (${(error as Error).message.split('\n')[0]})`;
  }

  const problems: string[] = [];
  visit(document, {
    OperationDefinition(node) {
      if (node.operation !== 'query') problems.push(`is a ${node.operation}, not a read-only query`);
    },
    Field(node) {
      const name = node.name.value;
      if (name.startsWith('__')) return;
      if (IDENTIFYING_FIELD.test(name)) problems.push(`selects identifying field "${name}"`);
      else if (!knownFields.has(name)) problems.push(`uses unknown field "${name}"`);
    },
  });
  return problems.length ? Array.from(new Set(problems)).join('; ') : null;
}
