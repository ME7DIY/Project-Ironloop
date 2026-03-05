@echo off
REM Dependency Check Script for engine-sim on Windows
REM This script checks if all required tools are installed and in PATH

echo.
echo ========================================
echo ENGINE-SIM DEPENDENCY CHECK
echo ========================================
echo.

setlocal enabledelayedexpansion

set "missing="

REM Check CMake
echo Checking CMake...
cmake --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] CMake is installed
    for /f "tokens=3" %%i in ('cmake --version ^| findstr /R "cmake version"') do echo      Version: %%i
) else (
    echo [MISSING] CMake
    set "missing=!missing! CMake"
)
echo.

REM Check MSVC Compiler
echo Checking MSVC Compiler (cl.exe)...
cl.exe >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] MSVC compiler found
) else (
    echo [MISSING] MSVC compiler (Visual Studio Build Tools needed)
    set "missing=!missing! MSVC"
)
echo.

REM Check Boost
echo Checking Boost library...
if defined BOOST_ROOT (
    if exist "!BOOST_ROOT!\lib" (
        echo [OK] Boost found at: !BOOST_ROOT!
    ) else (
        echo [WARNING] BOOST_ROOT set but lib folder not found
        set "missing=!missing! Boost"
    )
) else (
    echo [MISSING] Boost (BOOST_ROOT environment variable not set)
    set "missing=!missing! Boost"
)
echo.

REM Check SDL2
echo Checking SDL2...
if defined SDL2_PATH (
    if exist "!SDL2_PATH!\include\SDL2" (
        echo [OK] SDL2 found at: !SDL2_PATH!
    ) else (
        echo [WARNING] SDL2_PATH set but SDL2 headers not found
        set "missing=!missing! SDL2"
    )
) else (
    echo [MISSING] SDL2 (SDL2_PATH environment variable not set)
    set "missing=!missing! SDL2"
)
echo.

REM Check SDL2_image
echo Checking SDL2_image...
if defined SDL2_IMAGE_PATH (
    if exist "!SDL2_IMAGE_PATH!\include\SDL2" (
        echo [OK] SDL2_image found at: !SDL2_IMAGE_PATH!
    ) else (
        echo [WARNING] SDL2_IMAGE_PATH set but headers not found
    )
) else (
    echo [INFO] SDL2_image not found (optional, but recommended)
)
echo.

REM Check Flex and Bison
echo Checking Flex...
flex --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Flex is installed
) else (
    echo [MISSING] Flex (WinFlexBison needed)
    set "missing=!missing! Flex"
)
echo.

echo Checking Bison...
bison --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Bison is installed
) else (
    echo [MISSING] Bison (WinFlexBison needed)
    set "missing=!missing! Bison"
)
echo.

REM Summary
echo ========================================
echo SUMMARY
echo ========================================
if "!missing!"=="" (
    echo [SUCCESS] All required dependencies are installed!
    echo You can proceed with building engine-sim.
    exit /b 0
) else (
    echo [ERROR] Missing dependencies:!missing!
    echo.
    echo See Source/Phase-01-EngineSimPatch/docs/BUILD.md for installation instructions.
    exit /b 1
)
