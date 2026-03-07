# Project IRONLOOP - New Chat Handoff
Last updated: 2026-03-07 (America/Chicago)
Owner: `kitza`
Repo root: `C:\Users\kitza\Documents\Project-Ironloop`
Branch: `main`
Latest pushed commit: `9b2666e`

## 1) Project Mission
Project IRONLOOP is a bench Hardware-in-the-Loop (HIL) system to connect:
- virtual engine state from `engine-sim`
- into real ME7/ME7.5 ECU-like sensor signals
- then later read ECU output behavior back into the sim loop

High-level phase model:
1. Engine state output from sim
2. Fake minimum sensor signal generation
3. Crank/cam trigger generation
4. Closed-loop ECU output feedback
5. AI-assisted map discovery/tuning workflows

## 2) What Is Done Right Now
### Phase 1 software status
- UDP state broadcast path implemented in engine-sim patch workflow.
- Python bridge path is working for conversion and CSV logging flows.
- Validation script has passed minimum profile checks with no range/rate violations.

### Website and docs status
- GitHub Pages canonical source is `docs/` only.
- Redundant root website mirrors were removed from repo.
- Main dashboard text encoding corruption (mojibake sequences) was fixed and pushed.
- Main index AI card emojis were removed per user preference.

## 3) Recently Pushed Commits (Most Relevant)
- `b4fe4ab` Fix UTF-8 mojibake on main docs index page
- `91e4105` Remove legacy site mirrors and keep docs as canonical
- `26b7f1b` Remove emoji icons from AI cards on main index
- `e3d8e0f` Finalize ME7.5 AK pinout page with explicit Elsa-confirmed mapping
- `0ee9ad0` Add ME7 bench core quickstart card and link it in guides
- `7ff9f75` Add Funktionsrahmen digest and Phase 2 minimum signals research pages

## 4) Current Public Site Structure (Canonical)
Only these site entry pages should be treated as canonical:
- `docs/index.html`
- `docs/research/index.html`
- `docs/roadmap/index.html`
- `docs/guides/index.html`

Deployment notes:
- GitHub Pages source: `main /docs`
- `docs/.nojekyll` is present
- Deployment behavior should ignore non-`docs` website files (which were removed)

## 5) Current Working Tree State (Not Committed)
Important: repo is currently dirty with active local work. Do not reset or clean blindly.

Tracked modifications currently present:
- `Source/Phase-01-EngineSimPatch/python-bridge/bridge_config.json`
- `Source/Phase-01-EngineSimPatch/python-bridge/hardware_io.py`
- `Source/Phase-01-EngineSimPatch/python-bridge/signal_generator.py`
- `docs/roadmap/index.html`
- Submodule path marked dirty: `Source/Phase-01-EngineSimPatch/engine-sim`

Untracked additions currently present (selected highlights):
- `Source/Phase-01-EngineSimPatch/python-bridge/start_logging_run.py`
- `Source/Phase-01-EngineSimPatch/python-bridge/validate_signal_outputs.py`
- `docs/roadmap/nohardware-3week-roadmap.md`
- `docs/research/ME7-Universal-Harness-Guide.html`
- `docs/guides/Pinout Diagrams/SS/` (screenshot evidence bundle)
- `docs/guides/Harness Diagram/` (drawio source set)
- `docs/handoffs/` (this handoff folder)

## 6) ECU and Harness Context Captured So Far
Target ECU discussed:
- Audi ME7.5 family example: `8E0 909 518 AK`, marked as ME7.5 `0004`

Core bench power/diagnostic intent documented:
- ECU grounds and power rails separated as constant vs switched bench rails
- OBD bench access path documented around:
  - OBD pin 16 = +12V supply
  - OBD pin 4/5 = ground
  - OBD pin 7 = K-line

Important process correction learned:
- Earlier community/AI pin claims were treated as untrusted until ElsaWin cross-check.
- User now has ElsaWin running and has begun extracting current flow diagrams directly.

## 7) Key Docs Added/Used
### Guides
- `docs/guides/pinout-diagrams-8e0-909-518-ak-me7-5-0004.html`
- `docs/guides/pinout-golden-worksheet-8e0-909-518-ak.html`
- `docs/guides/me7-bench-core-quickstart-card.html`

### Research pages
- `docs/research/phase-02-minimum-signals-research.html`
- `docs/research/funktionsrahmen-me7-reference.html`

### Local design artifacts
- Draw.io harness diagrams under `docs/guides/Harness Diagram/`
- Pinout screenshot/source bundle under `docs/guides/Pinout Diagrams/SS/`

