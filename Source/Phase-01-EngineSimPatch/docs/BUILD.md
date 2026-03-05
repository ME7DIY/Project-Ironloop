# Engine-Sim Build Guide (Windows, Known-Good)

This guide matches the setup that successfully built this repo on March 5, 2026.

## Confirmed Working Stack

- Visual Studio Community 2026 (`Dev18`) with C++ toolchain
- CMake `3.28.x`
- `vcpkg` at `C:\vcpkg`
- NMake generator (not Visual Studio generator)

Note: CMake 3.28 does not expose a VS 2026 generator, so this project is built through `VsDevCmd.bat` + `NMake Makefiles`.

## One-Time Dependency Install

```powershell
git clone https://github.com/microsoft/vcpkg C:\vcpkg
C:\vcpkg\bootstrap-vcpkg.bat

C:\vcpkg\vcpkg install sdl2:x64-windows sdl2-image:x64-windows
C:\vcpkg\vcpkg install boost-filesystem:x64-windows-static-md
```

Install winflexbison (used by `piranha`):

```powershell
$toolsDir="C:\Users\kitza\Documents\Project-Ironloop\.tools\winflexbison"
New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
$zip="$env:TEMP\win_flex_bison-2.5.25.zip"
Invoke-WebRequest -Uri "https://github.com/lexxmark/winflexbison/releases/download/v2.5.25/win_flex_bison-2.5.25.zip" -OutFile $zip
Expand-Archive -LiteralPath $zip -DestinationPath $toolsDir -Force
```

## Source Compatibility Fixes Required

These fixes are needed for modern dependencies and are already applied in this working tree:

1. [`src/piston_engine_simulator.cpp`](C:\Users\kitza\Documents\Project-Ironloop\Source\Phase-01-EngineSimPatch\engine-sim\src\piston_engine_simulator.cpp): remove stale `m_antialiasingFilters` assert.
2. [`dependencies/submodules/piranha/src/path.cpp`](C:\Users\kitza\Documents\Project-Ironloop\Source\Phase-01-EngineSimPatch\engine-sim\dependencies\submodules\piranha\src\path.cpp): replace `is_complete()` with `is_absolute()`.

## Configure

From `Source\Phase-01-EngineSimPatch\engine-sim`:

```powershell
$cmd='"C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64 >nul && "C:\Program Files\CMake\bin\cmake.exe" -S . -B build-vs18-md -G "NMake Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake -DVCPKG_TARGET_TRIPLET=x64-windows-static-md -DSDL2_DIR=C:/vcpkg/installed/x64-windows -DBOOST_ROOT=C:/vcpkg/installed/x64-windows-static-md -DBoost_INCLUDE_DIR=C:/vcpkg/installed/x64-windows-static-md/include -DBoost_FILESYSTEM_LIBRARY_RELEASE=C:/vcpkg/installed/x64-windows-static-md/lib/boost_filesystem-vc145-mt-x64-1_90.lib -DBoost_FILESYSTEM_LIBRARY_DEBUG=C:/vcpkg/installed/x64-windows-static-md/debug/lib/boost_filesystem-vc145-mt-gd-x64-1_90.lib -DFLEX_EXECUTABLE=C:/Users/kitza/Documents/Project-Ironloop/.tools/winflexbison/win_flex.exe -DBISON_EXECUTABLE=C:/Users/kitza/Documents/Project-Ironloop/.tools/winflexbison/win_bison.exe'
cmd /c $cmd
```

## Build

```powershell
$cmd='"C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64 >nul && "C:\Program Files\CMake\bin\cmake.exe" --build build-vs18-md'
cmd /c $cmd
```

## Run

Set SDL runtime DLL path, then launch:

```powershell
$env:PATH="C:\vcpkg\installed\x64-windows\bin;$env:PATH"
.\build-vs18-md\engine-sim-app.exe
```

Optional UDP runtime config (for Phase 01 state stream):

