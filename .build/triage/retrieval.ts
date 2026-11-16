import { existsSync, readdirSync, readFileSync, statSync } from 'fs';
import { join, relative } from 'path';
import { Bm25Index } from './bm25';
import { BLUEPRINTS_DIR, BLUEPRINTS_REPO_PREFIX, REPO_ROOT, SOURCE_DIR } from './config';
import { LogSignals } from './logs';

export interface CodeChunk {
  /** Repo-relative path, e.g. custom_components/octopus_energy/coordinators/electricity_rates.py */
  file: string;
  name: string;
  startLine: number;
  endLine: number;
  lines: string[];
}

export interface SourceFile {
  file: string;
  lines: string[];
}

const MAX_CHUNK_LINES = 150;
const MAX_CHUNKS_PER_FILE = 12;
const DEF_LINE = /^(\s*)(?:async\s+def|def|class)\s+(\w+)/;

function walkPythonFiles(dir: string): string[] {
  const results: string[] = [];
  for (const entry of readdirSync(dir)) {
    if (entry === '__pycache__') {
      continue;
    }
    const fullPath = join(dir, entry);
    if (statSync(fullPath).isDirectory()) {
      results.push(...walkPythonFiles(fullPath));
    } else if (entry.endsWith('.py')) {
      results.push(fullPath);
    }
  }
  return results;
}

/**
 * Splits a Python file into one chunk per def/class (decorators included), plus a module header
 * chunk for imports/constants. Very long functions are split into parts so one huge function
 * can't use up the whole context budget.
 */
function chunkFile(file: string, lines: string[]): CodeChunk[] {
  const starts: Array<{ line: number; name: string }> = [];
  lines.forEach((line, index) => {
    const match = line.match(DEF_LINE);
    if (match) {
      let start = index;
      while (start > 0 && lines[start - 1].trim().startsWith('@')) {
        start--;
      }
      starts.push({ line: start, name: match[2] });
    }
  });

  // Code before the first def/class (imports, constants) becomes a <module> chunk.
  const boundaries = starts[0]?.line === 0 ? starts : [{ line: 0, name: '<module>' }, ...starts];

  const chunks: CodeChunk[] = [];
  boundaries.forEach((boundary, index) => {
    const end = index + 1 < boundaries.length ? boundaries[index + 1].line : lines.length;
    for (let partStart = boundary.line, part = 1; partStart < end; partStart += MAX_CHUNK_LINES, part++) {
      const partEnd = Math.min(partStart + MAX_CHUNK_LINES, end);
      const chunkLines = lines.slice(partStart, partEnd);
      if (chunkLines.every((line) => !line.trim())) {
        continue;
      }
      chunks.push({
        file,
        name: part > 1 ? `${boundary.name} (part ${part})` : boundary.name,
        startLine: partStart + 1,
        endLine: partEnd,
        lines: chunkLines,
      });
    }
  });
  return chunks;
}

export class CodeIndex {
  readonly files = new Map<string, SourceFile>();
  readonly chunks: CodeChunk[] = [];
  private readonly symbols = new Map<string, CodeChunk[]>();
  /** unique_id f-string prefix/suffix -> entity file, e.g. ("octopus_energy_electricity_", "_current_rate") */
  private readonly entityPatterns: Array<{ prefix: string; suffix: string; file: string }> = [];
  /** Literal start of entity `name` f-strings -> file, e.g. "current accumulative consumption gas" */
  private readonly entityNames: Array<{ name: string; file: string }> = [];
  /** file -> in-repo files it imports (relative imports only) */
  private readonly imports = new Map<string, string[]>();
  /** blueprint file -> lower-cased blueprint name, e.g. "octopus energy - join weekend happy hour event" */
  private readonly blueprintNames = new Map<string, string>();
  private readonly bm25: Bm25Index;

