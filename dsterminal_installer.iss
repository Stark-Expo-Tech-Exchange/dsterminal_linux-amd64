; DSTerminal Installer Script - With License Key Validation
; Version: 4.0.0.113
; Date: 2026
; FEATURE: License key validation during installation with 3-trial limit and rollback

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
AppCopyright=Copyright © 2024-2026 Stark Expo Tech Exchange

; Installation Paths (User AppData - No Admin Required)
DefaultDirName={pf}\DSTerminal
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
VersionInfoCopyright=© 2024-2026 Stark Expo Tech Exchange
VersionInfoProductName=DSTerminal
VersionInfoProductVersion=4.0.0.113

; Create uninstaller in registry
CreateUninstallRegKey=yes
UpdateUninstallLogAppName=yes

; ensure proper permissions
DirExistsWarning=no
DisableDirPage=no

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
Name: "vtmodule"; Description: "VirusTotal Threat Intelligence Module"; Types: full custom

Name: "bundles"; Description: "Bundled Security Tools & Dependencies"; Types: full custom
Name: "bundles\nmap"; Description: "Nmap Network Scanner"; Types: full
Name: "bundles\npcap"; Description: "Npcap Packet Capture Library"; Types: full
Name: "bundles\sqlmap"; Description: "SQLMap (SQL Injection Tool)"; Types: full
Name: "bundles\nikto"; Description: "Nikto Web Vulnerability Scanner"; Types: full
Name: "bundles\whois"; Description: "WHOIS Domain Lookup Tool"; Types: full

Name: "dependencies"; Description: "Install Required Dependencies"; Types: full custom
Name: "dependencies\nmap"; Description: "Nmap Network Scanner"; Types: full
Name: "dependencies\sqlmap"; Description: "SQLMap (SQL Injection Tool)"; Types: full
Name: "dependencies\whois"; Description: "WHOIS Domain Lookup"; Types: full
Name: "dependencies\python"; Description: "Python 3.11+"; Types: full
Name: "dependencies\packages"; Description: "Python Packages"; Types: full
Name: "dependencies\npcap"; Description: "Npcap (Packet Capture Library)"; Types: full
Name: "dependencies\nikto"; Description: "Nikto Web Vulnerability Scanner"; Types: full

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Components: core; Flags: checkedonce
Name: "quicklaunchicon"; Description: "Create a &Quick Launch shortcut"; GroupDescription: "Additional icons:"; Components: core; Flags: unchecked
Name: "autoupdate"; Description: "Automatically check for updates on startup"; GroupDescription: "Update settings:"; Components: core; Flags: checkedonce
Name: "docshortcut"; Description: "Create Documentation shortcut on desktop"; GroupDescription: "Documentation:"; Components: docs; Flags: unchecked
Name: "startwithwindows"; Description: "Start DSTerminal with Windows (minimized)"; GroupDescription: "Startup options:"; Components: core; Flags: unchecked
Name: "installdeps"; Description: "Install/Update missing dependencies on completion"; GroupDescription: "Dependency management:"; Components: dependencies; Flags: checkedonce

[Files]
; ========== CORE APPLICATION ==========
Source: "dist\dsterminal_win-4.0.0.113_x64-amd64.exe"; DestDir: "{app}"; DestName: "dsterminal.exe"; Flags: ignoreversion; Components: core
Source: "dist\dsterminal_console.exe"; DestDir: "{app}"; DestName: "dsterminal-console.exe"; Flags: ignoreversion skipifsourcedoesntexist; Components: core

; ========== ICON FILES ==========
Source: "installer_assets\3486-removebg-preview.ico"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "static\3486-removebg-preview.ico"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "3486-removebg-preview.ico"; DestDir: "{app}\static"; Flags: ignoreversion

; ========== LAUNCHER ==========
Source: "launch_dsterminal.bat"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; ========== CONFIGURATION FILES ==========
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "config\settings.json"; DestDir: "{app}\config"; Flags: ignoreversion onlyifdoesntexist; Components: core
Source: "config\default.profile"; DestDir: "{app}\config"; Flags: ignoreversion; Components: core
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; ========== VT MODULE FILES ==========
;Source: "vt_scan.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
;Source: "web_security_analyzer.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
;Source: "edu_typing_engine.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
;Source: "recon.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
;Source: "recon_full.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule

;Source: "soc_automated_lab.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
;Source: "update.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
;Source: "dsterminal_complete.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule

;Source: "dsterminal_dashboard.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
;Source: "sqlmap_advanced.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
;Source: "soc_enhanced_modules.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule

