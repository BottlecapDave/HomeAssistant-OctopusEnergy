import { buildAnalysisComment, buildDuplicateComment, buildFixedInNewerVersionComment, CommentContext } from './comments';
import { BUG_LABEL, ENHANCEMENT_LABEL, INTEGRATION_DOMAIN, KNOWN_SIBLING_INTEGRATIONS, LABELS } from './config';
import { DocSection, DocsIndex, renderDocSections } from './docs';
import { GithubClient, GithubIssueSummary } from './github';
import { buildSchemaContext, featureNeedsSchema } from './graphql';
import { GithubIssue, hasAiTriageConsent, hasLogConsent, isBotAuthor, isGenericTitle, parseIssueForm, parseReportedVersion } from './issue';
import { callJson, CostTracker, LlmConfig, loadPrompt } from './llm';
import { extractDiagnostics, extractSignals, fetchAttachmentLogs, firstLogMessage, reduceLogs, redactSecrets } from './logs';
import { CodeChunk, CodeIndex, renderChunks } from './retrieval';
import {
  Analysis,
  AnalysisOutcome,
  analysisSchema,
  BUG_OUTCOMES,
  CHANGELOG_SCHEMA,
  ChangelogMatchResult,
  CRITIC_SCHEMA,
  CriticResult,
  DOCS_OUTCOMES,
  DUPLICATE_SCHEMA,
  DuplicateResult,
  FEATURE_OUTCOMES,
  FILTER_SCHEMA,
  FilterResult,
  Outcome,
} from './schemas';
import { checkTariffs, TariffCheck } from './tariff';
import { CONTENT_TAG, heuristicTamperDetected, sanitizeUntrustedText, tokenize } from './text';
import { graphqlQueryProblem, quoteInText, validateDocLinks, validateEvidence, validateGraphqlFields } from './validate';
import {
  ChangelogLine,
  compareVersions,
  currentVersion,
  isMinorOrMoreBehind,
  parseChangelog,
  plainChangelogText,
  releasesBetween,
  splitVersion,
  upgradeReleaseNotes,
} from './version';

// Budgets in characters (~4 chars per token). Together these keep the analysis call around 30-40k
// tokens of input.
const BUDGET = {
  section: 5000,
  logs: 14000,
  diagnostics: 6000,
  issueTotal: 40000,
  code: 80000,
  docs: 25000,
};

// Only outcomes that assert something (a cause, an answer, "this belongs elsewhere") need a minimum
// confidence. needs_info and implementation_notes are pointers - questions for the reporter, or
// where to start for the maintainer - so the critic alone judges whether they're worth posting.
const MIN_CONFIDENCE: Record<string, number> = {
  root_cause: 0.7,
  already_supported: 0.75,
  docs_answer: 0.65, // also needs a verified doc quote and the critic's approval
  wrong_repo: 0.8,
};
const DUPLICATE_MIN_CONFIDENCE = 0.85;
const CHANGELOG_MIN_CONFIDENCE = 0.75;
const CRITIC_MIN_SCORE = 4;
// Asking a reporter to run a GraphQL query is only worth it when the model has a specific hypothesis.
const GRAPHQL_QUESTION_MIN_CONFIDENCE = 0.8;

export interface TriageContext {
  llm: LlmConfig;
  github: GithubClient;
  commentContext: CommentContext;
}

export interface TriageResult {
  /** comment: post `comment` (+labels). assign: hand to the maintainer without commenting. ignore: do nothing. */
  action: 'comment' | 'assign' | 'ignore';
  outcome: Outcome | null;
  reason: string;
  comment: string | null;
  labels: string[];
  gates: string[];
  analysis?: Analysis;
  critic?: CriticResult;
  /** A comment that was drafted but blocked by the critic (kept for dry runs/evals). */
  draft?: string;
  /** Replacement for a generic title, applied whatever the action (it helps the maintainer and duplicate search too). */
  newTitle?: string;
  /** Set when triage crashed (e.g. an LLM/API error); the issue is handed to the maintainer. */
  error?: string;
  evidenceFiles: string[];
  costs: CostTracker;
}

let codeIndex: CodeIndex | null = null;
let docsIndex: DocsIndex | null = null;
const getCode = () => (codeIndex ??= new CodeIndex());
const getDocs = () => (docsIndex ??= new DocsIndex());

