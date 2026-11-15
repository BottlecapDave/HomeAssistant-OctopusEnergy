import { INTEGRATION_DOMAIN, SOURCE_REPO_PREFIX } from './config';

// ---------------------------------------------------------------------------------------------
// Secret redaction. Applied to every piece of reporter text before it is sent to the LLM. Comments
// are built only from validated model fields, so redacted values can never be echoed back.
// ---------------------------------------------------------------------------------------------

const REDACTIONS: Array<[RegExp, string]> = [
  [/sk_live_[A-Za-z0-9]+/g, '[REDACTED_API_KEY]'],
  [/\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}/g, '[REDACTED_TOKEN]'],
  [/\b(Bearer|JWT|Token)\s+[A-Za-z0-9._~+/=-]{12,}/gi, '$1 [REDACTED_TOKEN]'],
  [/("?(?:api_key|apikey|token|access_token|refresh_token|password|authorization)"?\s*[:=]\s*)"[^"]*"/gi, '$1"[REDACTED]"'],
  [/\bA-[0-9A-F]{8}\b/g, '[REDACTED_ACCOUNT]'],
  [/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g, '[REDACTED_EMAIL]'],
  // Entity ids embed the meter serial and MPAN/MPRN; keep the type and suffix (which identify the
  // entity class) but drop the identifiers.
  [/octopus_energy_(electricity|gas)_[a-z0-9]+_\d{6,13}/gi, 'octopus_energy_$1_<serial>_<id>'],
  // Account-level entity ids embed the account number (A-1234ABCD -> a_1234abcd).
  [/octopus_energy_a_[0-9a-z]{6,10}(?=_|\b)/gi, 'octopus_energy_a_<account>'],
  // Device ids (e.g. intelligent devices), hyphenated or as they appear in entity ids.
  [/(?<![0-9a-f])[0-9a-f]{8}[-_][0-9a-f]{4}[-_][0-9a-f]{4}[-_][0-9a-f]{4}[-_][0-9a-f]{12}(?![0-9a-f])/gi, '[REDACTED_ID]'],
  // Bare meter serials, e.g. typed into the tariff code field: electricity 22M0244366, gas E6S12345678961.
  [/(?<![A-Za-z0-9])\d{2}[A-Z]\d{7,8}(?![A-Za-z0-9])/gi, '[REDACTED_SERIAL]'],
  [/(?<![A-Za-z0-9])[EG]\d[A-Z][0-9A-Z]{8,}(?![A-Za-z0-9])/g, '[REDACTED_SERIAL]'],
  [/("?(?:mpan|mprn|serial_number|serial|device_id|meter_serial)"?\s*[:=]\s*)"?[A-Za-z0-9-]{5,}"?/gi, '$1"[REDACTED]"'],
  [/(?<![0-9])\d{13}(?![0-9])/g, '[REDACTED_MPAN]'],
];

export function redactSecrets(text: string): string {
  return REDACTIONS.reduce((result, [pattern, replacement]) => result.replace(pattern, replacement), text ?? '');
}

// ---------------------------------------------------------------------------------------------
// Diagnostics JSON. Reporters often paste the whole HA diagnostics download into the logs field;
// the system/manifest blocks waste the budget, but `data` (account, entity states) is useful.
// ---------------------------------------------------------------------------------------------

export interface DiagnosticsExtract {
  diagnostics: string | null;
  integrationVersion: string | null;
  rest: string;
}

const DIAGNOSTICS_DROP_KEYS = ['home_assistant', 'custom_components', 'integration_manifest', 'setup_times', 'issues'];

