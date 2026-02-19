# 🛠️ Entwickler-Anleitung - MyDownloader C++

## Schnellstart Entwicklung

### Einmalige Einrichtung

1. **vcpkg installieren:**
   ```powershell
   cd C:\
   git clone https://github.com/Microsoft/vcpkg.git
   cd vcpkg
   .\bootstrap-vcpkg.bat
   .\vcpkg integrate install
   ```

2. **Dependencies installieren:**
   ```powershell
   .\vcpkg install wxwidgets:x64-windows nlohmann-json:x64-windows cpr:x64-windows
   ```

3. **Umgebungsvariable setzen:**
   ```powershell
   # Dauerhaft:
   [System.Environment]::SetEnvironmentVariable('VCPKG_ROOT', 'C:\vcpkg', 'User')
   
   # Oder nur für aktuelle Session:
   $env:VCPKG_ROOT = "C:\vcpkg"
   ```

### Erstes Build

```powershell
cd cpp
mkdir build
cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=C:\vcpkg\scripts\buildsystems\vcpkg.cmake
cmake --build . --config Debug
```

---

## Entwicklungs-Workflow

### Schnelle Entwicklung (empfohlen)

1. **Code ändern** (z.B. `src/ui/download_panel.cpp`)

2. **Schneller Rebuild & Run:**
   ```powershell
   .\dev-build.bat
   ```
   Dieser Skript baut nur geänderte Dateien neu und startet die App!

3. **Bei Problemen - Clean Build:**
   ```powershell
   .\clean-build.bat
   ```

### Nur Kompilieren (ohne Run)

```powershell
cd build
cmake --build . --config Debug -- /m
```

### Release Build

```powershell
cd build
cmake --build . --config Release -- /m
.\Release\MyDownloader.exe
```

---

## IDEs

### Visual Studio 2019/2022

1. **Projekt öffnen:**
   - File → Open → Folder
   - Wähle `cpp` Ordner

2. **CMake konfigurieren:**
   - CMake → CMake Settings
   - Füge hinzu: `"CMAKE_TOOLCHAIN_FILE": "C:/vcpkg/scripts/buildsystems/vcpkg.cmake"`

3. **Entwickeln:**
   - F7: Build
   - F5: Debug
   - Ctrl+F5: Run ohne Debug

### VS Code

1. **Extensions installieren:**
   - C/C++
   - CMake Tools

2. **Konfiguration:**
   Datei `.vscode/settings.json`:
   ```json
   {
       "cmake.configureSettings": {
           "CMAKE_TOOLCHAIN_FILE": "C:/vcpkg/scripts/buildsystems/vcpkg.cmake"
       }
   }
   ```

3. **Entwickeln:**
   - Ctrl+Shift+P → CMake: Configure
   - Ctrl+Shift+P → CMake: Build
   - F5: Debug

### CLion

1. **Projekt öffnen:**
   - Open → `cpp` Ordner

2. **CMake Settings:**
   - File → Settings → Build, Execution, Deployment → CMake
   - CMake options: `-DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake`

3. **Entwickeln:**
   - Shift+F10: Run
   - Shift+F9: Debug

---

## Debugging

### Breakpoints

**Visual Studio / VS Code:**
- Klick auf linken Rand neben Zeilennummer
- Oder F9 auf gewünschter Zeile

**Beispiel-Breakpoint in `download_panel.cpp`:**
```cpp
void DownloadPanel::OnDownload(wxCommandEvent& event)
{
    wxString url = m_urlInput->GetValue();
    // <-- Breakpoint hier setzen
    if (!ValidateUrl(url))
    {
        // ...
    }
}
```

### Logging

**In Code hinzufügen:**
```cpp
// In download_panel.cpp
void DownloadPanel::Log(const wxString& message)
{
    #ifdef _DEBUG
    wxLogDebug(message);  // Nur in Debug-Build
    #endif
    m_logTextCtrl->AppendText(message + "\n");
}
```

### Debug vs Release

```powershell
# Debug: Mit Symbolen, langsamer, größer
cmake --build . --config Debug

# Release: Optimiert, schneller, kleiner
cmake --build . --config Release
```

---

## Dateistruktur für neue Features

### Neues UI-Panel hinzufügen

1. **Header erstellen:** `include/ui/my_new_panel.h`
   ```cpp
   #pragma once
   #include <wx/wx.h>
   
   class MyNewPanel : public wxPanel
   {
   public:
       MyNewPanel(wxWindow* parent);
       virtual ~MyNewPanel();
   private:
       void CreateControls();
       void LayoutControls();
       wxDECLARE_EVENT_TABLE();
   };
   ```

