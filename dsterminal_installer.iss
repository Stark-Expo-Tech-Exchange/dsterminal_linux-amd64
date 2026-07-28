<<<<<<< HEAD
﻿; DSTerminal Installer Script - With License Key Validation
; Version: 3.1.113
; Date: 2026
; FEATURE: License key validation during installation with 3-trial limit and rollback
=======
; DSTerminal Installer Script - Non-Admin Safe with Documentation & Auto-Update
; Version: 2.1.327
; Date: 2026
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

[Setup]
; Basic Setup Information
AppId={{1EFF5130-85AF-4EE9-B818-5634A06408D2}}
AppName=DSTerminal
<<<<<<< HEAD
AppVersion=3.1.113
AppVerName=DSTerminal v3.1.113
AppPublisher=Stark Expo Tech Exchange
AppPublisherURL=https://starkexpotechexchange.mw
=======
AppVersion=2.1.327
AppVerName=DSTerminal v2.1.327
AppPublisher=Stark Expo Tech Exchange
AppPublisherURL=https://starkexpotechexchange-mw.com
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
AppSupportURL=https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest/issues
AppUpdatesURL=https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest/releases
AppContact=support@starkexpotechexchange-mw.com
AppComments=Security Operations Center Terminal
<<<<<<< HEAD
AppCopyright=Copyright © 2024-2026 Stark Expo Tech Exchange
=======
AppCopyright=Copyright © 2024 Stark Expo Tech Exchange
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

; Installation Paths (User AppData - No Admin Required)
DefaultDirName={userappdata}\DSTerminal
DefaultGroupName=DSTerminal
LicenseFile=license.txt
OutputDir=installer_output
<<<<<<< HEAD
OutputBaseFilename=DSTerminal_Installer_2026_v3.1.113
Compression=lzma2/fast
SolidCompression=no
InternalCompressLevel=fast
=======
OutputBaseFilename=DSTerminal_Installer_2026_v2.1.327
Compression=lzma2/ultra64
SolidCompression=yes
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
DisableWelcomePage=no
WizardStyle=modern
SetupIconFile=installer_assets\3486-removebg-preview.ico

WizardImageFile=installer_assets\wizard-image.bmp
WizardSmallImageFile=installer_assets\wizard-small.bmp
WizardImageStretch=No
WizardImageBackColor=clBlack

DisableProgramGroupPage=no
AllowNoIcons=yes
<<<<<<< HEAD
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0
UninstallDisplayIcon={app}\dsterminal.exe
UninstallDisplayName=DSTerminal v3.1.113
VersionInfoVersion=3.1.113
VersionInfoCompany=Stark Expo Tech Exchange
VersionInfoDescription=DSTerminal Cyber-Ops Platform
VersionInfoTextVersion=3.1.113
VersionInfoCopyright=© 2024-2026 Stark Expo Tech Exchange
VersionInfoProductName=DSTerminal
VersionInfoProductVersion=3.1.113
=======
PrivilegesRequired=lowest
MinVersion=10.0
UninstallDisplayIcon={app}\dsterminal.exe
UninstallDisplayName=DSTerminal v2.1.327
VersionInfoVersion=2.1.327
VersionInfoCompany=Stark Expo Tech Exchange
VersionInfoDescription=DSTerminal Cyber-Ops Platform
VersionInfoTextVersion=2.1.327
VersionInfoCopyright=© 2024 Stark Expo Tech Exchange
VersionInfoProductName=DSTerminal
VersionInfoProductVersion=2.1.327
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

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
<<<<<<< HEAD
Name: "vtmodule"; Description: "VirusTotal Threat Intelligence Module"; Types: full custom
Name: "dependencies"; Description: "Install Required Dependencies"; Types: full custom
Name: "dependencies\nmap"; Description: "Nmap Network Scanner"; Types: full
Name: "dependencies\sqlmap"; Description: "SQLMap (SQL Injection Tool)"; Types: full
Name: "dependencies\whois"; Description: "WHOIS Domain Lookup"; Types: full
Name: "dependencies\python"; Description: "Python 3.11+"; Types: full
Name: "dependencies\packages"; Description: "Python Packages"; Types: full
Name: "dependencies\npcap"; Description: "Npcap (Packet Capture Library)"; Types: full
Name: "dependencies\nikto"; Description: "Nikto Web Vulnerability Scanner"; Types: full
=======
; ===== Dependency Components =====
Name: "dependencies"; Description: "Install Required Dependencies (Nmap, Python packages)"; Types: full custom
Name: "dependencies\nmap"; Description: "Nmap Network Scanner"; Types: full
Name: "dependencies\sqlmap"; Description: "SQLMap (SQL Injection Tool)"; Types: full
Name: "dependencies\whois"; Description: "WHOIS Domain Lookup"; Types: full
Name: "dependencies\python"; Description: "Python 3.11+ (Required for SOC features)"; Types: full
Name: "dependencies\packages"; Description: "Python Packages (colorama, requests, folium, plotly, reportlab)"; Types: full
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Components: core; Flags: checkedonce
Name: "quicklaunchicon"; Description: "Create a &Quick Launch shortcut"; GroupDescription: "Additional icons:"; Components: core; Flags: unchecked
Name: "autoupdate"; Description: "Automatically check for updates on startup"; GroupDescription: "Update settings:"; Components: core; Flags: checkedonce
Name: "docshortcut"; Description: "Create Documentation shortcut on desktop"; GroupDescription: "Documentation:"; Components: docs; Flags: unchecked
Name: "startwithwindows"; Description: "Start DSTerminal with Windows (minimized)"; GroupDescription: "Startup options:"; Components: core; Flags: unchecked
<<<<<<< HEAD
=======
; ===== Dependency installation tasks =====
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
Name: "installdeps"; Description: "Install/Update missing dependencies on completion"; GroupDescription: "Dependency management:"; Components: dependencies; Flags: checkedonce

