import { execFileSync } from 'child_process';
import { readFileSync } from 'fs';
import { join } from 'path';
import { CHANGELOG_PATH, DEFAULT_GITHUB_REPOSITORY, REPO_ROOT, SOURCE_DIR } from './config';
import { DocSection } from './docs';

/**
 * The integration version of the checked-out code. The release process bumps manifest.json, so
 * this is the latest release - and it's the same code the analysis is shown. Falls back to the
 * newest CHANGELOG.md heading.
 */
export function currentVersion(): string | null {
  try {
    const manifest = JSON.parse(readFileSync(join(SOURCE_DIR, 'manifest.json'), 'utf-8'));
    const match = String(manifest.version ?? '').match(/^(\d+\.\d+\.\d+)/);
    if (match) return match[1];
  } catch {
    // fall through to the changelog
  }
  return parseChangelog()[0]?.version ?? null;
}

export interface ChangelogLine {
  id: string;
  version: string;
  section: string;
  text: string;
  closes: number[];
}

export interface ChangelogRelease {
  version: string;
  lines: ChangelogLine[];
}

/** "19.0.0-beta.4" -> { base: "19.0.0", prerelease: "beta.4" }. */
export function splitVersion(full: string | null): { base: string | null; prerelease: string | null } {
  const match = full?.match(/^(\d+\.\d+\.\d+)(?:-(.+))?$/);
  return { base: match?.[1] ?? null, prerelease: match?.[2] ?? null };
}

export function compareVersions(a: string, b: string): number {
  const pa = a.split('.').map(Number);
  const pb = b.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    if (pa[i] !== pb[i]) return pa[i] - pb[i];
  }
  return 0;
}

/** True when the versions differ by at least a minor release (patch-only gaps don't nag). */
export function isMinorOrMoreBehind(reported: string, latest: string): boolean {
  const [rMajor, rMinor] = reported.split('.').map(Number);
  const [lMajor, lMinor] = latest.split('.').map(Number);
  return lMajor > rMajor || (lMajor === rMajor && lMinor > rMinor);
}

export function parseChangelog(): ChangelogRelease[] {
  const releases: ChangelogRelease[] = [];
  let current: ChangelogRelease | null = null;
  let section = '';
  let counter = 0;

  for (const line of readFileSync(CHANGELOG_PATH, 'utf-8').split('\n')) {
    const heading = line.match(/^#{1,2}\s+\[?(\d+\.\d+\.\d+)\]?/);
    if (heading) {
      current = { version: heading[1], lines: [] };
      releases.push(current);
      section = '';
      continue;
    }
    const sectionHeading = line.match(/^###\s+(.+)$/);
    if (sectionHeading) {
      section = sectionHeading[1].trim();
      continue;
    }
    const bullet = line.match(/^\*\s+(.+)$/);
    if (bullet && current) {
      const closesPart = bullet[1].match(/closes\s+(.+)$/)?.[1] ?? '';
      const closes = Array.from(closesPart.matchAll(/\[#(\d+)\]/g), (m) => Number(m[1]));
      current.lines.push({ id: `C${++counter}`, version: current.version, section, text: bullet[1].trim(), closes });
    }
  }
  return releases;
}

/** Releases newer than `reported`, up to and including `latest`. */
export function releasesBetween(releases: ChangelogRelease[], reported: string, latest: string): ChangelogRelease[] {
  return releases.filter((release) => compareVersions(release.version, reported) > 0 && compareVersions(release.version, latest) <= 0);
}

/** Changelog text without the markdown link noise, for sending to the model. */
export function plainChangelogText(text: string): string {
  return text
    .replace(/\(\[[0-9a-f]{7}\]\([^)]*\)\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/,?\s*closes\b.*$/i, '') // issue refs are rendered separately from `closes`
    .replace(/(^|[^\w`])@([A-Za-z0-9][A-Za-z0-9-]*)/g, '$1`@$2`') // credit contributors without pinging them
    .replace(/\s+/g, ' ')
    .trim();
}

function git(args: string[]): string | null {
  try {
    return execFileSync('git', args, { cwd: REPO_ROOT, encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'], maxBuffer: 20 * 1024 * 1024 });
  } catch {
    return null;
  }
}

export function currentSha(): string {
  return process.env.GITHUB_SHA || git(['rev-parse', 'HEAD'])?.trim() || 'HEAD';
}

/**
 * For "after upgrading" bugs: release notes as doc sections, so a reply can quote them (and links
 * are verified like any doc link). That's the release the reporter upgraded into, plus the breaking
 * changes of every release in the same major up to it - someone on 17.0.2 hit 17.0.0's (#1514).
 */
export function upgradeReleaseNotes(reportedVersion: string, releases: ChangelogRelease[]): DocSection[] {
  const major = reportedVersion.split('.')[0];
  const section = (release: ChangelogRelease, lines: ChangelogLine[], heading: string): DocSection => ({
    url: `https://github.com/${DEFAULT_GITHUB_REPOSITORY}/releases/tag/v${release.version}`,
    page: `Release notes v${release.version}`,
    headingPath: [`Release notes v${release.version}`, heading],
    content: lines.map((line) => `- [${line.section}] ${plainChangelogText(line.text)}`).join('\n'),
  });
  // The changelog can list a version more than once (pre-release headings); merge so each release URL
  // maps to one section, which doc-link validation relies on.
  const merged = new Map<string, ChangelogRelease>();
  for (const r of releases.filter((r) => r.version.split('.')[0] === major && compareVersions(r.version, reportedVersion) <= 0)) {
    const existing = merged.get(r.version);
    merged.set(r.version, existing ? { ...existing, lines: [...existing.lines, ...r.lines.filter((l) => !existing.lines.some((e) => e.text === l.text))] } : r);
  }
  return Array.from(merged.values())
    .map((release) =>
      release.version === reportedVersion
        ? release.lines.length
          ? section(release, release.lines, 'The release the reporter upgraded into')
          : null
        : release.lines.some((l) => /breaking/i.test(l.section))
          ? section(release, release.lines.filter((l) => /breaking/i.test(l.section)), 'Breaking changes')
          : null,
    )
    .filter((s): s is DocSection => s !== null);
}