2. **Implementation:** `src/ui/my_new_panel.cpp`
   ```cpp
   #include "ui/my_new_panel.h"
   
   wxBEGIN_EVENT_TABLE(MyNewPanel, wxPanel)
   wxEND_EVENT_TABLE()
   
   MyNewPanel::MyNewPanel(wxWindow* parent)
       : wxPanel(parent)
   {
       CreateControls();
       LayoutControls();
   }
   // ...
   ```

3. **In CMakeLists.txt hinzufügen:**
   ```cmake
   set(SOURCES
       # ... existing files ...
       src/ui/my_new_panel.cpp
   )
   set(HEADERS
       # ... existing files ...
       include/ui/my_new_panel.h
   )
   ```

4. **Neu konfigurieren:**
   ```powershell
   cd build
   cmake ..
   ```

### Neue Core-Funktionalität

Gleicher Prozess, aber in `include/core/` und `src/core/`

---

## Häufige Build-Probleme

### "Cannot find wxWidgets"
```powershell
# Neu installieren:
cd C:\vcpkg
.\vcpkg remove wxwidgets:x64-windows
.\vcpkg install wxwidgets:x64-windows
```

### "LNK1104: cannot open file"
- CMake neu konfigurieren
- Build-Ordner löschen und neu erstellen

### Änderungen werden nicht übernommen
```powershell
# Clean rebuild:
.\clean-build.bat
```

### "Permission denied" beim Ausführen
- Schließe laufende MyDownloader.exe Instanzen
- Prüfe Antivirus-Software

---

## Code-Style

### Konventionen

- **Namensgebung:**
  - Klassen: `PascalCase` (DownloadPanel)
  - Methoden: `PascalCase` (OnDownload)
  - Member-Variablen: `m_camelCase` (m_urlInput)
  - Lokale Variablen: `camelCase` (fileName)

- **Header Guards:** `#pragma once`

- **Indentation:** 4 Spaces (keine Tabs)

- **Kommentare:**
  ```cpp
  // Kurze Erklärung auf einer Zeile
  
  /**
   * Längere Dokumentation
   * für Funktionen/Klassen
   */
  ```

### Beispiel

```cpp
#include "ui/download_panel.h"

void DownloadPanel::OnDownload(wxCommandEvent& event)
{
    wxString url = m_urlInput->GetValue();
    
    if (!ValidateUrl(url))
    {
        wxMessageBox("Invalid URL", "Error", wxOK | wxICON_ERROR);
        return;
    }
    
    // Create download config
    DownloadConfig config;
    config.url = url.ToStdString();
    config.format = m_formatCombo->GetValue().ToStdString();
    
    // Start download
    m_downloader->Download(config);
}
```

---

## Testing

### Manuelles Testing

1. Build Debug-Version
2. Starte App
3. Teste Features:
   - URL eingeben
   - Format wählen
   - Download starten
   - Prüfe Logs
   - Prüfe Output-Dateien

### Test-URLs

```
# Einzelnes Video:
https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Playlist:
https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK
```

---

## Performance-Profiling

### Visual Studio Profiler

1. Debug → Performance Profiler
2. Wähle "CPU Usage"
3. Start
4. Nutze App
5. Stop → Analysiere Results

### Memory Leaks

```cpp
// In main.cpp (Debug-Build):
#ifdef _DEBUG
#define _CRTDBG_MAP_ALLOC
#include <crtdbg.h>
#endif

// Am Ende von OnExit():
#ifdef _DEBUG
_CrtDumpMemoryLeaks();
#endif
```

---

## Nützliche Befehle

```powershell
# Schneller Dev-Cycle:
.\dev-build.bat

# Clean Build:
.\clean-build.bat

# Nur kompilieren:
cd build; cmake --build . --config Debug

# Release kompilieren:
cd build; cmake --build . --config Release

# CMake neu konfigurieren:
cd build; cmake ..

# Alle Targets anzeigen:
cd build; cmake --build . --target help
```

---

## Nächste Schritte

1. **Erste Änderung:** Ändere Text in `info_panel.cpp`
2. **Build:** `.\dev-build.bat`
3. **Test:** Prüfe ob Änderung sichtbar ist
4. **Erweitere:** Füge neue Features hinzu!

**Viel Erfolg beim Entwickeln! 🚀**