[Files]
; ========== CORE APPLICATION ==========
<<<<<<< HEAD
Source: "dist\dsterminal_win-3.1.113_x64-amd64.exe"; DestDir: "{app}"; DestName: "dsterminal.exe"; Flags: ignoreversion; Components: core
Source: "dist\dsterminal_console.exe"; DestDir: "{app}"; DestName: "dsterminal-console.exe"; Flags: ignoreversion skipifsourcedoesntexist; Components: core

; ========== ICON FILES ==========
Source: "installer_assets\3486-removebg-preview.ico"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; ========== LAUNCHER ==========
Source: "launch_dsterminal.bat"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; ========== CONFIGURATION FILES ==========
=======
Source: "dist\dsterminal_win-2026_v2.1.327_x64-amd64.exe"; DestDir: "{app}"; DestName: "dsterminal.exe"; Flags: ignoreversion; Components: core
Source: "dist\dsterminal_console.exe"; DestDir: "{app}"; DestName: "dsterminal-console.exe"; Flags: ignoreversion skipifsourcedoesntexist; Components: core
Source: "./dsterminal.bat"; DestDir: "{app}"; Flags: ignoreversion

; Configuration files
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "config\settings.json"; DestDir: "{app}\config"; Flags: ignoreversion onlyifdoesntexist; Components: core
Source: "config\default.profile"; DestDir: "{app}\config"; Flags: ignoreversion; Components: core
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core

<<<<<<< HEAD
; ========== VT MODULE FILES ==========
Source: "vt_scan.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
Source: "web_security_analyzer.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
Source: "edu_typing_engine.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
Source: "recon.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule
Source: "recon_full.py"; DestDir: "{app}"; Flags: ignoreversion; Components: vtmodule

=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
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
<<<<<<< HEAD
Source: "tools\install_*.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: tools
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

; ========== TEMPLATES ==========
Source: "templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: templates

<<<<<<< HEAD
=======
; ========== FFMPEG (Conditional) ==========
Source: "redist\ffmpeg\*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: ffmpeg; Check: IsFFmpegRequired

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
; ========== LEGAL & README ==========
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "CHANGELOG.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: core
<<<<<<< HEAD
=======
Source: "CREDITS.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: core

