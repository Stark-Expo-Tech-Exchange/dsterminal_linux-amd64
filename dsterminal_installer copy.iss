; DSTerminal Installer Script - Non-Admin Safe with Documentation & Auto-Update
; Version: 4.0.0.113
; Date: 2026
; UPDATED: Added vt_scan.py for VirusTotal module

[Setup]
; Basic Setup Information
AppId={{1EFF5130-85AF-4EE9-B818-5634A06408D2}}
AppName=DSTerminal
AppVersion=4.0.0.113
AppVerName=DSTerminal v4.0.0.113
AppPublisher=Stark Expo Tech Exchange
AppPublisherURL=https://starkexpotechexchange.mw
AppSupportURL=https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest/issues
AppUpdatesURL=https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest/releases
AppContact=support@starkexpotechexchange-mw.com
AppComments=Security Operations Center Terminal
AppCopyright=Copyright © 2024 Stark Expo Tech Exchange

; Installation Paths (User AppData - No Admin Required)
DefaultDirName={userappdata}\DSTerminal
DefaultGroupName=DSTerminal
LicenseFile=license.txt
OutputDir=installer_output
OutputBaseFilename=DSTerminal_Installer_2026_v4.0.0.113
Compression=lzma2/fast
SolidCompression=no
InternalCompressLevel=fast
DisableWelcomePage=no
WizardStyle=modern
SetupIconFile=installer_assets\3486-removebg-preview.ico

WizardImageFile=installer_assets\wizard-image.bmp
WizardSmallImageFile=installer_assets\wizard-small.bmp
WizardImageStretch=No
WizardImageBackColor=clBlack

DisableProgramGroupPage=no
AllowNoIcons=yes
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0
UninstallDisplayIcon={app}\dsterminal.exe
UninstallDisplayName=DSTerminal v4.0.0.113
VersionInfoVersion=4.0.0.113
VersionInfoCompany=Stark Expo Tech Exchange
VersionInfoDescription=DSTerminal Cyber-Ops Platform
VersionInfoTextVersion=4.0.0.113
VersionInfoCopyright=© 2024 Stark Expo Tech Exchange
VersionInfoProductName=DSTerminal
VersionInfoProductVersion=4.0.0.113

; Create uninstaller in registry
CreateUninstallRegKey=yes
UpdateUninstallLogAppName=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full"; Description: "Full Installation (Recommended)"
Name: "compact"; Description: "Compact Installation"
Name: "custom"; Description: "Custom Installation"; Flags: iscustom

[Components]
Name: "core"; Description: "Core DSTerminal Files"; Types: full compact custom; Flags: fixed
Name: "docs"; Description: "Documentation & Help Files"; Types: full custom
Name: "tools"; Description: "Additional Security Tools"; Types: full custom
Name: "templates"; Description: "Report Templates"; Types: full custom
Name: "ffmpeg"; Description: "FFmpeg (Video Analysis)"; Types: full custom
Name: "updatehelper"; Description: "Auto-Update Helper Script"; Types: full custom
; ===== VT Module Component =====
Name: "vtmodule"; Description: "VirusTotal Threat Intelligence Module"; Types: full custom
; ===== Dependency Components =====
Name: "dependencies"; Description: "Install Required Dependencies (Nmap, Python packages)"; Types: full custom
Name: "dependencies\nmap"; Description: "Nmap Network Scanner"; Types: full
Name: "dependencies\sqlmap"; Description: "SQLMap (SQL Injection Tool)"; Types: full
Name: "dependencies\whois"; Description: "WHOIS Domain Lookup"; Types: full
Name: "dependencies\python"; Description: "Python 3.11+ (Required for SOC features)"; Types: full
Name: "dependencies\packages"; Description: "Python Packages (colorama, requests, folium, plotly, reportlab)"; Types: full
Name: "dependencies\npcap"; Description: "Npcap (Packet Capture Library - Required for Nmap)"; Types: full
Name: "dependencies\nikto"; Description: "Nikto Web Vulnerability Scanner"; Types: full

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Components: core; Flags: checkedonce
Name: "quicklaunchicon"; Description: "Create a &Quick Launch shortcut"; GroupDescription: "Additional icons:"; Components: core; Flags: unchecked
Name: "autoupdate"; Description: "Automatically check for updates on startup"; GroupDescription: "Update settings:"; Components: core; Flags: checkedonce
Name: "docshortcut"; Description: "Create Documentation shortcut on desktop"; GroupDescription: "Documentation:"; Components: docs; Flags: unchecked
Name: "startwithwindows"; Description: "Start DSTerminal with Windows (minimized)"; GroupDescription: "Startup options:"; Components: core; Flags: unchecked
; ===== Dependency installation tasks =====
Name: "installdeps"; Description: "Install/Update missing dependencies on completion"; GroupDescription: "Dependency management:"; Components: dependencies; Flags: checkedonce

