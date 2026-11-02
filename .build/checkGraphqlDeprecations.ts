import { readFileSync } from 'fs';
import { join } from 'path';
import {
  ASTNode,
  GraphQLError,
  GraphQLSchema,
  Kind,
  NoDeprecatedCustomRule,
  buildClientSchema,
  getIntrospectionQuery,
  parse,
  validate,
} from 'graphql';

// Queries/mutations without a `backend_` prefix talk to the standard Kraken API, `backend_`
// prefixed ones talk to the Octopus Energy backend API - each is backed by its own schema.
const DEFAULT_GRAPHQL_ENDPOINT = 'https://api.oegb-kraken.energy/v1/graphql/';
const BACKEND_GRAPHQL_ENDPOINT = 'https://api.backend.octopus.energy/v1/graphql/';

const API_CLIENT_FILE_PATH = join(__dirname, '../custom_components/octopus_energy/api_client/__init__.py');

const DEFAULT_GITHUB_REPOSITORY = 'BottlecapDave/HomeAssistant-OctopusEnergy';
const DEFAULT_OPENROUTER_MODEL = 'openai/gpt-4o-mini';

// e.g. "- Scheduled for removal on or after 2026-10-15."
const REMOVAL_DATE_REGEX = /removal on or after (\d{4}-\d{2}-\d{2})/i;

interface GraphqlOperation {
  name: string;
  operationType: 'query' | 'mutation';
  isBackend: boolean;
  sanitizedBody: string;
}

interface DeprecationFinding {
  kind: string;
  name: string;
  qualifiedName: string;
  deprecationReason: string;
  removalDate: string | null;
}

interface AggregatedFinding {
  name: string;
  kind: string;
  removalDate: string | null;
  deprecationReason: string;
  isBackend: boolean;
  qualifiedNames: Set<string>;
  operationNames: Set<string>;
}

interface GithubIssueSummary {
  number: number;
  url: string;
  state: string;
}

/**
 * Pulls out every module-level `..._query`/`..._mutation` triple-quoted string from the API
 * client so we don't have to hand-maintain a separate list of operations to check.
 */
function extractGraphqlOperations(filePath: string): GraphqlOperation[] {
  const content = readFileSync(filePath, 'utf-8');
  const assignmentRegex = /^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*'''([\s\S]*?)'''/gm;

  const operations: GraphqlOperation[] = [];
  let match: RegExpExecArray | null;
  while ((match = assignmentRegex.exec(content)) !== null) {
    const [, name, body] = match;
    const trimmedBody = body.trim();

    if (!/^(query|mutation)\b/.test(trimmedBody)) {
      // Not a top level operation (e.g. `intelligent_settings_mutation_schedule`, which is a
      // fragment interpolated into another mutation).
      continue;
    }

    operations.push({
      name,
      operationType: trimmedBody.startsWith('mutation') ? 'mutation' : 'query',
      isBackend: name.startsWith('backend_'),
      sanitizedBody: sanitizeGraphqlTemplate(body),
    });
  }

  return operations;
}

/**
 * The API client builds queries with Python's `str.format()`, so literal braces are doubled
 * (`{{`/`}}`) and `{param}` placeholders are substituted in at call time. This undoes both so the
 * result is syntactically valid GraphQL that the `graphql` package can parse. The substituted
 * dummy value is deliberately a bare name so it's valid whether it lands inside a quoted string
 * argument or a raw (int/enum/boolean) one.
 */
function sanitizeGraphqlTemplate(body: string): string {
  const OPEN_BRACE_TOKEN = '';
  const CLOSE_BRACE_TOKEN = '';

  return body
    .replace(/\{\{/g, OPEN_BRACE_TOKEN)
    .replace(/\}\}/g, CLOSE_BRACE_TOKEN)
    .replace(/\{[a-zA-Z_][a-zA-Z0-9_]*\}/g, 'PLACEHOLDER_VALUE')
    .replace(new RegExp(OPEN_BRACE_TOKEN, 'g'), '{')
    .replace(new RegExp(CLOSE_BRACE_TOKEN, 'g'), '}');
}

