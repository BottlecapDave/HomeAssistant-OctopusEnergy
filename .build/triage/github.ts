export interface GithubComment {
  id: number;
  body: string;
  created_at: string;
  user: { login: string; type: string };
}

export interface GithubReaction {
  content: string;
  created_at: string;
  user: { login: string; type: string };
}

export interface GithubIssueSummary {
  number: number;
  title: string;
  body: string | null;
  state: string;
  html_url: string;
  created_at: string;
  closed_at?: string | null;
  state_reason?: string | null;
  user: { login: string; type: string };
  labels: Array<{ name: string } | string>;
  pull_request?: unknown;
}

export class GithubClient {
  private readonly permissionCache = new Map<string, string>();

  constructor(
    readonly repo: string,
    private readonly token: string | undefined,
  ) {}

  private async request<T>(method: string, path: string, body?: unknown, ignoreNotFound = false): Promise<T> {
    const headers: Record<string, string> = {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    };
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }
    if (body !== undefined) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`https://api.github.com${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(20000),
    });

    if (ignoreNotFound && response.status === 404) {
      return undefined as T;
    }
    if (!response.ok) {
      throw new Error(`GitHub ${method} ${path} failed: ${response.status} ${response.statusText}`);
    }

    return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
  }

  /** Follows `page=N` until a short page (max 10 pages of 100). */
  private async paginate<T>(path: string): Promise<T[]> {
    const results: T[] = [];
    for (let page = 1; page <= 10; page++) {
      const items = await this.request<T[]>('GET', `${path}${path.includes('?') ? '&' : '?'}per_page=100&page=${page}`);
      results.push(...items);
      if (items.length < 100) break;
    }
    return results;
  }

  getIssue(issueNumber: number): Promise<GithubIssueSummary> {
    return this.request('GET', `/repos/${this.repo}/issues/${issueNumber}`);
  }

  async searchIssues(query: string, perPage = 10): Promise<GithubIssueSummary[]> {
    const q = encodeURIComponent(`repo:${this.repo} is:issue ${query}`);
    const result = await this.request<{ items: GithubIssueSummary[] }>('GET', `/search/issues?q=${q}&per_page=${perPage}`);
    return result.items ?? [];
  }

  async listIssuesWithLabel(label: string, state: 'open' | 'closed' | 'all'): Promise<GithubIssueSummary[]> {
    const items = await this.paginate<GithubIssueSummary>(`/repos/${this.repo}/issues?state=${state}&labels=${encodeURIComponent(label)}`);
    return items.filter((item) => !item.pull_request);
  }

  listComments(issueNumber: number): Promise<GithubComment[]> {
    return this.paginate(`/repos/${this.repo}/issues/${issueNumber}/comments`);
  }

  listCommentReactions(commentId: number): Promise<GithubReaction[]> {
    return this.request('GET', `/repos/${this.repo}/issues/comments/${commentId}/reactions?per_page=100`);
  }

  async updateTitle(issueNumber: number, title: string): Promise<void> {
    await this.request('PATCH', `/repos/${this.repo}/issues/${issueNumber}`, { title });
  }

  async postComment(issueNumber: number, body: string): Promise<void> {
    await this.request('POST', `/repos/${this.repo}/issues/${issueNumber}/comments`, { body });
  }

  // Labels that don't exist yet are created automatically by this endpoint.
  async addLabels(issueNumber: number, labels: string[]): Promise<void> {
    if (labels.length) {
      await this.request('POST', `/repos/${this.repo}/issues/${issueNumber}/labels`, { labels });
    }
  }

  async removeLabel(issueNumber: number, label: string): Promise<void> {
    await this.request('DELETE', `/repos/${this.repo}/issues/${issueNumber}/labels/${encodeURIComponent(label)}`, undefined, true);
  }

  async addAssignees(issueNumber: number, assignees: string[]): Promise<void> {
    await this.request('POST', `/repos/${this.repo}/issues/${issueNumber}/assignees`, { assignees });
  }

  async closeIssue(issueNumber: number, stateReason: 'completed' | 'not_planned' | 'duplicate'): Promise<void> {
    await this.request('PATCH', `/repos/${this.repo}/issues/${issueNumber}`, { state: 'closed', state_reason: stateReason });
  }

  /** Same check as label_issues.yml: does this user have write/admin access to the repo? */
  async isMaintainer(username: string): Promise<boolean> {
    if (!this.permissionCache.has(username)) {
      try {
        const result = await this.request<{ permission: string }>(
          'GET',
          `/repos/${this.repo}/collaborators/${encodeURIComponent(username)}/permission`,
        );
        this.permissionCache.set(username, result.permission);
      } catch {
        this.permissionCache.set(username, 'none');
      }
    }
    return ['admin', 'write'].includes(this.permissionCache.get(username) ?? 'none');
  }
}