; ========== BUNDLED PACKAGES ==========
; Nmap
Source: "bundled\nmap\*"; DestDir: "{app}\bundled\nmap"; Flags: ignoreversion recursesubdirs; Components: bundles\nmap

; Npcap
Source: "bundled\npcap\*"; DestDir: "{app}\bundled\npcap"; Flags: ignoreversion recursesubdirs; Components: bundles\npcap

; SQLMap
Source: "bundled\sqlmap\*"; DestDir: "{app}\bundled\sqlmap"; Flags: ignoreversion recursesubdirs; Components: bundles\sqlmap

; Nikto
Source: "bundled\nikto\*"; DestDir: "{app}\bundled\nikto"; Flags: ignoreversion recursesubdirs; Components: bundles\nikto

; Whois
Source: "bundled\whois\*"; DestDir: "{app}\bundled\whois"; Flags: ignoreversion recursesubdirs; Components: bundles\whois

; Bundle manifest
Source: "bundled\manifest.json"; DestDir: "{app}\bundled"; Flags: ignoreversion; Components: bundles

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

; ========== LEGAL & README ==========
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "CHANGELOG.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: core

; ========== DEPENDENCY INSTALLATION SCRIPTS ==========
Source: "tools\check_dependencies.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_all_dependencies.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_python.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_nmap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\nmap
Source: "tools\install_npcap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\npcap
Source: "tools\install_sqlmap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\sqlmap
Source: "tools\install_whois.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\whois
Source: "tools\install_nikto.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\nikto
Source: "tools\install_python_packages.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\packages

[Dirs]
; Create workspace directories in AppData (not in Program Files)
Name: "{userappdata}\DSTerminal_Workspace"
Name: "{userappdata}\DSTerminal_Workspace\operators"
Name: "{userappdata}\DSTerminal_Workspace\scans"
Name: "{userappdata}\DSTerminal_Workspace\reports"
Name: "{userappdata}\DSTerminal_Workspace\exploits"
Name: "{userappdata}\DSTerminal_Workspace\sandbox"
Name: "{userappdata}\DSTerminal_Workspace\quarantine"
Name: "{userappdata}\DSTerminal_Workspace\logs"
Name: "{userappdata}\DSTerminal_Workspace\config"

Name: "{userappdata}\DSTerminal\workspace"
Name: "{userappdata}\DSTerminal\workspace\operators"
Name: "{userappdata}\DSTerminal\workspace\scans"
Name: "{userappdata}\DSTerminal\workspace\reports"
Name: "{userappdata}\DSTerminal\workspace\exploits"
Name: "{userappdata}\DSTerminal\workspace\sandbox"
Name: "{userappdata}\DSTerminal\workspace\quarantine"
Name: "{userappdata}\DSTerminal\workspace\logs"
Name: "{userappdata}\DSTerminal\workspace\config"
Name: "{userappdata}\DSTerminal\workspace\bundled"

; Application directories in Program Files
Name: "{app}\logs"; Flags: uninsalwaysuninstall
Name: "{app}\updates"; Flags: uninsalwaysuninstall
Name: "{app}\cache"; Flags: uninsalwaysuninstall
Name: "{app}\temp"; Flags: uninsalwaysuninstall
Name: "{app}\config"; Flags: uninsalwaysuninstall
Name: "{app}\bundled"; Flags: uninsalwaysuninstall

[Icons]
; Desktop shortcut
Name: "{userdesktop}\DSTerminal CyberOps"; Filename: "{app}\launch_dsterminal.bat"; WorkingDir: "{app}"; IconFilename: "{app}\dsterminal.exe"; Tasks: desktopicon; Comment: "DSTerminal Security Terminal"

; Start Menu shortcuts
Name: "{group}\DSTerminal CyberOps"; Filename: "{app}\launch_dsterminal.bat"; WorkingDir: "{app}"; IconFilename: "{app}\dsterminal.exe"; Comment: "Launch DSTerminal Cyber Ops Platform"
Name: "{group}\Uninstall DSTerminal"; Filename: "{uninstallexe}"; Comment: "Remove DSTerminal from your system"
Name: "{group}\DSTerminal Documentation"; Filename: "{app}\docs\index.html"; IconFilename: "{app}\dsterminal.exe"; Components: docs

[Run]
; Launch documentation after install
Filename: "{app}\docs\index.html"; Description: "View DSTerminal Documentation"; Flags: postinstall shellexec skipifsilent; Components: docs

; Launch DSTerminal after install
Filename: "{app}\launch_dsterminal.bat"; Description: "Launch DSTerminal"; Flags: nowait postinstall skipifsilent; Components: core

