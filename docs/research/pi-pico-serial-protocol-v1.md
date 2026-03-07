# Project IRONLOOP - Pi <-> Pico Serial Protocol v1
Last updated: 2026-03-07
Owner: `kitza`
Status: Draft for implementation (software-only validation phase)

## 1) Purpose
Define a stable command/response contract between:
- Raspberry Pi 5 bridge process (controller)
- Raspberry Pi Pico crank/cam generator firmware (device)

This supports no-hardware Phase 3 prep and gives a deterministic interface for later bench integration.

## 2) Transport
- Physical path: USB CDC serial (`/dev/ttyACM*` on Linux, `COMx` on Windows)
- UART config: `115200 8N1`
- Line format: ASCII text, one command per line, newline-terminated (`\n`)
- Max line length: 120 bytes
- Device should ignore empty lines and trim trailing `\r`

## 3) Protocol Versioning
- Protocol ID: `IRONLOOP-PICO-1`
- Pi handshake command must include protocol token.
- Pico must reject mismatched versions with explicit error.

## 4) Message Format
All command lines follow:
`<COMMAND> [key=value ...]`

All responses follow one of:
- `OK cmd=<COMMAND> ...`
- `ERR code=<CODE> msg=<TEXT>`
- `STATUS key=value ...`
- `EVENT key=value ...` (asynchronous; optional in v1)

Values are ASCII tokens with no spaces. Use `_` instead of spaces.

## 5) Command Set (v1)
### `HELLO`
Purpose: session start and version check.

Request:
`HELLO proto=IRONLOOP-PICO-1 client=pi5`

Success response:
`OK cmd=HELLO proto=IRONLOOP-PICO-1 fw=<version> state=<IDLE|RUNNING>`

Failure response:
`ERR code=PROTO_MISMATCH msg=expected_IRONLOOP-PICO-1`

### `SET_RPM`
Purpose: set crank target RPM.

Request:
`SET_RPM value=<rpm>`

Rules:
- Integer RPM in range `0..9000`
- `value=0` is valid and means no pulse output when running.

Success response:
`OK cmd=SET_RPM value=<accepted_rpm>`

Failure response examples:
- `ERR code=BAD_VALUE msg=rpm_out_of_range`
- `ERR code=BAD_FORMAT msg=missing_value`

### `START`
Purpose: enter signal-output state.

Request:
`START`

Success response:
`OK cmd=START state=RUNNING`

### `STOP`
Purpose: force output disabled and return to idle-safe state.

Request:
`STOP`

Success response:
`OK cmd=STOP state=IDLE`

### `STATUS`
Purpose: query current state.

Request:
`STATUS`

Success response:
`STATUS state=<IDLE|RUNNING> rpm=<current_rpm> sync=<0|1> proto=IRONLOOP-PICO-1`

### `PING`
Purpose: liveness and latency check.

Request:
`PING t=<unix_ms>`

Success response:
`OK cmd=PING t=<unix_ms>`

## 6) State Model
- Initial state after boot: `IDLE` (outputs off)
- `START` transitions `IDLE -> RUNNING`
- `STOP` transitions `RUNNING -> IDLE`
- `SET_RPM` allowed in both states, but output only active in `RUNNING`
- Any fatal internal fault must force `IDLE` and emit:
  - `EVENT type=FAULT code=<CODE> state=IDLE`

## 7) Safety Defaults
- On serial disconnect timeout (>1000 ms without valid command while RUNNING), Pico must:
  - transition to `IDLE`
  - disable crank/cam outputs
- On parse errors, Pico should emit `ERR ...` and continue session.
- Unknown commands must not change output state.

## 8) Timing Targets
- Command parse + response target: `<10 ms` at idle CPU load
- `SET_RPM` application target:
  - visible output-frequency update within `<50 ms`
- `STATUS` response target: `<20 ms`

These are software targets for Phase 3 prep; final limits will be verified with scope/logic analyzer on hardware.

## 9) Example Session
```text
Pi   -> HELLO proto=IRONLOOP-PICO-1 client=pi5
Pico <- OK cmd=HELLO proto=IRONLOOP-PICO-1 fw=0.1.0 state=IDLE

Pi   -> SET_RPM value=1200
Pico <- OK cmd=SET_RPM value=1200

Pi   -> START
Pico <- OK cmd=START state=RUNNING

Pi   -> STATUS
Pico <- STATUS state=RUNNING rpm=1200 sync=1 proto=IRONLOOP-PICO-1

Pi   -> STOP
Pico <- OK cmd=STOP state=IDLE
```

## 10) Acceptance Checklist (Week 2 Task 1)
- [x] Versioned handshake defined
- [x] RPM update command defined
- [x] Start/stop commands defined
- [x] Status query/response defined
- [x] Error envelope defined (`ERR code=... msg=...`)
- [ ] Implement parser in Pico firmware
- [ ] Implement host adapter in Pi bridge
- [ ] Add protocol replay tests from canned command vectors

## 11) In-Repo Artifacts
- Generator script: `Source/Phase-03-CrankCamSignal/generate_protocol_vectors.py`
- Sample vector set: `Source/Phase-03-CrankCamSignal/vectors/pi_pico_protocol_smoke_v1.json`

Generate/update vectors:
```powershell
cd Source\Phase-03-CrankCamSignal
python .\generate_protocol_vectors.py
```

## 12) Next Tasks
1. Define crank/cam timing vector output schema for software-only golden traces.
2. Add bridge-side serial adapter module that enforces v1 message formatting.
3. Add protocol replay tests that consume the generated vector JSON.