export function extractDiagnostics(text: string, maxLength: number): DiagnosticsExtract {
  const start = text.indexOf('"home_assistant"');
  if (start === -1) {
    return { diagnostics: null, integrationVersion: null, rest: text };
  }

  const openBrace = text.lastIndexOf('{', start);
  const integrationVersion =
    text.match(/"octopus_energy"\s*:\s*\{[^}]*?"version"\s*:\s*"(\d+\.\d+\.\d+(?:-[0-9a-z.]+)?)"/i)?.[1] ??
    text.match(/"domain"\s*:\s*"octopus_energy"[\s\S]*?"version"\s*:\s*"(\d+\.\d+\.\d+(?:-[0-9a-z.]+)?)"/i)?.[1] ??
    null;
  const haVersion = text.match(/"home_assistant"\s*:\s*\{[\s\S]*?"version"\s*:\s*"([^"]+)"/)?.[1] ?? 'unknown';

  // Find the end of the JSON object by brace matching (ignoring braces inside strings).
  let depth = 0;
  let end = -1;
  let inString = false;
  for (let i = openBrace; i < text.length && openBrace !== -1; i++) {
    const char = text[i];
    if (inString) {
      if (char === '\\') {
        i++;
      } else if (char === '"') {
        inString = false;
      }
    } else if (char === '"') {
      inString = true;
    } else if (char === '{') {
      depth++;
    } else if (char === '}') {
      depth--;
      if (depth === 0) {
        end = i;
        break;
      }
    }
  }

  const jsonText = end !== -1 ? text.slice(openBrace, end + 1) : text.slice(Math.max(openBrace, 0));
  const rest = end !== -1 ? `${text.slice(0, openBrace)}\n${text.slice(end + 1)}` : text.slice(0, Math.max(openBrace, 0));

  let compact: string;
  try {
    const parsed = JSON.parse(jsonText);
    for (const key of DIAGNOSTICS_DROP_KEYS) {
      delete parsed[key];
    }
    compact = JSON.stringify(parsed.data ?? parsed);
  } catch {
    // Truncated/invalid JSON - keep from "data" onwards with indentation squeezed out.
    const dataIndex = jsonText.indexOf('"data"');
    compact = (dataIndex !== -1 ? jsonText.slice(dataIndex) : jsonText).replace(/\n\s*/g, ' ');
  }

  const header = `integration version: ${integrationVersion ?? 'unknown'}, HA version: ${haVersion}`;
  const body = compact.length > maxLength ? `${compact.slice(0, maxLength)} ...[truncated]` : compact;
  return { diagnostics: `${header}\n${body}`, integrationVersion, rest };
}

// ---------------------------------------------------------------------------------------------
// Log reduction and retrieval signals
// ---------------------------------------------------------------------------------------------

export interface LogSignals {
  /** Repo-relative source files named by `custom_components.octopus_energy.*` logger names. */
  loggerFiles: string[];
  tracebackFrames: Array<{ file: string; line: number; func: string }>;
  exceptionTypes: string[];
  /** Other custom integration domains mentioned in the logs - a hint only, never decisive. */
  otherDomains: string[];
}

const HA_LOG_LINE = /^(\d{4}-\d{2}-\d{2}[ T][\d:.,]+)\s+(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+\(([^)]*)\)\s+\[([^\]]+)\]\s?(.*)$/;

interface LogRecord {
  index: number;
  level: string;
  logger: string;
  text: string;
  count: number;
}

function loggerToFiles(logger: string): string[] {
  const prefix = `custom_components.${INTEGRATION_DOMAIN}`;
  if (!logger.startsWith(prefix)) {
    return [];
  }
  const modulePath = logger.slice(prefix.length).replace(/^\./, '').split('.').filter(Boolean).join('/');
  return modulePath
    ? [`${SOURCE_REPO_PREFIX}/${modulePath}.py`, `${SOURCE_REPO_PREFIX}/${modulePath}/__init__.py`]
    : [`${SOURCE_REPO_PREFIX}/__init__.py`];
}

