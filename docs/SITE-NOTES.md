# Site Notes (GitHub Pages)

This repo uses GitHub Pages from:

- Branch: `main`
- Folder: `/docs`

## Why this matters

GitHub Pages only serves files inside the selected folder. If a link points outside `/docs`, it will break on the public site.

## Current structure

- `Docs/index.html` -> main IRONLOOP page
- `Docs/research/index.html` -> research hub
- `Docs/research/phase-01-state-output-research.html` -> first Phase 1 research page

## Link rules

- Keep public website links relative to files inside `Docs/`
- Do not link public nav directly to `Research/`, `Source/`, etc.
- Use local filesystem links (`file:///...`) only for local testing, not for committed site nav

## Publish checklist

1. Ensure new site pages are under `Docs/`
2. Check links are relative and resolve from `Docs/`
3. In GitHub Settings -> Pages, keep source as `main /docs`
4. After push, verify:
   - Main page loads
   - Research tab works
   - Research article pages load

## If you want canonical research docs in `Research/`

Keep `Research/` for project documentation if desired, but mirror any public pages into `Docs/` (or generate them) so Pages can serve them.

---

Created: March 5, 2026
