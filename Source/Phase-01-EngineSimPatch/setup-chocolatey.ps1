# Chocolatey Setup Script for engine-sim Dependencies
# Run this as Administrator in PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ENGINE-SIM CHOCOLATEY SETUP SCRIPT  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "[ERROR] This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Running as Administrator" -ForegroundColor Green
Write-Host ""

# Step 1: Check if Chocolatey is installed
Write-Host "Step 1: Checking for Chocolatey..." -ForegroundColor Cyan
choco --version >$null 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Chocolatey is already installed" -ForegroundColor Green
    choco --version
} else {
    Write-Host "[INSTALLING] Chocolatey..." -ForegroundColor Yellow
    
    # Install Chocolatey
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Chocolatey installed!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to install Chocolatey" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 2: Install dependencies
Write-Host "Step 2: Installing dependencies via Chocolatey..." -ForegroundColor Cyan
Write-Host ""

$packages = @(
    "cmake",
    "visualstudio2022buildtools",
    "boost-msvc-14.3",
    "sdl2",
    "winflexbison"
)

$failedPackages = @()

foreach ($package in $packages) {
    Write-Host "  Installing: $package" -ForegroundColor Yellow
    
    choco install -y $package
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $package installed" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] $package installation had issues (may still work)" -ForegroundColor Yellow
        $failedPackages += $package
    }
    
    Write-Host ""
}

Write-Host ""

# Step 3: Set up environment variables
Write-Host "Step 3: Setting environment variables..." -ForegroundColor Cyan

# Find Boost installation
$boostPath = "C:\local\boost*"
$boostFound = Get-ChildItem -Path "C:\local" -Directory -Filter "boost*" 2>$null | Select-Object -First 1

if ($boostFound) {
    $BOOST_ROOT = $boostFound.FullName
    Write-Host "  Found Boost at: $BOOST_ROOT" -ForegroundColor Green
    [Environment]::SetEnvironmentVariable("BOOST_ROOT", $BOOST_ROOT, "User")
    Write-Host "  [OK] BOOST_ROOT set" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] Could not auto-detect Boost path" -ForegroundColor Yellow
    Write-Host "  If Boost installation fails, manually set:"
    Write-Host "    BOOST_ROOT=C:\path\to\boost" -ForegroundColor Cyan
}

Write-Host ""

# SDL2 path (usually installed by Chocolatey)
$sdl2Path = "C:\tools\SDL2*"
$sdl2Found = Get-ChildItem -Path "C:\tools" -Directory -Filter "SDL2*" 2>$null | Select-Object -First 1

if ($sdl2Found) {
    $SDL2_PATH = $sdl2Found.FullName
    Write-Host "  Found SDL2 at: $SDL2_PATH" -ForegroundColor Green
    [Environment]::SetEnvironmentVariable("SDL2_PATH", $SDL2_PATH, "User")
    Write-Host "  [OK] SDL2_PATH set" -ForegroundColor Green
} else {
    Write-Host "  [INFO] SDL2 path will be detected by CMake" -ForegroundColor Cyan
}

Write-Host ""

# Step 4: Verify installation
Write-Host "Step 4: Verifying installation..." -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check CMake
Write-Host "  Checking CMake..."
cmake --version >$null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    [OK] CMake is available" -ForegroundColor Green
} else {
    Write-Host "    [ERROR] CMake not found in PATH" -ForegroundColor Red
    $allGood = $false
}

# Check MSVC
Write-Host "  Checking MSVC compiler..."
cl.exe >$null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    [OK] MSVC compiler is available" -ForegroundColor Green
} else {
    Write-Host "    [WARNING] MSVC not in PATH - you may need to run from Developer Command Prompt" -ForegroundColor Yellow
}

# Check Flex
Write-Host "  Checking Flex..."
flex --version >$null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    [OK] Flex is available" -ForegroundColor Green
} else {
    Write-Host "    [ERROR] Flex not found in PATH" -ForegroundColor Red
    $allGood = $false
}

# Check Bison
Write-Host "  Checking Bison..."
bison --version >$null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    [OK] Bison is available" -ForegroundColor Green
} else {
    Write-Host "    [ERROR] Bison not found in PATH" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""

# Step 5: Final summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($allGood) {
    Write-Host "[SUCCESS] All dependencies are ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now proceed with building engine-sim:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  cd 'C:\Users\kitza\Documents\Project-Ironloop\Source\Phase-01-EngineSimPatch\engine-sim'" -ForegroundColor White
    Write-Host "  mkdir build" -ForegroundColor White
    Write-Host "  cd build" -ForegroundColor White
    Write-Host "  cmake .. -G 'Visual Studio 17 2022'" -ForegroundColor White
    Write-Host "  cmake --build . --config Release" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "[WARNING] Some dependencies may have issues." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Failed packages: $($failedPackages -join ', ')" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Restart PowerShell (as Administrator)" -ForegroundColor White
    Write-Host "  2. Run: '.\setup-chocolatey.ps1' again" -ForegroundColor White
    Write-Host "  3. Or install manually: https://github.com/ME7DIY/Project-Ironloop/tree/main/Source/Phase-01-EngineSimPatch/docs/BUILD.md" -ForegroundColor White
    Write-Host ""
}

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
