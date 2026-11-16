import { parseCommentMarker, REPORTER_RESOLVABLE } from './comments';
import { DEFAULT_BOT_LOGIN, DEFAULT_GITHUB_REPOSITORY, DEFAULT_MAINTAINER_GITHUB_USERNAME, FEEDBACK_TIMEOUT_DAYS, LABELS } from './config';
import { GithubClient, GithubIssueSummary, GithubReaction } from './github';
import { Outcome } from './schemas';
import { hasFlag } from './text';

/*
 * Acts on 👍/👎 reactions to triage comments. GitHub doesn't trigger workflows on reactions, so
 * this runs on a schedule (.github/workflows/triage_feedback.yml) over open issues labelled
 * ai-triage:awaiting-feedback. No LLM calls.
 *
 *   npm run triage-feedback -- --dry-run
 */

const CLOSE_REASONS: Partial<Record<Outcome, 'not_planned' | 'duplicate'>> = { duplicate: 'duplicate', wrong_repo: 'not_planned' };

// A 👎 always hands over. A 👍 closes reporter-resolvable outcomes, waits on needs_info (the
// reporter is expected to reply), and hands over diagnoses (the code still needs fixing).
export function onThumbsUp(outcome: Outcome): 'close' | 'wait' | 'hand_over' {
  if (REPORTER_RESOLVABLE.includes(outcome)) return 'close';
  return outcome === 'needs_info' ? 'wait' : 'hand_over';
}

// Most recent 👍/👎 from the reporter or a maintainer - nobody else can close someone's issue.
async function latestVote(github: GithubClient, issue: GithubIssueSummary, reactions: GithubReaction[]): Promise<string | null> {
  const votes = reactions.filter((r) => r.content === '+1' || r.content === '-1').sort((a, b) => b.created_at.localeCompare(a.created_at));
  for (const vote of votes) {
    if (vote.user.login === issue.user.login || (await github.isMaintainer(vote.user.login))) return vote.content;
  }
  return null;
}

async function processIssue(github: GithubClient, issue: GithubIssueSummary, maintainer: string, botLogin: string, dryRun: boolean): Promise<void> {
  const log = (message: string) => console.log(`#${issue.number}: ${message}`);

  const handOver = async (label: string, why: string) => {
    log(`${why} -> assign ${maintainer}, label ${label}`);
    if (dryRun) return;
    await github.addAssignees(issue.number, [maintainer]);
    await github.addLabels(issue.number, [label]);
    await github.removeLabel(issue.number, LABELS.awaitingFeedback);
  };

  const close = async (outcome: Outcome) => {
    const reason = CLOSE_REASONS[outcome] ?? 'completed';
    log(`${outcome} confirmed -> close (${reason})`);
    if (dryRun) return;
    await github.addLabels(issue.number, [LABELS.accepted]);
    await github.removeLabel(issue.number, LABELS.awaitingFeedback);
    await github.postComment(issue.number, 'Thanks for confirming - closing this issue. If the problem comes back, please comment here.');
    await github.closeIssue(issue.number, reason);
  };

  const comments = await github.listComments(issue.number);
  const botComment = [...comments].reverse().find((c) => c.user.login === botLogin && parseCommentMarker(c.body));
  if (!botComment) {
    log('no triage comment found -> remove awaiting label');
    if (!dryRun) await github.removeLabel(issue.number, LABELS.awaitingFeedback);
    return;
  }
  const outcome = parseCommentMarker(botComment.body);

  const vote = await latestVote(github, issue, await github.listCommentReactions(botComment.id));
  if (vote === '-1') return handOver(LABELS.rejected, `${outcome} 👎`);
  if (vote === '+1') {
    const decision = onThumbsUp(outcome);
    if (decision === 'close') return close(outcome);
    if (decision === 'hand_over') return handOver(LABELS.accepted, `${outcome} 👍`);
  }

  // People often reply instead of reacting; any reply from the reporter hands over to a human.
  if (comments.some((c) => c.user.login === issue.user.login && c.created_at > botComment.created_at)) {
    return handOver(LABELS.replied, `${outcome}: reporter replied`);
  }

  const ageDays = (Date.now() - new Date(botComment.created_at).getTime()) / 86400000;
  if (ageDays >= FEEDBACK_TIMEOUT_DAYS) {
    return handOver(LABELS.noFeedback, `${outcome}: no feedback after ${Math.floor(ageDays)} days`);
  }
  log(`${outcome}: waiting (${ageDays.toFixed(1)} days)`);
}

async function main() {
  const dryRun = hasFlag('--dry-run');
  const token = process.env.GITHUB_TOKEN;
  if (!token && !dryRun) {
    throw new Error('GITHUB_TOKEN not set');
  }

  const github = new GithubClient(process.env.GITHUB_REPOSITORY || DEFAULT_GITHUB_REPOSITORY, token);
  const maintainer = process.env.MAINTAINER_GITHUB_USERNAME || DEFAULT_MAINTAINER_GITHUB_USERNAME;
  const botLogin = process.env.TRIAGE_BOT_LOGIN || DEFAULT_BOT_LOGIN;

  const issues = await github.listIssuesWithLabel(LABELS.awaitingFeedback, 'open');
  console.log(`${issues.length} issue(s) awaiting feedback${dryRun ? ' (dry run)' : ''}`);
  for (const issue of issues) {
    await processIssue(github, issue, maintainer, botLogin, dryRun).catch((error) => console.error(`#${issue.number}: failed - ${(error as Error).message}`));
  }
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
