#!/usr/bin/env python3
"""
check_links.py — lint-style link checker for the author-site starter template.

Built to pass with NO NETWORK, first try, on a fresh clone. Offline-first design:

  * Every local href/src in every .html page must point at a file that exists
    inside the site. Directory links (e.g. "books/") fall back to that
    directory's index.html.
  * #fragments are verified against id (and legacy <a name>) attributes in the
    target page.
  * Each page is linted for: lang attribute, non-empty <title>, viewport meta,
    tag balance, exactly one <h1> (warn), img without alt (warn),
    duplicate ids (warn), http:// externals (warn), javascript: URLs (error,
    this is a zero-JavaScript template), and internal links starting with "/"
    (warn, since they break on project Pages sites like /repo/).
  * External http(s) links are NOT fetched. They are syntax-checked and
    skipped, so a clean clone passes offline. Use --external (opt-in, online)
    to also best-effort fetch each external link.

Usage:
  python3 scripts/check_links.py              # check the site around this script
  python3 scripts/check_links.py --quiet      # only print problems
  python3 scripts/check_links.py --external   # also try fetching external URLs

Exit codes: 0 = no errors (warnings allowed), 1 = errors found.
"""
from __future__ import annotations

import argparse
import posixpath
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
BALANCED_TAGS = {
    "html", "head", "body", "header", "footer", "main", "section", "article",
    "aside", "nav", "div", "ul", "ol", "li", "p", "h1", "h2", "h3", "h4", "h5",
    "h6", "form", "label", "blockquote", "figure", "figcaption", "a", "button",
    "details", "summary", "table", "tr", "td", "th", "thead", "tbody",
}
HREF_TAGS = {"a", "link", "area"}
SRC_TAGS = {"img", "script", "iframe", "source"}
SKIP_SCHEMES = {"mailto", "tel", "sms", "data"}


