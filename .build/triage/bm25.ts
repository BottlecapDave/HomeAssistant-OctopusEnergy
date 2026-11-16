import { tokenize } from './text';

/**
 * Minimal BM25 index. Unlike the old raw keyword count, scores are normalised by document length,
 * so large files no longer win just by being large, and rare terms count for more than common ones.
 */
export class Bm25Index {
  private readonly termFrequencies: Array<Map<string, number>>;
  private readonly lengths: number[];
  private readonly documentFrequency = new Map<string, number>();
  private readonly averageLength: number;

  constructor(documents: string[], private readonly k1 = 1.2, private readonly b = 0.75) {
    this.termFrequencies = documents.map((document) => {
      const frequencies = new Map<string, number>();
      for (const token of tokenize(document)) {
        frequencies.set(token, (frequencies.get(token) ?? 0) + 1);
      }
      for (const token of frequencies.keys()) {
        this.documentFrequency.set(token, (this.documentFrequency.get(token) ?? 0) + 1);
      }
      return frequencies;
    });
    this.lengths = this.termFrequencies.map((frequencies) => Array.from(frequencies.values()).reduce((a, c) => a + c, 0));
    this.averageLength = this.lengths.reduce((a, c) => a + c, 0) / Math.max(this.lengths.length, 1) || 1;
  }

  /** Returns a score per document, scaled so the best document scores 1 (all zero if no match). */
  score(query: string): number[] {
    const terms = Array.from(new Set(tokenize(query)));
    const total = this.termFrequencies.length;
    const scores = this.termFrequencies.map((frequencies, index) => {
      let score = 0;
      for (const term of terms) {
        const frequency = frequencies.get(term);
        if (!frequency) {
          continue;
        }
        const df = this.documentFrequency.get(term) ?? 0;
        const idf = Math.log(1 + (total - df + 0.5) / (df + 0.5));
        const norm = frequency + this.k1 * (1 - this.b + (this.b * this.lengths[index]) / this.averageLength);
        score += idf * ((frequency * (this.k1 + 1)) / norm);
      }
      return score;
    });
    const max = Math.max(...scores, 0);
    return max > 0 ? scores.map((score) => score / max) : scores;
  }
}
