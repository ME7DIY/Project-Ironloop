# Site Notes (GitHub Pages)

This repo uses GitHub Pages from:

- Branch: `main`
- Folder: `/docs`

## Why this matters

GitHub Pages only serves files inside the selected folder. If a link points outside `/docs`, it will break on the public site.

## Current structure

- `docs/index.html` -> main IRONLOOP page
- `docs/research/index.html` -> research hub
- `docs/research/phase-01-state-output-research.html` -> first Phase 1 research page
- `docs/` is the only public website tree (root mirror pages were removed)

## Link rules

- Keep public website links relative to files inside `docs/`
- Do not link public nav directly to `Research/`, `Source/`, etc.
- Use local filesystem links (`file:///...`) only for local testing, not for committed site nav

## Publish checklist

1. Ensure new site pages are under `docs/`
2. Check links are relative and resolve from `docs/`
3. In GitHub Settings -> Pages, keep source as `main /docs`
4. After push, verify:
   - Main page loads
   - Research tab works
   - Research article pages load

## If you want canonical research docs in `Research/`

Keep `Research/` for project documentation if desired, and publish any public pages into `docs/` so Pages can serve them.

---

Created: March 5, 2026
