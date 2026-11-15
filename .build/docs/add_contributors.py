"""Add a "Contributors" footer to each built docs page.

Zensical doesn't support the mkdocs git-authors plugin yet, so this replicates it as a
post-build step. Contributors are taken from `git blame` of each page's source file
(i.e. people with lines still present in the page) and grouped by email, matching the plugin's behaviour.

Usage: python .build/docs/add_contributors.py [docs_dir] [site_dir]
"""

import html
import subprocess
import sys
from collections import Counter
from pathlib import Path

CONTRIBUTORS_ICON = (
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 5.5A3.5 3.5 0 0 1 15.5 9a3.5 3.5 0 0 1-3.5 '
  '3.5A3.5 3.5 0 0 1 8.5 9 3.5 3.5 0 0 1 12 5.5M5 8c.56 0 1.08.15 1.53.42-.15 1.43.27 2.85 1.13 3.96C7.16 13.34 6.16 14 '
  '5 14a3 3 0 0 1-3-3 3 3 0 0 1 3-3m14 0a3 3 0 0 1 3 3 3 3 0 0 1-3 3c-1.16 0-2.16-.66-2.66-1.62a5.54 5.54 0 0 0 '
  '1.13-3.96c.45-.27.97-.42 1.53-.42M5.5 18.25c0-2.07 2.91-3.75 6.5-3.75s6.5 1.68 6.5 3.75V20h-13zM0 '
  '20v-1.5c0-1.39 1.89-2.56 4.45-2.9-.59.68-.95 1.62-.95 2.65V20zm24 0h-3.5v-1.75c0-1.03-.36-1.97-.95-2.65 2.56.34 '
  '4.45 1.51 4.45 2.9z"/></svg>'
)

UNCOMMITTED_AUTHOR = "Not Committed Yet"


def git(*args: str) -> str:
  return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def get_blamed_lines(source: Path) -> Counter:
  """Count the lines in the file attributed to each (email, name) pair."""
  lines = Counter()
  name = None
  for line in git("blame", "--line-porcelain", "--", str(source)).splitlines():
    if line.startswith("author "):
      name = line[len("author "):].strip()
    elif line.startswith("author-mail ") and name and name != UNCOMMITTED_AUTHOR:
      email = line[len("author-mail "):].strip().strip("<>").casefold()
      lines[(email, name)] += 1
  return lines


def get_display_names(blamed: dict[Path, Counter]) -> dict[str, str]:
  """People can commit under several names with the same email (like the git-authors plugin, group by email).
  Use the name that owns the most lines across all docs, so each person is named consistently on every page."""
  totals = Counter()
  for lines in blamed.values():
    totals.update(lines)

  display_names = {}
  for (email, name), _ in totals.most_common():
    display_names.setdefault(email, name)
  return display_names


def get_built_page(source: Path, docs_dir: Path, site_dir: Path) -> Path:
  relative = source.relative_to(docs_dir).with_suffix("")
  if relative.name in ("index", "README"):
    return site_dir / relative.parent / "index.html"
  return site_dir / relative / "index.html"


def build_footer(contributors: list[str]) -> str:
  names = html.escape(", ".join(contributors))
  return (
    '<aside class="md-source-file">'
    '<span class="md-source-file__fact">'
    f'<span class="md-icon" title="Contributors">{CONTRIBUTORS_ICON}</span>'
    f'<nav>{names}</nav>'
    '</span>'
    '</aside>'
  )


def main() -> int:
  docs_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "_docs")
  site_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "site")

  # A shallow clone would attribute every line to the oldest fetched commit, giving wrong names
  if git("rev-parse", "--is-shallow-repository").strip() == "true":
    print("Repository is a shallow clone; fetch full history (e.g. fetch-depth: 0) to add contributors", file=sys.stderr)
    return 1

  pages = {}
  for source in sorted(docs_dir.rglob("*.md")):
    page = get_built_page(source, docs_dir, site_dir)
    if page.is_file():
      pages[source] = page

  blamed = {source: get_blamed_lines(source) for source in pages}
  display_names = get_display_names(blamed)

  updated = 0
  for source, page in pages.items():
    contributors = sorted({display_names[email] for email, _ in blamed[source]})
    if not contributors:
      continue

    content = page.read_text(encoding="utf-8")
    if 'title="Contributors"' in content or "</article>" not in content:
      continue

    head, tail = content.rsplit("</article>", 1)
    page.write_text(f"{head}{build_footer(contributors)}</article>{tail}", encoding="utf-8")
    updated += 1

  print(f"Added contributors to {updated} page(s)")
  return 0


if __name__ == "__main__":
  sys.exit(main())