async function fetchSchema(endpoint: string): Promise<GraphQLSchema> {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: getIntrospectionQuery() }),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch schema from ${endpoint}: ${response.status} ${response.statusText}`);
  }

  const result = await response.json();
  if (result.errors) {
    throw new Error(`Introspection query against ${endpoint} returned errors: ${JSON.stringify(result.errors)}`);
  }

  return buildClientSchema(result.data);
}

function getFindingName(node: ASTNode): string | null {
  switch (node.kind) {
    case Kind.FIELD:
    case Kind.ARGUMENT:
    case Kind.OBJECT_FIELD:
      return node.name.value;
    case Kind.ENUM:
      return node.value;
    default:
      return null;
  }
}

function extractRemovalDateFromReason(reason: string): string | null {
  const match = reason.match(REMOVAL_DATE_REGEX);
  return match ? match[1] : null;
}

function parseDeprecationError(error: GraphQLError): DeprecationFinding | null {
  const node = error.nodes?.[0];
  if (!node) {
    return null;
  }

  const name = getFindingName(node);
  if (!name) {
    return null;
  }

  // NoDeprecatedCustomRule messages look like:
  //   The field Query.electricVehicles is deprecated. <reason...>
  //   The argument "accountNumber" is deprecated. <reason...>
  const messageMatch = error.message.match(/^The (field|argument|input field|enum value) (.+?) is deprecated\.\s*([\s\S]*)$/);

  return {
    kind: messageMatch ? messageMatch[1] : 'field',
    name,
    qualifiedName: messageMatch ? messageMatch[2].replace(/^"|"$/g, '') : name,
    deprecationReason: (messageMatch ? messageMatch[3] : error.message).trim(),
    removalDate: extractRemovalDateFromReason(messageMatch ? messageMatch[3] : error.message),
  };
}

function findDeprecationFindings(schema: GraphQLSchema, operation: GraphqlOperation): DeprecationFinding[] {
  const document = parse(operation.sanitizedBody);
  const errors = validate(schema, document, [NoDeprecatedCustomRule]);

  const findings: DeprecationFinding[] = [];
  for (const error of errors) {
    const finding = parseDeprecationError(error);
    if (finding) {
      findings.push(finding);
    }
  }

  return findings;
}

/**
 * Falls back to an LLM (via OpenRouter) to pull a removal date out of a deprecation reason that
 * doesn't follow the standard "Scheduled for removal on or after YYYY-MM-DD" phrasing.
 */
async function extractRemovalDateViaLlm(
  fieldName: string,
  deprecationReason: string,
  apiKey: string,
  model: string,
): Promise<string | null> {
  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      temperature: 0,
      messages: [
        {
          role: 'system',
          content:
            'You extract the scheduled removal date of a deprecated GraphQL schema member from its deprecation reason. ' +
            'Respond with ONLY a date in YYYY-MM-DD format, or the single word NONE if no removal date is mentioned or implied.',
        },
        {
          role: 'user',
          content: `Field/argument/enum value: ${fieldName}\nDeprecation reason: ${deprecationReason}`,
        },
      ],
    }),
  });

  if (!response.ok) {
    throw new Error(`OpenRouter request failed: ${response.status} ${response.statusText}`);
  }

  const result = await response.json();
  const content: string | undefined = result?.choices?.[0]?.message?.content?.trim();
  if (!content || content.toUpperCase() === 'NONE') {
    return null;
  }

  const match = content.match(/\d{4}-\d{2}-\d{2}/);
  return match ? match[0] : null;
}

function buildIssueTitle(finding: AggregatedFinding, removalDateLabel: string): string {
  return `[Graphql Deprecation] ${finding.name} - ${removalDateLabel}`;
}

function buildIssueBody(finding: AggregatedFinding, removalDateLabel: string): string {
  const endpoint = finding.isBackend ? BACKEND_GRAPHQL_ENDPOINT : DEFAULT_GRAPHQL_ENDPOINT;
  const qualifiedNames = [...finding.qualifiedNames].sort();
  const operationNames = [...finding.operationNames].sort();

  return [
    `A deprecated GraphQL ${finding.kind} named \`${finding.name}\` is still referenced by this integration.`,
    '',
    `**Schema endpoint**: ${endpoint}`,
    `**Scheduled removal**: ${removalDateLabel}`,
    '',
    '**Deprecation reason**',
    '```',
    finding.deprecationReason,
    '```',
    '',
    '**Affected schema reference(s)**',
    ...qualifiedNames.map((name) => `- \`${name}\``),
    '',
    `**Affected quer${operationNames.length === 1 ? 'y' : 'ies'}/mutation(s) in \`custom_components/octopus_energy/api_client/__init__.py\`**`,
    ...operationNames.map((name) => `- \`${name}\``),
    '',
    '_This issue was automatically generated by `.build/checkGraphqlDeprecations.ts`._',
  ].join('\n');
}