```powershell
$env:ENGINE_SIM_UDP_ENABLED="1"
$env:ENGINE_SIM_UDP_HOST="127.0.0.1"
$env:ENGINE_SIM_UDP_PORT="5555"
```

If you still get missing DLL errors:

```powershell
Copy-Item C:\vcpkg\installed\x64-windows\bin\*.dll .\build-vs18-md\ -Force
.\build-vs18-md\engine-sim-app.exe
```

## Output Paths

- App: [`build-vs18-md/engine-sim-app.exe`](C:\Users\kitza\Documents\Project-Ironloop\Source\Phase-01-EngineSimPatch\engine-sim\build-vs18-md\engine-sim-app.exe)
- Tests: `build-vs18-md/engine-sim-test.exe`

## Phase 01 Receiver / Bridge Scripts

From `Source\Phase-01-EngineSimPatch`:

```powershell
python .\python-bridge\socket_receiver.py
python .\python-bridge\signal_generator.py --sink stub
python .\python-bridge\signal_generator.py --sink csv --csv-path .\logs\signal_targets.csv
python .\python-bridge\udp_test_sender.py --duration 10 --hz 60
```

Receiver schema options:

- `--expected-schema-version 1`
- `--no-schema-check` (debug only)

`signal_generator.py` options:

- `--sink stub|console|csv|pi`
- `--config .\python-bridge\bridge_config.json`
- `--print-input` (debug)

Temperature mapping notes:

- `combustion_temp_c` is remapped into ECU-like ECT range via `ect_remap` in `bridge_config.json`.
- `intake_temp_c` is remapped via `iat_remap` to avoid sitting on clamp limits.
- Hard clamps for ECT/IAT are controlled by `sensor_temp_limits`.
- If resistance pins near NTC min (e.g., `100ohm`), lower `ect_remap.out_max_c` or tighten `sensor_temp_limits.ect_c_max`.

Narrowband O2 model notes:

- `o2_narrowband.model` supports `step` or `sigmoid`.
- Recommended default is `sigmoid` for smoother transitions around stoich:
  - `switch_lambda` (usually `1.0`)
  - `sigmoid_gain` (higher = sharper switching)

Pi hardware sink (safe pre-hardware mode):

```powershell
python .\python-bridge\signal_generator.py --sink pi
```

If Pi dependencies/devices are missing, it automatically falls back to mock mode
when `hardware.mock_on_missing=true` in `bridge_config.json`.

## Smoke Test Flow (No Hardware Needed)

Use two terminals from `Source\Phase-01-EngineSimPatch`:

1. Consumer (`signal_generator`):
```powershell
python .\python-bridge\signal_generator.py --sink stub
```
2. Producer (`udp_test_sender`):
```powershell
python .\python-bridge\udp_test_sender.py --duration 15 --hz 60
```

Expected result:
- `signal_generator.py` continuously prints target outputs (`dac[tps]`, `dac[map]`, `dac[o2]`, `r_ect`, `r_iat`, `rpm`).

Observer mode (alternative to signal generator):

1. `python .\python-bridge\socket_receiver.py`
2. `python .\python-bridge\udp_test_sender.py --duration 15 --hz 60`

Note: `socket_receiver.py` and `signal_generator.py` both bind UDP `127.0.0.1:5555`, so run one or the other unless you add a relay/fan-out process.

## Common Failures

### `Could NOT find SDL2`

Use `sdl2:x64-windows` and set `-DSDL2_DIR=C:/vcpkg/installed/x64-windows`.

### Boost runtime mismatch (`MT` vs `MD`)

Use `boost-filesystem:x64-windows-static-md` and point CMake at `x64-windows-static-md` libs.

### FLEX/BISON not found

Point CMake explicitly:

- `-DFLEX_EXECUTABLE=.../win_flex.exe`
- `-DBISON_EXECUTABLE=.../win_bison.exe`

### VS generator not found

Do not use `-G "Visual Studio 17 2022"` on this stack. Use `-G "NMake Makefiles"` through `VsDevCmd.bat`.

---

Last Updated: March 5, 2026  
Status: Verified working on this machine
