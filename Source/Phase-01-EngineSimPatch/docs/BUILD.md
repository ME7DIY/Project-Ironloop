# Engine-Sim Build Guide

## Status: Dependencies Not Yet Installed

This document walks through building engine-sim on Windows with all necessary dependencies.

---

## System Requirements

- **OS:** Windows 10 or 11
- **Compiler:** Visual Studio 2019+ or MinGW (MSVC recommended)
- **RAM:** 8GB+ recommended
- **Disk:** ~10GB for source + build artifacts

---

## Step 1: Install CMake

CMake is the build system used by engine-sim.

1. Download CMake from: https://cmake.org/download/
2. Choose the latest stable version (e.g., cmake-3.28.x-windows-x86_64.msi)
3. Run the installer
4. **Important:** During installation, check "Add CMake to the system PATH"
5. Verify installation:
   ```powershell
   cmake --version
   ```
   Should output: `cmake version X.XX.X`

---

## Step 2: Install Visual Studio Build Tools (or Full VS)

You need a C++ compiler. Choose one:

### Option A: Visual Studio Community (Free, ~4GB)
1. Download from: https://visualstudio.microsoft.com/downloads/
2. Select "Community" edition
3. During installation, check **"Desktop development with C++"**
4. This includes MSVC compiler, CMake tools, and NuGet
5. Installation takes 20-30 minutes

### Option B: Visual Studio Build Tools Only (~1GB)
1. Go to: https://visualstudio.microsoft.com/downloads/
2. Scroll down to "All Downloads"
3. Find "Tools for Visual Studio"
4. Download "Build Tools for Visual Studio 202X"
5. Check **"Desktop development with C++"**

---

## Step 3: Install Boost Library

Boost is a large C++ library. Building from source takes time (~30-60 minutes).

### Option A: Pre-built Boost (Easiest)
1. Download pre-built binaries from: https://sourceforge.net/projects/boost/files/boost-binaries/
2. Look for the latest version: `boost_1_XX_0-msvc...exe`
3. Run installer, choose installation path (e.g., `C:\boost`)
4. Note the install path - you'll need it for CMake

### Option B: Build Boost from Source
1. Download from: https://www.boost.org/users/download/
2. Extract to `C:\boost_source`
3. Open Command Prompt or PowerShell as Administrator:
   ```powershell
   cd C:\boost_source
   .\bootstrap.bat
   .\b2 --with-system --with-filesystem --with-thread thread-model=multi
   ```
4. Wait 30-60 minutes (Boost is large!)

---

## Step 4: Install SDL2

SDL2 is the graphics/window library used by engine-sim.

### Option A: Pre-built Development Library (Recommended)
1. Download from: https://github.com/libsdl-org/SDL/releases
2. Look for `SDL2-devel-X.X.X-VC.zip` (VC = Visual C++)
3. Extract to a permanent location (e.g., `C:\SDL2`)
4. Note the path for CMake configuration

### Optional: SDL2_image
1. Download from: https://github.com/libsdl-org/SDL_image/releases
2. Look for `SDL2_image-devel-X.X.X-VC.zip`
3. Extract to `C:\SDL2_image` (or same location as SDL2)

---

## Step 5: Install Flex and Bison

These are lexer/parser generators used by engine-sim's scripting system.

### Option A: WinFlexBison (One-Click Solution)
1. Download from: https://github.com/lexxmark/winflexbison/releases
2. Download `win_flex_bison-X.X.X.zip`
3. Extract to `C:\FlexBison` (or similar)
4. Add to PATH (see "Add to PATH" section below)

### Option B: Cygwin or MinGW (More Complex)
- Cygwin: https://cygwin.com/ (includes flex and bison)
- Download installer, search for "flex" and "bison" in setup

---

## Add Dependencies to PATH

For CMake to find these libraries, they need to be in your system PATH.

### Method 1: Environment Variables GUI
1. Press `Win + X` → "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Create these:

| Variable Name | Value |
|---------------|-------|
| `BOOST_ROOT` | `C:\boost` (or your boost path) |
| `SDL2_PATH` | `C:\SDL2` (or your SDL2 path) |
| `SDL2_IMAGE_PATH` | `C:\SDL2_image` (optional) |

6. Also add to "Path" variable:
   - `C:\FlexBison` (or wherever you extracted WinFlexBison)
   - `C:\cmake\bin` (usually auto-added by CMake installer)

### Method 2: Command Line
```powershell
$env:BOOST_ROOT = "C:\boost"
$env:SDL2_PATH = "C:\SDL2"
$env:Path = "$env:Path;C:\FlexBison"
```

---

## Build Engine-Sim

Once all dependencies are installed and added to PATH:

```powershell
cd C:\Users\kitza\Documents\Project-Ironloop\Source\Phase-01-EngineSimPatch\engine-sim

# Create build directory
mkdir build
cd build

# Run CMake
cmake .. -G "Visual Studio 17 2022"

# Build (Release mode is faster)
cmake --build . --config Release
```

This generates a Visual Studio solution in the `build` folder. You can also open it with VS GUI:
```powershell
start .\engine-sim.sln
```

---

## Expected Build Time

| Step | Time |
|------|------|
| Boost (if building) | 30-60 min |
| CMake configuration | 2-5 min |
| First build | 20-40 min |
| Incremental builds | 1-5 min |

**Total first build:** ~1-2 hours (mostly waiting)

---

## Troubleshooting

### CMake can't find Boost
```
-- Could NOT find Boost
```

Solution:
```powershell
$env:BOOST_ROOT = "C:\your\boost\path"
cd build
rm -r CMakeFiles CMakeCache.txt
cmake .. -G "Visual Studio 17 2022"
```

### CMake can't find SDL2
```
Could not find SDL2
```

Solution: Same as above, set `SDL2_PATH` environment variable.

### "flex" or "bison" not found
Add `C:\FlexBison` to your PATH and restart PowerShell.

### "MSVC not found"
You need to install Visual Studio Build Tools. CMake can't find the compiler if it's not installed.

---

## After Successful Build

Once the build completes:

1. **Executable location:** `engine-sim\build\bin\engine-sim-app.exe`
2. **Run with:** `.\build\bin\engine-sim-app.exe` from engine-sim directory
3. This should launch the engine simulator GUI

If DLL errors occur, copy required DLLs from dependency folders to the `bin/` directory.

---

## Next: Adding Socket Broadcast

Once engine-sim builds and runs successfully:

1. Identify the main simulation loop in `src/`
2. Add JSON serialization library (nlohmann/json)
3. Add socket broadcast code
4. Emit engine state every frame

See `Source/Phase-01-EngineSimPatch/README.md` for implementation steps.

---

## Resources

- CMake: https://cmake.org/cmake/help/latest/
- Boost: https://www.boost.org/doc/
- SDL2: https://wiki.libsdl.org/SDL2/
- WinFlexBison: https://github.com/lexxmark/winflexbison
- engine-sim source: https://github.com/ange-yaghi/engine-sim

**Note:** This is experimental and setup is complex. Don't hesitate to reach out if you hit issues!

---

**Last Updated:** March 5, 2026  
**Status:** Build environment setup guide created, actual build pending dependency installation