export function extractSignals(text: string): LogSignals {
  const loggerFiles = new Set<string>();
  for (const match of text.matchAll(/custom_components\.octopus_energy(?:\.[a-z0-9_]+)*/g)) {
    loggerToFiles(match[0]).forEach((file) => loggerFiles.add(file));
  }

  const tracebackFrames: LogSignals['tracebackFrames'] = [];
  for (const match of text.matchAll(/File "[^"]*custom_components\/octopus_energy\/([^"]+\.py)", line (\d+), in (\w+)/g)) {
    tracebackFrames.push({ file: `${SOURCE_REPO_PREFIX}/${match[1]}`, line: Number(match[2]), func: match[3] });
  }

  const exceptionTypes = Array.from(new Set(Array.from(text.matchAll(/\b([A-Z]\w*(?:Error|Exception))\b/g), (m) => m[1])));

  const otherDomains = new Set<string>();
  for (const match of text.matchAll(/custom_components[./]([a-z0-9_]+)/g)) {
    if (match[1] !== INTEGRATION_DOMAIN) {
      otherDomains.add(match[1]);
    }
  }

  return { loggerFiles: Array.from(loggerFiles), tracebackFrames, exceptionTypes, otherDomains: Array.from(otherDomains) };
}

// Metadata lines of the log viewer's "copy" format (Settings > System > Logs), which reporters
// paste as often as raw log lines.
const LOG_VIEWER_METADATA = /^(Logger|Source|Integration|First occurred|Last logged|This error originated)\b/i;

/**
 * The first warning/error message in the logs, preferring this integration's - used as a search
 * signal for duplicates, since a generic title ("Error after updating") often hides a specific error.
 * Handles raw HA log lines and the log viewer's copy format (metadata block, blank line, message).
 */
export function firstLogMessage(text: string): string | null {
  const messages: Array<{ message: string; ours: boolean }> = [];
  const lines = (text ?? '').replace(/\r\n?/g, '\n').split('\n');
  let afterMetadata = false;
  for (const line of lines) {
    const raw = line.match(HA_LOG_LINE);
    if (raw) {
      if (['WARNING', 'ERROR', 'CRITICAL'].includes(raw[2]) && raw[5].trim()) {
        messages.push({ message: raw[5].trim(), ours: raw[4].startsWith(`custom_components.${INTEGRATION_DOMAIN}`) || raw[5].includes(INTEGRATION_DOMAIN) });
      }
      afterMetadata = false;
      continue;
    }
    const trimmed = line.trim().replace(/^>\s*/, '');
    if (LOG_VIEWER_METADATA.test(trimmed)) {
      afterMetadata = true;
    } else if (afterMetadata && trimmed && !trimmed.startsWith('```')) {
      messages.push({ message: trimmed, ours: trimmed.includes(INTEGRATION_DOMAIN) });
      afterMetadata = false;
    }
  }
  const chosen = messages.find((m) => m.ours) ?? messages[0];
  // Quoted values and URLs are instance-specific (entry names, entity ids) - keep the wording.
  return chosen ? chosen.message.replace(/'[^']*'|"[^"]*"|https?:\/\/\S+/g, ' ').replace(/\s+/g, ' ').trim() || null : null;
}

function recordPriority(record: LogRecord): number {
  const ours = record.logger.startsWith(`custom_components.${INTEGRATION_DOMAIN}`) || record.text.includes(`/${INTEGRATION_DOMAIN}/`);
  const severe = record.level === 'ERROR' || record.level === 'CRITICAL';
  const hasTraceback = record.text.includes('Traceback');
  if (ours && (severe || hasTraceback)) return 4;
  if (ours && record.level === 'WARNING') return 3;
  if (ours) return 2;
  if (severe || hasTraceback) return 1;
  if (record.level === 'WARNING') return 0.5;
  return 0;
}

/**
 * Keeps the parts of a log that matter for triage: tracebacks, warnings/errors, and anything from
 * this integration's loggers. Repeated lines are collapsed, and when over budget the highest
 * priority and most recent records win. Text that isn't in HA log format is kept head+tail.
 */
export function reduceLogs(text: string, maxLength: number): string {
  if (!text.trim()) {
    return '';
  }

  const lines = text.replace(/\r\n?/g, '\n').split('\n');
  const records: LogRecord[] = [];
  let current: LogRecord | null = null;

  for (const line of lines) {
    const match = line.match(HA_LOG_LINE);
    if (match) {
      current = { index: records.length, level: match[2], logger: match[4], text: line, count: 1 };
      records.push(current);
    } else if (current && line.trim() && !line.startsWith('```')) {
      current.text += `\n${line}`;
    }
  }

  if (records.length === 0) {
    if (text.length <= maxLength) {
      return text.trim();
    }
    const half = Math.floor(maxLength / 2);
    return `${text.slice(0, half)}\n...[middle of log omitted]...\n${text.slice(-half)}`;
  }

  // Collapse repeats (same level/logger/message once digits are ignored), keeping the latest.
  const byKey = new Map<string, LogRecord>();
  for (const record of records) {
    const message = record.text.replace(HA_LOG_LINE, '$2 $4 $5').replace(/\d+/g, '#');
    const existing = byKey.get(message);
    if (existing) {
      record.count = existing.count + 1;
      byKey.delete(message);
    }
    byKey.set(message, record);
  }

  const candidates = Array.from(byKey.values())
    .filter((record) => recordPriority(record) > 0)
    .sort((a, b) => recordPriority(b) - recordPriority(a) || b.index - a.index);

  const selected: LogRecord[] = [];
  let length = 0;
  for (const record of candidates) {
    const rendered = record.count > 1 ? `${record.text}  (repeated ${record.count}x)` : record.text;
    if (length + rendered.length + 1 > maxLength) {
      continue;
    }
    selected.push({ ...record, text: rendered });
    length += rendered.length + 1;
  }

  const omitted = records.length - selected.length;
  const output = selected.sort((a, b) => a.index - b.index).map((record) => record.text).join('\n');
  return omitted > 0 ? `${output}\n...[${omitted} lower-priority or repeated log line(s) omitted]` : output;
}

// ---------------------------------------------------------------------------------------------
// Attachments (bug issues with log consent only)
// ---------------------------------------------------------------------------------------------

const ATTACHMENT_URL = /https:\/\/github\.com\/user-attachments\/files\/\d+\/[^\s)\]"'<>]+/g;
const MAX_ATTACHMENTS = 3;
const MAX_ATTACHMENT_BYTES = 1024 * 1024;