  constructor() {
    for (const fullPath of walkPythonFiles(SOURCE_DIR)) {
      const file = relative(REPO_ROOT, fullPath).split('\\').join('/');
      const lines = readFileSync(fullPath, 'utf-8').split('\n');
      this.files.set(file, { file, lines });
      for (const chunk of chunkFile(file, lines)) {
        this.chunks.push(chunk);
        const symbol = chunk.name.replace(/ \(part \d+\)$/, '');
        this.symbols.set(symbol, [...(this.symbols.get(symbol) ?? []), chunk]);
      }

      const text = lines.join('\n');
      for (const match of text.matchAll(/return f"(octopus_energy_[a-z_]*?)\{[^"]*\}([a-z_]+)"/g)) {
        this.entityPatterns.push({ prefix: match[1], suffix: match[2], file });
      }
      for (const match of text.matchAll(/def name\(self\)[^\n]*\n(?:\s*"""[^\n]*\n)?\s*return f?"([^"{]+)/g)) {
        const name = match[1].replace(/[\s([:-]+$/, '').trim().toLowerCase();
        if (name.split(/\s+/).length >= 2) {
          this.entityNames.push({ name, file });
        }
      }
      const dir = file.split('/').slice(0, -1);
      const imported = Array.from(text.matchAll(/^from (\.+)([\w.]*) import/gm), (m) => {
        const base = dir.slice(0, dir.length - (m[1].length - 1));
        return [...base, ...m[2].split('.').filter(Boolean)].join('/');
      });
      this.imports.set(file, imported.flatMap((path) => [`${path}.py`, `${path}/__init__.py`]));
    }

    for (const entry of existsSync(BLUEPRINTS_DIR) ? readdirSync(BLUEPRINTS_DIR).sort() : []) {
      if (!entry.endsWith('.yaml')) continue;
      const file = `${BLUEPRINTS_REPO_PREFIX}/${entry}`;
      const lines = readFileSync(join(BLUEPRINTS_DIR, entry), 'utf-8').split('\n');
      this.files.set(file, { file, lines });
      const name = lines.join('\n').match(/^\s+name:\s*(.+)$/m)?.[1].trim() ?? entry;
      this.blueprintNames.set(file, name.toLowerCase());
      for (let start = 0, part = 1; start < lines.length; start += MAX_CHUNK_LINES, part++) {
        const chunkLines = lines.slice(start, start + MAX_CHUNK_LINES);
        if (chunkLines.every((line) => !line.trim())) continue;
        this.chunks.push({ file, name: `blueprint: ${name}${part > 1 ? ` (part ${part})` : ''}`, startLine: start + 1, endLine: start + chunkLines.length, lines: chunkLines });
      }
    }

    // The chunk's file path and name are included so e.g. "standing charge" matches
    // electricity/current_standing_charge.py even if the words don't appear in the body.
    this.bm25 = new Bm25Index(this.chunks.map((chunk) => `${chunk.file} ${chunk.name}\n${chunk.lines.join('\n')}`));
  }

  /** Entity files for entity ids mentioned in the text, matched on unique_id prefix + suffix. */
  entityFilesFor(text: string): string[] {
    const files = new Set<string>();
    for (const token of text.toLowerCase().match(/octopus_energy_[a-z0-9_<>]+/g) ?? []) {
      const matches = this.entityPatterns.filter((pattern) => token.includes(pattern.prefix) && token.endsWith(pattern.suffix));
      const longest = Math.max(0, ...matches.map((match) => match.suffix.length));
      matches.filter((match) => match.suffix.length === longest).forEach((match) => files.add(match.file));
    }
    return Array.from(files);
  }

  /** Entity files whose display name (e.g. "Current Standing Charge") appears in the text. */
  entityFilesByName(text: string): string[] {
    const lower = text.toLowerCase().replace(/\s+/g, ' ');
    return Array.from(new Set(this.entityNames.filter((entity) => lower.includes(entity.name)).map((entity) => entity.file)));
  }

  /** Source files referenced by path in the text, e.g. "coordinators/account.py" or "__init__.py". */
  mentionedFiles(text: string): string[] {
    const files = new Set<string>();
    for (const match of text.match(/[\w/]+\.py\b/g) ?? []) {
      const path = match.replace(/^.*custom_components\/octopus_energy\//, '');
      const exact = `custom_components/octopus_energy/${path}`;
      if (this.files.has(exact)) files.add(exact);
    }
    return Array.from(files);
  }

  /** File/symbol sets derived from the issue text and logs, used to boost chunks in select(). */
  private querySignals(query: string, signals: LogSignals) {
    const entityFiles = new Set([...this.entityFilesFor(query), ...this.entityFilesByName(query)]);
    const mentionedFiles = new Set(this.mentionedFiles(query));
    // Coordinators/helpers imported by the entity, traceback and mentioned files usually hold the logic.
    const importedFiles = new Set(
      [...entityFiles, ...mentionedFiles, ...signals.tracebackFrames.map((frame) => frame.file)]
        .flatMap((file) => this.imports.get(file) ?? [])
        .filter((imported) => this.files.has(imported) && !imported.endsWith('/const.py')),
    );
    return {
      entityFiles,
      mentionedFiles,
      importedFiles,
      loggerFiles: new Set(signals.loggerFiles),
      mentionsBlueprint: /blueprint/i.test(query),
      // Named by its title (with or without the "Octopus Energy - " prefix) or by file name.
      blueprintFiles: new Set(
        Array.from(this.blueprintNames).filter(([file, name]) => {
          const lower = query.toLowerCase().replace(/\s+/g, ' ');
          return lower.includes(name) || lower.includes(name.replace(/^octopus energy - /, '')) || lower.includes(file.split('/').pop().replace(/\.yaml$/, ''));
        }).map(([file]) => file),
      ),
      mentionedSymbols: new Set((query.match(/\b[A-Za-z_][A-Za-z0-9_]{5,}\b/g) ?? []).filter((word) => this.symbols.has(word))),
    };
  }

  /**
   * Picks the chunks most likely to matter, strongest signal first: traceback frames, then entity
   * classes and files named in the issue, imported coordinators, logger modules, symbols named in
   * the issue, and finally BM25 relevance.
   */
  select(query: string, signals: LogSignals, maxChars: number): CodeChunk[] {
    const bm25 = this.bm25.score(query);
    const q = this.querySignals(query, signals);

    const scored = this.chunks.map((chunk, index) => {
      let score = bm25[index] * 10;
      // Not cumulative per frame: a long traceback through one big file shouldn't drag in all of it.
      const frames = signals.tracebackFrames.filter((frame) => frame.file === chunk.file);
      if (frames.some((frame) => frame.line >= chunk.startLine && frame.line <= chunk.endLine)) score += 100;
      else if (frames.length) score += 2;
      if (q.loggerFiles.has(chunk.file)) score += 2 + 4 * bm25[index];
      if (q.entityFiles.has(chunk.file)) score += 12;
      if (q.mentionedFiles.has(chunk.file)) score += 10;
      if (q.importedFiles.has(chunk.file)) score += 4;
      if (q.blueprintFiles.has(chunk.file)) score += 30;
      else if (q.mentionsBlueprint && this.blueprintNames.has(chunk.file)) score += 3 * bm25[index];
      // A name defined in many files (e.g. async_setup_entry in every platform) is a weak signal.
      if (q.mentionedSymbols.has(chunk.name)) score += 30 / (this.symbols.get(chunk.name)?.length ?? 1);
      return { chunk, score };
    });

    scored.sort((a, b) => b.score - a.score);
    // Cap chunks per file so one large module can't crowd everything else out (traceback hits exempt).
    const perFile = new Map<string, number>();
    const ranked = scored
      .filter((s) => s.score > 0)
      .filter((s) => {
        const count = (perFile.get(s.chunk.file) ?? 0) + 1;
        perFile.set(s.chunk.file, count);
        return count <= MAX_CHUNKS_PER_FILE || s.score >= 100;
      })
      .map((s) => s.chunk);
    return takeWithinBudget(ranked, maxChars);
  }


}

function chunkSize(chunk: CodeChunk): number {
  return chunk.lines.reduce((total, line) => total + line.length + 8, 0);
}

/** Chunks in order (duplicates skipped) for as long as they fit in the budget. */
function takeWithinBudget(chunks: CodeChunk[], maxChars: number): CodeChunk[] {
  const result = new Set<CodeChunk>();
  let used = 0;
  for (const chunk of chunks) {
    const size = chunkSize(chunk);
    if (!result.has(chunk) && used + size <= maxChars) {
      result.add(chunk);
      used += size;
    }
  }
  return Array.from(result);
}

/** Renders chunks grouped by file in line order, each line prefixed with its number for citation. */
export function renderChunks(chunks: CodeChunk[]): string {
  const byFile = new Map<string, CodeChunk[]>();
  for (const chunk of chunks) {
    byFile.set(chunk.file, [...(byFile.get(chunk.file) ?? []), chunk]);
  }

  const sections: string[] = [];
  for (const [file, fileChunks] of byFile) {
    fileChunks.sort((a, b) => a.startLine - b.startLine);
    const parts: string[] = [`### ${file}`];
    let lastEnd = 0;
    for (const chunk of fileChunks) {
      if (lastEnd && chunk.startLine > lastEnd + 1) {
        parts.push('...');
      }
      chunk.lines.forEach((line, offset) => parts.push(`L${chunk.startLine + offset}: ${line}`));
      lastEnd = chunk.endLine;
    }
    sections.push(parts.join('\n'));
  }
  return sections.join('\n\n');
}
