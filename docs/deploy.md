# Deploying to GitHub Pages

This is a zero-build site: every file here is exactly what gets served. Deploying is
"put the files on Pages and point it on" — two supported routes below, plus the
prep work that never changes.

Works for both kinds of sites:

- **User/organization site** — repo named `<username>.github.io`, published at
  `https://<username>.github.io/`. This template ships pre-configured for that case.
- **Project site** — any repo name, published at `https://<username>.github.io/<repo>/`.
  The template's relative links already work there; for the two notes, see
  "Project-site specifics" at the bottom.

## Step 1 — Put the template into your repo

Create an empty repository on GitHub (do **not** let GitHub initialize it with a
README — you already have one). Then, from this folder:

```bash
git init                        # skip if this folder is already a git repo
git add -A
git commit -m "Initial author site"
git remote add origin https://github.com/<username>/<repo>.git
git branch -M main
git push -u origin main
```

Tip: if you cloned this template from somewhere, the fastest path is
`git remote set-url origin https://github.com/<username>/<repo>.git` instead of
`git remote add`.

## Step 2a — Recommended: deploy with the included workflow

This template includes `.github/workflows/deploy-pages.yml`.

1. Open your repo on GitHub → **Settings** → **Pages**.
2. Under *Build and deployment*, set **Source** to **GitHub Actions**.
3. Done. Every push to `main` (or a manual run from the *Actions* tab) deploys the
   site. First deployment usually takes about a minute.

The included workflow uploads the whole repository (wherever your HTML files live),
so it works either for a user site or a project site, with no per-deploy editing.

## Step 2b — Alternative: deploy from a branch

If you prefer not to use Actions at all:

1. **Settings** → **Pages**.
2. *Build and deployment* → **Source: Deploy from a branch**.
3. Choose **main** and **/(root)** → **Save**.

Same result for a static site; the workflow file simply sits unused (and harmless)
until you switch to Step 2a.

## Step 3 — Verify

1. Run the link checker locally before you announce anything:

   ```bash
   python3 scripts/check_links.py
   ```

   It is offline-first and should pass on a fresh clone. A twin workflow
   (`.github/workflows/check-links.yml`) runs the same check on every push, so a
   bad link on a live site should be rare and instantly visible in the *Actions* tab.

2. Open your site: `https://<username>.github.io/` (or `/<repo>/` for project sites).
3. Click the nav links, the buy slots, and the newsletter page.

## Before you announce it

Work through the customization checklist in the README — most importantly:

- the newsletter form's `action` attribute (currently a placeholder), and
- the buy-link slots on the books page (currently `https://example.com` placeholders).

## Project-site specifics

- The template's **relative links** (`books/`, `../assets/style.css`, …) work
  unchanged on both site types.
- `404.html` uses **absolute** links (`https://dylanasdale.github.io/books/`) because
  a 404 page is served at the URL of the missing page, where relative links cannot
  be trusted. On a project site, edit those absolute URLs to include your repo path
  (`https://<username>.github.io/<repo>/books/`). The file is marked with
  an `EDIT:` comment.

## Troubleshooting

| Symptom                                  | Fix                                                        |
| ---------------------------------------- | ---------------------------------------------------------- |
| First visit shows a GitHub 404           | Deployment is still building; wait a minute and refresh.   |
| Deploy fails in the Actions tab          | Check Settings → Pages → Source is "GitHub Actions".       |
| Styles missing only on a project site    | A link somewhere starts with `/` — the checker warns about those, so it will point at the exact line. |
| Checker fails after a new page           | It names file, line, and the problem; fix that first link. |
| Want a custom domain                     | Add a `CNAME` file containing your domain, and see GitHub Docs: "Managing a custom domain for your GitHub Pages site". |