; Run during installation
Filename: "powershell.exe"; \
    Parameters: "-ExecutionPolicy Bypass -File '{app}\tools\install_bundled_deps.ps1'"; \
    Components: bundles; \
    Flags: runhidden; \
    StatusMsg: "Installing dependencies... (GUI wizards will open)"
    
; Launch dependency installation batch file
;Filename: "{app}\tools\install_dependencies.bat"; \
;   Description: "Install Nmap, Npcap and other security tools"; \
;   Components: bundles; \
;  Flags: postinstall nowait shellexec; \
; StatusMsg: "Launching dependency installers..."; \
;Tasks: installdeps

[Registry]
; Add DSTerminal to user PATH
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "PATH"; \
ValueData: "{olddata};{app}"; Flags: preservestringtype
[Code]
// ============================================================
// LICENSE KEY VALIDATION WITH 3-TRIAL LIMIT AND ROLLBACK
// ============================================================

var
  LicensePage: TInputQueryWizardPage;
  LicenseKey: string;
  AttemptCount: Integer;
  InstallAborted: Boolean;

// ============================================================
// GET CURRENT DATE TIME STRING (Uses Inno Setup Native Function)
// ============================================================
function MyFormatDateTime: string;
begin
  // Use Inno Setup's native built-in function to format the date/time.
  // (Custom function name changed so it doesn't conflict with Inno's internal one)
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':');
end;

// ============================================================
// VALIDATE LICENSE KEY FORMAT
// ============================================================
function IsValidLicenseKey(Key: string): Boolean;
var
  CleanKey: string;
  DashPos1, DashPos2: Integer;
  Part1, Part2, Part3: string;
  i: Integer;
begin
  Result := False;
  
  // Remove spaces
  CleanKey := Key;
  while Pos(' ', CleanKey) > 0 do
    Delete(CleanKey, Pos(' ', CleanKey), 1);
  
  CleanKey := UpperCase(CleanKey);
  
  // Check if key starts with "STARK-"
  if Pos('STARK-', CleanKey) <> 1 then
  begin
    Result := False;
    Exit;
  end;
  
  // Remove "STARK-" prefix
  Delete(CleanKey, 1, 6);
  
  // Find first dash
  DashPos1 := Pos('-', CleanKey);
  if DashPos1 = 0 then
  begin
    Result := False;
    Exit;
  end;
  
  // Get first part
  Part1 := Copy(CleanKey, 1, DashPos1 - 1);
  Delete(CleanKey, 1, DashPos1);
  
  // Find second dash
  DashPos2 := Pos('-', CleanKey);
  if DashPos2 = 0 then
  begin
    Result := False;
    Exit;
  end;
  
  // Get second part
  Part2 := Copy(CleanKey, 1, DashPos2 - 1);
  Delete(CleanKey, 1, DashPos2);
  
  // Remaining is third part
  Part3 := CleanKey;
  
  // Check each part is 8 characters
  if (Length(Part1) <> 8) or (Length(Part2) <> 8) or (Length(Part3) <> 8) then
  begin
    Result := False;
    Exit;
  end;
  
  // Check each part contains only uppercase letters and numbers
  for i := 1 to 8 do
  begin
    if not ( (Part1[i] >= 'A') and (Part1[i] <= 'Z') ) and
       not ( (Part1[i] >= '0') and (Part1[i] <= '9') ) then
    begin
      Result := False;
      Exit;
    end;
    
    if not ( (Part2[i] >= 'A') and (Part2[i] <= 'Z') ) and
       not ( (Part2[i] >= '0') and (Part2[i] <= '9') ) then
    begin
      Result := False;
      Exit;
    end;
    
    if not ( (Part3[i] >= 'A') and (Part3[i] <= 'Z') ) and
       not ( (Part3[i] >= '0') and (Part3[i] <= '9') ) then
    begin
      Result := False;
      Exit;
    end;
  end;
  
  Result := True;
end;

// ============================================================
// ACTIVATE LICENSE KEY (SIMULATED)
// ============================================================
function ActivateLicenseKey(Key: string): Boolean;
begin
  // In a real implementation, this would call an activation server
  // For now, we accept any key that passes the format check
  Result := True;
end;

