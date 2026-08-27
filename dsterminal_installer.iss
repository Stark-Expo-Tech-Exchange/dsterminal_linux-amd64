; DSTerminal Installer Script - With Full Dependency Management
; Version: 4.0.0.113
; Date: 2026
; FEATURES: License validation + Dependency checking + Auto-install + Documentation

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

; Installation Paths
DefaultDirName={pf}\DSTerminal
DefaultGroupName=DSTerminal
LicenseFile=license.txt

; ========== OUTPUT FOLDER ==========
OutputDir=output
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
DisableReadyPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full"; Description: "Full Installation (Recommended)"
Name: "compact"; Description: "Compact Installation"
Name: "custom"; Description: "Custom Installation"; Flags: iscustom

[Components]
Name: "core"; Description: "Core DSTerminal Files"; Types: full compact custom; Flags: fixed
Name: "docs"; Description: "Documentation & Help Files"; Types: full custom; Flags: fixed
Name: "tools"; Description: "Additional Security Tools"; Types: full custom
Name: "templates"; Description: "Report Templates"; Types: full custom
Name: "updatehelper"; Description: "Auto-Update Helper Script"; Types: full custom

; ========== BUNDLED DEPENDENCIES ==========
Name: "bundles"; Description: "Bundled Security Tools & Dependencies"; Types: full custom
Name: "bundles\nmap"; Description: "Nmap Network Scanner"; Types: full
Name: "bundles\npcap"; Description: "Npcap Packet Capture Library"; Types: full
Name: "bundles\sqlmap"; Description: "SQLMap (SQL Injection Tool)"; Types: full
Name: "bundles\nikto"; Description: "Nikto Web Vulnerability Scanner"; Types: full
Name: "bundles\whois"; Description: "WHOIS Domain Lookup Tool"; Types: full

; ========== DEPENDENCY INSTALLATION COMPONENTS ==========
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
Name: "docshortcut"; Description: "Create Cyber-Ops Documentation shortcut on desktop"; GroupDescription: "Documentation:"; Components: docs; Flags: checkedonce
Name: "startwithwindows"; Description: "Start DSTerminal with Windows (minimized)"; GroupDescription: "Startup options:"; Components: core; Flags: unchecked
Name: "installdeps"; Description: "Install/Update missing dependencies on completion"; GroupDescription: "Dependency management:"; Components: dependencies; Flags: checkedonce

; ========== MAIN FILES SECTION ==========
[Files]
; ========== CORE APPLICATION - FROM auto-py-to-exe ==========
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; ========== ICON FILES ==========
Source: "installer_assets\3486-removebg-preview.ico"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "static\3486-removebg-preview.ico"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "3486-removebg-preview.ico"; DestDir: "{app}\static"; Flags: ignoreversion

; ========== LOGO / ICON FILES ==========
; Copy logo to multiple locations for redundancy
Source: "static\3486-removebg-preview.ico"; DestDir: "{app}\static"; Flags: ignoreversion; Components: core
Source: "static\3486-removebg-preview.ico"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "static\3486-removebg-preview.ico"; DestDir: "{userappdata}\DSTerminal_Workspace\static"; Flags: ignoreversion; Components: core

; Also copy to the workspace static folder during installation
Source: "static\3486-removebg-preview.ico"; DestDir: "{userappdata}\DSTerminal_Workspace\static"; Flags: ignoreversion; Components: core

; ========== LAUNCHER ==========
Source: "launch_dsterminal.bat"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; ========== CONFIGURATION FILES ==========
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "config\settings.json"; DestDir: "{app}\config"; Flags: ignoreversion onlyifdoesntexist; Components: core
Source: "config\default.profile"; DestDir: "{app}\config"; Flags: ignoreversion; Components: core
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core

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
; Main documentation files
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: docs
Source: "docs\index.html"; DestDir: "{app}\docs"; Flags: ignoreversion; Components: docs
Source: "docs\user_guide.pdf"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist; Components: docs
Source: "docs\api_reference.md"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist; Components: docs
Source: "docs\quickstart.txt"; DestDir: "{app}"; DestName: "QUICKSTART.txt"; Flags: ignoreversion; Components: docs