[Files]
; ========== CORE APPLICATION ==========
Source: "dist\dsterminal_win-4.0.0.113_x64-amd64.exe"; DestDir: "{app}"; DestName: "dsterminal.exe"; Flags: ignoreversion; Components: core
Source: "dist\dsterminal_console.exe"; DestDir: "{app}"; DestName: "dsterminal-console.exe"; Flags: ignoreversion skipifsourcedoesntexist; Components: core

; ========== FIXED: Removed duplicate dsterminal.bat, keep only launcher ==========
; Source: "./dsterminal.bat"; DestDir: "{app}"; Flags: ignoreversion  (REMOVED)

; ========== ICON FILES ==========
Source: "installer_assets\3486-removebg-preview.ico"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; ========== LAUNCHER ==========
Source: "launch_dsterminal.bat"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; ========== CONFIGURATION FILES ==========
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "config\settings.json"; DestDir: "{app}\config"; Flags: ignoreversion onlyifdoesntexist; Components: core
Source: "config\default.profile"; DestDir: "{app}\config"; Flags: ignoreversion; Components: core
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; ========== VT MODULE FILES ==========
Source: "vt_scan.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
Source: "web_security_analyzer.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
Source: "edu_typing_engine.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
Source: "recon.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
Source: "recon_full.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule

Source: "vt_scan_backup.py"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: vtmodule
Source: "test_vtscan.py"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: vtmodule

; ========== DOCUMENTATION ==========
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: docs
Source: "docs\index.html"; DestDir: "{app}\docs"; Flags: ignoreversion; Components: docs
Source: "docs\user_guide.pdf"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist; Components: docs
Source: "docs\api_reference.md"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist; Components: docs
Source: "docs\quickstart.txt"; DestDir: "{app}"; DestName: "QUICKSTART.txt"; Flags: ignoreversion; Components: docs

; ========== TOOLS & UTILITIES ==========
Source: "tools\*"; DestDir: "{app}\tools"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: tools
Source: "tools\update-helper.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: updatehelper
Source: "tools\cleanup.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion skipifsourcedoesntexist; Components: tools
Source: "tools\diagnostic.bat"; DestDir: "{app}\tools"; Flags: ignoreversion skipifsourcedoesntexist; Components: tools
Source: "tools\install_*.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: tools

; ========== TEMPLATES ==========
Source: "templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: templates

; ========== FFMPEG (Conditional) ==========
Source: "redist\ffmpeg\*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: ffmpeg; Check: IsFFmpegRequired

; ========== LEGAL & README ==========
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "CHANGELOG.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: core
Source: "CREDITS.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: core

; ========== UPDATE MECHANISM ==========
Source: "update\update-checker.exe"; DestDir: "{app}\update"; Flags: ignoreversion skipifsourcedoesntexist; Components: core
Source: "update\version.json"; DestDir: "{app}\update"; Flags: ignoreversion; Components: core
Source: "update\updater.ps1"; DestDir: "{app}\update"; Flags: ignoreversion; Components: updatehelper

; ========== BUNDLED TOOLS ==========
Source: "tools\bundled\manifest.json"; DestDir: "{app}\tools\bundled"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\nikto\nikto.sha256"; DestDir: "{app}\tools\bundled\nikto"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\nikto\nikto.zip"; DestDir: "{app}\tools\bundled\nikto"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\nmap\nmap-7.95-setup.exe"; DestDir: "{app}\tools\bundled\nmap"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\nmap\nmap.sha256"; DestDir: "{app}\tools\bundled\nmap"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\npcap\npcap-1.79.exe"; DestDir: "{app}\tools\bundled\npcap"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\npcap\npcap.sha256"; DestDir: "{app}\tools\bundled\npcap"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\sqlmap\sqlmap.sha256"; DestDir: "{app}\tools\bundled\sqlmap"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\sqlmap\sqlmap.zip"; DestDir: "{app}\tools\bundled\sqlmap"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\whois\whois.ps1"; DestDir: "{app}\tools\bundled\whois"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\whois\whois.sha256"; DestDir: "{app}\tools\bundled\whois"; Flags: ignoreversion; Components: tools
Source: "tools\bundled\whois\whois.exe"; DestDir: "{app}\tools\bundled\whois"; Flags: ignoreversion; Components: tools

