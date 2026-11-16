import { readdirSync, readFileSync, statSync } from 'fs';
import { join, relative } from 'path';
import { Bm25Index } from './bm25';
import { DOCS_BASE_URL, DOCS_DIR } from './config';
import { normalizeWhitespace } from './text';

export interface DocSection {
  url: string;
  page: string;
  headingPath: string[];
  content: string;
}

const MAX_SECTION_CHARS = 3000;

function walkMarkdown(dir: string): string[] {
  const results: string[] = [];
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry);
    if (statSync(fullPath).isDirectory()) {
      results.push(...walkMarkdown(fullPath));
    } else if (entry.endsWith('.md')) {
      results.push(fullPath);
    }
  }
  return results;
}

/** Python-Markdown `toc` extension's default slugify, which mkdocs uses for heading anchors. */
export function slugify(heading: string): string {
  const text = heading
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1') // links -> link text
    .replace(/<[^>]+>/g, '') // inline html
    .replace(/[`*]/g, '') // inline code / emphasis markers
    .normalize('NFKD')
    .replace(/[^\x00-\x7F]/g, '');
  return text
    .replace(/[^\w\s-]/g, '')
    .trim()
    .toLowerCase()
    .replace(/[-\s]+/g, '-');
}

function pageUrl(relativePath: string): string {
  const withoutExt = relativePath.split('\\').join('/').replace(/\.md$/, '');
  if (withoutExt === 'index') return DOCS_BASE_URL;
  if (withoutExt.endsWith('/index')) return `${DOCS_BASE_URL}${withoutExt.slice(0, -'index'.length)}`;
  return `${DOCS_BASE_URL}${withoutExt}/`;
}

function parsePage(fullPath: string): DocSection[] {
  const page = pageUrl(relative(DOCS_DIR, fullPath));
  const lines = readFileSync(fullPath, 'utf-8').split('\n');
  const sections: DocSection[] = [];
  const usedIds = new Set<string>();
  const headingStack: Array<{ level: number; text: string }> = [];
  let current: { url: string; lines: string[] } = { url: page, lines: [] };
  let inFence = false;

  const flush = () => {
    const content = current.lines.join('\n').trim();
    if (content) {
      sections.push({ url: current.url, page, headingPath: headingStack.map((h) => h.text), content });
    }
  };

  for (const line of lines) {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence;
    }
    const heading = !inFence && line.match(/^(#{1,6})\s+(.+?)\s*(?:\{\s*#([\w-]+)[^}]*\})?\s*$/);
    if (!heading) {
      current.lines.push(line);
      continue;
    }

    flush();
    const level = heading[1].length;
    const text = heading[2].replace(/\s+#+$/, '');
    // Python-Markdown makes duplicate ids unique by appending _1, _2, ...
    let id = heading[3] ?? slugify(text);
    if (usedIds.has(id)) {
      let suffix = 1;
      while (usedIds.has(`${id}_${suffix}`)) suffix++;
      id = `${id}_${suffix}`;
    }
    usedIds.add(id);

    while (headingStack.length && headingStack[headingStack.length - 1].level >= level) {
      headingStack.pop();
    }
    headingStack.push({ level, text });
    current = { url: level === 1 ? page : `${page}#${id}`, lines: [line] };
  }
  flush();
  return sections;
}

export class DocsIndex {
  readonly sections: DocSection[];
  private readonly bm25: Bm25Index;

  constructor() {
    this.sections = walkMarkdown(DOCS_DIR).flatMap(parsePage);
    // Headings are repeated so a heading match outweighs a passing mention in a long section.
    this.bm25 = new Bm25Index(
      this.sections.map((s) => `${s.headingPath.join(' ')} ${s.headingPath.join(' ')} ${s.headingPath.join(' ')}\n${s.content}`),
    );
  }

  select(query: string, maxChars: number): DocSection[] {
    const scores = this.bm25.score(query);
    const ranked = this.sections
      .map((section, index) => ({ section, score: scores[index] }))
      .filter((s) => s.score > 0.15)
      .sort((a, b) => b.score - a.score);

    const selected: DocSection[] = [];
    let used = 0;
    for (const { section } of ranked) {
      const size = Math.min(section.content.length, MAX_SECTION_CHARS) + 200;
      if (used + size > maxChars) continue;
      selected.push(section);
      used += size;
    }
    return selected;
  }
}

export function renderDocSections(sections: DocSection[]): string {
  return sections
    .map((section) => {
      const content =
        section.content.length > MAX_SECTION_CHARS ? `${section.content.slice(0, MAX_SECTION_CHARS)}\n...[section truncated]` : section.content;
      return `[DOC] URL: ${section.url}\nSection: ${section.headingPath.join(' > ')}\n${content}`;
    })
    .join('\n\n---\n\n');
}

export function normalizeDocUrl(url: string): string {
  const [path, anchor] = url.trim().split('#');
  const withSlash = path.endsWith('/') ? path : `${path}/`;
  return anchor ? `${withSlash}#${anchor}` : withSlash;
}

/** True if the quote appears in the section (whitespace-insensitive, truncated sections included). */
export function sectionContainsQuote(section: DocSection, quote: string): boolean {
  const normalizedQuote = normalizeWhitespace(quote).toLowerCase();
  return normalizedQuote.length >= 10 && normalizeWhitespace(section.content).toLowerCase().includes(normalizedQuote);
}
