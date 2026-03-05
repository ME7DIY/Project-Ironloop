# Chocolatey Setup Instructions

Use this script to automatically install all engine-sim dependencies on Windows.

## Quick Start

### Step 1: Open PowerShell as Administrator

1. Press `Win + X`
2. Select **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**
3. If prompted, click **"Yes"** to allow the app to make changes

### Step 2: Run the Setup Script

```powershell
cd "C:\Users\kitza\Documents\Project-Ironloop\Source\Phase-01-EngineSimPatch"
.\setup-chocolatey.ps1
```

The script will:
- ✅ Install Chocolatey (if not already installed)
- ✅ Install all dependencies (CMAKE, MSVC, Boost, SDL2, Flex, Bison)
- ✅ Set up environment variables automatically
- ✅ Verify everything is working

### Step 3: Wait for Installation to Complete

**This will take 30-60 minutes** since Boost is large. Go grab a coffee ☕

The script will show green `[OK]` messages as each tool installs.

---

## What Gets Installed?

| Package | Size | Time | Purpose |
|---------|------|------|---------|
| CMake | ~30MB | 2 min | Build system |
| Visual Studio Build Tools | ~1.5GB | 15-20 min | MSVC Compiler |
| Boost | ~500MB | 30-45 min | C++ Libraries |
| SDL2 | ~100MB | 5 min | Graphics Library |
| WinFlexBison | ~50MB | 2 min | Parser/Lexer Generator |

---

## After Installation

Once the script completes successfully, you can build engine-sim:

```powershell
cd "C:\Users\kitza\Documents\Project-Ironloop\Source\Phase-01-EngineSimPatch\engine-sim"

mkdir build
cd build

cmake .. -G "Visual Studio 17 2022"
cmake --build . --config Release
```

The build will take 20-40 minutes on first run.

---

## Troubleshooting

### "PowerShell execution policy" error
Run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then run the script again.

### "Access Denied" error
Make sure you're running PowerShell **as Administrator**.

### Script stuck on Visual Studio Build Tools
Visual Studio is huge (~1.5GB). Just let it run. Check Windows' Downloads folder to see progress.

### Boost installation failing
Boost is notoriously flaky on Windows. You might see errors but it usually still works. The script will verify at the end.

---

## Manual Installation Alternative

If Chocolatey fails, see `Source/Phase-01-EngineSimPatch/docs/BUILD.md` for manual installation steps.

---

**Ready? Open PowerShell as Admin and run the script!** 🚀
