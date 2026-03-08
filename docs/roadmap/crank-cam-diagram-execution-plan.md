# Project IRONLOOP - Crank/Cam Diagram Execution Plan
Last updated: 2026-03-08
Owner: `kitza`
Scope: Build the crank/cam simulation layer into the advanced harness diagram without breaking the locked analog-sensor layer.

## Working File
- `docs/guides/Harness Diagram/Advanced_Harness/Project-Ironloop_Advanced-CrankCam-Layer.drawio`

## Objective
- Add a complete, reviewable crank/cam signal path to the harness diagram.
- Keep decisions explicit so hardware purchases and bench wiring follow the same plan.

## Decision Gates (Must Lock Before Final Wiring)
- [ ] Stim source choice locked:
  - `Option A`: Raspberry Pi Pico (PIO firmware path)
  - `Option B`: Ardu-Stim/JimStim style external stim board
- [ ] ECU crank input electrical expectation confirmed for this ECU context (`VR` vs `Hall/TTL-level` path handling).
- [ ] ECU cam input electrical expectation confirmed for this ECU context.
- [ ] Conditioning/translation path locked (if required) for crank and cam outputs.

## Diagram Build Phases
### Phase 1 - Block Layout (No final pin ties yet)
- [ ] Add new block: `CRANK/CAM STIM`.
- [ ] Add output labels from stim block:
  - `CRANK_OUT+`
  - `CRANK_OUT-` (or `CRANK_REF` if single-ended path is chosen)
  - `CAM_OUT`
  - `CAM_GND/REF`
- [ ] Add power and ground feeds for stim block from existing rails.
- [ ] Add note box: `Final electrical mode pending (VR/Hall lock)`.

### Phase 2 - ECU Tie-In Paths
- [ ] Add placeholder net labels for ECU crank/cam destinations.
- [ ] Draw final routed lines from stim outputs to ECU destination pins.
- [ ] Add any required inline components as separate symbols:
  - `series resistor`
  - `pull-up`
  - `conditioner/translator module`
- [ ] Mark each tied path as `LOCKED` or `PROVISIONAL`.

### Phase 3 - Validation Layer
- [ ] Add mini checklist on diagram:
  - `Power rails continuity`
  - `Ground reference shared`
  - `Signal amplitude mode set`
  - `Expected frequency/rpm mapping documented`
- [ ] Add expected waveform labels:
  - `Crank: 60-2`
  - `Cam: sync pulse phase relationship`

## Bench Bring-Up Sequence (When Hardware Is Present)
1. Power only, no signal output enabled.
2. Enable crank only, verify ECU RPM detection.
3. Add cam sync, verify sync state stability.
4. Sweep RPM low to high and log stability/fault behavior.
5. Record first pass/fail evidence and update diagram labels from provisional to locked.

## Session Log
## 2026-03-08
- Created crank/cam working diagram copy:
  - `docs/guides/Harness Diagram/Advanced_Harness/Project-Ironloop_Advanced-CrankCam-Layer.drawio`
- Initialized this execution plan to track decisions and wiring build order.
