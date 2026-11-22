# Dark Echo

Static horror video and fiction site at https://darkechoproject.github.io/darkecho/.

## Edit and build

The canonical video catalog is `data/videos.json`. Every card and watch page is generated from the same video ID, title, description, duration, date, and channel entry. View counts are a dated snapshot, not a live counter. `data/articles.json` holds the labelled original fiction and its explicit update dates. `data/series.json` contains the ordered chapters and complete versions; `data/site.json` contains the production base URL and the maintained site revision date.

```powershell
python scripts/build.py
python scripts/check.py
python scripts/test_catalog.py
node --test scripts/test-browser-helpers.cjs
```

The build requires Python 3.12 or later; the browser-helper regression checks require Node.js 18 or later. The generator uses the Python standard library. Generated HTML and optimized assets are checked in so GitHub Pages can publish directly from `main`; no package installation or API key is required to serve the website.

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

## Browsing features

- Archive search matches every typed word regardless of order and handles accents, apostrophe variants, and punctuation. Filters and sort order are shareable through the URL; returning from a watch page preserves the number of revealed results.
- `series.html` and `series/SLUG.html` group existing horror chapters in the explicit source order. Chapter watch pages link to the previous/next part and complete story.
- `watch-later.html` reads a device-only saved-video list (`darkecho-watch-later-v1`). It has no server account and is intentionally `noindex, follow`. Its card templates are inert until a video is saved; empty lists load no thumbnail images or YouTube frames. Clearing browser site data removes the list.
- Watch, story, and series pages offer a copy-link action with a selectable URL fallback. Stories include chapter links and an approximate reading time.
- Content and ordinary links are server-rendered. Menus remain visible without JavaScript; enhanced controls are hidden until initialized. All archive cards remain available in the HTML.

When content changes, maintain `contentUpdatedAt` and `revision` in `data/site.json`. Update an article's own `updated` date only when that article changes. Thumbnail view counts remain dated to `data/videos.json` rather than presented as live totals.
