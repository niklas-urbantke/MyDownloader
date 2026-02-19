@echo off
REM Quick build script for Windows

echo 🎵 MyDownloader - Building...

REM Check if vcpkg toolchain file is set
if "%VCPKG_ROOT%"=="" (
    echo ⚠️ VCPKG_ROOT not set. Please set it or provide CMAKE_TOOLCHAIN_FILE manually.
    echo Example: set VCPKG_ROOT=C:\path\to\vcpkg
    pause
    exit /b 1
)

REM Create build directory
if not exist build mkdir build
cd build

REM Configure
echo ⚙️ Configuring with CMake...
cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_TOOLCHAIN_FILE=%VCPKG_ROOT%\scripts\buildsystems\vcpkg.cmake

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Visual Studio 2022 not found, trying Visual Studio 2019...
    cmake .. -G "Visual Studio 16 2019" -A x64 -DCMAKE_TOOLCHAIN_FILE=%VCPKG_ROOT%\scripts\buildsystems\vcpkg.cmake
    
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ CMake configuration failed!
        echo Please install Visual Studio 2019 or 2022 with C++ support.
        pause
        exit /b 1
    )
)

REM Build
echo 🔨 Building...
cmake --build . --config Release

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo ✅ Build successful!
echo.
echo To run:
echo   Release\MyDownloader.exe
pause
