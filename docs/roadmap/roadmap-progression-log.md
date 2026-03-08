# Project IRONLOOP - Roadmap Progression Log
Started: 2026-03-07
Owner: `kitza`
Purpose: Daily, short progress entries that track what changed and why.

## How To Use
- Add short bullets under the current date whenever meaningful progress is made.
- Create a new date header each day (for example `## 2026-03-08`) and continue logging below it.
- Keep entries concise and concrete (what changed, where, and outcome).

## 2026-03-07
- Added Pi<->Pico serial protocol v1 draft: `docs/research/pi-pico-serial-protocol-v1.md`.
- Added protocol vector generator: `Source/Phase-03-CrankCamSignal/generate_protocol_vectors.py`.
- Added first command/response smoke vectors: `Source/Phase-03-CrankCamSignal/vectors/pi_pico_protocol_smoke_v1.json`.
- Updated no-hardware 3-week roadmap task checkboxes for Week 2 deliverables.
- Updated validator behavior to:
  - apply profile `slew_limits` as rate limits when present
  - skip rate checks for very short intervals below configurable `--rate-min-dt`
  - apply configurable `--rate-tolerance` to reduce tiny over-limit noise
- Added validator `--rate-source` mode:
  - `max` (default): uses larger default/config limit per field for practical day-to-day checks
  - `config`: strict profile slew-limit enforcement
  - `default`: legacy fixed limits only
- Tuned validator practical defaults after WOT replay calibration:
  - `--rate-min-dt` default set to `0.003`
  - `--rate-tolerance` default set to `0.10` (10%)
  - strict validation still available with `--rate-source config`
- Commit `55eff6c`: updated ME7 bench order guide with AK pin-confidence workflow (scope: docs/guides).
- Added reusable git safety process doc: `docs/roadmap/git-safety-cleanup-playbook.md`.
- Committed to logging every scoped commit in this progression file to keep history clear and prevent drift.
- Updated `docs/handoffs/HANDOFF.md` with persistent collaboration memory: agent handles git stage/commit/push by default and logs each scoped commit here.
- Added new breakout wiring execution guide: `docs/guides/me7-breakout-output-tie-map-8e0-909-518-ak.html`.
- Linked the breakout tie map from `docs/guides/index.html` and `docs/guides/pinout-diagrams-8e0-909-518-ak-me7-5-0004.html`.
- Synced guide pages to latest locked breakout mapping:
  - `T121/101` MAP, `T121/68` O2, `T121/93` ECT, `T121/85` IAT, `T121/84` + `T121/91` TPS tracks, `T121/83` sensor ground.
  - Updated `docs/guides/me7-breakout-output-tie-map-8e0-909-518-ak.html` from hold/partial rows to locked tie-in matrix + validation targets.
  - Updated `docs/guides/pinout-diagrams-8e0-909-518-ak-me7-5-0004.html`, `docs/guides/pinout-golden-worksheet-8e0-909-518-ak.html`, and guide index copy to match.

## 2026-03-08
- Added dedicated crank/cam diagram execution plan: `docs/roadmap/crank-cam-diagram-execution-plan.md`.
- Created crank/cam working diagram copy: `docs/guides/Harness Diagram/Advanced_Harness/Project-Ironloop_Advanced-CrankCam-Layer.drawio`.
- Locked a step-by-step build flow: decision gates -> layout -> ECU tie-in -> validation checklist.