class PageParse(HTMLParser):
    """Collect links, ids, and lint facts from one HTML page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[int, str, str]] = []   # (line, href|src, raw value)
        self.ids: dict[str, int] = {}                  # anchor -> first line seen
        self.dup_ids: list[tuple[str, int]] = []
        self.imbalance: list[tuple[int, str]] = []     # (line, message)
        self.imgs_missing_alt: list[int] = []
        self.lang = ""
        self.title = ""
        self.viewport = False
        self.h1_count = 0
        self._stack: list[tuple[int, str]] = []
        self._in_title = False

    # -- hooks ------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        pos = self.getpos()[0]
        if tag == "html":
            self.lang = a.get("lang") or ""
        if tag == "title":
            self._in_title = True
        if tag == "meta" and a.get("name", "").lower() == "viewport":
            self.viewport = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "img" and "alt" not in a:
            self.imgs_missing_alt.append(pos)
        if a.get("id"):
            anchor = a["id"]
            if anchor in self.ids:
                self.dup_ids.append((anchor, pos))
            else:
                self.ids[anchor] = pos
        elif tag == "a" and a.get("name"):
            self.ids.setdefault(a["name"], pos)
        if tag in HREF_TAGS and a.get("href") is not None:
            self.links.append((pos, "href", a["href"]))
        if tag in SRC_TAGS and a.get("src") is not None:
            self.links.append((pos, "src", a["src"]))
        if tag in BALANCED_TAGS and tag not in VOID_TAGS:
            self._stack.append((pos, tag))

    def handle_data(self, data):
        if self._in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in BALANCED_TAGS and tag not in VOID_TAGS:
            if self._stack and self._stack[-1][1] == tag:
                self._stack.pop()
                return
            names = [t for _, t in self._stack]
            if tag in names:
                # Unclosed children between here and the matching opener.
                while self._stack and self._stack[-1][1] != tag:
                    pos, unclosed = self._stack.pop()
                    self.imbalance.append((pos, f"unclosed <{unclosed}>"))
                if self._stack:
                    self._stack.pop()
            else:
                self.imbalance.append((self.getpos()[0], f"</{tag}> without opener"))

    def finish(self):
        for pos, tag in self._stack:
            self.imbalance.append((pos, f"unclosed <{tag}>, never closed before end of file"))

    # -- results ----------------------------------------------------------
    def facts(self) -> dict:
        return {
            "lang": self.lang,
            "title": self.title.strip(),
            "viewport": self.viewport,
            "h1": self.h1_count,
        }


class Site:
    def __init__(self, root: Path, args) -> None:
        self.root = root
        self.args = args
        self.ignore_parts = {".git", ".github", "node_modules", ".venv", "__pycache__"}
        self.problems: list[tuple[str, int, str, str]] = []   # (relpath, line, sev, msg)
        self.external: dict[str, list[tuple[str, int]]] = {}  # url -> [(path, line)]
        self.ext_done: set[str] = set()
        self.stats = {"pages": 0, "internal": 0, "anchors": 0, "placeholders": 0,
                      "external": 0, "warns": 0, "errors": 0}
        self._ids_cache: dict[Path, dict[str, int]] = {}

    # -- helpers ----------------------------------------------------------
    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def report(self, path: Path, line: int, sev: str, msg: str) -> None:
        self.problems.append((self.rel(path), line, sev, msg))
        if sev == "error":
            self.stats["errors"] += 1
        else:
            self.stats["warns"] += 1

    def ids_of(self, path: Path) -> dict[str, int]:
        if path not in self._ids_cache:
            parser = PageParse()
            parser.feed(path.read_text(encoding="utf-8", errors="replace"))
            parser.close()
            self._ids_cache[path] = parser.ids
        return self._ids_cache[path]

    def link_stack(self, page: Path, raw_path: str, root_absolute: bool) -> list[str] | None:
        """Turn a link path into a list of segs from the site root; None means 'escapes root'."""
        stack = [] if root_absolute else list(page.relative_to(self.root).parts[:-1])
        for seg in raw_path.split("/"):
            if seg in ("", ".",):
                continue
            if seg == "..":
                if not stack:
                    return None
                stack.pop()
            else:
                stack.append(unquote(seg))
        return stack

    def resolve_stack(self, stack: list[str]) -> Path | None:
        """Walk segs from the site root; a final directory falls back to its index.html."""
        cur = self.root
        for seg in stack:
            nxt = cur / seg
            if nxt.exists():
                cur = nxt
                continue
            try:
                entries = list(cur.iterdir())
            except OSError:
                return None
            hits = [e for e in entries if e.name.lower() == seg.lower()]
            if len(hits) != 1:  # no match, or ambiguous case-insensitive match
                return None
            cur = hits[0]
        if cur.is_dir():
            idx = cur / "index.html"
            return idx if idx.is_file() else None
        return cur

    # -- main walk --------------------------------------------------------
    def run(self) -> bool:
        pages = sorted(
            p for p in self.root.rglob("*.html")
            if not any(part in self.ignore_parts for part in p.relative_to(self.root).parts)
        )
        for page in pages:
            self.check_page(page)
        ok = self.stats["errors"] == 0
        return ok

    def check_page(self, page: Path) -> None:
        self.stats["pages"] += 1
        parser = PageParse()
        parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        parser.close()
        parser.finish()
        facts = parser.facts()

        for line, msg in parser.imbalance:
            self.report(page, line, "error", f"bad tag nesting: {msg}")
        if not facts["lang"]:
            self.report(page, 1, "error", '<html> tag is missing a lang attribute')
        if not facts["title"]:
            self.report(page, 1, "error", "missing or empty <title>")
        if not facts["viewport"]:
            self.report(page, 1, "error", "missing <meta name=\"viewport\"> (needed on small screens)")
        if facts["h1"] != 1:
            self.report(page, 1, "warn", f"expected exactly one <h1>, found {facts['h1']}")
        for line in parser.imgs_missing_alt:
            self.report(page, line, "warn", "<img> is missing alt text")
        for anchor, line in parser.dup_ids:
            self.report(page, line, "warn", f"duplicate id=\"{anchor}\" — targets would be ambiguous")

        for line, kind, raw in parser.links:
            self.check_link(page, line, raw, parser.ids)

    def check_link(self, page: Path, line: int, raw: str, own_ids: dict[str, int]) -> None:
        value = raw.strip()
        if value in ("", "#"):
            self.stats["placeholders"] += 1   # deliberate empty slots are allowed
            return

        parts = urlsplit(value)
        scheme = parts.scheme.lower()

        if scheme == "javascript":
            self.report(page, line, "error", "javascript: URL found — this template is zero-JavaScript by policy")
            return
        if scheme in SKIP_SCHEMES:
            return
        if scheme in ("http", "https"):
            self.external.setdefault(value, []).append((page, line))
            self.stats["external"] += 1
            if scheme == "http":
                self.report(page, line, "warn", "http:// external link — prefer https://")
            return
        if scheme:  # unknown scheme, keep it linted but skipped
            self.report(page, line, "warn", f"unrecognised URL scheme '{scheme}:' — left unverified")
            return
        if parts.netloc:  # protocol-relative //example.com/x
            self.report(page, line, "warn", "protocol-relative URL — write https://… explicitly if you intend external")
            return

        # ---- local link from here on ----
        self.stats["internal"] += 1
        fragment = unquote(parts.fragment)
        path = parts.path

        if not path:
            if fragment:
                if fragment not in own_ids:
                    self.report(page, line, "error", f"anchor #{fragment} not found on this page")
                else:
                    self.stats["anchors"] += 1
            else:
                self.report(page, line, "error", "empty href/src value")
            return

        root_absolute = path.startswith("/")
        decoded = path.lstrip("/")  # absolute /books/ and relative books/ resolve the same way
        stack = self.link_stack(page, decoded, root_absolute)
        if stack is None:
            self.report(page, line, "error", f"link '{value}' escapes the site root — keep links inside the site")
            return

        target = self.resolve_stack(stack)
        if target is None:
            parent = self.root.joinpath(*stack[:-1]) if len(stack) > 1 else self.root
            near = sorted(p.name for p in parent.glob("*"))
            hint = f" — nothing here looks similar, nearby names: {near}" if near else ""
            self.report(page, line, "error", f"link target does not exist: '{value}'{hint}")
            return
        if stack and not self.root.joinpath(*stack).exists():
            self.report(page, line, "warn",
                        f"link '{value}' matches only case-insensitively — GitHub Pages is case-sensitive, match the file's real name")

        dirish = path.endswith(("/", ".html")) or path in (".", "..", "./", "../")
        if not dirish and target.name == "index.html":
            suggestion = posixpath.normpath("/".join(stack)) + "/"
            self.report(page, line, "warn",
                        f"link '{value}' points at a folder without a trailing slash — prefer '{suggestion}'")

        if root_absolute:
            self.report(page, line, "warn",
                        f"link '{value}' starts with '/': fine on site-root domains, breaks on project Pages sites — prefer relative links")

        if fragment:
            if fragment not in self.ids_of(target):
                what = self.rel(target)
                self.report(page, line, "error", f"anchor #{fragment} not found in '{what}'")
            else:
                self.stats["anchors"] += 1

    # -- external mode ----------------------------------------------------
    def check_external(self) -> None:
        for url in sorted(self.external):
            if url in self.ext_done:
                continue
            self.ext_done.add(url)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "link-check/1.0 (+static site)"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status >= 400:
                        self.external_warn(url, f"HTTP {resp.status}")
            except Exception as exc:  # noqa: BLE001 — offline or bad URL, both are lint notes
                self.external_warn(url, f"could not fetch ({type(exc).__name__}: {exc})")

    def external_warn(self, url: str, why: str) -> None:
        where = self.external[url][0]
        self.report(where[0], where[1], "warn", f"external link {why}: {url}")

    # -- output -----------------------------------------------------------
    def print_report(self, quiet: bool) -> None:
        sev_rank = {"error": 0, "warn": 1}
        self.problems.sort(key=lambda t: (t[0], t[1], sev_rank[t[2]]))
        for relpath, line, sev, msg in self.problems:
            if quiet and sev != "error":
                continue
            print(f"{relpath}:{line}: {sev}: {msg}")

        s = self.stats
        if not quiet:
            print(f"pages scanned:        {s['pages']}")
            print(f"internal links ok:    {s['internal']}  (fragments verified: {s['anchors']})")
            print(f"external skipped:     {s['external']}  (offline-first; retry with --external to fetch them)")
            print(f"placeholders skipped: {s['placeholders']}  (hrefs like '#' are called out by design)")
            print(f"warnings:             {s['warns']}")
            print(f"errors:               {s['errors']}")
        print("RESULT: " + ("OK — site passes" if s["errors"] == 0 else "PROBLEMS FOUND — see above"))


def main() -> int:
    default_root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="Lint-style link checker for the author site template (offline-first).")
    ap.add_argument("root", nargs="?", default=default_root, type=Path,
                    help="site root (default: the folder this script lives in)")
    ap.add_argument("-q", "--quiet", action="store_true", help="print only errors")
    ap.add_argument("--external", action="store_true",
                    help="also best-effort fetch external http(s) links (requires network)")
    args = ap.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: site root '{root}' is not a directory", file=sys.stderr)
        return 2

    site = Site(root, args)
    ok = site.run()
    if ok and args.external:
        site.check_external()
        ok = site.stats["errors"] == 0
    site.print_report(args.quiet)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
