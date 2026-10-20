# Goodscroll v1.2 — Research Trails

An editorial research-discovery web app for GitHub Pages. Research trails link papers by shared concepts from their actual titles and abstracts; **they are not citation relationships, scientific agreement, or AI conclusions**.

## Deploy

1. Upload all files and folders in this ZIP **to the repository root**, including `.github`.
2. Settings → Pages → Source: **GitHub Actions**.
3. Actions → **Collect research papers** → Run workflow. Wait for it to finish and inspect `app/data/health.json` and `app/data/feed.json` in the repository.
4. Actions → **Deploy Goodscroll** (or wait for deployment) and reload the site.
5. The feed initially contains no fabricated papers. **Collection is required** to populate it.

## Data providers

- OpenAlex: works metadata, abstracts where supplied. An `OPENALEX_API_KEY` GitHub Actions repository secret may be needed depending on API access policies.
- Crossref: DOI and publisher metadata; abstracts are not always available.
- arXiv: preprint Atom API; preprints are **not automatically peer reviewed**.
- Europe PMC: biomedical papers and abstracts via public REST search.

Collectors use Python standard library. Per-source failures are recorded in `app/data/health.json`. Previously collected papers are retained on failures. The feed refreshes every six hours via GitHub Actions, and can be triggered manually. Sources can impose quotas, rate limits or change their interfaces.

## New in v1.2

- **Explore connections** on every paper: start a research trail.
- Follow papers with overlapping concepts; filter within the same discipline or across disciplines.
- Click another paper to branch the trail.
- Explicit research-context warnings; no unsupported claims about consensus or contradiction.
- Added Europe PMC as a fourth metadata source.
- Better empty-state instructions for first-time deployment.

## Privacy and limitations

Saved papers stay in browser local storage. Paper matching is a simple keyword-overlap heuristic and is sensitive to the quality and breadth of collected abstracts. It does not yet use Semantic Scholar citations or OpenAlex citation graph. Do not treat automated connections as a literature review. Source links remain available for verification.
