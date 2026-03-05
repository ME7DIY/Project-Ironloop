# Phase 01 Progress Log - Engine State Socket Output

Date started: March 5, 2026  
Owner: Project IRONLOOP

## Goal

Patch `engine-sim` to broadcast live engine state over UDP so the Python bridge can consume it and drive Phase 02 signal generation.

## Current Status

- Build environment: working on this machine (`build-vs18-md`).
- UDP broadcaster: implemented and emitting packets on `127.0.0.1:5555`.
- Validation: live packet stream confirmed in terminal receiver.

## Milestone Checklist

- [x] Build forked `engine-sim` on local Windows toolchain
- [x] Add UDP socket broadcaster module
- [x] Hook broadcast into per-frame simulation loop
- [x] Emit JSON payload (`timestamp_ms`, `frame`, `rpm`, `throttle`, `manifold_pressure`)
- [x] Validate receiver sees live stream
- [x] Expand payload fields (`intake_afr`, `exhaust_o2`, temps, etc.)
- [x] Add reusable Python receiver script in `python-bridge/`
- [x] Document wire/schema contract for bridge consumers
- [x] Add graceful runtime config (host/port enable flag)

## Session Notes

### 2026-03-05 - MVP Socket Stream Working

- Implemented `StateBroadcaster` in engine-sim app layer.
- Added Windows UDP send path and app lifecycle init/shutdown.
- Confirmed packets continuously received while engine-sim runs.
- Observed payload values in receiver output:
  - `timestamp_ms`
  - `frame`
  - `engine.rpm`
  - `engine.throttle`
  - `engine.manifold_pressure`

### 2026-03-05 - Payload Expansion + Bridge Utilities

- Added `engine.intake_afr` and `engine.exhaust_o2` to UDP JSON payload.
- Added reusable receiver script:
  - `Source/Phase-01-EngineSimPatch/python-bridge/socket_receiver.py`
- Added schema doc:
  - `Source/Phase-01-EngineSimPatch/docs/PHASE-01-UDP-SCHEMA.md`
- Rebuilt `engine-sim-app` successfully after changes.

### 2026-03-05 - Runtime Config + Signal Scaffold

- Added env-driven runtime config in engine-sim app:
  - `ENGINE_SIM_UDP_ENABLED`
  - `ENGINE_SIM_UDP_HOST`
  - `ENGINE_SIM_UDP_PORT`
- Enhanced receiver with packet/drop/out-of-order stats.
- Added `python-bridge/signal_generator.py` scaffold to convert state into preliminary ME7 sensor target values.
- Added pluggable output sinks (`console` + `stub`) for Phase 02 hardware wiring prep.

### 2026-03-05 - Bridge Hardening (Pre-Hardware)

- Added bridge config file:
  - `python-bridge/bridge_config.json`
- Added configurable sink modes in signal generator:
  - `stub`, `console`, `csv`
- Added CSV telemetry target logging for tuning/analysis:
  - default `logs/signal_targets.csv`
- Added optional low-pass smoothing in signal conversion path.

### 2026-03-05 - Pi Backend Skeleton (Hardware-Ready Structure)

- Added `python-bridge/pi_hardware.py` backend skeleton for:
  - MCP4728 DAC path (TPS/MAP/O2 channels)
  - MCP4131 digital pot command path
- Added new sink mode:
  - `signal_generator.py --sink pi`
- Added safe fallback behavior:
  - if Pi dependencies/hardware are missing, backend auto-falls to mock mode (config-driven).

### 2026-03-05 - Schema + Temperature Expansion

- Added `schema_version` to UDP payload.
- Added payload temperature fields:
  - `engine.combustion_temp_c`
  - `engine.intake_temp_c`
- Added schema validation in:
  - `python-bridge/socket_receiver.py`
  - `python-bridge/signal_generator.py`
- Added NTC conversion in bridge:
  - ECT/IAT temperature -> resistance targets (ohms)
- Updated docs and examples for schema checks.

### 2026-03-05 - Verified Build + Synthetic Stream Tool

- Rebuilt `engine-sim-app` successfully after schema/temperature changes.
- Confirmed executable output path remains:
  - `Source/Phase-01-EngineSimPatch/engine-sim/build-vs18-md/engine-sim-app.exe`
- Added repeatable smoke-test packet generator:
  - `Source/Phase-01-EngineSimPatch/python-bridge/udp_test_sender.py`
- Updated build docs with a no-hardware smoke-test flow.

### 2026-03-05 - Temperature Saturation Fix (Bridge)

- Identified ECT/IAT resistance pinning at `100ohm` during live runs.
- Added config-driven sensor temperature shaping in bridge:
  - `sensor_temp_limits`
  - `ect_remap`
  - `iat_remap`
- Updated conversion path so raw sim temps are remapped/clamped before NTC resistance conversion.
- Goal: keep Phase 1 sensor targets in ECU-plausible ranges before hardware loop-in.

### 2026-03-05 - Sensor Model Calibration Pass

- Enabled `iat_remap` by default with ECU-safe output range to reduce IAT clamp saturation.
- Upgraded narrowband O2 model to support:
  - `step` mode (legacy behavior)
  - `sigmoid` mode (recommended default)
- Added config controls:
  - `o2_narrowband.model`
  - `o2_narrowband.switch_lambda`
  - `o2_narrowband.sigmoid_gain`
- Updated build docs with tuning notes for temperature/O2 model behavior.

### 2026-03-05 - Final Phase 1 Software Validation

- Ran final CSV baseline (`logs/phase1-final.csv`) after calibration updates.
- Verified output ranges:
  - `o2_narrowband_v`: `0.173` to `0.850`
  - `iat_temp_c`: `20.0` to `56.5`
  - `iat_resistance_ohm`: `705.3` to `3133.8`
- Result: software-side Phase 1 bridge pipeline is behaving as expected (no temperature clamp saturation, O2 output no longer pinned).

## Known Issues / Follow-ups

- On Windows, running from wrong working directory can cause app to close early due to relative asset paths.
- Smart App Control can block unsigned local builds; local allow/disable may be required during dev.
- Exe may fail to relink if currently running (`LNK1104` file lock); close app before rebuild.

## Next Actions

1. Freeze Phase 1 software defaults and tag this checkpoint.
2. Validate Pi sink against real MCP4728/MCP4131 hardware on arrival.
3. Split ECT and IAT onto separate digital-pot/output paths (currently ECT-biased placeholder for MCP4131).
4. Tune/calibrate NTC and MAP/TPS transfer curves against real ME7 behavior.
