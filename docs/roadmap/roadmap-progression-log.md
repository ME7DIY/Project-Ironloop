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
