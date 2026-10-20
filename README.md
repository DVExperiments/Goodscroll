# Goodscroll V1.3 — Research Discovery

An editorial mobile-friendly research feed hosted entirely on GitHub Pages.

## Upgrade from V1.2.1

1. Download and extract this ZIP.
2. Upload all files **inside** the ZIP to the repository root (including `.github`); replace existing files. **Keep** your existing `app/data/feed.json` if it already contains live papers, or let the collector repopulate it.
3. Commit to the default branch. Under Settings → Pages, set **GitHub Actions** as the source.
4. Actions → **Collect research papers** → Run workflow. This workflow collects, commits, and deploys directly; no second run is required.
5. Hard-refresh the browser or clear the PWA cache if you still see the previous version.

## Changes

- Wider subject queries and three-month collection window for OpenAlex, Crossref, arXiv, and Europe PMC.
- Explicit source diagnostics in `app/data/health.json`, including HTTP status, response size, accepted records, and exceptions.
- Deduplication by normalised DOI, preservation of old records, and category caps to limit a single discipline taking over.
- Date, access and preprint filters; persistent ordering; Serendipity reshuffle.
- Research Trails use citation metadata where available (OpenAlex `referenced_works`, Crossref DOIs) plus textual similarity. **Neither implies agreement or contradiction.**
- At-a-glance previews are labelled abstract excerpts, not invented findings or AI interpretations.
- Metadata-only review status: do not treat “journal article” as proof of peer review.

## Config

`OPENALEX_API_KEY` — optional workflow secret **if your API plan permits anonymous calls**; some OpenAlex API access now requires a key. A key is recommended. `OPENALEX_EMAIL` optional environment variable. Do not put keys in the frontend or repository. For no-access or rate-limit responses, the source error appears in health diagnostics and other sources remain usable.

## Known limitations

- The development environment cannot verify live responses from every public API; the GitHub Action is the integration test.
- Crossref may return few abstracts; the pipeline only publishes Crossref records with substantial abstract metadata. This is a deliberate accuracy/quality restriction, not necessarily an outage.
- Some papers are assigned `Other` or imperfect subject classifications using lightweight keyword tagging.
- Open-access metadata is not verified full-text permission; check original provider pages.
- The feed uses the paper abstract as its summary; full methodological reviews require reading the primary source. Some publisher abstracts have reuse restrictions; display only permitted excerpts and review the licensing terms for public use.
- GitHub Pages keeps preferences in the local browser rather than synced accounts.

## Diagnostics

View `https://YOUR-USERNAME.github.io/Goodscroll/data/health.json` (case-sensitive project path).
Check `sources`, `errors`, `by_category`, and `diagnostics` to diagnose zero-source contributions.

## Test locally

```bash
python -m py_compile collector/research.py
node --check app/app.js
python -m http.server 8080 --directory app
```

Open http://localhost:8080.
