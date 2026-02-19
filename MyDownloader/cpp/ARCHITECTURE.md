# MyDownloader C++ Native Version

This is the C++ implementation with native UI elements using wxWidgets.

## Key Features

- **Native UI**: Uses platform-native controls (Win32/Cocoa/GTK+)
- **Performance**: Compiled C++ for better performance
- **Cross-platform**: Single codebase for Windows, macOS, and Linux
- **Modern C++17**: Uses modern C++ features and best practices

## Differences from Python Version

| Feature | Python Version | C++ Version |
|---------|---------------|-------------|
| UI Framework | tkinter/customtkinter | wxWidgets |
| UI Elements | Themed widgets | Native OS widgets |
| Performance | Interpreted | Compiled (faster) |
| Memory Usage | Higher | Lower |
| Dependencies | Python + packages | Compiled binary |
| Distribution | Requires Python | Standalone executable |
| Startup Time | Slower | Faster |
| File Size | Smaller (with Python) | Larger (standalone) |

## Platform-Specific Notes

### Windows
- Uses native Win32 controls
- Modern Windows UI theming
- Windows manifest for DPI awareness
- Compatible with Windows 7 and later

### macOS
- Uses native Cocoa controls
- Supports Dark Mode automatically
- Creates proper .app bundle
- Compatible with macOS 10.13 and later

### Linux
- Uses native GTK+ controls
- Integrates with desktop environment
- Supports system themes
- Works on most Linux distributions

## Building

See [README.md](README.md) for complete build instructions.

Quick start:
- **Windows**: Run `build.bat`
- **Linux/macOS**: Run `./build.sh`

## Architecture

```
┌─────────────────────────────────────┐
│         Application Layer           │
│         (app.cpp/main.cpp)          │
└─────────────────────────────────────┘
           │
┌──────────┴──────────┬────────────────┐
│                     │                │
▼                     ▼                ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ UI Layer │   │   Core   │   │  Utils   │
│ (wx...)  │   │ (down... │   │ (file... │
└──────────┘   └──────────┘   └──────────┘
     │              │                │
     └──────────────┴────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   External Tools     │
         │  (yt-dlp, ffmpeg)    │
         └──────────────────────┘
```

## Future Enhancements

- [ ] Drag & Drop support
- [ ] System tray integration
- [ ] Auto-update functionality
- [ ] Portable mode
- [ ] Multi-language support
- [ ] Custom themes
- [ ] Browser integration
- [ ] Playlist manager

## Contributing

Contributions are welcome! Please ensure:
- Code follows C++17 standards
- Cross-platform compatibility is maintained
- All platforms are tested before PR

## License

MIT License - See [LICENSE](../LICENSE)
