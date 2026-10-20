# Goodscroll V1.1 — Research Edition

An adult-focused research discovery feed for GitHub Pages. This release pivots from cheerful generic cards to actual scholarly metadata.

## What's new
- Editorial dark/light responsive UI
- Real research collector adapters: OpenAlex, Crossref, arXiv
- Publication dates, authors, journal/repository, DOI links, abstract previews
- Explicit preprint and evidence-status labeling; no invented AI summaries
- Research category filtering, search, reading list (localStorage)
- Explore Lab: serendipity, catalogue-based concept links, interdisciplinary prompts (no quizzes)
- API health diagnostics and last-known-good feed retention

## Deploy
1. Upload **the contents** of this ZIP to the root of your existing Goodscroll GitHub repository, replacing existing files. Preserve `.github/workflows`.
2. Under Settings → Pages, choose **GitHub Actions**.
3. In Actions, manually run **Collect research papers**. It attempts OpenAlex, Crossref, and arXiv. Check logs and `app/data/health.json` for per-source status.
4. Run **Deploy Goodscroll** if deployment has not run automatically. Refresh the site. If old styling persists, hard-refresh or clear the site's service-worker cache.
5. Optional: create an `OPENALEX_API_KEY` repository secret if the OpenAlex endpoint requires a key or imposes stricter anonymous limits.

## Important
- This archive intentionally starts with an **empty catalogue**, not fabricated research papers. Run the collection workflow to populate it.
- The collector has not been end-to-end verified against live APIs in this build environment. Provider errors are recorded in `health.json`; some providers may require API keys or endpoint changes.
- OpenAlex and Crossref records do not by themselves confirm peer-review status. arXiv is labeled as preprints.
- Research titles and abstracts may be copyrighted. Review provider terms and rights before any commercial release.
- The Explore Lab's interdisciplinary mode generates prompts, not scientifically verified connections; future versions should use citations/semantic links.
- User saves from the old version may not carry across due to the changed content IDs and storage keys.
