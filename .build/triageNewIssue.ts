import { DEFAULT_GITHUB_REPOSITORY, DEFAULT_MAINTAINER_GITHUB_USERNAME } from './triage/config';
import { GithubClient } from './triage/github';
import { GithubIssue, issueFromApi, loadIssueFromEvent, loadIssueFromFile } from './triage/issue';
import { llmConfigFromEnv } from './triage/llm';
import { TriageResult, triageIssue } from './triage/pipeline';
import { getArgValue, hasFlag } from './triage/text';
import { currentSha } from './triage/version';

/*
 * Usage:
 *   (GitHub Actions `issues: opened`)       npm run triage-new-issue
 *   Dry run against a real issue:           npm run triage-new-issue -- --issue 1954 --dry-run
 *   Dry run against a local file:           npm run triage-new-issue -- --file body.md --label bug --consent [--title "..."] [--bot]
 *   Print the full prompts:                 add --print-prompts
 *   Override models:                        add --model <analysis model> / --filter-model <model>
 */

export function printResult(issue: GithubIssue, result: TriageResult): void {
  console.log(`\nIssue #${issue.number}: ${issue.title}`);
  console.log(`Action: ${result.action} | outcome: ${result.outcome ?? '-'} | ${result.reason}`);
  result.gates.forEach((gate) => console.log(`  - ${gate}`));
  if (result.costs.calls.length) {
    console.log(`LLM usage:\n${result.costs.summary()}`);
  }
}

async function main() {
  const filePath = getArgValue('--file');
  const issueNumber = getArgValue('--issue');
  // File mode has no real issue to act on, so it always behaves as a dry run.
  const dryRun = hasFlag('--dry-run') || Boolean(filePath);
  const repo = process.env.GITHUB_REPOSITORY || DEFAULT_GITHUB_REPOSITORY;
  const maintainer = process.env.MAINTAINER_GITHUB_USERNAME || DEFAULT_MAINTAINER_GITHUB_USERNAME;
  const github = new GithubClient(repo, process.env.GITHUB_TOKEN);

  if (dryRun) {
    console.log('Running in dry-run mode - nothing will be posted or changed');
  }

  const llm = llmConfigFromEnv({
    analysisModel: getArgValue('--model') ?? undefined,
    filterModel: getArgValue('--filter-model') ?? undefined,
    logPrompts: hasFlag('--print-prompts') && dryRun,
  });

  const issue = filePath
    ? loadIssueFromFile(filePath, { title: getArgValue('--title'), label: getArgValue('--label'), isBot: hasFlag('--bot'), consent: hasFlag('--consent') })
    : issueNumber
      ? issueFromApi(await github.getIssue(Number(issueNumber)))
      : loadIssueFromEvent();

  console.log(`Triaging issue #${issue.number}: ${issue.title} (analysis: ${llm.analysisModel}, filter: ${llm.filterModel})`);
  const result = await triageIssue(issue, { llm, github, commentContext: { repo, sha: currentSha(), maintainer } });
  printResult(issue, result);

  if (dryRun) {
    if (result.comment) console.log(`\n[DRY RUN] Would post comment:\n${result.comment}`);
    if (result.draft) console.log(`\n[DRY RUN] Draft blocked by critic:\n${result.draft}`);
    if (result.newTitle) console.log(`[DRY RUN] Would rename the issue to: ${result.newTitle}`);
    if (result.labels.length) console.log(`[DRY RUN] Would add labels: ${result.labels.join(', ')}`);
    if (result.action === 'assign') console.log(`[DRY RUN] Would assign @${maintainer}`);
    return;
  }

  if (result.action === 'ignore') {
    return;
  }
  if (!process.env.GITHUB_TOKEN) {
    console.warn('GITHUB_TOKEN not set - skipping all GitHub changes');
    return;
  }

  if (result.comment) {
    await github.postComment(issue.number, result.comment);
    console.log(`Posted triage comment on issue #${issue.number}`);
  }
  if (result.newTitle) {
    // GitHub's timeline keeps the original title, so the rename is visible and reversible.
    await github.updateTitle(issue.number, result.newTitle);
    console.log(`Renamed issue #${issue.number} to "${result.newTitle}"`);
  }
  await github.addLabels(issue.number, result.labels);
  if (result.action === 'assign') {
    // Assigned == "needs a human": the bot had nothing it could verify, so hand over now.
    await github.addAssignees(issue.number, [maintainer]);
    console.log(`Assigned issue #${issue.number} to ${maintainer}`);
  }
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
