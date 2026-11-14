import { JsonSchemaSpec } from './llm';

// Schemas are written for strict structured outputs: every property required, no
// additionalProperties, no nulls (empty string / empty array / 0 mean "not applicable").

export type BugOutcome = 'root_cause' | 'needs_info' | 'docs_answer' | 'wrong_repo' | 'none';
export type FeatureOutcome = 'already_supported' | 'implementation_notes' | 'needs_info' | 'wrong_repo' | 'none';
export type DocsOutcome = 'docs_answer' | 'needs_info' | 'none';
export type AnalysisOutcome = BugOutcome | FeatureOutcome | DocsOutcome;

export type Outcome = AnalysisOutcome | 'fixed_in_newer_version' | 'duplicate';

export interface Evidence {
  file: string;
  start_line: number;
  end_line: number;
  quote: string;
  why: string;
}

export interface DocLink {
  url: string;
  quote: string;
}

export interface Analysis {
  outcome: AnalysisOutcome;
  /** Plain English for the reporter - shown first. Everything technical is collapsed for the maintainer. */
  reporter_message: string;
  summary: string;
  new_findings: string[];
  evidence: Evidence[];
  suggested_fix: string;
  /** graphql_query: a query for the reporter to run via octopus_energy.run_graphql_query, or "". */
  questions_for_reporter: Array<{ ask: string; why: string; graphql_query: string }>;
  doc_links: DocLink[];
  issue_quote: string;
  other_integration: string;
  graphql_fields: string[];
  /** A clearer title, or "" - only used when the current title is generic (see isGenericTitle). */
  suggested_title: string;
  confidence: number;
}

const str = { type: 'string' };
const strArray = { type: 'array', items: str };

function object(properties: Record<string, unknown>): Record<string, unknown> {
  return { type: 'object', additionalProperties: false, required: Object.keys(properties), properties };
}

export function analysisSchema(outcomes: string[]): JsonSchemaSpec {
  return {
    name: 'triage_analysis',
    schema: object({
      outcome: { type: 'string', enum: outcomes },
      reporter_message: str,
      summary: str,
      new_findings: strArray,
      evidence: { type: 'array', items: object({ file: str, start_line: { type: 'integer' }, end_line: { type: 'integer' }, quote: str, why: str }) },
      suggested_fix: str,
      questions_for_reporter: { type: 'array', items: object({ ask: str, why: str, graphql_query: str }) },
      doc_links: { type: 'array', items: object({ url: str, quote: str }) },
      issue_quote: str,
      other_integration: str,
      graphql_fields: strArray,
      suggested_title: str,
      confidence: { type: 'number' },
    }),
  };
}

export const BUG_OUTCOMES: BugOutcome[] = ['root_cause', 'needs_info', 'docs_answer', 'wrong_repo', 'none'];
export const FEATURE_OUTCOMES: FeatureOutcome[] = ['already_supported', 'implementation_notes', 'needs_info', 'wrong_repo', 'none'];
export const DOCS_OUTCOMES: DocsOutcome[] = ['docs_answer', 'needs_info', 'none'];

export interface FilterResult {
  suspicious: boolean;
  reason: string;
}

export const FILTER_SCHEMA: JsonSchemaSpec = {
  name: 'injection_filter',
  schema: object({ suspicious: { type: 'boolean' }, reason: str }),
};

export interface DuplicateResult {
  reason: string;
  duplicate_of: number;
  why: string;
  confidence: number;
}

export const DUPLICATE_SCHEMA: JsonSchemaSpec = {
  name: 'duplicate_check',
  schema: object({ reason: str, duplicate_of: { type: 'integer' }, why: str, confidence: { type: 'number' } }),
};

export interface ChangelogMatchResult {
  reason: string;
  matches: Array<{ line_id: string; why: string }>;
  confidence: number;
}

export const CHANGELOG_SCHEMA: JsonSchemaSpec = {
  name: 'changelog_match',
  schema: object({ reason: str, matches: { type: 'array', items: object({ line_id: str, why: str }) }, confidence: { type: 'number' } }),
};

export interface CriticResult {
  reason: string;
  problems: string[];
  score: number;
}

export const CRITIC_SCHEMA: JsonSchemaSpec = {
  name: 'comment_critic',
  schema: object({ reason: str, problems: strArray, score: { type: 'integer' } }),
};