; Additional documentation files
Source: "docs\index.html"; DestDir: "{app}\docs"; DestName: "Cyber-Ops_Documentation.html"; Flags: ignoreversion; Components: docs
Source: "docs\Dsterminal_Manifest_v4.0.0.113.pdf"; DestDir: "{app}\docs"; DestName: "Dsterminal_Manifest_v4.0.0.113.pdf"; Flags: ignoreversion skipifsourcedoesntexist; Components: docs
Source: "docs\DSTerminal_User_Guide_v4.0.0.113.pdf"; DestDir: "{app}\docs"; DestName: "DSTerminal_User_Guide_v3.1.113.pdf"; Flags: ignoreversion skipifsourcedoesntexist; Components: docs

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

; Documentation directory
Name: "{app}\docs"; Flags: uninsalwaysuninstall

[Icons]
; Desktop shortcut for DSTerminal - FIXED
Name: "{userdesktop}\DSTerminal CyberOps"; \
    Filename: "{app}\dsterminal.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\dsterminal.exe"; \
    IconIndex: 0; \
    Tasks: desktopicon; \
    Comment: "DSTerminal Security Terminal"

; ========== DOCUMENTATION DESKTOP SHORTCUT ==========
; Cyber-Ops Documentation shortcut on Desktop
Name: "{userdesktop}\Cyber-Ops Documentation"; \
    Filename: "{app}\docs\Cyber-Ops_Documentation.html"; \
    IconFilename: "{app}\dsterminal.exe"; \
    Tasks: docshortcut; \
    Comment: "DSTerminal Cyber-Ops Documentation"; \
    Components: docs

; Alternative documentation shortcut (if PDF exists)
Name: "{userdesktop}\Cyber-Ops Documentation (PDF)"; \
    Filename: "{app}\docs\Dsterminal_Manifest_v4.0.0.113.pdf"; \
    IconFilename: "{app}\dsterminal.exe"; \
    Tasks: docshortcut; \
    Comment: "DSTerminal Cyber-Ops Documentation (PDF)"; \
    Components: docs

; ========== START MENU SHORTCUTS ==========
Name: "{group}\DSTerminal CyberOps"; \
    Filename: "{app}\dsterminal.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\dsterminal.exe"; \
    IconIndex: 0; \
    Comment: "Launch DSTerminal Cyber Ops Platform"

Name: "{group}\Uninstall DSTerminal"; \
    Filename: "{uninstallexe}"; \
    Comment: "Remove DSTerminal from your system"

; Start Menu documentation shortcuts
Name: "{group}\Cyber-Ops Documentation"; \
    Filename: "{app}\docs\Cyber-Ops_Documentation.html"; \
    IconFilename: "{app}\dsterminal.exe"; \
    Components: docs

Name: "{group}\DSTerminal Quick Start"; \
    Filename: "{app}\QUICKSTART.txt"; \
    Components: docs

[Run]
; Launch documentation after install
Filename: "{app}\docs\Cyber-Ops_Documentation.html"; \
    Description: "View Cyber-Ops Documentation"; \
    Flags: postinstall shellexec skipifsilent; \
    Components: docs

; Launch DSTerminal after install - SIMPLIFIED
Filename: "{app}\dsterminal.exe"; \
    Description: "Launch DSTerminal"; \
    Flags: nowait postinstall skipifsilent; \
    Components: core

; Alternative: Launch using Windows start command
Filename: "{cmd}"; \
    Parameters: "/c start ""DSTerminal"" /D ""{app}"" ""{app}\dsterminal.exe"""; \
    Description: "Launch DSTerminal (alternate)"; \
    Flags: postinstall nowait skipifsilent hidewizard; \
    Components: core
    
; ========== DEPENDENCY INSTALLATION DURING SETUP ==========
; Run dependency installation during installation
Filename: "powershell.exe"; \
    Parameters: "-ExecutionPolicy Bypass -File '{app}\tools\install_all_dependencies.ps1'"; \
    Components: dependencies; \
    Flags: runhidden; \
    StatusMsg: "Checking and installing required dependencies... (This may take a few minutes)"

; Install bundled dependencies
Filename: "powershell.exe"; \
    Parameters: "-ExecutionPolicy Bypass -File '{app}\tools\install_bundled_deps.ps1'"; \
    Components: bundles; \
    Flags: runhidden; \
    StatusMsg: "Installing bundled security tools... (GUI wizards may open)"

; Launch dependency installation batch file
Filename: "{app}\tools\install_dependencies.bat"; \
    Description: "Install Nmap, Npcap and other security tools"; \
    Components: bundles; \
    Flags: postinstall nowait shellexec; \
    StatusMsg: "Launching dependency installers..."; \
    Tasks: installdeps

