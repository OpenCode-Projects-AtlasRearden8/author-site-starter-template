# STATUS.md — author-site-starter-template

Last updated: 2026-10-27 · repository: this folder (git initialized, one commit below)

## What was built

A copy-ready, zero-JavaScript author website template for GitHub Pages. Plain HTML
files are edited directly — there is no build step, no package manager, and no
JavaScript anywhere.

| File | Role |
| --- | --- |
| `index.html` | Landing page: hero, three "what you'll find here" cards, featured book, newsletter teaser |
| `books/index.html` | Books grid with buy-link slots: one live-pattern card, one in-progress card, one dashed empty slot |
| `newsletter/index.html` | Newsletter signup placeholder: plain HTML POST form, provider slot documented in comments |
| `about/index.html` | About page with photo slot and an "education, never medical advice" callout |
| `contact/index.html` | Contact page: email slot, response expectation, reasons to write, social slots |
| `404.html` | Friendly not-found page served by GitHub Pages |
| `page-template.html` | Copy-paste starting point for new pages; every slot marked `EDIT:` in comments |
| `assets/style.css` | The one stylesheet: large-print-friendly default (~18px base, one-knob scaling), dark mode via `prefers-color-scheme`, `@media print` styles, warm cream/terracotta palette |
| `scripts/check_links.py` | Lint-style link checker, Python 3.9+, standard library only, offline-first |
| `docs/deploy.md` | Full deploy-to-Pages walkthrough (Actions route + branch route + troubleshooting) |
| `.github/workflows/deploy-pages.yml` | Publishes the site on every push to `main` (after one-time "Source: GitHub Actions" setting) |
| `.github/workflows/check-links.yml` | Runs the link checker on every push/PR |
| `.nojekyll`, `.gitignore`, `LICENSE`, `README.md` | Repo plumbing; MIT License, copyright exactly `Copyright (c) 2026 Asdale Dynamics, LLC` |

Example content carries the intended audience's voice (Dylan Asdale / Asdale Dynamics,
LLC); every content slot is marked with `EDIT:` or `BUY-LINK SLOT:` comments and the
README has a one-line-per-item customization checklist.

## How to run it

```bash
# preview locally
python3 -m http.server 8000          # open http://localhost:8000

# or with no server at all
# open index.html directly in a browser (fully static, works)

# lint check (offline by default)
python3 scripts/check_links.py
python3 scripts/check_links.py --quiet      # errors only
python3 scripts/check_links.py --external   # opt-in online fetch of external links
```

Deploying: follow `docs/deploy.md` (git push, then Settings → Pages → Source:
"GitHub Actions" once).

## Verification results (all run here, python 3.13.5 / git 2.47.3)

1. **Offline checker pass on the working copy**:
   `7 pages, 59 internal links ok (6 fragments verified), 16 external skipped, 0 warnings, 0 errors — RESULT: OK` · exit 0.
2. **Offline pass on a fresh copy** — site copied to `/tmp`, checker run before any
   mutation: passes with the same counts (proves "clones cleanly, passes offline first try").
3. **HTTP smoke test** — `python3 -m http.server`, curl on all seven pages plus stylesheet:
   every URL returns `200`, and an unrelated path returns `404` (Pages will serve `404.html` there).
4. **Negative tests (checker really checks)** — on a mutated copy, the checker exits 1 and reports:
   - renamed link target `bookz/`: 3× `link target does not exist` errors, each with nearby-name hints;
   - broken fragment `#maain`: `anchor not found` error;
   - unclosed `<h2>`: `bad tag nesting` error;
   - case-mismatched `Assets/style.css`: warning ("GitHub Pages is case-sensitive"); exit stays 0.
5. **Online mode** — `--external` fetched all 16 external URLs: the real hub domain and
   GitHub resolve; the five deliberately-fake `example.com` placeholders are reported as
   warnings; exit code remains 0 (external misses are warnings by design).
6. **Git** — initialized on `main`, single commit `ab0ff8a "Add zero-JavaScript author site
   template for GitHub Pages"`, committed as the pre-existing identity
   (Dylan Asdale `dylanasdale@users.noreply.github.com`), no co-author trailers, working tree clean.

## Known gaps (deliberate, and where to fix them)

- **Newsletter form is not wired** — the `action` points at an `example.com` placeholder by
  design; set your provider's endpoint (README checklist item 4) before announcing the page.
- **Buy links are placeholders** — swaps are documented; nothing else changes.
- **No sitemap.xml / canonical URLs / Open Graph tags** — omitted to keep the template
  minimal and domain-free; add your own once the final domain is fixed.
- **External link health is not verified in CI** — the CI workflow runs offline-first;
  add a nightly `--external` job if you want live store links monitored.
- **HTML validation is lint-level** — the checker catches broken links, anchors, tag
  balance, and missing basics, but it is not a full W3C validator (which needs network).
- **`404.html` uses absolute URLs** — correct for a `username.github.io` site; needs a
  `/repo/` insertion on project-site deploys (marked `EDIT:` in the file and in `docs/deploy.md`).
- **Actions marketplace versions** — the pinned `actions/*` versions were current at
  writing time but not verified live; worth bumping when you adopt the template.

## Notes for the next person

- All pages share one `<head>`/header/footer shape; copy from `page-template.html`.
- Relative links everywhere (except the documented `404.html` case) keep the template
  working on both `username.github.io` and `username.github.io/repo/` URLs.
- The large-print knob is the `font-size` line inside `:root` in `assets/style.css`.
