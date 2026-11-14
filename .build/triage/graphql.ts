import { GraphQLNamedType, GraphQLObjectType, GraphQLSchema, buildClientSchema, getIntrospectionQuery, getNamedType } from 'graphql';
import { tokenize } from './text';

export const GRAPHQL_ENDPOINTS = [
  { label: 'Standard Kraken API', url: 'https://api.oegb-kraken.energy/v1/graphql/' },
  { label: 'Octopus Energy backend API', url: 'https://api.backend.octopus.energy/v1/graphql/' },
];

const MAX_SCHEMA_FIELDS = 50;
const MAX_SUB_FIELDS = 15;

// Only send the schema when the request is plausibly about data from Octopus. Startup behaviour,
// config flow changes etc. (e.g. #1916) don't need it and it just invites irrelevant suggestions.
const API_HINT = /\b(api|graphql|endpoint|kraken|app|website|online account|retrieve|expose|provider|dispatch(es)?|new (sensor|entity|attribute)|available (from|in) octopus)\b/i;

export function featureNeedsSchema(text: string): boolean {
  return API_HINT.test(text);
}

async function fetchSchema(endpoint: string): Promise<GraphQLSchema> {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: getIntrospectionQuery() }),
    signal: AbortSignal.timeout(30000),
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

function subFields(type: GraphQLNamedType): string[] {
  if (!(type instanceof GraphQLObjectType)) {
    return [];
  }
  const fields = type.getFields();
  return Object.keys(fields).filter((name) => !fields[name].deprecationReason);
}

/**
 * Non-deprecated Query/Mutation fields ranked by relevance, each with one level of its return
 * type's fields (the old summary only showed top-level names, which hid most of the data).
 * Returns the rendered summary plus the set of valid names for validating model output.
 */
export async function buildSchemaContext(query: string): Promise<{ text: string; validFields: Set<string> }> {
  const terms = new Set(tokenize(query));
  const validFields = new Set<string>();
  const sections: string[] = [];

  for (const endpoint of GRAPHQL_ENDPOINTS) {
    let schema: GraphQLSchema;
    try {
      schema = await fetchSchema(endpoint.url);
    } catch (error) {
      console.warn((error as Error).message);
      continue;
    }

    const entries: Array<{ text: string; score: number }> = [];
    for (const [kind, type] of [['Query', schema.getQueryType()], ['Mutation', schema.getMutationType()]] as const) {
      if (!type) continue;
      const fields = type.getFields();
      for (const name of Object.keys(fields)) {
        const field = fields[name];
        if (field.deprecationReason) continue;
        const returnType = getNamedType(field.type);
        const children = subFields(returnType);
        validFields.add(name);
        children.forEach((child) => validFields.add(`${name}.${child}`));

        const args = field.args.map((arg) => `${arg.name}: ${String(arg.type)}`).join(', ');
        const description = field.description ? ` - ${field.description.replace(/\s+/g, ' ').slice(0, 200)}` : '';
        const childText = children.length ? `\n    fields: ${children.slice(0, MAX_SUB_FIELDS).join(', ')}${children.length > MAX_SUB_FIELDS ? ', ...' : ''}` : '';
        const text = `- [${kind}] ${name}(${args}): ${String(field.type)}${description}${childText}`;
        const score = tokenize(text).filter((token) => terms.has(token)).length;
        entries.push({ text, score });
      }
    }

    entries.sort((a, b) => b.score - a.score);
    const top = entries.slice(0, MAX_SCHEMA_FIELDS);
    sections.push([`# ${endpoint.label} - ${endpoint.url}`, ...top.map((e) => e.text), `(${entries.length - top.length} less relevant field(s) omitted)`].join('\n'));
  }

  return { text: sections.join('\n\n'), validFields };
}
