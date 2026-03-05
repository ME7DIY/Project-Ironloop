# Phase 01 Research: Engine State Socket Output

## Why This Exists

Phase 01 is the gateway for the entire IRONLOOP loop. If engine-sim cannot publish state in real time, the Pi bridge has no live input and Phase 02+ cannot proceed.

## What We Learned So Far

### Build/Toolchain Lessons

- The fork builds successfully on this machine with a VS 2026 toolchain + NMake workflow.
- CMake 3.28 does not expose a VS 2026 generator directly, so we use `VsDevCmd.bat` and `NMake Makefiles`.
- Reliable build output folder: `Source/Phase-01-EngineSimPatch/engine-sim/build-vs18-md`.
- Runtime dependencies include SDL2/SDL2_image and legacy D3DX runtime components.

### Source Compatibility Fixes Applied During Bring-Up

- Removed stale assert for a removed member in `src/piston_engine_simulator.cpp`.
- Updated legacy Boost filesystem API in `dependencies/submodules/piranha/src/path.cpp` (`is_complete()` -> `is_absolute()`).
- Removed forced debug D3DX link libs in `dependencies/submodules/delta-studio/CMakeLists.txt` to avoid debug DLL runtime requirement.

These were prerequisite stability fixes before Phase 01 feature work.

## Why We Need Socket Output

We need a machine-readable stream from engine-sim to external processes.

Primary consumers:

1. Python bridge (Pi side) for sensor emulation outputs.
2. Logging pipeline for validation/tuning.
3. Future loop-closure logic (ECU output -> sim feedback).

Without this stream, the ECU bench has no dynamic virtual engine context.

## What Data We Need to Emit

Minimum viable payload (per frame):

- `timestamp_ms`
- `frame_number`
- `engine.rpm`
- `engine.throttle_position`
- `engine.manifold_pressure`
- `engine.coolant_temp`
- `engine.intake_air_temp`
- `engine.lambda`

Good follow-on fields:

- `fuel.injector_pw_ms`
- `fuel.fuel_flow_cc_s`
- `ignition.advance_deg_btdc`
- `timing.cam_angle`
- `timing.crank_angle`

## Transport Decision

Recommended start:

- UDP
- `127.0.0.1:5555`
- JSON payload
- Fire-and-forget each simulation frame

Why UDP first:

- Lowest integration overhead for frame telemetry
- No connection management complexity
- Packet loss is acceptable for high-rate real-time state

## Integration Strategy in Engine-Sim

### Hook Point

Use the per-frame simulation path inside `EngineSimApplication::process(...)` after simulation state is advanced (after `simulateStep()` loop / frame end), so exported data is coherent for that frame.

### Implementation Approach

1. Add a small broadcaster module in `engine-sim` source:
   - `include/state_broadcaster.h`
   - `src/state_broadcaster.cpp`
2. Use Winsock2 (project is Windows-oriented).
3. Add a lightweight JSON serialization path:
   - MVP can use manual JSON formatting to avoid dependency churn.
   - Optional follow-up: nlohmann/json if we want stronger schema handling.
4. Gate broadcasting behind a runtime flag/config default ON for localhost.
5. Keep send path non-blocking and fail-soft (never stall sim loop).

## Validation Plan

### Functional Validation

- Run engine-sim, verify UDP packets arrive in a Python receiver.
- Validate schema keys and numeric ranges.
- Confirm stream cadence roughly matches frame rate.

### Performance/Robustness Validation

- Ensure sim FPS does not materially degrade with broadcaster enabled.
- Verify socket failures do not crash or block simulation.

## Suggested Work Breakdown (Immediate Next Steps)

1. Locate exact getter path for each required state variable in current code.
2. Implement broadcaster class + init/shutdown lifecycle.
3. Inject one payload send per simulation frame.
4. Create `python-bridge/socket_receiver.py` MVP to print/validate packets.
5. Document schema and known caveats in Phase 01 docs.

## File Format Decision

For research docs, use `.md` as primary:

- Diffable in git
- Easy review and iteration
- Can export to `.doc`/PDF later for presentation polish

If needed, we can generate a polished `.docx` version once this content stabilizes.

---

Author: IRONLOOP Phase 01 research log  
Date: March 5, 2026
