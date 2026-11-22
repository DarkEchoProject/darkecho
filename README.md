# Dark Echo

Static horror video and fiction site at https://darkechoproject.github.io/darkecho/.

## Edit and build

The canonical video catalog is `data/videos.json`. Every card and watch page is generated from the same video ID, title, description, duration, date, and channel entry. View counts are a dated snapshot, not a live counter. `data/articles.json` holds the labelled original fiction.

```powershell
python scripts/build.py
python scripts/check.py
```

The build requires Python 3.12 or later and uses the standard library. Generated HTML and optimized assets are checked in so GitHub Pages can publish directly from `main`; no package installation or API key is required to serve the website.

For a local preview:

```powershell
python scripts/serve.py
```

Open `http://localhost:4173/darkecho/`. Use the same `/darkecho/` path as production.

## Update a video

1. Add or update the single catalog entry using its exact YouTube ID. Verify the title, summary, upload time, channel, duration, and view-count date against the original upload.
2. Add the existing thumbnail optimized as `assets/thumbs/ID-320.webp` and `ID-640.webp` at 16:9. Keep the two variants small; do not reuse the former large background photos as card thumbnails.
3. Build, validate, review, then publish the generated changes together.

`clip` means running time up to three minutes; the site does not infer YouTube's Shorts classification from duration alone.

## Publishing

GitHub Pages publishes the checked-in site on the existing branch. Preserve `.nojekyll`. The existing page paths remain available. New watch pages use `watch/VIDEO_ID.html`. Shared CSS and JavaScript use content-derived cache version parameters.

The Nasser tutorial archive and its watch pages remain available through navigation but have `noindex, follow` and are excluded from the search sitemap. They are labelled as historical material.

See `docs/hosting.md` for host-root robots and HTTP-header limitations, and `docs/repairs-2026-11-22.md` for the repair record.
