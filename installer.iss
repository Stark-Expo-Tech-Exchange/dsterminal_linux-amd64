[Setup]
AppName=Exploit Scanner
AppVersion=1.0
AppPublisher=Your Company
AppPublisherURL=https://your-website.com
AppSupportURL=https://your-website.com/support
AppUpdatesURL=https://your-website.com/updates
DefaultDirName={pf}\ExploitScanner
DefaultGroupName=Exploit Scanner
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=ExploitScanner_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=app.ico
UninstallDisplayIcon={app}\exploit_scanner.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\exploit_scanner.exe"; DestDir: "{app}"; Flags: ignoreversion
; Add any data files your app needs
; Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
; Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Exploit Scanner"; Filename: "{app}\exploit_scanner.exe"
Name: "{group}\{cm:UninstallProgram,Exploit Scanner}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Exploit Scanner"; Filename: "{app}\exploit_scanner.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\exploit_scanner.exe"; Description: "{cm:LaunchProgram,Exploit Scanner}"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"
Type: dirifempty; Name: "{app}"
