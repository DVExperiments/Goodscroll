# Goodscroll V1.5 — Research Intelligence

A complete replacement for V1.4, including **the 538-paper feed provided for this update**, already reclassified and enriched offline. No empty-feed startup.

## Install
1. Extract the ZIP; upload all contents (including `.github`) to the repository root.
2. GitHub Settings → Pages → GitHub Actions (as before).
3. Run **Collect research papers** under Actions to refresh the live catalogue and publish it automatically.
4. Hard-refresh the browser if its service worker cached the prior app.

## Changes
- Multi-label discipline classification using source metadata where available (OpenAlex field names, arXiv categories) and weighted title/abstract patterns.
- New categories: AI & Computing, Robotics, Creative Technology, Engineering and Business.
- Paper-specific **extractive** research question, methodology, author-reported findings, and limitations. Missing fields are explicitly marked unavailable. These excerpts are **not verified summaries of full papers**.
- Citation relationships ahead of keyword matches in Research Trails; citation direction retained.
- Quality flags, category confidence and category audit diagnostics in feed/health outputs.
- V1.4 direct-deploy GitHub Actions workflow preserved.

## Caveats
- Topic classification is heuristic and can be inaccurate; especially multi-disciplinary titles.
- An abstract can omit findings or limitations; no unsupported finding is created to fill gaps.
- Citation matches only work for references represented in the local catalogue.
- Live collection was not exercised in the offline build environment.
