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

// Other integrations that reporters commonly confuse with this one; a wrong-repo comment links to
// these (any other target gets a generic "doesn't look like this integration" reply).
// `dataFromHere` is set when the sibling consumes this integration's data: then a bad result there
// may really be bad data from here, so the reply asks the reporter to check that first.
export const KNOWN_SIBLING_INTEGRATIONS: Record<string, { name: string; repo: string; dataFromHere?: { what: string; check: string } }> = {
  target_timeframes: {
    name: 'Target Timeframes',
    repo: 'BottlecapDave/HomeAssistant-TargetTimeframes',
    dataFromHere: {
      what: 'its rates come from this integration (the current/next day rates event entities)',
      check:
        "Target Timeframes gets its rates from this integration, so first check that the `rates` attribute of this integration's current day rates event entity (Developer tools > States) matches the Octopus app for that period. If the rates match, please raise it there. If they don't, reply here instead, as the problem is then with the rates this integration supplies.",
    },
  },
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
