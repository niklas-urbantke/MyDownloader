; Inno Setup Script for MyDownloader
; Requires Inno Setup 6.0 or later
; Download from: https://jrsoftware.org/isinfo.php

#define MyAppName "MyDownloader"
#define MyAppVersion "3.0.0"
#define MyAppPublisher "UST-Germany"
#define MyAppURL "https://github.com/yourusername/mydownloader"
#define MyAppExeName "MyDownloader.exe"

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

; Installation Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=dist\installer
OutputBaseFilename=MyDownloader-{#MyAppVersion}-Setup
SetupIconFile=assets\icons\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes

; Windows Version
MinVersion=6.1sp1
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; UI
WizardStyle=modern
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp
DisableWelcomePage=no

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable (created with PyInstaller)
Source: "dist\MyDownloader\MyDownloader.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\MyDownloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "README_V3.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "README.md"
Source: "SCHNELLSTART_V3.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "SCHNELLSTART.md"
Source: "FEATURE_VERGLEICH.md"; DestDir: "{app}";Flags: ignoreversion

; License (create if needed)
; Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\README"; Filename: "{app}\README.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop Icon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Launch application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Custom installation code

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Add custom initialization here if needed
end;

procedure InitializeWizard();
begin
  // Custom wizard initialization
  WizardForm.WelcomeLabel2.Caption := 
    'Dies installiert MyDownloader ' + '{#MyAppVersion}' + ' auf Ihrem Computer.' + #13#10 + #13#10 +
    'MyDownloader ist ein leistungsstarker YouTube Downloader ' +
    'für Musik und Videos.' + #13#10 + #13#10 +
    'Klicken Sie auf Weiter um fortzufahren.';
end;

function InitializeUninstall(): Boolean;
begin
  Result := MsgBox('Möchten Sie MyDownloader wirklich deinstallieren?', 
                   mbConfirmation, MB_YESNO) = IDYES;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Ask to delete user data
    AppDataPath := ExpandConstant('{userappdata}\.mydownloader');
    if DirExists(AppDataPath) then
    begin
      if MsgBox('Möchten Sie auch die Einstellungen und den Verlauf löschen?' + #13#10 +
                'Pfad: ' + AppDataPath, mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(AppDataPath, True, True, True);
      end;
    end;
  end;
end;
