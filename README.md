# Goodscroll V1.4 — Evidence & Discovery

A direct-upload GitHub Pages upgrade built on the functioning V1.3 deployment pipeline.

## Install
1. Upload **all files inside** this ZIP to the root of your existing Goodscroll GitHub repository, replacing files, including `.github`.
2. Important: this archive contains an empty `app/data/feed.json` placeholder because your real 539-paper catalogue lives in GitHub, not this workspace. **Keep your existing populated `app/data/feed.json` and `app/data/health.json` when uploading**, or run **Actions → Collect research papers** immediately afterwards to repopulate.
3. The collection workflow collects, commits and deploys in one job. If caching persists, hard-refresh or clear website data.
4. Confirm `app/data/health.json` displays `version: 1.4.0` and inspect About / Sources.

## Highlights
- Redesigned editorial cards with provenance cues, labelled abstract extracts, careful “why it might matter” topic context, and expandable evidence notes.
- Evidence notes never claim to have assessed the full methodology, peer-review status or strength of findings.
- Editorial mix ordering uses transparent metadata indicators and recency; newest and serendipity remain.
- Research Trails retain citation connections where metadata is provided; do not imply consensus or contradiction.
- Collection health adds abstract presence, DOI availability, open access indicators, preprints, citation metadata, age bands, and candidate merging counts.
- Content source and direct deployment workflow unchanged, keeping all four working API adapters.

## Limitations
No LLM or full-text synthesis is included. “Why it might matter” is discipline-level topic context, **not a paper-specific verified finding**. Abstract excerpts may have publisher reuse restrictions: check terms before broad public release. Open-access flags do not automatically grant permission to redistribute full text. Publication type does not independently prove peer review. `duplicate_or_replaced_candidates` is a merged-candidate metric, not a confirmed count of identical studies.

## Test
```
python -m py_compile collector/research.py
node --check app/app.js
python -m http.server 8080 --directory app
```