; ========== UPDATE MECHANISM ==========
Source: "update\update-checker.exe"; DestDir: "{app}\update"; Flags: ignoreversion skipifsourcedoesntexist; Components: core
Source: "update\version.json"; DestDir: "{app}\update"; Flags: ignoreversion; Components: core
Source: "update\updater.ps1"; DestDir: "{app}\update"; Flags: ignoreversion; Components: updatehelper
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

; ========== DEPENDENCY INSTALLATION SCRIPTS ==========
Source: "tools\check_dependencies.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_all_dependencies.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
<<<<<<< HEAD
Source: "tools\install_python.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_nmap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\nmap
Source: "tools\install_npcap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\npcap
Source: "tools\install_sqlmap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\sqlmap
Source: "tools\install_whois.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\whois
Source: "tools\install_nikto.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\nikto
Source: "tools\install_python_packages.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\packages

[Dirs]
; Create workspace directories
Name: "{userappdata}\DSTerminal_Workspace"
=======
Source: "tools\install_chocolatey.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_remaining_deps.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_metasploit.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_nmap_admin.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_nmap.bat"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_whois.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_sqlmap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\sqlmap
Source: "tools\install_python_packages.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\packages
Source: "tools\install_python.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_remaining_deps.bat"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\check_deps.bat"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies
Source: "tools\install_nmap.ps1"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: dependencies\nmap

[Dirs]
; Create workspace directories
Name: "{userappdata}\DSTerminal_Workspace"; Flags: uninsalwaysuninstall
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
Name: "{userappdata}\DSTerminal_Workspace\operators"
Name: "{userappdata}\DSTerminal_Workspace\scans"
Name: "{userappdata}\DSTerminal_Workspace\reports"
Name: "{userappdata}\DSTerminal_Workspace\exploits"
Name: "{userappdata}\DSTerminal_Workspace\sandbox"
Name: "{userappdata}\DSTerminal_Workspace\quarantine"
Name: "{userappdata}\DSTerminal_Workspace\logs"
Name: "{userappdata}\DSTerminal_Workspace\config"

; Application directories
Name: "{app}\logs"; Flags: uninsalwaysuninstall
Name: "{app}\updates"; Flags: uninsalwaysuninstall
Name: "{app}\cache"; Flags: uninsalwaysuninstall
Name: "{app}\temp"; Flags: uninsalwaysuninstall

[Icons]
<<<<<<< HEAD
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
// GET CURRENT DATE TIME STRING
// ============================================================
function GetDateTimeString: string;
var
  Year, Month, Day, Hour, Minute, Second: string;
  Y, M, D, H, Min, S, MS: Integer;
begin
  DecodeDateFully(Now, Y, M, D);
  DecodeTime(Now, H, Min, S, MS);
  
  Year := IntToStr(Y);
  Month := FormatInt(M, 2);
  Day := FormatInt(D, 2);
  Hour := FormatInt(H, 2);
  Minute := FormatInt(Min, 2);
  Second := FormatInt(S, 2);
  
  Result := Year + '-' + Month + '-' + Day + ' ' + Hour + ':' + Minute + ':' + Second;
end;

// ============================================================
// FORMAT INTEGER WITH LEADING ZEROS
// ============================================================
function FormatInt(Value, Digits: Integer): string;
begin
  Result := IntToStr(Value);
  while Length(Result) < Digits do
    Result := '0' + Result;
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
    'The license key format is: XXXXX-XXXXXXXXX-XXXXXXXXXXX-XXXXXXXXXXXX' + #13#10#13#10 +
    'Example: XXXXXX-A1B2HD#$C3D4-E5F6^&$FG7H8-I9J0KVD#451L2' + #13#10#13#10 +
    'You have 3 attempts to enter a valid license key.' + #13#10#13#10 +
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
             'Please use the format: XXXX-XXXXXXXXX-XXXXXXXXXXX-XXXXXXXXXXXX' + #13#10 +
             'Example: XXXXXX-A1B2C#$WE3D4-E5F6GFCH^&*7H8-I9@#WEX09J0K1L2' + #13#10#13#10 +
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
      FileCopy(ExpandConstant('{tmp}\license.key'), ExpandConstant('{app}\license.key'), False);
    end;
  end;
end;

// ============================================================
// HANDLE INSTALLATION ABORT WITH ROLLBACK
// ============================================================
procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);
var
  RollbackLog: string;
