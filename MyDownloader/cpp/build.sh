#!/bin/bash
# Quick build script for Linux/macOS

echo "🎵 MyDownloader - Building..."

# Create build directory
mkdir -p build
cd build

# Configure
echo "⚙️ Configuring with CMake..."
cmake ..

if [ $? -ne 0 ]; then
    echo "❌ CMake configuration failed!"
    exit 1
fi

# Build
echo "🔨 Building..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    make -j$(sysctl -n hw.ncpu)
else
    # Linux
    make -j$(nproc)
fi

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"
echo ""
echo "To run:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  ./MyDownloader.app/Contents/MacOS/MyDownloader"
else
    echo "  ./MyDownloader"
fi
