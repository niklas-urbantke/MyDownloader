@echo off
REM Quick rebuild for development

echo 🔨 Rebuilding MyDownloader (Debug)...

if not exist build (
    echo Creating build directory...
    mkdir build
    cd build
    cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_TOOLCHAIN_FILE=C:\vcpkg\scripts\buildsystems\vcpkg.cmake
    if %ERRORLEVEL% NEQ 0 (
        cmake .. -G "Visual Studio 16 2019" -A x64 -DCMAKE_TOOLCHAIN_FILE=C:\vcpkg\scripts\buildsystems\vcpkg.cmake
    )
) else (
    cd build
)

cmake --build . --config Debug -- /m

if %ERRORLEVEL% EQU 0 (
    echo ✅ Build successful!
    echo.
    echo Running MyDownloader...
    .\Debug\MyDownloader.exe
) else (
    echo ❌ Build failed!
    pause
)