[Registry]
; Add DSTerminal to user PATH
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "PATH"; \
ValueData: "{olddata};{app}"; Flags: preservestringtype

; Register DSTerminal as a security tool
Root: HKCU; Subkey: "Software\DSTerminal"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\DSTerminal"; ValueType: string; ValueName: "Version"; ValueData: "4.0.0.113"
Root: HKCU; Subkey: "Software\DSTerminal"; ValueType: string; ValueName: "LicenseKey"; ValueData: "{code:GetLicenseKey}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\DSTerminal"; ValueType: string; ValueName: "DocPath"; ValueData: "{app}\docs"; Flags: uninsdeletekey

; Register documentation path
Root: HKCU; Subkey: "Software\DSTerminal\Documentation"; ValueType: string; ValueName: "DocsPath"; ValueData: "{app}\docs\Cyber-Ops_Documentation.html"
Root: HKCU; Subkey: "Software\DSTerminal\Documentation"; ValueType: string; ValueName: "QuickStartPath"; ValueData: "{app}\QUICKSTART.txt"

; ========== ADD APPLICATION REGISTRATION FOR TASKBAR ICON ==========
; Register AppUserModelID for Windows taskbar
Root: HKCU; Subkey: "Software\Classes\AppUserModelId\StarkExpoTechExchange.DSTerminal"; ValueType: string; ValueName: "DisplayName"; ValueData: "DSTerminal CyberOps"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AppUserModelId\StarkExpoTechExchange.DSTerminal"; ValueType: string; ValueName: "IconUri"; ValueData: "{app}\dsterminal.exe"; Flags: uninsdeletekey

; Add to Windows Application Compatibility
Root: HKCU; Subkey: "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"; ValueType: string; ValueName: "{app}\dsterminal.exe"; ValueData: "~ DISABLEAAM"; Flags: uninsdeletekey

; ============================================================
; LICENSE KEY VALIDATION WITH 3-TRIAL LIMIT AND ROLLBACK
; ============================================================

[Code]
var
  LicensePage: TInputQueryWizardPage;
  LicenseKey: string;
  AttemptCount: Integer;
  InstallAborted: Boolean;

// ============================================================
// GET LICENSE KEY FOR REGISTRY
// ============================================================
function GetLicenseKey(Param: string): string;
begin
  Result := LicenseKey;
end;

// ============================================================
// GET CURRENT DATE TIME STRING
// ============================================================
function MyFormatDateTime: string;
begin
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
    'The license key format is: XXXXXX-XXXXXCXXXX-XXXXXCCCXXX-XXXXXHHHSXXX' + #13#10#13#10 +
    'Example: XXXXXX-XXXXXCXXXX-XXXXXCCCXXX-XXXXXHHHSXXX' + #13#10#13#10 +
    'You have 3 attempts to enter a valid license key.' + #13#10#13#10 +
    'If you don''t have a license key, please visit:' + #13#10 +
    'https://starkexpotechexchange.mw/license');
  
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
               'Installation aborted.', mbError, MB_OK);
        Result := False;
        InstallAborted := True;
        WizardForm.Close;
        Exit;
      end;
      
      MsgBox('Invalid license key format.' + #13#10#13#10 +
             'Please use the format: XXXXXX-XXXXXCXXXX-XXXXXCCCXXX-XXXXXHHHSXXX' + #13#10 +
             'Example: XXXXXX-XXXXXCXXXX-XXXXXCCCXXX-XXXXXHHHSXXX' + #13#10#13#10 +
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
               'Installation aborted.', mbError, MB_OK);
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
        CopyFile(ExpandConstant('{tmp}\license.key'), ExpandConstant('{app}\license.key'), False);
    end;
  end;
end;

// ============================================================
// HANDLE INSTALLATION ABORT WITH ROLLBACK
// ============================================================
procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);
begin
  if InstallAborted then
  begin
    Confirm := False;
    Cancel := True;
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

function IsSqlmapMissing: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if Exec(ExpandConstant('{cmd}'), '/c where sqlmap', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := False;
  end;
end;

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
end;

[Messages]
BeveledLabel=DSTerminal Cyber-Ops Platform v4.0.0.113

[CustomMessages]
SetupAppTitle=DSTerminal Installer
SetupWindowTitle=DSTerminal v4.0.0.113 Setup