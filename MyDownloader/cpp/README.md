# 🎵 MyDownloader v3.0 - C++ Native Edition

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![C++17](https://img.shields.io/badge/C%2B%2B-17-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Professional YouTube Downloader with native UI elements for each platform**

Built with **wxWidgets**, this version provides truly native user interface elements:
- **Windows**: Native Win32 controls
- **macOS**: Native Cocoa controls  
- **Linux**: Native GTK+ controls

---

## ✨ Features

### 🎯 Download Capabilities
- ✅ **Single Videos/Songs** download
- ✅ **Complete Playlists** with one click
- ✅ **Queue System** for batch downloads
- ✅ **Download History** tracking

### 🎵 Audio Formats
- MP3, M4A, OPUS, FLAC, WAV
- Quality levels: 0 (best) to 9 (smallest file)
- Embed thumbnail as cover art
- Automatic ID3 metadata

### 🎨 Native UI
- Tab-based navigation (Download, Queue, History, Settings, Info)
- Platform-native controls and dialogs
- System theme integration
- Responsive layout

### ⚙️ Advanced Options
- Subtitle download (multiple languages)
- Speed limit configuration
- Auto-queue mode
- Export history

---

## 📋 Requirements

### All Platforms
- **CMake** 3.20 or higher
- **C++17** compatible compiler
- **wxWidgets** 3.2 or higher
- **nlohmann/json** 3.11.0 or higher
- **cpr** (libcurl wrapper) or libcurl
- **yt-dlp** (runtime dependency)
- **FFmpeg** (runtime dependency)

### Windows
- **Visual Studio 2019** or higher (with C++ desktop development)
- OR **MinGW-w64** with GCC 9+

### macOS
- **Xcode** 12 or higher
- **Xcode Command Line Tools**

### Linux
- **GCC** 9+ or **Clang** 10+
- **GTK+ 3** development libraries

---

## 🚀 Installation

### Windows

#### 1. Install Dependencies

Using **vcpkg** (recommended):
```powershell
# Install vcpkg
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat

# Install dependencies
.\vcpkg install wxwidgets:x64-windows
.\vcpkg install nlohmann-json:x64-windows
.\vcpkg install cpr:x64-windows

# Integrate with CMake
.\vcpkg integrate install
```

#### 2. Install Runtime Dependencies
```powershell
# Install yt-dlp
winget install yt-dlp.yt-dlp

# Install FFmpeg
winget install Gyan.FFmpeg
```

#### 3. Build
```powershell
cd MyDownloader\cpp
mkdir build
cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=[path-to-vcpkg]/scripts/buildsystems/vcpkg.cmake
cmake --build . --config Release
```

#### 4. Run
```powershell
.\Release\MyDownloader.exe
```

---

### macOS

#### 1. Install Dependencies

Using **Homebrew**:
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cmake
brew install wxwidgets
brew install nlohmann-json
brew install cpr
brew install yt-dlp
brew install ffmpeg
```

#### 2. Build
```bash
cd MyDownloader/cpp
mkdir build
cd build
cmake ..
make -j$(sysctl -n hw.ncpu)
```

#### 3. Run
```bash
./MyDownloader.app/Contents/MacOS/MyDownloader
# Or double-click MyDownloader.app in Finder
```

---

### Linux (Ubuntu/Debian)

#### 1. Install Dependencies
```bash
# Build tools
sudo apt update
sudo apt install build-essential cmake git

# wxWidgets dependencies
sudo apt install libwxgtk3.0-gtk3-dev

# Other dependencies
sudo apt install nlohmann-json3-dev
sudo apt install libcpr-dev

# Runtime dependencies
sudo apt install yt-dlp ffmpeg

# If yt-dlp is not in repos:
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp
```

#### 2. Build
```bash
cd MyDownloader/cpp
mkdir build
cd build
cmake ..
make -j$(nproc)
```

#### 3. Install (optional)
```bash
sudo make install
```

#### 4. Run
```bash
./MyDownloader
# Or if installed:
MyDownloader
```

---

## 📁 Project Structure

```
cpp/
├── CMakeLists.txt          # CMake build configuration
├── README.md               # This file
├── include/                # Header files
│   ├── app.h
│   ├── core/              # Core functionality
│   │   ├── downloader.h
│   │   ├── queue_manager.h
│   │   ├── settings_manager.h
│   │   └── history_manager.h
│   ├── ui/                # UI components
│   │   ├── main_frame.h
│   │   ├── download_panel.h
│   │   ├── queue_panel.h
│   │   ├── history_panel.h
│   │   ├── settings_panel.h
│   │   └── info_panel.h
│   └── utils/             # Utilities
│       ├── file_utils.h
│       └── string_utils.h
├── src/                   # Source files
│   ├── main.cpp
│   ├── app.cpp
│   ├── core/
│   ├── ui/
│   └── utils/
└── resources/             # Platform-specific resources
    ├── windows/           # Windows resources (.rc, .ico)
    ├── macos/            # macOS resources (.icns, Info.plist)
    └── linux/            # Linux resources (.desktop, .png)
```

---

## 🔧 Development

### Building for Debug
```bash
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build .
```

### Code Style
- Follow **C++ Core Guidelines**
- Use **modern C++17** features
- RAII for resource management
- Smart pointers over raw pointers

### Adding Features
1. Create header in `include/`
2. Implement in `src/`
3. Update `CMakeLists.txt` if needed
4. Test on all platforms

---

## 🐛 Troubleshooting

### Windows
**Problem**: CMake cannot find wxWidgets  
**Solution**: Make sure vcpkg is integrated and CMAKE_TOOLCHAIN_FILE is set

**Problem**: Missing DLL errors  
**Solution**: Copy DLLs from vcpkg/installed/x64-windows/bin/ to exe directory

### macOS  
**Problem**: "MyDownloader.app" is damaged  
**Solution**: 
```bash
xattr -cr MyDownloader.app
```

### Linux
**Problem**: Cannot find wxWidgets  
**Solution**: Install development package:
```bash
sudo apt install libwxgtk3.0-gtk3-dev
```

**Problem**: yt-dlp not found  
**Solution**: Install manually or add to PATH

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) file

---

## 🙏 Credits

- **wxWidgets** - Cross-platform GUI framework
- **yt-dlp** - YouTube downloader
- **FFmpeg** - Audio/video processing
- **nlohmann/json** - JSON library
- **cpr** - HTTP requests

---

## 📞 Support

For issues and questions, please open a GitHub issue.

**Built with ❤️ using C++ and wxWidgets**