// ============================================================
// LICENSE KEY INPUT PAGE
// ============================================================
procedure InitializeWizard;
begin
  AttemptCount := 0;
  InstallAborted := False;
  
  // Create license key input page
  LicensePage := CreateInputQueryPage(wpWelcome,
    'DSTerminal License Validation',
    'Enter your DSTerminal license key to activate and continue installation',
    'Please enter your DSTerminal license key from the official website.' + #13#10#13#10 +
    'The license key format is: XXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX' + #13#10#13#10 +
    'Example: XXXXXX-ACX1B2C3D4-E5FXX6G7H8-I9JXXX0K1L2' + #13#10#13#10 +
    'You have 3 attempts to enter a valid license key, otherwise the installation will terminate naturally.' + #13#10#13#10 +
    'If you don''t have a license key, please visit:' + #13#10 +
    'https://starkexpotechexchange.mw/license for licensing');
  
  LicensePage.Add('License Key:', False);
  LicensePage.Values[0] := '';
end;

// ============================================================
// VALIDATE LICENSE BEFORE INSTALLATION WITH 3-TRIAL LIMIT
// ============================================================
function NextButtonClick(CurPageID: Integer): Boolean;
var
  Key: string;
begin
  Result := True;
  
  if CurPageID = LicensePage.ID then
  begin
    Key := LicensePage.Values[0];
    Key := Trim(Key);
    Key := UpperCase(Key);
    
    // Remove any spaces
    while Pos(' ', Key) > 0 do
      Delete(Key, Pos(' ', Key), 1);
    
    if Key = '' then
    begin
      MsgBox('Please enter your DSTerminal license key to Activate and Continue installation.', mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Validate format
    if not IsValidLicenseKey(Key) then
    begin
      AttemptCount := AttemptCount + 1;
      
      // Check if max attempts reached
      if AttemptCount >= 3 then
      begin
        MsgBox('You have exceeded the maximum number of license validation attempts (3).' + #13#10#13#10 +
               'Rolling back changes... Aborting installation.', mbError, MB_OK);
        Result := False;
        InstallAborted := True;
        WizardForm.Close;
        Exit;
      end;
      
      MsgBox('Invalid license key format.' + #13#10#13#10 +
             'Please use the format: XXXXXX-XXXXXXXCCXX-XXXXXBB87XXX-XXXXXXXX' + #13#10 +
             'Example: XXXXXX-ACX1B2C3D4-E5FXX6G7H8-I9JXXX0K1L2' + #13#10#13#10 +
             'Attempts remaining: ' + IntToStr(3 - AttemptCount), mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Activate license key
    if not ActivateLicenseKey(Key) then
    begin
      AttemptCount := AttemptCount + 1;
      
      if AttemptCount >= 3 then
      begin
        MsgBox('You have exceeded the maximum number of license validation attempts (3).' + #13#10#13#10 +
               'Rolling back changes... Aborting installation.', mbError, MB_OK);
        Result := False;
        InstallAborted := True;
        WizardForm.Close;
        Exit;
      end;
      
      MsgBox('License key activation failed. Please check your license key and try again.' + #13#10#13#10 +
             'Attempts remaining: ' + IntToStr(3 - AttemptCount), mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Store the license key
    LicenseKey := Key;
    
    // Save license key to file for later use
    SaveStringToFile(ExpandConstant('{tmp}\license.key'), Key, False);
  end;
end;

// ============================================================
// COPY LICENSE KEY TO INSTALLED LOCATION
// ============================================================
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Save the license key to the installation directory
    if FileExists(ExpandConstant('{tmp}\license.key')) then
    begin
        CopyFile(ExpandConstant('{tmp}\license.key'), ExpandConstant('{app}\license.key'), False);    end;
  end;
end;

// ============================================================
// HANDLE INSTALLATION ABORT WITH ROLLBACK
// ============================================================
procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);
begin
  if InstallAborted then
  begin
    // Prevent the "Are you sure?" popup
    Confirm := False;
    // Tell Inno Setup to cancel the installer naturally
    Cancel := True;
    
    // Wait a moment so the user sees the last message
    Sleep(500);
  end;
end;

// ============================================================
// SKIP LICENSE PAGE IN SILENT MODE
// ============================================================
function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  if (PageID = LicensePage.ID) and (WizardSilent) then
    Result := True;
end;

// ============================================================
// DEPENDENCY CHECK FUNCTIONS
// ============================================================

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

function IsNpcapMissing: Boolean;
begin
  Result := not FileExists(ExpandConstant('{sys}\npcap\wpcap.dll')) and
            not FileExists(ExpandConstant('{sys}\Npcap\wpcap.dll')) and
            not FileExists(ExpandConstant('{sys}\npcap.dll')) and
            not FileExists(ExpandConstant('{pf}\Npcap\wpcap.dll'));
end;

[Messages]
BeveledLabel=DSTerminal Cyber-Ops Platform v4.0.0.113

[CustomMessages]
SetupAppTitle=DSTerminal Installer
SetupWindowTitle=DSTerminal v4.0.0.113 Setup