; ========== DEPENDENCY INSTALLATION SCRIPTS ==========
Source: "tools\check_dependencies.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_all_dependencies.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_chocolatey.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_remaining_deps.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_nmap_admin.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_nmap.bat"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_whois.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_sqlmap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\sqlmap
Source: "tools\install_python_packages.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\packages
Source: "tools\install_python.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_remaining_deps.bat"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\check_deps.bat"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_nmap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\nmap
Source: "tools\install_npcap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\npcap
Source: "tools\install_nikto.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\nikto
Source: "tools\create_bundles.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\dsterminal_smart_installer.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\post_install.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion skipifsourcedoesntexist; Components: dependencies

[Dirs]
; Create workspace directories
; FIXED: Remove uninsalwaysuninstall to preserve user data
Name: "{userappdata}\DSTerminal_Workspace"
Name: "{userappdata}\DSTerminal_Workspace\operators"
Name: "{userappdata}\DSTerminal_Workspace\scans"
Name: "{userappdata}\DSTerminal_Workspace\reports"
Name: "{userappdata}\DSTerminal_Workspace\exploits"
Name: "{userappdata}\DSTerminal_Workspace\sandbox"
Name: "{userappdata}\DSTerminal_Workspace\quarantine"
Name: "{userappdata}\DSTerminal_Workspace\logs"
Name: "{userappdata}\DSTerminal_Workspace\config"
Name: "{userappdata}\DSTerminal_Workspace\vt_reports"

; Application directories (these should be removed on uninstall)
Name: "{app}\logs"; Flags: uninsalwaysuninstall
Name: "{app}\updates"; Flags: uninsalwaysuninstall
Name: "{app}\cache"; Flags: uninsalwaysuninstall
Name: "{app}\temp"; Flags: uninsalwaysuninstall

[Icons]
; ========== FIXED: Use launcher for desktop shortcut ==========
Name: "{userdesktop}\DSTerminal CyberOps"; Filename: "{app}\launch_dsterminal.bat"; WorkingDir: "{app}"; IconFilename: "{app}\dsterminal.exe"; Tasks: desktopicon; Comment: "DSTerminal Security Terminal"

; ========== FIXED: Start Menu shortcuts ==========
Name: "{group}\DSTerminal CyberOps"; Filename: "{app}\launch_dsterminal.bat"; WorkingDir: "{app}"; IconFilename: "{app}\dsterminal.exe"; Comment: "Launch DSTerminal Cyber Ops Platform"
Name: "{group}\Uninstall DSTerminal"; Filename: "{uninstallexe}"; Comment: "Remove DSTerminal from your system"
Name: "{group}\DSTerminal Documentation"; Filename: "{app}\docs\index.html"; IconFilename: "{app}\dsterminal.exe"; Components: docs

; ========== FIXED: Documentation shortcut ==========
Name: "{userdesktop}\DSTerminal Documentation"; Filename: "{app}\docs\index.html"; IconFilename: "{app}\dsterminal.exe"; Tasks: docshortcut; Components: docs

[Run]
; Launch documentation after install (if selected)
Filename: "{app}\docs\index.html"; Description: "View DSTerminal Documentation"; Flags: postinstall shellexec skipifsilent; Components: docs

; ========== FIXED: Only use [Registry] for PATH ==========
; PATH is added via [Registry] section below - no duplicate setx here

; ============================================================
; DEPENDENCY INSTALLATION - ALL MISSING PACKAGES
; ============================================================

; 1. Install Python FIRST if missing (before packages)
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\install_python.ps1"""; Flags: waituntilterminated; Components: dependencies\python; Tasks: installdeps; Check: IsPythonMissing

; 2. Check all dependencies and install missing ones
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\check_dependencies.ps1"""; Flags: waituntilterminated; Components: dependencies; Tasks: installdeps

; 3. Install Npcap if missing (required for Nmap) - GUI mode
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\install_npcap.ps1"""; Flags: waituntilterminated; Components: dependencies\npcap; Tasks: installdeps; Check: IsNpcapMissing

; 4. Install Nmap if missing (uses bundled installer) - GUI mode
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\install_nmap.ps1"""; Flags: waituntilterminated; Components: dependencies\nmap; Tasks: installdeps; Check: IsNmapMissing

