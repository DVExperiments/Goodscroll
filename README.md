# ✳ Goodscroll v1.0 — Find your good

A mobile-first, installable discovery feed designed around **joy, wonder, creativity, calm, and play**. No accounts, no trackers, no engagement bait.

## What works
- Mixed feed with responsive card layout and source links
- Five content pillars and mood filters
- Save/unsave content in browser localStorage
- Interest weighting, negative feedback, simple variety-aware feed ranking
- Three original interactive quiz cards
- Sharing, browser installability, offline shell and cached feed fallback
- Python collector with NASA APOD, Wikimedia Commons and Met Open Access adapters
- Content-health report and scheduled GitHub Actions refresh

## Publish on GitHub Pages
1. Create a new public repository named `Goodscroll` (or any name).
2. **Upload the files and folders inside this archive directly into the repository root**, including `.github`. Do not upload the outer `goodscroll-v1` folder as one nested directory.
3. In **Settings → Pages → Build and deployment**, choose **GitHub Actions**.
4. In **Actions**, run **Deploy Goodscroll** manually if it does not trigger after uploading.
5. Open `https://YOUR-USERNAME.github.io/Goodscroll/` (adjust for repo name). On Android, use browser menu → **Add to Home screen** / **Install app**.
6. In **Actions**, run **Collect Goodscroll content** manually to try fetching live items. It will then run every six hours. Optional: set repository secret `NASA_API_KEY` to improve NASA request quota.

## Local development
From the repository root:

```sh
python -m http.server 8000 --directory app
```

Open http://localhost:8000/ . To refresh feed data:

```sh
python collector/build.py
```

No Node build, pip dependencies or API keys are required to run the starter app.

## Content sources and licensing
- The initial feed includes 15 authored starter items. These are **not** fetched live.
- Live collectors require outbound internet access and are **not verified against live endpoints in this release**. Failures are recorded in `app/data/health.json`, and the last valid feed is retained.
- NASA imagery may have additional restrictions; see NASA's media usage guidelines.
- Wikimedia Commons items are linked to file descriptions and show reported license/artist; verify requirements before redistributing images.
- The Met adapter only selects public-domain objects. The Met API may change; failures are nonfatal.
- The app does **not** scrape social networks, republish copyrighted articles, or run an AI content generator.
- Media remains linked to its original source; remote availability may vary.

## Limitations / next iteration
- No accounts, cloud sync, comments, or user submissions.
- Recommendation weights are simple and local, not machine learning.
- The feed starts small and relies on online media providers; emoji placeholders are intentional when image rights are unclear.
- The collector's Wikipedia/Openverse/YouTube integrations, richer interactive experiences, verification queue and human content review are planned but not implemented.
- Content health is a developer-oriented status panel under About, not a full administrative dashboard.
- Cached feed is available only after the app has successfully fetched it at least once.

## Privacy
Saved items, preferences, and reactions remain in the browser's local storage. No analytics SDK or tracking pixels are included. Third-party media and outbound source links may contact those providers.

## Structure
- `app/`: deployable static PWA
- `app/data/`: published content catalogue and collection health
- `collector/build.py`: collection and safe fallback pipeline
- `content/seed.json`: manually authored starter content
- `.github/workflows/`: scheduled collection and Pages deployment