interface PreparedIssue {
  issue: GithubIssue;
  isBug: boolean;
  isFeature: boolean;
  /** Redacted issue text sent to the model, wrapped in the untrusted-content tags. */
  issueBlock: string;
  /** Title + non-log form sections only: what the reporter wrote in their own words. */
  reporterText: string;
  retrievalQuery: string;
  /** The form's Tariff Code field, checked against Octopus's public API. */
  tariffText: string;
  /** Provider name from the "Unknown intelligent provider" form, if it's a plain identifier. */
  provider: string | null;
  signals: ReturnType<typeof extractSignals>;
  /** First warning/error message in the logs (quoted values stripped), for duplicate search. */
  logMessage: string | null;
  /** x.y.z only, so version arithmetic works; see reportedPrerelease / displayVersion. */
  reportedVersion: string | null;
  /** e.g. "beta.4" when the reporter is on a pre-release, else null. */
  reportedPrerelease: string | null;
  /** The version as the reporter has it, for showing them (e.g. "19.0.0-beta.4"). */
  displayVersion: string | null;
  /** Whether reportedVersion is a release in CHANGELOG.md. False for e.g. another integration's "4.1.6" (#1872). */
  knownRelease: boolean;
  freshInstall: string;
  rawForTamperCheck: string[];
}

async function prepareIssue(issue: GithubIssue): Promise<PreparedIssue> {
  const parsed = parseIssueForm(issue.body);
  const isBug = issue.labels.includes(BUG_LABEL);
  const isFeature = issue.labels.includes(ENHANCEMENT_LABEL);

  // Attachments are only read for bug reports whose consent explicitly covers logs.
  const attachments = isBug && hasLogConsent(issue.body) ? await fetchAttachmentLogs(issue.body) : [];
  const diagnostics = extractDiagnostics(parsed.get('logs'), BUDGET.diagnostics);
  const rawLogs = [diagnostics.rest, ...attachments.map((a) => `--- attachment: ${a.name} ---\n${a.text}`)].join('\n').trim();
  const reducedLogs = reduceLogs(rawLogs, BUDGET.logs);

  const ownSections = parsed.sections
    .filter((section) => section.key !== 'logs')
    .map((section) => {
      const content = section.content.length > BUDGET.section ? `${section.content.slice(0, BUDGET.section)}\n...[truncated]` : section.content;
      return `## ${section.heading}\n${content || '(empty)'}`;
    });

  const reporterText = redactSecrets([`Title: ${issue.title}`, ...ownSections].join('\n\n'));
  const issueText = redactSecrets(
    [
      `Title: ${issue.title}`,
      ...ownSections,
      reducedLogs ? `## Logs (reduced to warnings/errors/tracebacks and this integration's lines)\n${reducedLogs}` : '',
      diagnostics.diagnostics ? `## Diagnostics (condensed)\n${diagnostics.diagnostics}` : '',
    ]
      .filter(Boolean)
      .join('\n\n'),
  );
  const sanitized = sanitizeUntrustedText(issueText, BUDGET.issueTotal);
  const displayVersion = parseReportedVersion(parsed.get('integration_version')) ?? diagnostics.integrationVersion;
  const { base: reportedVersion, prerelease: reportedPrerelease } = splitVersion(displayVersion);

  return {
    issue,
    isBug,
    isFeature,
    issueBlock: `<${CONTENT_TAG}>\n${sanitized}\n</${CONTENT_TAG}>`,
    reporterText,
    // The provider name finds the provider lists in intelligent/__init__.py.
    retrievalQuery: [issue.title, parsed.get('provider'), parsed.get('description'), parsed.get('preamble'), parsed.get('reproduction'), parsed.get('expected'), parsed.get('use_case'), reducedLogs].join('\n'),
    // Only a plain provider id is used in notes (it's reporter-supplied).
    provider: /^[A-Za-z0-9_ -]{2,40}$/.test(parsed.get('provider').trim()) ? parsed.get('provider').trim() : null,
    signals: extractSignals(`${rawLogs}\n${issue.body}`),
    logMessage: firstLogMessage(redactSecrets(rawLogs)),
    reportedVersion,
    reportedPrerelease,
    displayVersion: reportedVersion ? displayVersion : null,
    knownRelease: Boolean(reportedVersion && parseChangelog().some((release) => release.version === reportedVersion)),
    freshInstall: parsed.get('fresh_install'),
    tariffText: parsed.get('tariff'),
    rawForTamperCheck: [issue.title, issue.body, ...attachments.map((a) => a.text)],
  };
}

function untrustedBlock(text: string): string {
  return `<${CONTENT_TAG}>\n${sanitizeUntrustedText(text, BUDGET.issueTotal)}\n</${CONTENT_TAG}>`;
}