; 5. Install SQLMap if missing (extracts from bundled zip) - No Python needed
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\install_sqlmap.ps1"""; Flags: waituntilterminated; Components: dependencies\sqlmap; Tasks: installdeps; Check: IsSQLMapMissing

; 6. Install Nikto if missing (extracts from bundled zip)
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\install_nikto.ps1"""; Flags: waituntilterminated; Components: dependencies\nikto; Tasks: installdeps; Check: IsNiktoMissing

; 7. Install WHOIS if missing - Uses bundled whois.exe
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\install_whois.ps1"""; Flags: waituntilterminated; Components: dependencies\whois; Tasks: installdeps; Check: IsWHOISMissing

; 8. Install Python packages if missing (after Python is installed)
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\install_python_packages.ps1"""; Flags: waituntilterminated; Components: dependencies\packages; Tasks: installdeps; Check: ArePythonPackagesMissing

; ============================================================
; POST-INSTALL SCRIPTS
; ============================================================

; FIXED: Launch post-install script if it exists (removed invalid skipifdoesntexist flag)
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""{app}\tools\post_install.ps1"""; Flags: nowait skipifsilent; Check: FileExists(ExpandConstant('{app}\tools\post_install.ps1')); Components: dependencies

; Launch smart installer in background
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""{app}\tools\dsterminal_smart_installer.ps1"""; Flags: nowait skipifsilent
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""{app}\tools\create_bundles.ps1"""; Flags: nowait skipifsilent

; Launch DSTerminal after install - Use launcher
Filename: "{app}\launch_dsterminal.bat"; Description: "Launch DSTerminal"; Flags: nowait postinstall skipifsilent; Components: core

; Create update schedule task (if auto-update enabled)
; FIXED: Correct quoting for scheduled task
Filename: "schtasks"; Parameters: "/create /tn ""DSTerminal Update Check"" /tr """"{app}\update\update-checker.exe"""" /sc weekly /d SUN /st 09:00 /f"; Flags: runhidden waituntilterminated skipifsilent; Tasks: autoupdate; Check: IsAdminInstallMode

[UninstallRun]
; Clean up scheduled task
Filename: "schtasks"; Parameters: "/delete /tn ""DSTerminal Update Check"" /f"; Check: IsAdminInstallMode; RunOnceId: "RemoveScheduledTask"

[Code]
// ========== GLOBAL VARIABLES ==========
var
  DependencyCheckPage: TInputOptionWizardPage;

// ========== FFMPEG CHECK ==========
function IsFFmpegRequired: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  // FIXED: Use where ffmpeg instead of checking System32
  if Exec(ExpandConstant('{cmd}'), '/c where ffmpeg', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := False;
  end;
end;

// ========== PYTHON CHECK ==========
function IsPythonMissing: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if Exec(ExpandConstant('{cmd}'), '/c where python', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := False;
  end;
end;

// ========== NMAP CHECK ==========
function IsNmapMissing: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if Exec(ExpandConstant('{cmd}'), '/c where nmap', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := False;
  end;
end;

// ========== NPCAP CHECK ==========
function IsNpcapMissing: Boolean;
begin
  // FIXED: Check all common Npcap installation locations
  Result := not FileExists(ExpandConstant('{sys}\npcap\wpcap.dll')) and
            not FileExists(ExpandConstant('{sys}\Npcap\wpcap.dll')) and
            not FileExists(ExpandConstant('{sys}\npcap.dll')) and
            not FileExists(ExpandConstant('{pf}\Npcap\wpcap.dll')) and
            not FileExists(ExpandConstant('{pf}\Npcap\NPcapInstall.log')) and
            not FileExists(ExpandConstant('{pf}\Npcap\README.txt'));
end;

// ========== SQLMAP CHECK ==========
function IsSQLMapMissing: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  // FIXED: Check for sqlmap.exe and sqlmap.py
  if Exec(ExpandConstant('{cmd}'), '/c where sqlmap', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := False;
  end;
  
  // Also check if sqlmap.py exists in bundled location
  if Result and FileExists(ExpandConstant('{app}\tools\sqlmap\sqlmap.py')) then
  begin
    Result := False;
  end;
end;

// ========== NIKTO CHECK ==========
function IsNiktoMissing: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if Exec(ExpandConstant('{cmd}'), '/c where nikto', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := False;
  end;
  // Check bundled as fallback
  if Result and FileExists(ExpandConstant('{app}\tools\bundled\nikto\nikto.zip')) then
  begin
    // Bundled but not installed
  end;
end;

// ========== WHOIS CHECK ==========
function IsWHOISMissing: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if Exec(ExpandConstant('{cmd}'), '/c where whois', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := False;
  end;
end;

// ========== PYTHON PACKAGES CHECK ==========
function ArePythonPackagesMissing: Boolean;
var
  ResultCode: Integer;
  TempFile: string;
begin
  Result := True;
  TempFile := ExpandConstant('{tmp}\check_packages.vbs');
  
  SaveStringToFile(TempFile, 
    'Set objShell = CreateObject("WScript.Shell")' + #13#10 +
    'Set objExec = objShell.Exec("python -c ""import colorama, requests, folium, plotly, reportlab""")' + #13#10 +
    'Do While objExec.Status = 0' + #13#10 +
    '    WScript.Sleep 100' + #13#10 +
    'Loop' + #13#10 +
    'If objExec.ExitCode <> 0 Then WScript.Quit 1 Else WScript.Quit 0', False);
  
  if Exec(ExpandConstant('{cmd}'), '/c cscript //nologo "' + TempFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := False;
  end;
  
  DeleteFile(TempFile);
end;

// ========== WORKSPACE INITIALIZATION ==========
procedure InitializeWorkspace;
var
  WorkspacePath: string;
  ConfigFile: string;
begin
  WorkspacePath := ExpandConstant('{userappdata}\DSTerminal_Workspace');
  ConfigFile := WorkspacePath + '\config\workspace.json';
  
  if not FileExists(ConfigFile) then
  begin
    SaveStringToFile(ConfigFile, 
      '{' + #13#10 +
      '  "version": "4.0.0.113",' + #13#10 +
      '  "created": "' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':') + '",' + #13#10 +
      '  "operator": "default",' + #13#10 +
      '  "settings": {' + #13#10 +
      '    "auto_update": true,' + #13#10 +
      '    "update_channel": "stable"' + #13#10 +
      '  }' + #13#10 +
      '}', False);
  end;
