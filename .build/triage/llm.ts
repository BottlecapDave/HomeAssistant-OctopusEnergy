import { readFileSync } from 'fs';
import { join } from 'path';
import { DEFAULT_ANALYSIS_MODEL, DEFAULT_FILTER_MODEL, PROMPTS_DIR } from './config';
import { UNTRUSTED_CONTENT_GUARD } from './text';

export interface LlmConfig {
  apiKey: string;
  analysisModel: string;
  filterModel: string;
  /** Print full prompts (dry-run debugging; never enabled in the workflow). */
  logPrompts?: boolean;
}

export function llmConfigFromEnv(overrides: Partial<LlmConfig> = {}): LlmConfig {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    throw new Error('OPENROUTER_API_KEY not set - cannot triage an issue without an LLM');
  }
  return {
    apiKey,
    // OPENROUTER_MODEL is the original single-model env var, kept as an analysis override.
    analysisModel: overrides.analysisModel || process.env.OPENROUTER_ANALYSIS_MODEL || process.env.OPENROUTER_MODEL || DEFAULT_ANALYSIS_MODEL,
    filterModel: overrides.filterModel || process.env.OPENROUTER_FILTER_MODEL || DEFAULT_FILTER_MODEL,
    logPrompts: overrides.logPrompts,
  };
}

// System prompts live as plain text files under .build/prompts/ so they can be reviewed/edited
// without touching the pipeline logic. `{{UNTRUSTED_CONTENT_GUARD}}` is substituted in, and
// `{{INCLUDE:file}}` pulls in shared rules.
export function loadPrompt(fileName: string, variables: Record<string, string> = {}): string {
  let prompt = readFileSync(join(PROMPTS_DIR, fileName), 'utf-8').trimEnd();
  prompt = prompt.replace(/\{\{INCLUDE:([\w.-]+)\}\}/g, (_, include: string) => readFileSync(join(PROMPTS_DIR, include), 'utf-8').trimEnd());
  prompt = prompt.split('{{UNTRUSTED_CONTENT_GUARD}}').join(UNTRUSTED_CONTENT_GUARD);
  for (const [key, value] of Object.entries(variables)) {
    prompt = prompt.split(`{{${key}}}`).join(value);
  }
  return prompt;
}

export interface JsonSchemaSpec {
  name: string;
  schema: Record<string, unknown>;
}

export class CostTracker {
  total = 0;
  readonly calls: Array<{ label: string; model: string; promptTokens: number; completionTokens: number; cost: number }> = [];

  record(label: string, model: string, usage: any): void {
    const cost = Number(usage?.cost) || 0;
    this.total += cost;
    this.calls.push({
      label,
      model,
      promptTokens: Number(usage?.prompt_tokens) || 0,
      completionTokens: Number(usage?.completion_tokens) || 0,
      cost,
    });
  }

  summary(): string {
    return this.calls
      .map((c) => `  ${c.label.padEnd(18)} ${c.model.padEnd(32)} in=${c.promptTokens} out=${c.completionTokens} $${c.cost.toFixed(4)}`)
      .concat(`  total $${this.total.toFixed(4)}`)
      .join('\n');
  }
}

/** OpenRouter balance can't cover the request (402) - retrying won't help until credits are added. */
export class CreditsError extends Error {}

async function postChat(config: LlmConfig, body: Record<string, unknown>): Promise<Response> {
  for (let attempt = 1; ; attempt++) {
    // OPENROUTER_BASE_URL is only for local testing against a mock server.
    const response = await fetch(`${process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1'}/chat/completions`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${config.apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(180000),
    });
    // 402: account out of credits. 403 "Key limit exceeded": the key's own spend cap was reached.
    if (response.status === 402 || response.status === 403) {
      const body = await response.text().catch(() => '');
      if (response.status === 402 || /limit/i.test(body)) {
        throw new CreditsError(`OpenRouter has insufficient credits or the key's spend limit was reached (${response.status}): ${body.slice(0, 300)}`);
      }
      return new Response(body, { status: response.status, statusText: response.statusText });
    }
    if ((response.status === 429 || response.status >= 500) && attempt < 3) {
      await new Promise((resolve) => setTimeout(resolve, 2000 * attempt));
      continue;
    }
    return response;
  }
}

/**
 * Calls OpenRouter with a strict JSON schema (structured outputs). `require_parameters` stops
 * OpenRouter routing to a provider that would silently ignore the schema, so a model that can't
 * do structured outputs fails loudly instead of returning non-JSON.
 */
export async function callJson<T>(
  config: LlmConfig,
  costs: CostTracker,
  label: string,
  model: string,
  systemPrompt: string,
  userPrompt: string,
  schema: JsonSchemaSpec,
  // Reasoning tokens count against this cap, and OpenRouter reserves credit for the full cap before
  // each call, so keep it ~3x real usage (small calls have used up to ~1.1k), not arbitrarily high.
  maxTokens = 3000,
): Promise<T> {
  if (config.logPrompts) {
    console.log(`\n===== PROMPT [${label}] (${model}) =====\n--- system ---\n${systemPrompt}\n--- user ---\n${userPrompt}\n===== END PROMPT =====\n`);
  }

  const base = {
    model,
    max_tokens: maxTokens,
    usage: { include: true },
    provider: { require_parameters: true },
    response_format: { type: 'json_schema', json_schema: { name: schema.name, strict: true, schema: schema.schema } },
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt },
    ],
  };

  const response = await postChat(config, base);
  if (!response.ok) {
    throw new Error(`OpenRouter request [${label}] failed: ${response.status} ${response.statusText} ${await response.text().catch(() => '')}`);
  }

  const result = await response.json();
  costs.record(label, model, result?.usage);
  const content: string | undefined = result?.choices?.[0]?.message?.content;
  if (!content) {
    const choice = result?.choices?.[0];
    const detail = [
      choice?.finish_reason && `finish_reason=${choice.finish_reason}`,
      choice?.native_finish_reason && `native=${choice.native_finish_reason}`,
      choice?.message?.refusal && `refusal=${choice.message.refusal}`,
      (choice?.error ?? result?.error) && `error=${JSON.stringify(choice?.error ?? result?.error)}`,
    ]
      .filter(Boolean)
      .join(', ');
    throw new Error(`OpenRouter response [${label}] did not contain any content${detail ? ` (${detail})` : ''}`);
  }
  try {
    return JSON.parse(content) as T;
  } catch {
    throw new Error(`OpenRouter response [${label}] was not valid JSON: ${content.slice(0, 500)}`);
  }
}
