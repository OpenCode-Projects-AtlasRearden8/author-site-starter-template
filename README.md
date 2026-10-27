# Author Site Starter Template — zero JavaScript, buildless, GitHub Pages ready

A copy-ready website for authors: a landing page, a books grid with buy-link slots, a
newsletter signup placeholder, about and contact pages, one shared stylesheet with a
large-print-friendly default, a copy-paste page template, a deploy-to-Pages walkthrough,
and a lint-style link checker that passes offline on a fresh clone.

No npm. No build step. No JavaScript. You edit HTML and push.

Built by **Asdale Dynamics, LLC** (Indiana) — the folks behind Dylan Asdale's
plain-English AI books and the hub site
[dylanasdale.github.io](https://dylanasdale.github.io/). MIT licensed; see [LICENSE](LICENSE).

Related starters by the same publisher — [open-book-starter-template](https://github.com/dylanasdale/open-book-starter-template)
for manuscript and book interiors, and [open-webapp-starter-template](https://github.com/dylanasdale/open-webapp-starter-template)
for web apps. This one is strictly the public-facing author website.

## Why zero JavaScript

Static pages load instantly, work with JavaScript off, print well, need no dependencies
to rot, and are trivially private — no folder of telemetry here even if you wanted any.
Readers notice the speed, and the site survives every redesign of every toolchain.

## What's inside

```
index.html          landing page (hero, three starter points, featured book, newsletter teaser)
books/index.html    books grid with buy-link slots (one live example, one pattern card, one empty slot)
newsletter/index.html  newsletter signup placeholder (plain HTML form; wire your provider, see checklist)
about/index.html    about page with photo slot and copy that is easy to rewrite in your voice
contact/index.html  contact page (email slot, social slots, response expectation)
404.html            friendly not-found page served on GitHub Pages
page-template.html  copy-paste starting point for new pages, slot walkthrough in comments
assets/style.css    the ONE stylesheet: large-print-friendly default, dark mode, print styles
scripts/check_links.py  lint-style link checker (Python 3.9+, standard library only)
docs/deploy.md      the full deploy-to-Pages walkthrough
.github/workflows/  check-links.yml (lint on every push) and deploy-pages.yml (publish on push to main)
```

## Quick start

1. **Edit the text.** Every customizable slot in the HTML is marked with
   `<!-- EDIT: ... -->` or `<!-- BUY-LINK SLOT: ... -->` comments. Open the files, replace
   what the comments point at, save — that is the entire build system.
2. **Check your work:**

   ```bash
   python3 scripts/check_links.py
   ```

   A fresh clone passes offline, first try. The checker verifies that every local link
   and fragment resolves, and lints pages for missing titles, viewport tags, spread-out
   tags, images without alt text, `javascript:` URLs, and non-relative internal links.

3. **Preview locally** (optional but nice):

   ```bash
   python3 -m http.server 8000
   ```

   then open http://localhost:8000 in a browser.

4. **Push to GitHub** and follow `docs/deploy.md` to switch Pages on (recommended route:
   the included `deploy-pages.yml` workflow; the classic "Deploy from branch" route works
   too and is documented).

## Customization checklist

Work top to bottom; each line searches to exactly one thing.

- [ ] **Site name** — `<p class="site-name">` in every page's header (and `404.html`).
- [ ] **Hero wording** — `index.html`, the `<h1>` and `<p class="lede">`.
- [ ] **Books grid** — `books/index.html`; replace the buy-link slots
      (`https://example.com` placeholders) with real store URLs, and edit or delete the
      example card and the empty slot card.
- [ ] **Newsletter** — `newsletter/index.html`: set the form's `action` to your provider
      (Buttondown, Kit, Mailchimp, Formspree, self-hosted listmonk — anything accepting a
      plain POST). Until you do, nothing is sent; wire it before announcing.
- [ ] **Email** — `hello@example.com` appears in `contact/index.html` and
      `newsletter/index.html`.
- [ ] **Social links** — `https://github.com/dylanasdale` appears in every footer; swap
      or add profiles on `contact/index.html`.
- [ ] **About page** — photo slot and bio on `about/index.html`; keep the "education,
      never medical advice" note if your subject touches health, and delete it if not.
- [ ] **Footer line** — `© ... · published by ...` in every page's footer.
- [ ] **404 page** — absolute links there assume a `username.github.io`-style site; for
      project-site deploys, insert `/repo/` into them (marked with `EDIT:` comments).
- [ ] **Colors and size** — `assets/style.css`, the `:root` block at the top. The
      `font-size` line is the large-print knob.

## New pages, buildless editing

Copy `page-template.html`, rename it, and follow its comments:

- A plain copy `my-page.html` is reachable at `/my-page.html`; for clean URLs use a
  folder: `my-page/index.html` (reachable at `/my-page/`).
- Keep internal links **relative** (never starting with `/`), and adjust `assets/...`
  to `../assets/...`, nav links to `../books/` etc. if the page moves into a folder —
  the template comments spell this out, and the checker corrects you if you forget.
- Run `python3 scripts/check_links.py` before pushing. That's it.

## Large print and accessibility

- The site's default type is deliberately big (approx. 18px) with generous line-height;
  one CSS line (commented in `assets/style.css`) moves the whole site to true large print.
- Dark mode follows the reader's system (`prefers-color-scheme`); nothing to toggle.
- Skip link, keyboard-visible focus styles, one `h1` per page, alt-text lint — built in,
  and partly enforced by the checker.
- Print stylesheet: the buttons hide, the copy prints warm-and-readable.

## Verification the checker actually checks

Beyond link existence, each run verifies anchors against real `id`s, tags nest cleanly
(unclosed `<div>`s get caught with a line number), pages have a `lang` attribute, a
title, and a viewport meta, and local links stay inside the site. External links are
counted and skipped (offline-first); use `--external` while connected to
best-effort fetch them all, too.

## Credits and license

Written and maintained by **Asdale Dynamics, LLC** — beginner-friendly AI education,
open-source author tools, and practical small-business helpers.

MIT License. [LICENSE](LICENSE) carries the full text; the copyright line is:

```
Copyright (c) 2026 Asdale Dynamics, LLC
```

The template is meant to be copied, rebranded, and shipped by other authors. If you
would like to credit it, a link back to
[dylanasdale.github.io](https://dylanasdale.github.io/) is the warm, optional way to do
so.
