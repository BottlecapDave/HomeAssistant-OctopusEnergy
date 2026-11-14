import { join } from 'path';

export const REPO_ROOT = join(__dirname, '..', '..');
export const SOURCE_REPO_PREFIX = 'custom_components/octopus_energy';
export const SOURCE_DIR = join(REPO_ROOT, SOURCE_REPO_PREFIX);
export const DOCS_DIR = join(REPO_ROOT, '_docs');
// Blueprints are YAML shipped with the docs; they're indexed alongside the source so blueprint
// bugs (e.g. #1878) can be diagnosed with quoted evidence.
export const BLUEPRINTS_REPO_PREFIX = '_docs/blueprints';
export const BLUEPRINTS_DIR = join(REPO_ROOT, BLUEPRINTS_REPO_PREFIX);
export const PROMPTS_DIR = join(__dirname, '..', 'prompts');
export const CHANGELOG_PATH = join(REPO_ROOT, 'CHANGELOG.md');

export const DOCS_BASE_URL = 'https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/';
export const DEFAULT_GITHUB_REPOSITORY = 'BottlecapDave/HomeAssistant-OctopusEnergy';
export const DEFAULT_MAINTAINER_GITHUB_USERNAME = 'BottlecapDave';
export const DEFAULT_BOT_LOGIN = 'github-actions[bot]';

// Analysis is the one large call per issue, so it gets the stronger model. Everything else
// (injection screening, duplicate/changelog matching, critic) is small and uses the cheap model.
export const DEFAULT_ANALYSIS_MODEL = 'anthropic/claude-sonnet-5.5';
export const DEFAULT_FILTER_MODEL = 'anthropic/claude-haiku-5.5';

export const INTEGRATION_DOMAIN = 'octopus_energy';

// Other integrations that reporters commonly confuse with this one. A wrong-repo comment is only
// ever posted for an integration listed here, so the bot never guesses where an issue belongs.
export const KNOWN_SIBLING_INTEGRATIONS: Record<string, { name: string; repo: string }> = {
  target_timeframes: { name: 'Target Timeframes', repo: 'BottlecapDave/HomeAssistant-TargetTimeframes' },
};

export const BUG_LABEL = 'bug';
export const ENHANCEMENT_LABEL = 'enhancement';

export const LABELS = {
  outcomePrefix: 'ai-triage:',
  awaitingFeedback: 'ai-triage:awaiting-feedback',
  accepted: 'ai-triage:accepted',
  rejected: 'ai-triage:rejected',
  replied: 'ai-triage:replied',
  noFeedback: 'ai-triage:no-feedback',
  noAnswer: 'ai-triage:no-answer',
};

// Hidden marker embedded in every triage comment so the feedback workflow can find it and know
// which outcome it was posted for. Model output is stripped of HTML comments so it can't forge one.
export const COMMENT_MARKER_PREFIX = '<!-- ai-triage v1';

export const FEEDBACK_TIMEOUT_DAYS = 3;
