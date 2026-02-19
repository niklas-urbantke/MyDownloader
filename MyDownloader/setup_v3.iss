; Inno Setup Script für MyDownloader V3
; Requires Inno Setup 6.0 or later
; Download from: https://jrsoftware.org/isinfo.php

#define MyAppName "MyDownloader"
#define MyAppVersion "3.0.0"
#define MyAppPublisher "UST-Germany"
#define MyAppURL "https://github.com/ust-germany/mydownloader"
#define MyAppExeName "MyDownloader.exe"
#define MyAppDescription "Ultimate Music & Video Downloader"

[Setup]
; Application Info
AppId={{B8F9E5D2-3C4A-4F1B-9A2D-6E8F7C9B1A3D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2026 {#MyAppPublisher}
AppComments={#MyAppDescription}

; Installation Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
AllowNoIcons=yes

; Output
OutputDir=dist\installer
OutputBaseFilename={#MyAppName}-{#MyAppVersion}-Setup
Compression=lzma2/ultra64
SolidCompression=yes
; Icon (optional - wird erstellt wenn nicht vorhanden)
#ifdef SetupIconFile
SetupIconFile=assets\icon.ico
#endif

; Windows Version
MinVersion=10.0.17763
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; UI
WizardStyle=modern
DisableWelcomePage=no
LicenseFile=LICENSE
InfoBeforeFile=

; Uninstaller
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallFilesDir={app}\uninstall

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Hauptanwendung
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Dokumentation
Source: "dist\README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

; Optional: Assets (falls vorhanden)
#ifdef IncludeAssets
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

; FFmpeg wird automatisch heruntergeladen von der App selbst

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop Icon (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"; Tasks: desktopicon

; Quick Launch (optional)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Starte App nach Installation (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Benutzerdefinierte Installer-Seiten und Funktionen

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpWelcome then
  begin
    WizardForm.WelcomeLabel2.Caption := 
      'Dieser Assistent wird {#MyAppName} Version {#MyAppVersion} auf Ihrem Computer installieren.' + #13#10 + #13#10 +
      '{#MyAppDescription}' + #13#10 + #13#10 +
      'Features:' + #13#10 +
      '  • Download einzelner Videos/Songs' + #13#10 +
      '  • Download kompletter Playlists' + #13#10 +
      '  • Queue-System für Batch-Downloads' + #13#10 +
      '  • Unterstützung für MP3, M4A, FLAC, WAV' + #13#10 +
      '  • Dark/Light Theme' + #13#10 +
      '  • Download-History' + #13#10 + #13#10 +
      'Klicken Sie auf "Weiter", um fortzufahren.';
  end;
end;

function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  Result := True;
  
  // Prüfe Windows-Version (Windows 10 = 10.0)
  GetWindowsVersionEx(Version);
  if (Version.Major < 10) then
  begin
    MsgBox('Diese Anwendung benötigt Windows 10 oder neuer.' + #13#10 + 
           'Ihre Version: Windows ' + IntToStr(Version.Major) + '.' + IntToStr(Version.Minor), 
           mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Zeige Info über optionale Software
    if MsgBox(
      'Optional: Node.js für optimale YouTube-Unterstützung' + #13#10 + #13#10 +
      'Möchten Sie Informationen zur Installation von Node.js erhalten?' + #13#10 +
      '(Empfohlen für beste YouTube-Kompatibilität)',
      mbInformation, MB_YESNO) = IDYES then
    begin
      MsgBox(
        'Node.js Installation:' + #13#10 + #13#10 +
        '1. Mit Chocolatey (empfohlen):' + #13#10 +
        '   choco install nodejs' + #13#10 + #13#10 +
        '2. Manuelle Installation:' + #13#10 +
        '   Download von https://nodejs.org' + #13#10 + #13#10 +
        'Nach der Installation konfigurieren Sie den Pfad' + #13#10 +
        'in den Einstellungen von MyDownloader.',
        mbInformation, MB_OK);
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
  AppDataPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Frage ob Einstellungen und Downloads gelöscht werden sollen
    AppDataPath := ExpandConstant('{userappdata}\MyDownloader');
    
    if DirExists(AppDataPath) then
    begin
      if MsgBox(
        'Möchten Sie auch Ihre persönlichen Einstellungen und' + #13#10 +
        'Download-History löschen?' + #13#10 + #13#10 +
        'Pfad: ' + AppDataPath,
        mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(AppDataPath, True, True, True);
      end;
    end;
  end;
end;