async function runCritic(
  ctx: TriageContext,
  costs: CostTracker,
  prepared: PreparedIssue,
  outcome: Outcome,
  facts: string,
  comment: string,
  gates: string[],
  linkedIssue?: string,
): Promise<CriticResult> {
  const critic = await callJson<CriticResult>(
    ctx.llm,
    costs,
    'critic',
    ctx.llm.filterModel,
    loadPrompt('comment-critic.txt', { REPLY_TYPE: outcome, FACTS: facts || '- (none)' }),
    [
      `Issue:`,
      prepared.issueBlock,
      '',
      'Draft reply:',
      '"""',
      comment.replace(/<!--[\s\S]*?-->/g, '').trim(),
      '"""',
      // Another reporter's text, so it stays inside the untrusted block like the issue itself.
      ...(linkedIssue ? ['', 'The existing issue the draft links to (its state as of when the new issue was opened, title and start of body):', untrustedBlock(linkedIssue)] : []),
    ].join('\n'),
    CRITIC_SCHEMA,
  );
  gates.push(`critic score ${critic.score}${critic.problems?.length ? ` (${critic.problems.join('; ')})` : ''}`);
  return critic;
}

async function checkFixedInNewerVersion(
  ctx: TriageContext,
  costs: CostTracker,
  prepared: PreparedIssue,
  latest: string,
  gates: string[],
): Promise<Array<ChangelogLine & { why: string }> | null> {
  const reported = prepared.reportedVersion;
  const lines = releasesBetween(parseChangelog(), reported, latest).flatMap((release) => release.lines);
  if (!lines.length) {
    gates.push('version: no changelog entries between reported and latest');
    return null;
  }

  // Deterministic: the reporter references an issue that a newer release closed.
  const referenced = new Set(Array.from(prepared.reporterText.matchAll(/#(\d+)/g), (m) => Number(m[1])));
  const direct = lines.filter((line) => line.closes.some((n) => referenced.has(n) && n !== prepared.issue.number));
  if (direct.length) {
    gates.push('version: reporter referenced an issue closed by a newer release');
    return direct.map((line) => ({ ...line, why: `This release closed ${line.closes.map((n) => `#${n}`).join(', ')}, which you referenced.` }));
  }

  const entries = lines.map((line) => `[${line.id}] (v${line.version}, ${line.section}) ${plainChangelogText(line.text)}`).join('\n');

  const result = await callJson<ChangelogMatchResult>(
    ctx.llm,
    costs,
    'changelog-match',
    ctx.llm.filterModel,
    loadPrompt('changelog-match.txt', { REPORTED_VERSION: reported, LATEST_VERSION: latest }),
    ['Changelog entries released since the reporter\'s version:', entries, '', 'New issue:', prepared.issueBlock].join('\n'),
    CHANGELOG_SCHEMA,
  );

  const byId = new Map(lines.map((line) => [line.id, line]));
  const unique = new Map<string, ChangelogLine & { why: string }>();
  for (const match of (result.matches ?? []).filter((m) => byId.has(m.line_id))) {
    const line = byId.get(match.line_id);
    const key = plainChangelogText(line.text).replace(/\s*\(Thanks[^)]*\)/i, '').toLowerCase();
    const existing = unique.get(key);
    const longer = existing && existing.text.length >= line.text.length ? existing : line;
    unique.set(key, { ...longer, closes: Array.from(new Set([...(existing?.closes ?? []), ...line.closes])), why: existing?.why ?? match.why });
  }
  const matches = Array.from(unique.values());
  gates.push(`version: changelog match confidence ${result.confidence}, ${matches.length} valid match(es)`);
  return matches.length && result.confidence >= CHANGELOG_MIN_CONFIDENCE ? matches : null;
}

async function checkDuplicate(
  ctx: TriageContext,
  costs: CostTracker,
  prepared: PreparedIssue,
  gates: string[],
): Promise<{ number: number; title: string; state: string; why: string; excerpt: string } | null> {
  // Titles are often generic ("Error after updating") while the logs or an action name carry the
  // real signal, so candidates come from up to three searches, merged in order.
  const searchTerms = (text: string) => Array.from(new Set(tokenize(text).filter((t) => t !== INTEGRATION_DOMAIN && !/^v\d/.test(t)))).slice(0, 5);
  const actionNames = Array.from(new Set(Array.from(`${prepared.issue.title}\n${prepared.issue.body}`.matchAll(/\boctopus_energy\.([a-z][a-z0-9_]{5,})\b/g), (m) => m[1])));
  const searches = [
    { name: 'title', terms: searchTerms(prepared.issue.title) },
    { name: 'log message', terms: prepared.logMessage ? searchTerms(prepared.logMessage) : [] },
    { name: 'actions/exceptions', terms: [...actionNames, ...prepared.signals.exceptionTypes].slice(0, 5) },
  ].filter((search) => search.terms.length);
  if (!searches.length) {
    return null;
  }
  // Only earlier issues can be the original (also keeps evals on old issues honest). Full timestamp,
  // not just the date: double submissions and outage reports arrive minutes apart (#1773 -> #1774).
  const before = prepared.issue.createdAt ? ` created:<${prepared.issue.createdAt}` : '';
  const results: GithubIssueSummary[][] = [];
  for (const search of searches) {
    try {
      results.push(await ctx.github.searchIssues(`${search.terms.join(' OR ')}${before}`, 10));
    } catch (error) {
      gates.push(`duplicate: ${search.name} search failed (${(error as Error).message})`);
    }
  }
  // Interleave so each search's best matches make the cut.
  const byNumber = new Map<number, GithubIssueSummary>();
  for (let rank = 0; rank < 10; rank++) {
    for (const result of results) {
      const candidate = result[rank];
      if (candidate && candidate.number !== prepared.issue.number && !byNumber.has(candidate.number)) byNumber.set(candidate.number, candidate);
    }
  }
  const candidates = Array.from(byNumber.values()).slice(0, 15);
  gates.push(`duplicate: ${candidates.length} candidate(s) from ${searches.map((s) => `${s.name} [${s.terms.join(', ')}]`).join('; ')}`);
  if (!candidates.length) {
    gates.push('duplicate: no candidates');
    return null;
  }

  // State as it was when the new issue was opened: replaying an old issue (evals) must not see an
  // original that was closed later as "closed", which reads as a possible regression.
  const createdAt = prepared.issue.createdAt;
  // Closed issues carry why they were closed: a declined request (#1717 -> #1570) is a duplicate,
  // while a bug closed as fixed may be a regression.
  const stateThen = (c: GithubIssueSummary) =>
    c.state !== 'closed' || (createdAt && c.closed_at && c.closed_at > createdAt)
      ? 'open'
      : `closed as ${c.state_reason === 'not_planned' ? 'not planned' : c.state_reason === 'duplicate' ? 'duplicate' : 'completed'}`;
  const candidateText = candidates
    .map((c) => `#${c.number} [${stateThen(c)}] ${c.title}\n${redactSecrets((c.body ?? '').slice(0, 500))}`)
    .join('\n\n');
  const result = await callJson<DuplicateResult>(
    ctx.llm,
    costs,
    'duplicate-check',
    ctx.llm.filterModel,
    loadPrompt('duplicate-check.txt'),
    ['Candidate existing issues:', untrustedBlock(candidateText), '', `New issue (${prepared.isFeature ? 'feature request' : 'bug report'}):`, prepared.issueBlock].join('\n'),
    DUPLICATE_SCHEMA,
  );

  const match = candidates.find((c) => c.number === result.duplicate_of);
  gates.push(`duplicate: ${result.duplicate_of ? `#${result.duplicate_of}` : 'no match'}, confidence ${result.confidence}${match || !result.duplicate_of ? '' : ' (not a candidate - ignored)'}`);
  return match && result.confidence >= DUPLICATE_MIN_CONFIDENCE
    ? { number: match.number, title: match.title, state: stateThen(match), why: result.why, excerpt: `#${match.number} [${stateThen(match)}] ${match.title}\n${redactSecrets((match.body ?? '').slice(0, 1500))}` }
    : null;
}

/** Field names a reporter query may use: identifiers in the integration's own API client, plus schema fields. */
function graphqlKnownFields(code: CodeIndex, schemaFields: Set<string>): Set<string> {
  const known = new Set<string>();
  for (const source of code.files.values()) {
    if (source.file.includes('/api_client')) {
      (source.lines.join('\n').match(/[A-Za-z_][A-Za-z0-9_]*/g) ?? []).forEach((word) => known.add(word));
    }
  }
  schemaFields.forEach((field) => field.split('.').forEach((part) => known.add(part)));
  return known;
}

const MAX_TITLE_CHARS = 80;

/**
 * The model's suggested title, but only for a title the offline check also finds generic (so
 * specific titles are never rewritten), and only if it's plain text with nothing identifying.
 */
function retitle(current: string, suggested: string, gates: string[]): string | undefined {
  const title = (suggested ?? '').replace(/\s+/g, ' ').replace(/^["']|["'.]$/g, '').trim();
  if (!isGenericTitle(current)) {
    if (title) gates.push('title: kept (current title is specific)');
    return undefined;
  }
  const problem = !title
    ? 'no suggestion'
    : title.length > MAX_TITLE_CHARS
      ? 'suggestion too long'
      : /[<>@`[\]]|https?:/i.test(title)
        ? 'suggestion contains markup or a link'
        : redactSecrets(title) !== title
          ? 'suggestion contains an identifier'
          : title.toLowerCase() === current.trim().toLowerCase() || isGenericTitle(title)
            ? 'suggestion is no more specific'
            : null;
  gates.push(problem ? `title: generic, not changed (${problem})` : `title: "${current}" -> "${title}"`);
  return problem ? undefined : title;
}

// What each outcome must still be backed by after validation, or it is downgraded.
const GROUNDED: Partial<Record<AnalysisOutcome, { ok: (a: Analysis) => boolean; reason: string }>> = {
  root_cause: { ok: (a) => a.evidence.length > 0, reason: 'no verifiable code evidence' },
  implementation_notes: { ok: (a) => a.evidence.length > 0 || a.graphql_fields.length > 0, reason: 'no verifiable code or schema references' },
  already_supported: { ok: (a) => a.evidence.length > 0 || a.doc_links.length > 0, reason: 'no verifiable code or docs' },
  docs_answer: { ok: (a) => a.doc_links.length > 0, reason: 'no verifiable documentation quote' },
};

async function buildAnalysisPrompt(
  prepared: PreparedIssue,
  kind: 'bug' | 'feature' | 'docs',
  chunks: CodeChunk[],
  docSections: DocSection[],
  latest: string | null,
  gates: string[],
  tariffFacts: string[] = [],
): Promise<{ prompt: string; validFields: Set<string> }> {
  const parts = ['# Source excerpts (function-level, with line numbers)', renderChunks(chunks) || '(none matched)', '', '# Documentation sections', renderDocSections(docSections) || '(none matched)'];

  let validFields = new Set<string>();
  if (kind === 'feature' && featureNeedsSchema(prepared.retrievalQuery)) {
    const schema = await buildSchemaContext(prepared.retrievalQuery);
    validFields = schema.validFields;
    if (schema.text) {
      parts.push('', '# GraphQL schema summary (deprecated fields omitted)', schema.text);
      gates.push('retrieval: graphql schema included');
    }
  }

  const notes = [
    ...(tariffFacts.length
      ? [
          '- Octopus Energy public API check of the reported tariff, run by the triage bot (verified - you may state these facts; if they show an unknown product or no rates, the problem is on Octopus Energy\'s side and any repair documentation shown says what the reporter should do):',
          ...tariffFacts.map((fact) => `  ${fact}`),
        ]
      : []),
    prepared.provider
      ? `- Raised from the "Unknown intelligent provider" form for provider "${prepared.provider}" (the repair notice the integration shows for providers it doesn't recognise). If the source excerpts already handle this provider name, choose "already_supported" and quote where - the reporter is most likely on an older version and needs to update. Otherwise choose "implementation_notes": where the provider would be added, and which features to enable based on what the reporter says the Octopus app offers for it (bump charge, charge target, target time, smart charge, planned dispatches).`
      : '',
    prepared.reportedVersion
      ? `- Reporter's integration version: ${prepared.displayVersion}${prepared.reportedPrerelease ? ' (a pre-release)' : ''}${latest ? ` (latest release: ${latest})` : ''}`
      : '',
    prepared.reportedVersion && !prepared.reportedPrerelease && !prepared.knownRelease && latest && compareVersions(prepared.reportedVersion, latest) < 0
      ? `- The reported version ${prepared.reportedVersion} is not a release of this integration - it may be a typo, or another integration's version.`
      : '',
    prepared.signals.exceptionTypes.length ? `- Exception types seen in logs: ${prepared.signals.exceptionTypes.join(', ')}` : '',
    prepared.signals.otherDomains.length
      ? `- Other custom integrations appearing in the logs (a hint only - logs routinely include other integrations): ${prepared.signals.otherDomains.join(', ')}`
      : '',
    `- Known separate integrations for "wrong_repo" (use these exact domains): ${Object.keys(KNOWN_SIBLING_INTEGRATIONS).join(', ')}. Otherwise use the other integration's domain if the reporter's text shows it, "home_assistant" for Home Assistant itself, "user_configuration" for the reporter's own templates/automations, or "unknown".`,
  ].filter(Boolean);
  parts.push('', '# Notes', ...notes, '', '# Issue', prepared.issueBlock);

  return { prompt: parts.join('\n'), validFields };
}

async function runAnalysis(ctx: TriageContext, costs: CostTracker, prepared: PreparedIssue, latest: string | null, gates: string[], tariff: TariffCheck): Promise<Analysis> {
  const code = getCode();
  const chunks = code.select(prepared.retrievalQuery, prepared.signals, BUDGET.code);
  const docSections = getDocs().select(prepared.retrievalQuery, BUDGET.docs);
  // After an upgrade, the release notes (including breaking changes) are quotable doc sections, so an
  // intended change (#1514 renamed entities, #1476 water heater) can be answered from them.
  if (prepared.isBug && prepared.reportedVersion && /upgrad/i.test(prepared.freshInstall)) {
    const releaseNotes = upgradeReleaseNotes(prepared.reportedVersion, parseChangelog());
    if (releaseNotes.length) {
      docSections.unshift(...releaseNotes);
      gates.push(`retrieval: release notes included (${releaseNotes.map((s) => s.page).join(', ')})`);
    }
  }
  // When the tariff check finds an Octopus-side problem, include the repair page that tells the
  // reporter what to do, so the answer can quote it.
  const repairPages = Array.from(new Set(tariff.problems.map((p) => (p === 'product_not_found' ? '/repairs/unknown_product/' : '/repairs/tariff_rates_empty/'))));
  const repairs = getDocs().sections.filter((s) => repairPages.some((page) => s.url.includes(page)) && !docSections.includes(s));
  if (repairs.length) {
    docSections.unshift(...repairs);
    gates.push(`retrieval: repair docs included for tariff check (${repairPages.join(', ')})`);
  }
  gates.push(`retrieval: ${chunks.length} code chunk(s) from ${new Set(chunks.map((c) => c.file)).size} file(s), ${docSections.length} doc section(s)`);

  const kind = prepared.isBug ? 'bug' : prepared.isFeature ? 'feature' : 'docs';
  const promptFile = { bug: 'bug-diagnosis.txt', feature: 'feature-analysis.txt', docs: 'docs-answer.txt' }[kind];
  const outcomes: string[] = { bug: BUG_OUTCOMES, feature: FEATURE_OUTCOMES, docs: DOCS_OUTCOMES }[kind];
  const { prompt, validFields } = await buildAnalysisPrompt(prepared, kind, chunks, docSections, latest, gates, tariff.facts);

  const raw = await callJson<Analysis>(
    ctx.llm,
    costs,
    `analysis:${kind}`,
    ctx.llm.analysisModel,
    loadPrompt(promptFile, { OUTCOMES: outcomes.map((o) => `"${o}"`).join(', ') }),
    prompt,
    analysisSchema(outcomes),
    12000, // observed up to ~3.3k including reasoning; 6k was too tight, and the cap is reserved up front

  );

  const analysis: Analysis = { ...raw, confidence: Number(raw.confidence) || 0 };
  if (!outcomes.includes(analysis.outcome)) {
    gates.push(`model returned invalid outcome ${analysis.outcome}`);
    analysis.outcome = 'none';
  }
  gates.push(`analysis: ${analysis.outcome} confidence ${analysis.confidence}`);

  // ---- Deterministic gates ----
  const evidence = validateEvidence(analysis.evidence, code);
  const links = validateDocLinks(analysis.doc_links, docSections);
  analysis.evidence = evidence.valid;
  analysis.doc_links = links.valid;
  analysis.graphql_fields = validateGraphqlFields(analysis.graphql_fields, validFields);
  [...evidence.rejected, ...links.rejected].forEach((r) => gates.push(`rejected ${r}`));

  // GraphQL query questions: only with high confidence, and only safe, grounded, read-only queries.
  const knownFields = graphqlKnownFields(code, validFields);
  analysis.questions_for_reporter = analysis.questions_for_reporter.filter((question) => {
    const query = question.graphql_query?.trim();
    const text = `${question.ask} ${question.why}`;
    // A query written into the question text would bypass every check below, so it's never allowed.
    const inlineQuery = /\b(query|mutation)\s*\w*\s*(\([^)]*\))?\s*\{/i.test(text);
    if (!query && !inlineQuery && !/run_graphql_query/i.test(text)) return true;
    const problem = inlineQuery
      ? 'query written in the question text, so it could not be checked'
      : !query
        ? 'asks the reporter to run a query without providing one that can be checked'
        : analysis.confidence < GRAPHQL_QUESTION_MIN_CONFIDENCE
          ? `confidence ${analysis.confidence} below ${GRAPHQL_QUESTION_MIN_CONFIDENCE}`
          : graphqlQueryProblem(query, knownFields);
    if (problem) gates.push(`removed graphql question: ${problem}`);
    return !problem;
  });

  const rule = GROUNDED[analysis.outcome];
  if (rule && !rule.ok(analysis)) {
    const next = analysis.questions_for_reporter.length ? 'needs_info' : 'none';
    gates.push(`downgraded ${analysis.outcome} -> ${next}: ${rule.reason}`);
    analysis.outcome = next;
  }
  // Known siblings get a link to their repo; anything else gets a generic "not this integration"
  // reply. Either way the reporter's own words must show it - logs alone can never trigger it.
  const otherIntegration = analysis.other_integration.trim();
  if (analysis.outcome === 'wrong_repo' && (!otherIntegration || otherIntegration === INTEGRATION_DOMAIN || !quoteInText(analysis.issue_quote, prepared.reporterText))) {
    gates.push(`downgraded wrong_repo -> none: other_integration "${analysis.other_integration}" missing/invalid or issue_quote not in reporter's own text`);
    analysis.outcome = 'none';
  }
  if (analysis.outcome === 'needs_info' && !analysis.questions_for_reporter.length) {
    gates.push('downgraded needs_info -> none: no questions');
    analysis.outcome = 'none';
  }

  return analysis;
}

export async function triageIssue(issue: GithubIssue, ctx: TriageContext): Promise<TriageResult> {
  const costs = new CostTracker();
  const gates: string[] = [];
  try {
    return await runTriage(issue, ctx, costs, gates);
  } catch (error) {
    // Never leave an issue unhandled: a crash hands it to the maintainer like any other "no answer".
    const message = (error as Error).message;
    gates.push(`error: ${message}`);
    return { action: 'assign', outcome: null, reason: `triage failed: ${message}`, comment: null, labels: [LABELS.noAnswer], gates, evidenceFiles: [], costs, error: message };
  }
}

async function runTriage(issue: GithubIssue, ctx: TriageContext, costs: CostTracker, gates: string[]): Promise<TriageResult> {
  const result = (action: TriageResult['action'], outcome: Outcome | null, reason: string, extra: Partial<TriageResult> = {}): TriageResult => ({
    action,
    outcome,
    reason,
    comment: null,
    labels: action === 'assign' ? [LABELS.noAnswer] : [],
    gates,
    evidenceFiles: [],
    costs,
    ...extra,
  });

  if (isBotAuthor(issue.author)) {
    return result('ignore', null, `raised by ${issue.author.login} (a bot)`);
  }
  if (!hasAiTriageConsent(issue.body)) {
    // Assign only - no AI label on an issue whose reporter declined AI processing.
    return result('assign', null, 'reporter did not consent to AI triage', { labels: [] });
  }

  const prepared = await prepareIssue(issue);

  if (prepared.rawForTamperCheck.some(heuristicTamperDetected)) {
    return result('assign', null, 'hidden characters or forged content tags detected', { labels: [] });
  }
  const filter = await callJson<FilterResult>(ctx.llm, costs, 'injection-filter', ctx.llm.filterModel, loadPrompt('untrusted-content-filter.txt'), prepared.issueBlock, FILTER_SCHEMA);
  if (filter.suspicious) {
    return result('assign', null, `content flagged as suspicious: ${filter.reason}`, { labels: [] });
  }

  const latest = currentVersion();
  // Deterministic: is the reported tariff in Octopus's public API, with rates around the report date?
  const tariff = prepared.isBug ? await checkTariffs(prepared.tariffText, prepared.issue.createdAt) : { facts: [], problems: [], gates: [] };
  gates.push(...tariff.gates);
  if (tariff.facts.length) gates.push(`tariff: ${tariff.problems.length ? tariff.problems.join(', ') : 'rates published'}`);
  const facts = [
    latest && `- Latest release: v${latest}`,
    ...tariff.facts,
    prepared.reportedVersion && `- Reporter's integration version: v${prepared.displayVersion}${prepared.reportedPrerelease ? ' (a pre-release)' : ''}`,
    '- Code under "Relevant code" is quoted verbatim from the source at the linked lines, so whatever those quoted lines directly show is verified.',
    '- A final checklist item asking the reporter to confirm on the latest release is added automatically when they are behind - do not count it against the draft.',
  ]
    .filter(Boolean)
    .join('\n');

  // Every comment must get past the critic before it is posted.
  const post = async (outcome: Outcome, comment: string, reason: string, extra: Partial<TriageResult> = {}, linkedIssue?: string): Promise<TriageResult> => {
    const critic = await runCritic(ctx, costs, prepared, outcome, facts, comment, gates, linkedIssue);
    return critic.score >= CRITIC_MIN_SCORE
      ? result('comment', outcome, reason, { ...extra, comment, critic, labels: [`${LABELS.outcomePrefix}${outcome}`, LABELS.awaitingFeedback] })
      : result('assign', outcome, `critic score ${critic.score} below ${CRITIC_MIN_SCORE}`, { ...extra, critic, draft: comment });
  };

  // 1. Already fixed in a newer release? A pre-release of the latest version counts as behind it.
  const comparison = prepared.reportedVersion && latest ? compareVersions(prepared.reportedVersion, latest) : null;
  const behind = comparison !== null && (comparison < 0 || (comparison === 0 && Boolean(prepared.reportedPrerelease)));
  // A version this integration never released is usually another integration's (e.g. #1872 "4.1.6"),
  // and matching it would mean sending hundreds of unrelated changelog entries; analysis handles it.
  // Pre-releases aren't in the changelog, so they're exempt.
  const plausibleVersion = prepared.knownRelease || Boolean(prepared.reportedPrerelease);
  if (prepared.isBug && behind && !plausibleVersion) {
    gates.push(`version: skipped changelog match (${prepared.reportedVersion} is not a release of this integration)`);
  }
  const fixed = prepared.isBug && behind && plausibleVersion ? await checkFixedInNewerVersion(ctx, costs, prepared, latest, gates) : null;
  if (fixed) {
    const posted = await post('fixed_in_newer_version', buildFixedInNewerVersionComment(prepared.displayVersion, latest, fixed, ctx.commentContext), 'fix found in a newer release');
    if (posted.action === 'comment') return posted;
  }

  // 2. Duplicate of an existing issue?
  const duplicate = await checkDuplicate(ctx, costs, prepared, gates);
  if (duplicate) {
    const posted = await post('duplicate', buildDuplicateComment(duplicate, duplicate.why, ctx.commentContext), `duplicate of #${duplicate.number}`, {}, duplicate.excerpt);
    if (posted.action === 'comment') return posted;
  }

  // 3. Analysis (bug diagnosis / feature analysis / docs answer).
  const analysis = await runAnalysis(ctx, costs, prepared, latest, gates, tariff);
  const extra = { analysis, evidenceFiles: analysis.evidence.map((e) => e.file), newTitle: retitle(prepared.issue.title, analysis.suggested_title, gates) };

  if (analysis.outcome === 'none') {
    return result('assign', 'none', 'nothing new and verifiable to add', extra);
  }
  if (analysis.confidence < (MIN_CONFIDENCE[analysis.outcome] ?? 0)) {
    return result('assign', analysis.outcome, `confidence ${analysis.confidence} below ${MIN_CONFIDENCE[analysis.outcome]} for ${analysis.outcome}`, extra);
  }

  // Beta testers are always pointed at the stable release, even a beta numbered above it (#1725:
  // the v19 betas were later released as v18.2.1).
  const askToConfirmOnLatest =
    analysis.outcome === 'needs_info' &&
    latest &&
    prepared.reportedVersion &&
    (prepared.reportedPrerelease || (behind && isMinorOrMoreBehind(prepared.reportedVersion, latest))) &&
    !analysis.questions_for_reporter.some((q) => q.ask.includes(latest) || /\b(latest|upgrad|update)/i.test(q.ask));
  const extraQuestions = askToConfirmOnLatest
    ? [
        prepared.reportedPrerelease
          ? `You're on a pre-release (v${prepared.displayVersion}). Can you confirm this still happens on the latest release (v${latest})?`
          : `Can you confirm this still happens on the latest release (v${latest})? You're currently on v${prepared.displayVersion}.`,
      ]
    : [];
  return post(analysis.outcome, buildAnalysisComment(analysis, ctx.commentContext, extraQuestions), `${analysis.outcome} passed all gates`, extra);
}
