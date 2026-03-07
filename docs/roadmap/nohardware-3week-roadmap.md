# Project IRONLOOP - No-Hardware 3-Week Roadmap
Last updated: 2026-03-06
Owner: `kitza`
Scope: Keep project momentum while bench hardware is unavailable.

## Why This Exists
Phase 01 is at `5/6` checkpoints complete. The remaining item requires real hardware validation.
This plan defines what can be completed now so hardware arrival does not block execution.

## Constraints
- No physical MCP4728/MCP4131/Pico/ME7 harness validation for ~3 weeks.
- Work must remain non-destructive to existing local repo state and submodule dirt.

## Outcomes By End of 3 Weeks
- Phase 2 software path hardened and testable with repeatable logs.
- Pre-hardware Phase 3 signal tooling prepared (protocol and waveform validation).
- Phase 4 interface contracts and mock closed-loop path in place.
- Hardware-day runbook and fault triage pack ready.

## Week 1 - Phase 2 Hardening (No Hardware)
### Goals
- Lock minimum signal profile for bench bring-up:
  - TPS
  - MAP
  - IAT
  - ECT
  - Narrowband O2
  - Voltage-aware correction path
- Add stability controls:
  - per-channel clamps
  - slew/rate limits
  - fallback defaults
- Add reliable logging mode:
  - `stub+csv` dual sink

### Deliverables
- [x] `phase2_minimum` bridge profile committed (`python-bridge/bridge_config.json` + `--profile phase2_minimum` support)
- [x] Output range/rate validator script committed (`python-bridge/validate_signal_outputs.py`)
- [x] Dual sink logging mode committed
- [x] One sample validation log set under `Research/Phase-02-FakeSensors/`

### Exit Criteria
- Bridge runs at target processing rate with no unstable spikes on minimum channels.
- Validator reports pass against defined bounds for replay test inputs.

## Week 2 - Phase 3 Software-Only Prep
### Goals
- Define and implement Pi->Pico serial command contract.
- Implement software-side waveform generation checks for:
  - crank `60-2`
  - cam sync pulse placement
- Produce expected trace references for later logic-analyzer comparison.

### Deliverables
- [x] Protocol spec doc (`rpm update`, `start/stop`, `status`) - `docs/research/pi-pico-serial-protocol-v1.md`
- [x] Command-vector test generator (RPM/state transitions) - `Source/Phase-03-CrankCamSignal/generate_protocol_vectors.py`
- [ ] Test generator for target tooth timing sequences
- [ ] Golden-vector outputs saved for bench comparison

### Exit Criteria
- Given an RPM command sequence, tooling outputs deterministic crank/cam timing vectors.
- Protocol commands are versioned and documented for firmware integration.

## Week 3 - Phase 4 Interface + Hardware-Day Pack
### Goals
- Lock data contracts for ECU output ingestion:
  - injector pulse width
  - ignition advance
  - key status flags
- Build mock adapters so feedback loop can be developed before bench hookup.
- Prepare first-day hardware execution checklist and DTC triage matrix.

### Deliverables
- [ ] Interface contract doc for ECU->bridge path
- [ ] Mock ECU output replay adapter
- [ ] Hardware-day checklist (ordered steps, pass/fail gates)
- [ ] DTC triage matrix (`symptom -> likely path -> measurement to confirm`)

### Exit Criteria
- Mock closed-loop path runs end-to-end with logged input/output traces.
- Hardware-day runbook is complete enough to execute without ad-hoc decisions.

## Tracking Cadence
- Daily: update checklist boxes for tasks touched.
- Every 3 days: add one short status note (`what moved`, `what blocked`, `next`).
- End of each week: mark week exit criteria pass/fail.

## Risks During No-Hardware Window
- Overfitting to synthetic inputs only.
- Hidden electrical behavior not visible in software-only tests.
- Late pinout/connector details if ECU part number is not finalized.

## Mitigations
- Use realistic replay traces and not just idealized ramps.
- Keep strict logs of raw input, mapped output, and applied clamps/fallbacks.
- Finalize ECU-specific pin worksheet before hardware arrival.

## Immediate Next Action
- [ ] Start Week 2 task 3: define crank/cam timing vector schema and generate first golden traces.