function isAllowedRedirectHost(url: URL): boolean {
  return (
    url.protocol === 'https:' &&
    (url.hostname.endsWith('.githubusercontent.com') ||
      (url.hostname.startsWith('github-production-') && url.hostname.endsWith('.s3.amazonaws.com')))
  );
}

/**
 * Downloads `.log`/`.txt` attachments from GitHub's user-attachments store. Only that URL shape is
 * fetched, at most one redirect is followed and only to GitHub's storage hosts, files over 1MB
 * (or without a declared size) are skipped, and the content is only ever treated as text.
 */
export async function fetchAttachmentLogs(body: string): Promise<Array<{ name: string; text: string }>> {
  // The same file is often linked twice with differently-encoded names (e.g. the link text and its
  // URL), so dedupe by GitHub's file id rather than the URL string.
  const byFileId = new Map<string, string>();
  for (const url of body.match(ATTACHMENT_URL) ?? []) {
    const id = url.match(/\/files\/(\d+)\//)?.[1] ?? url;
    if (!byFileId.has(id)) byFileId.set(id, url);
  }
  const urls = Array.from(byFileId.values())
    // .json: the FAQ asks reporters to attach the diagnostics download, which is a JSON file.
    .filter((url) => /\.(log|txt|json)$/i.test(new URL(url).pathname))
    .slice(0, MAX_ATTACHMENTS);

  const results: Array<{ name: string; text: string }> = [];
  for (const url of urls) {
    try {
      let response = await fetch(url, { redirect: 'manual', signal: AbortSignal.timeout(10000) });
      if (response.status >= 300 && response.status < 400) {
        const location = response.headers.get('location');
        const target = location ? new URL(location, url) : null;
        if (!target || !isAllowedRedirectHost(target)) {
          console.warn(`Skipping attachment ${url}: redirect to disallowed host`);
          continue;
        }
        response = await fetch(target, { redirect: 'error', signal: AbortSignal.timeout(10000) });
      }
      if (!response.ok) {
        console.warn(`Skipping attachment ${url}: ${response.status}`);
        continue;
      }
      const size = Number(response.headers.get('content-length'));
      if (!size || size > MAX_ATTACHMENT_BYTES) {
        console.warn(`Skipping attachment ${url}: size ${size || 'unknown'} exceeds limit`);
        continue;
      }
      const text = await response.text();
      // Reporters sometimes upload the same file twice (#1948).
      if (results.some((existing) => existing.text === text)) continue;
      results.push({ name: decodeURIComponent(new URL(url).pathname.split('/').pop() ?? 'attachment'), text });
    } catch (error) {
      console.warn(`Skipping attachment ${url}: ${(error as Error).message}`);
    }
  }
  return results;
}
