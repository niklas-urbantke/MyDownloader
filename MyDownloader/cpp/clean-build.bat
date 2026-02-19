@echo off
REM Clean and rebuild from scratch

echo 🧹 Cleaning build directory...

if exist build (
    rmdir /s /q build
)

echo 🔨 Building from scratch...

mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_TOOLCHAIN_FILE=C:\vcpkg\scripts\buildsystems\vcpkg.cmake

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Visual Studio 2022 not found, trying Visual Studio 2019...
    cmake .. -G "Visual Studio 16 2019" -A x64 -DCMAKE_TOOLCHAIN_FILE=C:\vcpkg\scripts\buildsystems\vcpkg.cmake
    
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ CMake configuration failed!
        echo Please install Visual Studio 2019 or 2022 with C++ support.
        pause
        exit /b 1
    )
)

cmake --build . --config Debug -- /m

if %ERRORLEVEL% EQU 0 (
    echo ✅ Clean build successful!
    pause
) else (
    echo ❌ Build failed!
    pause
)