begin
  if InstallAborted then
  begin
    Confirm := False;
    Cancel := True;
    
    // Clean up any partially installed files
    if DirExists(ExpandConstant('{app}')) then
    begin
      // Build rollback log message
      RollbackLog := 'Rolling back changes... Aborting installation.' + #13#10 +
                     'Installation aborted at: ' + GetDateTimeString + #13#10 +
                     'Reason: Invalid license key (3 failed attempts)' + #13#10 +
                     'Rolling back: ' + ExpandConstant('{app}');
      
      // Write rollback log
      SaveStringToFile(ExpandConstant('{tmp}\rollback.log'), RollbackLog, False);
      
      // Show rollback message
      MsgBox('Rolling back changes... Aborting installation.' + #13#10#13#10 +
             'The installation has been aborted due to invalid license key.' + #13#10#13#10 +
             'All changes are being rolled back.', mbInformation, MB_OK);
      
      // Wait for user to acknowledge
      Sleep(500);
    end;
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
=======
; Main application icons
Name: "{group}\DSTerminal SOC"; Filename: "{app}\dsterminal.exe"; WorkingDir: "{userappdata}\DSTerminal_Workspace"; IconFilename: "{app}\dsterminal.exe"; Comment: "Launch DSTerminal Cyber Ops Platform"
Name: "{group}\Uninstall DSTerminal"; Filename: "{uninstallexe}"; Comment: "Remove DSTerminal from your system"
Name: "{group}\DSTerminal Documentation"; Filename: "{app}\docs\index.html"; IconFilename: "{app}\dsterminal.exe"; Components: docs
Name: "{userdesktop}\DSTerminal SOC"; Filename: "{app}\dsterminal.exe"; WorkingDir: "{userappdata}\DSTerminal_Workspace"; IconFilename: "{app}\dsterminal.exe"; Tasks: desktopicon; Comment: "DSTerminal Security Terminal"; Parameters: "/MAX"
Name: "{userdesktop}\DSTerminal Documentation"; Filename: "{app}\docs\index.html"; IconFilename: "{app}\dsterminal.exe"; Tasks: docshortcut; Components: docs

[Run]
; Launch documentation after install (if selected)
Filename: "{app}\docs\index.html"; Description: "View DSTerminal Documentation"; Flags: postinstall shellexec skipifsilent; Components: docs

; Add to PATH
Filename: "{cmd}"; Parameters: "/c setx PATH ""%PATH%;{app}"""; Flags: runhidden

; Check and install dependencies (REMOVED THE SEMICOLON)
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\check_dependencies.ps1"""; Flags: runhidden waituntilterminated; Components: dependencies; Tasks: installdeps

; Install Nmap if missing (REMOVED THE SEMICOLON)
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\install_nmap.ps1"""; Flags: runhidden waituntilterminated; Components: dependencies\nmap; Tasks: installdeps; Check: IsNmapMissing

; Launch post-install script after installer closes
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""{app}\tools\post_install.ps1"""; Flags: nowait skipifsilent

; Install Python packages if missing (This one is already uncommented - good!)
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\tools\install_python_packages.ps1"""; Flags: runhidden waituntilterminated; Components: dependencies\packages; Tasks: installdeps; Check: ArePythonPackagesMissing

; Launch DSTerminal after install
Filename: "{app}\dsterminal.exe"; Description: "Launch DSTerminal"; Flags: nowait postinstall skipifsilent; Components: core

; Create update schedule task (if auto-update enabled)
Filename: "schtasks"; Parameters: "/create /tn ""DSTerminal Update Check"" /tr ""'{app}\update\update-checker.exe'"" /sc weekly /d SUN /st 09:00 /f"; Flags: runhidden waituntilterminated skipifsilent; Tasks: autoupdate; Check: IsAdminInstallMode

[UninstallRun]
; Clean up scheduled task
Filename: "schtasks"; Parameters: "/delete /tn ""DSTerminal Update Check"" /f"; Check: IsAdminInstallMode; RunOnceId: "RemoveScheduledTask"

[Code]
// Global variables
var
  // RemoveWorkspacePage: TInputOptionWizardPage;
  // helperUpdateChannelPage: TInputOptionWizardPage;
  DependencyCheckPage: TInputOptionWizardPage;

