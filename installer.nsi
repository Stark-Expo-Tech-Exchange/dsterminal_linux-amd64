!include "MUI2.nsh"

Name "DSTerminal"
OutFile "DSTerminal_Setup.exe"
InstallDir "$PROGRAMFILES\DSTerminal"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  
  # Copy all files
  File /r "dist\*"
  File "requirements.txt"
  File "README.md"
  File "LICENSE"
  
  # Create desktop shortcut
  CreateShortCut "$DESKTOP\DSTerminal.lnk" "$INSTDIR\DSTerminal.exe"
  
  # Create start menu shortcut
  CreateDirectory "$SMPROGRAMS\DSTerminal"
  CreateShortCut "$SMPROGRAMS\DSTerminal\DSTerminal.lnk" "$INSTDIR\DSTerminal.exe"
  CreateShortCut "$SMPROGRAMS\DSTerminal\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  
  # Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  # Write registry entries
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DSTerminal" \
    "DisplayName" "DSTerminal"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DSTerminal" \
    "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DSTerminal" \
    "DisplayVersion" "2.1.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DSTerminal" \
    "Publisher" "Stark Expo Tech Exchange"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\uninstall.exe"
  Delete "$DESKTOP\DSTerminal.lnk"
  RMDir /r "$SMPROGRAMS\DSTerminal"
  RMDir /r "$INSTDIR"
  
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DSTerminal"
SectionEnd