# 🚀 Quick Start Guide - MyDownloader C++

## Installation in 5 Minutes

### Windows (Quick Start)

1. **Install vcpkg** (dependency manager):
   ```powershell
   git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg
   cd C:\vcpkg
   .\bootstrap-vcpkg.bat
   .\vcpkg integrate install
   ```

2. **Install dependencies**:
   ```powershell
   .\vcpkg install wxwidgets:x64-windows nlohmann-json:x64-windows cpr:x64-windows
   ```

3. **Install runtime tools**:
   ```powershell
   winget install yt-dlp.yt-dlp
   winget install Gyan.FFmpeg
   ```

4. **Build**:
   ```powershell
   set VCPKG_ROOT=C:\vcpkg
   cd MyDownloader\cpp
   .\build.bat
   ```

5. **Run**:
   ```powershell
   cd build\Release
   .\MyDownloader.exe
   ```

---

### macOS (Quick Start)

1. **Install Homebrew** (if not installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install all dependencies**:
   ```bash
   brew install cmake wxwidgets nlohmann-json cpr yt-dlp ffmpeg
   ```

3. **Build**:
   ```bash
   cd MyDownloader/cpp
   chmod +x build.sh
   ./build.sh
   ```

4. **Run**:
   ```bash
   open build/MyDownloader.app
   # Or:
   ./build/MyDownloader.app/Contents/MacOS/MyDownloader
   ```

---

### Linux (Quick Start)

1. **Install dependencies** (Ubuntu/Debian):
   ```bash
   sudo apt update
   sudo apt install -y build-essential cmake git \
       libwxgtk3.0-gtk3-dev nlohmann-json3-dev \
       libcpr-dev yt-dlp ffmpeg
   ```

   **For Fedora/RHEL**:
   ```bash
   sudo dnf install -y gcc-c++ cmake git \
       wxGTK3-devel json-devel cpr-devel \
       yt-dlp ffmpeg
   ```

2. **Build**:
   ```bash
   cd MyDownloader/cpp
   chmod +x build.sh
   ./build.sh
   ```

3. **Run**:
   ```bash
   ./build/MyDownloader
   ```

---

## First Use

1. **Launch the application**
2. **Paste a YouTube URL** in the Download tab
3. **Select format** (MP3, M4A, etc.) and quality
4. **Click Download** 

That's it! 🎉

---

## Troubleshooting

### yt-dlp not found?
```bash
# Check if installed:
yt-dlp --version

# If not, install:
# Windows:
winget install yt-dlp.yt-dlp

# macOS:
brew install yt-dlp

# Linux:
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp
```

### FFmpeg not found?
```bash
# Check if installed:
ffmpeg -version

# If not, install:
# Windows:
winget install Gyan.FFmpeg

# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg  # or: sudo dnf install ffmpeg
```

### Build fails?
- Make sure all dependencies are installed
- Check CMake version: `cmake --version` (needs 3.20+)
- Check C++ compiler: `g++ --version` or `clang++ --version`

---

## Features Overview

| Tab | Purpose |
|-----|---------|
| 📥 **Download** | Download single videos/songs |
| 📋 **Queue** | Batch download multiple items |
| 📜 **History** | View past downloads |
| ⚙️ **Settings** | Configure app preferences |
| ℹ️ **Info** | About and help |

---

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Report issues on GitHub

**Enjoy MyDownloader! 🎵**