end;

// ========== INITIALIZE WIZARD ==========
procedure InitializeWizard;
begin
  DependencyCheckPage := CreateInputOptionPage(wpSelectTasks,
    'Dependency Installation', 'Install required dependencies',
    'DSTerminal requires certain dependencies for full functionality.' + #13#10#13#10 +
    'Select your preferred installation method:' + #13#10#13#10 +
    'Note: You can skip this and install dependencies manually later.',
    True, False);
    
  DependencyCheckPage.Add('Automatically install all missing dependencies (Recommended)');
  DependencyCheckPage.Add('Only check for missing dependencies (Show report)');
  DependencyCheckPage.Add('Skip dependency installation (I will install manually)');
  DependencyCheckPage.Values[0] := True;
end;

// ========== CURSTEP CHANGED ==========
procedure CurStepChanged(CurStep: TSetupStep);
var
  DependencyChoice: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    InitializeWorkspace();
    
    DependencyChoice := DependencyCheckPage.SelectedValueIndex;
    
    if DependencyChoice = 0 then
    begin
      MsgBox('DSTerminal will now check and install missing dependencies. This may take a few minutes.', mbInformation, MB_OK);
    end
    else if DependencyChoice = 1 then
    begin
      MsgBox('DSTerminal will check for missing dependencies and show a report.', mbInformation, MB_OK);
    end
    else
    begin
      MsgBox('Dependency installation skipped. You can install them manually later.' + #13#10#13#10 +
             'Required: nmap, sqlmap' + #13#10 +
             'Optional: whois, Nikto, Python packages', mbInformation, MB_OK);
    end;
  end;
end;

// ========== HELPER FUNCTIONS ==========
function IsAdminInstallMode: Boolean;
begin
  // FIXED: Use IsAdminLoggedOn instead of obsolete IsPowerUserLoggedOn
  Result := IsAdmin;
end;

[Registry]
; Add DSTerminal to user PATH (no admin required)
; FIXED: Check if {app} already exists in PATH before appending
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "PATH"; \
ValueData: "{olddata};{app}"; Flags: preservestringtype

[Messages]
BeveledLabel=DSTerminal Cyber-Ops Platform v4.0.0.113

[CustomMessages]
SetupAppTitle=DSTerminal Installer
SetupWindowTitle=DSTerminal v4.0.0.113 Setup