## 8) What The Next Chat Should Do First
1. Confirm whether to prioritize:
   - software bridge cleanup, or
   - ElsaWin pin extraction and guide hardening, or
   - no-hardware 3-week roadmap execution
2. If website/docs polish is the focus:
   - commit staged docs artifacts in small logical commits
   - keep all public links inside `docs/` only
3. If bench electrical work is the focus:
   - continue from ElsaWin current-flow pages for AMB/ME7.5
   - convert verified pin evidence into a pinned table in guides
4. If python-bridge work resumes:
   - reconcile modified + untracked bridge files
   - run validation scripts against saved CSV runs

## 9) Safety and Collaboration Rules For Next Agent
- Do not run destructive cleanup (`reset --hard`, mass deletes) without explicit user approval.
- Assume current dirt is intentional unless user says otherwise.
- Keep `docs/` as the only website source of truth.
- Treat ECU pin claims as provisional unless backed by ElsaWin or equivalent primary docs.
- User preference: the agent should handle staging/commits/pushes by default.
- For every scoped commit, append one short bullet to `docs/roadmap/roadmap-progression-log.md`.
- Use `docs/roadmap/git-safety-cleanup-playbook.md` as the default commit safety workflow.

## 10) Quick Continuation Prompt For New Chat
Use this starter prompt in a new chat:

"Read `docs/handoffs/HANDOFF.md` first. Treat `docs/` as canonical website source. Do not clean/reset unrelated local changes. Start by summarizing current dirty tree and propose the next smallest safe commit for either (A) bridge scripts, (B) ElsaWin pinout hardening, or (C) roadmap docs." 

## 11) Known-Good Commands (Fast Start)
Run from repo root unless noted.

Bridge validation run (existing workflow):
```powershell
cd Source\Phase-01-EngineSimPatch\python-bridge
python .\validate_signal_outputs.py --csv ..\logs\runs\20260305-210209_dual_sink_smoke.csv --config .\bridge_config.json --profile phase2_minimum
```

Expected success signature:
- `[validator] PASS: no range/rate violations detected`

Find website entry points quickly:
```powershell
Get-ChildItem -Recurse -Filter index.html | Select-Object -ExpandProperty FullName
```

Push website changes:
```powershell
git push origin main
```

## 12) Open Decisions (Needs User Direction)
1. Commit scope for in-progress bridge files:
- keep local-only for now, or
- stage and ship as Phase 1.5 tooling commit.

2. Pinout authority workflow:
- continue using ElsaWin-only verification first, then update guides, or
- draft provisional tables now with explicit "unverified" labels.

3. Roadmap execution priority:
- no-hardware tasks first, or
- immediate hardware prep doc tasks.

4. Research publishing:
- keep long-form references in `Research/` and publish concise versions to `docs/research/`.

## 13) Known Risks and Gotchas
- `engine-sim` submodule is dirty and ownership checks may fail in sandbox contexts.
- Do not clean submodule folders unless user explicitly asks.
- GitHub Pages only serves `/docs`; links to root or `Research/index.html` are invalid now.
- Some PowerShell views may still show mojibake in terminal output even when HTML is fixed.
- User has active untracked docs assets (screenshots, drawio, PDFs). Avoid accidental deletion.

## 14) Next Safe Commit Options
Option A (docs only, safest):
- stage `docs/roadmap/index.html`
- stage `docs/roadmap/nohardware-3week-roadmap.md`
- stage any finalized guides/research HTML under `docs/`

Option B (bridge tooling package):
- stage `Source/Phase-01-EngineSimPatch/python-bridge/start_logging_run.py`
- stage `Source/Phase-01-EngineSimPatch/python-bridge/validate_signal_outputs.py`
- include related config/script updates only if tested together

Option C (pinout evidence publish):
- stage curated screenshot evidence references from `docs/guides/Pinout Diagrams/SS/`
- update pinout guide pages with ElsaWin-backed notes and confidence labels

## 15) First 15-Minute Plan For New Chat
1. Read this handoff file fully.
2. Run `git status --short` and summarize dirty state in 5 lines max.
3. Ask user to choose A/B/C commit path (docs, bridge, pinout evidence).
4. Execute smallest complete commit with clear message.
5. Push to `main` and verify website-impacting changes if docs were touched.

## 16) User Communication Style Notes
- User prefers direct practical guidance and step-by-step wiring clarity.
- User is learning circuits from scratch; avoid jargon without plain-language translation.
- Confidence claims on pinouts should be tied to ElsaWin evidence, not forum memory.
- Keep momentum high with small wins and frequent concrete checkpoints.
- User usually wants the agent to execute git actions directly (stage, commit, push) rather than manual user git steps.
