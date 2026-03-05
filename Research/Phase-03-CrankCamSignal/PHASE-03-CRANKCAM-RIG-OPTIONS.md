# Phase 03 Research: Crank/Cam Rig Options (Community Input)

Date: March 5, 2026  
Status: Draft research note based on community discussion

## Why This Might Be Important

This could significantly reduce bring-up time for Phase 03 by using proven bench hardware patterns instead of building every piece from scratch.

## Inputs Captured

Community suggestions included:

- ArduStim (Mega2560-based) for crank/cam generation.
- 16-channel Saleae logic analyzer for full timing readout and validation.
- ECU-footprint stim baseboard matching the target connector layout.
- Modular add-ons: digital pot mounts, power distribution, CAN hub, Raspberry Pi node for `candump` and support tasks.

## Potential Impact on IRONLOOP

1. Faster path to stable crank/cam signal generation.
2. Cleaner signal observability during ME7 timing validation.
3. Better bench ergonomics and repeatability with a baseboard-centered architecture.
4. Easier migration path for additional ECUs if connector strategy is generalized.

## AC / VR Sensor Simulation Consideration

Open question raised: realistic AC VR simulation for conditioner testing.

Options to research:

- Dedicated VR waveform driver circuitry (variable amplitude/frequency, differential outputs).
- Physical wheel + pickup test rig (motorized trigger wheel) for highest realism.
- Lab function generator path for controlled waveform sweeps.

For IRONLOOP: this should be treated as a separate validation track for signal-conditioner testing, not a blocker for initial square-wave crank/cam bring-up.

## Recommended Plan

### Step 1: Keep Current Baseline

Continue Pico/Pi path as baseline implementation to maintain project momentum.

### Step 2: Parallel Prototype Track

Prototype a secondary crank/cam stack using ArduStim + Mega2560 and compare against Pico implementation.

### Step 3: Instrumentation-First Validation

Use 16-channel logic capture to compare:

- tooth timing jitter
- missing-tooth accuracy
- cam sync phase consistency
- startup/recovery behavior

### Step 4: Architecture Decision

Choose one of:

- Pico-only
- ArduStim-only
- Hybrid mode (ArduStim for quick testing, Pico for final deterministic timing)

Decision should be based on measured timing quality, integration effort, and maintainability.

## Immediate Action Items

1. Add this option set to Phase 03 execution planning.
2. Create a measurement checklist for logic analyzer captures.
3. Define objective pass/fail thresholds for crank/cam waveform quality.
4. Identify whether VR simulation is required in Phase 03 or deferred to Phase 03.5 validation.

