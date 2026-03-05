# Source — Implementation & Code

This directory contains all implementation code, firmware, and working projects for each phase of IRONLOOP.

## Directory Structure

```
Source/
├── Phase-01-EngineSimPatch/
│   ├── engine-sim/           # Fork of ange-yaghi/engine-sim with socket broadcast patch
│   ├── python-bridge/        # Python socket receiver & state processor
│   └── docs/                 # Phase 1 specific documentation
│
├── Phase-02-FakeSensors/
│   ├── dac-firmware/         # Pi code for MCP4728 DAC control
│   ├── pot-firmware/         # Pi code for MCP4131 digital pot
│   └── docs/
│
├── Phase-03-CrankCamSignal/
│   ├── pico-firmware/        # PIO assembly & MicroPython for Pico
│   ├── signal-verification/  # Logic analyzer test harness
│   └── docs/
│
├── Phase-04-CloseLoop/
│   ├── feedback-controller/  # Python loop closure logic
│   ├── kline-reader/         # K-Line ECU diagnostics
│   └── docs/
│
└── Phase-05-AITuning/
    ├── rl-environment/       # OpenAI Gym environment
    ├── training-scripts/     # PPO trainer, map optimizer
    └── docs/
```

## Phase 01: Engine Sim Patch

### Overview
Fork the official ange-yaghi/engine-sim C++ project and add a local UDP/TCP socket that broadcasts the engine state as JSON every frame.

### Tasks
- [ ] Fork and clone ange-yaghi/engine-sim
- [ ] Set up CMake build environment (MSVC or GCC)
- [ ] Identify key state variables (RPM, throttle, MAP, MAF, ECT, lambda)
- [ ] Add socket broadcasting to main simulation loop
- [ ] Write Python test receiver to validate JSON output
- [ ] Document JSON schema and API

### Files
- `engine-sim/` — Your working fork (will be very large, ~2GB with build artifacts)
- `python-bridge/` — Python socket receiver, state parser, signal generators
- `docs/` — Progress notes, build instructions, API schema

### Next Steps
1. **Fork on GitHub:** https://github.com/ange-yaghi/engine-sim → fork to ME7DIY account
2. **Clone to Local:** Clone into `Source/Phase-01-EngineSimPatch/engine-sim/`
3. **Add to .gitignore:** Engine-sim build artifacts are large; they should NOT be committed
4. **Create build script** to compile on your system
5. **Start patching** to add socket broadcast

---

## Working with Large Projects

When working with engine-sim and other large repositories:

**DO:**
- Commit your modifications and documentation
- Add `.gitignore` entries for build outputs
- Use feature branches for experiments
- Document build steps in README

**DON'T:**
- Commit compiled binaries (.exe, .so, .o files)
- Commit build directories (cmake_install.cmake, CMakeFiles/)
- Commit compiler outputs (obj/, bin/, dist/)

---

## Branch Naming Convention

When working on Phase 1 tasks, create feature branches:

```
feature/phase-01/socket-broadcast
bugfix/phase-01/cmake-windows-build
docs/phase-01/json-schema
```

Then create Pull Requests back to `main` when code is ready.

---

## Documentation Standards

Each phase should have:
- **README.md** — Phase overview, current status, next steps
- **BUILD.md** — Step-by-step compilation instructions
- **API.md** — Interface documentation (for socket protocol, for example)
- **PROGRESS.md** — Completed tasks, blockers, lessons learned

---

**Last Updated:** March 5, 2026
