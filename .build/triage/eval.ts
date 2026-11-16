import { mkdirSync, readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { DEFAULT_GITHUB_REPOSITORY, DEFAULT_MAINTAINER_GITHUB_USERNAME, LABELS } from './config';
import { GithubClient } from './github';
import { GithubIssue, hasAiTriageConsent, issueFromApi, loadIssueFromFile } from './issue';
import { llmConfigFromEnv } from './llm';
import { triageIssue } from './pipeline';
import { getArgValue, hasFlag } from './text';
import { currentSha } from './version';

/*
 * Runs the triage pipeline (always dry-run) over known issues and scores the results, so prompt,
 * retrieval and model changes can be compared.
 *
 *   npm run triage-eval
 *   npm run triage-eval -- --model openai/gpt-6.1-terra --only 1938,1916
 *   npm run triage-eval -- --from-rejected      # add issues whose triage got a 👎 (unscored, for review)
 *   npm run triage-eval -- --issues 1953,1950   # dry-run any issues instead of the fixtures (unscored)
 */

interface Fixture {
  issue?: number;
  file?: string;
  title?: string;
  label?: string;
  notes?: string;
  expected_outcomes?: string[];
  expected_files?: string[];
}

async function main() {
  const repo = process.env.GITHUB_REPOSITORY || DEFAULT_GITHUB_REPOSITORY;
  const github = new GithubClient(repo, process.env.GITHUB_TOKEN);
  const llm = llmConfigFromEnv({ analysisModel: getArgValue('--model') ?? undefined, filterModel: getArgValue('--filter-model') ?? undefined });
  const only = getArgValue('--only')?.split(',').map(Number);
  const adhoc = getArgValue('--issues')?.split(',').map(Number);

  let fixtures: Fixture[] = adhoc
    ? adhoc.map((issue) => ({ issue, notes: 'ad-hoc dry run (unscored - review the comment)' }))
    : JSON.parse(readFileSync(join(__dirname, 'evals.json'), 'utf-8'));
  if (hasFlag('--from-rejected')) {
    const rejected = await github.listIssuesWithLabel(LABELS.rejected, 'all');
    fixtures.push(...rejected.filter((r) => !fixtures.some((f) => f.issue === r.number)).map((r) => ({ issue: r.number, notes: 'from ai-triage:rejected (review manually)' })));
  }
  if (only) {
    fixtures = fixtures.filter((f) => f.issue && only.includes(f.issue));
  }

  const outDir = join(__dirname, 'eval-output', llm.analysisModel.replace(/[^a-z0-9.-]+/gi, '_'), adhoc ? 'adhoc' : '');
  mkdirSync(outDir, { recursive: true });
  const rows: string[][] = [];
  let totalCost = 0;

  for (const [index, fixture] of fixtures.entries()) {
    const id = fixture.issue ? `#${fixture.issue}` : fixture.file;
    const progress = `[${index + 1}/${fixtures.length}] ${id}`;
    let issue: GithubIssue;
    try {
      issue = fixture.file
        ? loadIssueFromFile(join(__dirname, fixture.file), { title: fixture.title, label: fixture.label, consent: true })
        : issueFromApi(await github.getIssue(fixture.issue));
    } catch (error) {
      console.log(`${progress}: failed to load - ${(error as Error).message}`);
      rows.push([id, 'ERROR', (error as Error).message, '', '', '']);
      continue;
    }
    // Respect reporters who declined AI processing, even for offline evaluation.
    if (!hasAiTriageConsent(issue.body)) {
      console.log(`${progress}: skipped (no AI consent)`);
      rows.push([id, 'skipped', 'no consent', '', '', '']);
      continue;
    }
    console.log(`${progress}: ${issue.title}`);

    try {
      const result = await triageIssue(issue, {
        llm,
        github,
        commentContext: { repo, sha: currentSha(), maintainer: DEFAULT_MAINTAINER_GITHUB_USERNAME },
      });
      totalCost += result.costs.total;
      if (result.error?.includes('insufficient credits')) {
        // Every later call would fail the same way, so stop rather than record a run of errors.
        console.error(`\nStopped at ${id}: ${result.error}\nAdd credits at https://openrouter.ai/settings/credits and rerun the remaining issues.`);
        break;
      }

      console.log(`  -> ${result.action}:${result.outcome ?? '-'} - ${result.error ? `ERROR ${result.error.slice(0, 120)}` : result.reason} ($${result.costs.total.toFixed(3)})`);

      const expected = fixture.expected_outcomes ?? [];
      const outcomePass = result.error ? 'ERROR' : expected.length ? (result.action === 'comment' && expected.includes(result.outcome) ? 'PASS' : 'FAIL') : 'review';
      const cited = new Set([...result.evidenceFiles, ...(result.analysis?.evidence ?? []).map((e) => e.file)]);
      const fileScore = fixture.expected_files?.length ? `${fixture.expected_files.filter((f) => cited.has(f)).length}/${fixture.expected_files.length}` : '-';
      rows.push([id, result.error ? result.error.slice(0, 60) : `${result.action}:${result.outcome ?? '-'}`, expected.join('|') || '-', outcomePass, fileScore, `$${result.costs.total.toFixed(3)}`]);

      writeFileSync(
        join(outDir, `${(id ?? 'fixture').replace(/[^a-z0-9]+/gi, '_')}.md`),
        [
          `# ${id}: ${issue.title}`,
          fixture.notes ? `> ${fixture.notes}` : '',
          `\n**Action:** ${result.action} | **Outcome:** ${result.outcome ?? '-'} | **Reason:** ${result.reason}`,
          `**Expected:** ${expected.join(', ') || '(review)'} | **Files:** ${fileScore}`,
          result.newTitle ? `**New title:** ${result.newTitle}` : '',
          '\n## Gates',
          ...result.gates.map((g) => `- ${g}`),
          '\n## Comment',
          result.comment ?? '(none posted)',
          result.draft ? `\n## Draft blocked by critic\n${result.draft}` : '',
          result.critic ? `\n## Critic\n\`\`\`json\n${JSON.stringify(result.critic, null, 2)}\n\`\`\`` : '',
          result.analysis ? `\n## Raw analysis\n\`\`\`json\n${JSON.stringify(result.analysis, null, 2)}\n\`\`\`` : '',
          `\n## Usage\n\`\`\`\n${result.costs.summary()}\n\`\`\``,
        ].join('\n'),
      );
    } catch (error) {
      rows.push([id, 'ERROR', (error as Error).message.slice(0, 80), '', '', '']);
    }
  }

  const header = ['fixture', 'result', 'expected', 'outcome', 'files', 'cost'];
  const widths = header.map((h, i) => Math.max(h.length, ...rows.map((r) => (r[i] ?? '').length)));
  const format = (row: string[]) => row.map((cell, i) => (cell ?? '').padEnd(widths[i])).join('  ');
  console.log(`\nModel: ${llm.analysisModel} (filter: ${llm.filterModel})`);
  console.log(format(header));
  rows.forEach((row) => console.log(format(row)));
  const passes = rows.filter((r) => r[3] === 'PASS').length;
  const scored = rows.filter((r) => r[3] === 'PASS' || r[3] === 'FAIL').length;
  console.log(`\n${passes}/${scored} outcome passes, total cost $${totalCost.toFixed(3)}. Details in ${outDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