async function findExistingIssue(repo: string, githubToken: string | undefined, title: string): Promise<GithubIssueSummary | null> {
  const searchQuery = `repo:${repo} type:issue in:title "${title}"`;
  const response = await fetch(`https://api.github.com/search/issues?q=${encodeURIComponent(searchQuery)}`, {
    headers: {
      Accept: 'application/vnd.github+json',
      ...(githubToken ? { Authorization: `Bearer ${githubToken}` } : {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to search for existing issues: ${response.status} ${response.statusText}`);
  }

  const result = await response.json();
  const exactMatch = (result.items ?? []).find((item: { title: string }) => item.title === title);

  return exactMatch ? { number: exactMatch.number, url: exactMatch.html_url, state: exactMatch.state } : null;
}

async function createIssue(repo: string, githubToken: string, title: string, body: string): Promise<GithubIssueSummary> {
  const response = await fetch(`https://api.github.com/repos/${repo}/issues`, {
    method: 'POST',
    headers: {
      Accept: 'application/vnd.github+json',
      Authorization: `Bearer ${githubToken}`,
      'X-GitHub-Api-Version': '2022-11-28',
    },
    body: JSON.stringify({ title, body, labels: ['graphql-deprecation'] }),
  });

  if (!response.ok) {
    throw new Error(`Failed to create issue '${title}': ${response.status} ${response.statusText}`);
  }

  const result = await response.json();
  return { number: result.number, url: result.html_url, state: result.state };
}

function groupFindingsByOperation(operations: GraphqlOperation[], schemasByEndpoint: Map<string, GraphQLSchema>): Map<string, AggregatedFinding> {
  const aggregated = new Map<string, AggregatedFinding>();

  for (const operation of operations) {
    const schema = schemasByEndpoint.get(operation.isBackend ? BACKEND_GRAPHQL_ENDPOINT : DEFAULT_GRAPHQL_ENDPOINT);
    if (!schema) {
      continue;
    }

    let findings: DeprecationFinding[];
    try {
      findings = findDeprecationFindings(schema, operation);
    } catch (error) {
      console.warn(`Skipping '${operation.name}' - failed to parse/validate against schema: ${(error as Error).message}`);
      continue;
    }

    for (const finding of findings) {
      const key = `${finding.name}::${finding.removalDate ?? 'unknown'}`;
      let entry = aggregated.get(key);
      if (!entry) {
        entry = {
          name: finding.name,
          kind: finding.kind,
          removalDate: finding.removalDate,
          deprecationReason: finding.deprecationReason,
          isBackend: operation.isBackend,
          qualifiedNames: new Set(),
          operationNames: new Set(),
        };
        aggregated.set(key, entry);
      }

      entry.qualifiedNames.add(finding.qualifiedName);
      entry.operationNames.add(operation.name);
    }
  }

  return aggregated;
}

async function main() {
  const dryRun = process.argv.includes('--dry-run');
  const githubRepository = process.env.GITHUB_REPOSITORY || DEFAULT_GITHUB_REPOSITORY;
  const githubToken = process.env.GITHUB_TOKEN;
  const openRouterApiKey = process.env.OPENROUTER_API_KEY;
  const openRouterModel = process.env.OPENROUTER_MODEL || DEFAULT_OPENROUTER_MODEL;

  if (dryRun) {
    console.log('Running in dry-run mode - no issues will be created');
  }
  if (!githubToken) {
    console.warn('GITHUB_TOKEN not set - issue search will be rate limited and issue creation will be skipped');
  }
  if (!openRouterApiKey) {
    console.log('OPENROUTER_API_KEY not set - removal dates that cannot be parsed with the standard pattern will be reported as unknown');
  }

  const operations = extractGraphqlOperations(API_CLIENT_FILE_PATH);
  console.log(`Extracted ${operations.length} queries/mutations from ${API_CLIENT_FILE_PATH}`);

  const schemasByEndpoint = new Map<string, GraphQLSchema>();
  if (operations.some((operation) => !operation.isBackend)) {
    console.log(`Fetching schema from ${DEFAULT_GRAPHQL_ENDPOINT}`);
    schemasByEndpoint.set(DEFAULT_GRAPHQL_ENDPOINT, await fetchSchema(DEFAULT_GRAPHQL_ENDPOINT));
  }
  if (operations.some((operation) => operation.isBackend)) {
    console.log(`Fetching schema from ${BACKEND_GRAPHQL_ENDPOINT}`);
    schemasByEndpoint.set(BACKEND_GRAPHQL_ENDPOINT, await fetchSchema(BACKEND_GRAPHQL_ENDPOINT));
  }

  const aggregatedFindings = groupFindingsByOperation(operations, schemasByEndpoint);
  console.log(`Found ${aggregatedFindings.size} distinct deprecated schema reference(s)`);

  for (const finding of aggregatedFindings.values()) {
    let removalDate = finding.removalDate;
    if (!removalDate && openRouterApiKey) {
      try {
        removalDate = await extractRemovalDateViaLlm(finding.name, finding.deprecationReason, openRouterApiKey, openRouterModel);
      } catch (error) {
        console.warn(`Failed to determine removal date for '${finding.name}' via OpenRouter: ${(error as Error).message}`);
      }
    }

    const removalDateLabel = removalDate ?? 'unknown-removal-date';
    const title = buildIssueTitle(finding, removalDateLabel);

    const existingIssue = await findExistingIssue(githubRepository, githubToken, title);
    if (existingIssue) {
      console.log(`[EXISTS] ${title} -> #${existingIssue.number} (${existingIssue.state}) ${existingIssue.url}`);
      continue;
    }

    const body = buildIssueBody(finding, removalDateLabel);

    if (dryRun) {
      console.log(`[DRY RUN] Would create issue: ${title}`);
      console.log(body.split('\n').map((line) => `    ${line}`).join('\n'));
      continue;
    }

    if (!githubToken) {
      console.warn(`[SKIPPED] Cannot create issue '${title}' without GITHUB_TOKEN`);
      continue;
    }

    const createdIssue = await createIssue(githubRepository, githubToken, title, body);
    console.log(`[CREATED] ${title} -> ${createdIssue.url}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
