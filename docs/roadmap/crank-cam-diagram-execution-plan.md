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
- [x] Stim source choice locked:
  - `Primary`: Raspberry Pi Pico (PIO firmware path)
  - `Secondary`: Ardu-Stim style external stim board (comparison/bring-up track)
- [ ] ECU crank input electrical expectation confirmed for this ECU context (`VR` vs `Hall/TTL-level` path handling).
- [ ] ECU cam input electrical expectation confirmed for this ECU context.
- [ ] Conditioning/translation path locked (if required) for crank and cam outputs.

## Board Lock Sheet (Fill Before Final Wiring)
| Function | Candidate Board | Required Layout/Schematic | Status |
|---|---|---|---|
| Crank/Cam signal generator (primary path) | Raspberry Pi Pico (or Pico 2) | Pico pin header map and chosen output pins | LOCKED (primary) |
| Crank/Cam signal generator (comparison path) | Ardu-Stim (Nano-based in current guide) | Ardu-Stim header/pinout for crank and cam outputs | LOCKED (secondary) |
| Signal conditioning/translation (if needed) | VR/Hall conditioning module (TBD) | Module input/output header map and wiring mode | PROVISIONAL (await ECU input-mode lock) |
| Timing verification instrument | 8+ channel logic analyzer (16ch preferred) | Channel map for crank, cam, and reference ground | LOCKED |

## Architecture Lock (Current)
1. Use `Pico` as the final intended crank/cam generator path.
2. Use `Ardu-Stim` as a fast bring-up and A/B comparison path.
3. Treat `VR/conditioning` as a dedicated follow-up decision after ECU crank/cam electrical mode is confirmed.
4. Require logic-analyzer capture before promoting any crank/cam tie from provisional to locked.

## Minimum Artifacts To Collect First
1. Board front/back photos with header labels visible.
2. Pinout sheet or manufacturer schematic PDF for each board.
3. One locked "which exact header pin carries which signal" mapping per board.
4. Voltage level notes for each output (`3.3V`, `5V`, differential VR-style, etc.).

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
- Locked baseline board selection:
  - Primary generator: `Raspberry Pi Pico`
  - Secondary generator: `Ardu-Stim`
  - Measurement requirement: `logic analyzer (16ch preferred)`