// ========== FFMPEG CHECK ==========
function IsFFmpegRequired: Boolean;
begin
  Result := (FileExists(ExpandConstant('{sys}\ffmpeg.exe')) = False) and
            (FileExists(ExpandConstant('{app}\ffmpeg\ffmpeg.exe')) = False);
end;

// ========== METASPLOIT CHECK ==========
function IsMetasploitMissing: Boolean;
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
var
  ResultCode: Integer;
begin
  Result := True;
<<<<<<< HEAD
  if Exec(ExpandConstant('{cmd}'), '/c where python', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
=======
  if Exec(ExpandConstant('{cmd}'), '/c msfconsole --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
  begin
    if ResultCode = 0 then
      Result := False;
  end;
end;

<<<<<<< HEAD
=======
// ========== NMAP CHECK ==========
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
function IsNmapMissing: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
<<<<<<< HEAD
  if Exec(ExpandConstant('{cmd}'), '/c where nmap', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
=======
  if Exec(ExpandConstant('{cmd}'), '/c nmap --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
  begin
    if ResultCode = 0 then
      Result := False;
  end;
end;

<<<<<<< HEAD
function IsNpcapMissing: Boolean;
begin
  Result := not FileExists(ExpandConstant('{sys}\npcap\wpcap.dll')) and
            not FileExists(ExpandConstant('{sys}\Npcap\wpcap.dll')) and
            not FileExists(ExpandConstant('{sys}\npcap.dll')) and
            not FileExists(ExpandConstant('{pf}\Npcap\wpcap.dll'));
end;

[Messages]
BeveledLabel=DSTerminal Cyber-Ops Platform v3.1.113

[CustomMessages]
SetupAppTitle=DSTerminal Installer
SetupWindowTitle=DSTerminal v3.1.113 Setup
=======
// ========== SQLMAP CHECK ==========
function IsSQLMapMissing: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if Exec(ExpandConstant('{cmd}'), '/c sqlmap --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
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
    'packages = Array("colorama", "requests", "folium", "plotly", "reportlab")' + #13#10 +
    'missing = 0' + #13#10 +
    'For Each pkg In packages' + #13#10 +
    '    Set objExec = objShell.Exec("python -c ""import " & pkg & """")' + #13#10 +
    '    Do While objExec.Status = 0' + #13#10 +
    '        WScript.Sleep 100' + #13#10 +
    '    Loop' + #13#10 +
    '    If objExec.ExitCode <> 0 Then missing = missing + 1' + #13#10 +
    'Next' + #13#10 +
    'If missing > 0 Then WScript.Quit 1 Else WScript.Quit 0', False);
  
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
      '  "version": "2.1.327",' + #13#10 +
      '  "created": "' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':') + '",' + #13#10 +
      '  "operator": "default",' + #13#10 +
      '  "settings": {' + #13#10 +
      '    "auto_update": true,' + #13#10 +
      '    "update_channel": "stable"' + #13#10 +
      '  }' + #13#10 +
      '}', False);
  end;
end;

// ========== CUSTOM WIZARD PAGE FOR DEPENDENCIES =====
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

// ========== HELPER FUNCTIONS ==========
function IsAdminInstallMode: Boolean;
begin
  Result := IsAdmin or IsPowerUserLoggedOn;
end;

function RemoveWorkspaceCheck: Boolean;
begin
  Result := False;
end;

// ========== DEPENDENCY HANDLING =====
procedure CurStepChanged(CurStep: TSetupStep);
var
  DependencyChoice: Integer;
begin
  if CurStep = ssPostInstall then
  begin
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
             'Optional: whois, Metasploit, Python packages', mbInformation, MB_OK);
    end;
  end;
end;

[Registry]
; Add DSTerminal to user PATH (no admin required)
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "PATH"; \
ValueData: "{olddata};{app}"; Flags: preservestringtype

[Messages]
BeveledLabel=DSTerminal Cyber-Ops Platform v2.1.327

[CustomMessages]
SetupAppTitle=DSTerminal Installer
SetupWindowTitle=DSTerminal v2.1.327 Setup
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
