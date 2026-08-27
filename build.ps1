# ============================================================
# DSTerminal® Console Build Orchestrator
# ============================================================
#
# IMPORTANT:
#   This script ORCHESTRATES the existing full PyInstaller spec.
#
#   It does NOT generate or replace:
#
#       dsterminal_console.spec
#
#   The existing spec remains responsible for:
#       - Flask
#       - Flask-SocketIO
#       - python-socketio
#       - python-engineio
#       - simple-websocket
#       - threading backend
#       - Shield_Core
#       - application data
#       - hidden imports
#       - runtime dependencies
#
# ============================================================

[CmdletBinding()]
param(
    [switch]$Clean,
    [switch]$BuildPy,
    [switch]$BuildInstaller,
    [switch]$BuildPortable,
    [switch]$Full,

    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

# ============================================================
# CONFIGURATION
# ============================================================

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ProjectRoot

$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PyInstallerExe = Join-Path $ProjectRoot ".venv\Scripts\pyinstaller.exe"

$MainScript = Join-Path $ProjectRoot "dsterminal.py"
$SpecFile = Join-Path $ProjectRoot "dsterminal_console.spec"

$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
$InstallerDir = Join-Path $ProjectRoot "installer_output"

$ExePath = Join-Path $DistDir "DSTerminal.exe"

$WixObj = Join-Path $ProjectRoot "DSTerminal.wixobj"
$WixSource = Join-Path $ProjectRoot "DSTerminal.wxs"
$MsiPath = Join-Path $InstallerDir "DSTerminal_Setup.msi"

# ============================================================
# COLORS
# ============================================================

$Green = "Green"
$Cyan = "Cyan"
$Yellow = "Yellow"
$Red = "Red"
$White = "White"
$DarkGray = "DarkGray"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

function Write-Section {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title
    )

    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor $Cyan
    Write-Host " $Title" -ForegroundColor $Green
    Write-Host ("=" * 60) -ForegroundColor $Cyan
    Write-Host ""
}

function Write-OK {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host "  [OK] $Message" -ForegroundColor $Green
}

function Write-Warn {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host "  [!] $Message" -ForegroundColor $Yellow
}

function Write-Fail {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host "  [ERROR] $Message" -ForegroundColor $Red
}

# ============================================================
# SAFE DIRECTORY REMOVAL
# ============================================================

function Remove-DirectorySafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [int]$Attempts = 5
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return $true
    }

    for ($i = 1; $i -le $Attempts; $i++) {

        try {

            Remove-Item `
                -LiteralPath $Path `
                -Recurse `
                -Force `
                -ErrorAction Stop

            if (-not (Test-Path -LiteralPath $Path)) {
                Write-OK "Removed $Path"
                return $true
            }
        }
        catch {

            Write-Warn "Attempt ${i}/${Attempts}: could not remove $Path"

            # Attempt to clear common read-only attributes.
            try {
                Get-ChildItem `
                    -LiteralPath $Path `
                    -Recurse `
                    -Force `
                    -ErrorAction SilentlyContinue |
                    ForEach-Object {
                        try {
                            $_.IsReadOnly = $false
                        }
                        catch {
                        }
                    }
            }
            catch {
            }
        }

        Start-Sleep -Seconds 2
    }

    return $false
}

# ============================================================
# SAFE FILE REMOVAL
# ============================================================

function Remove-FileSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [int]$Attempts = 5
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return $true
    }

    for ($i = 1; $i -le $Attempts; $i++) {

        try {

            Remove-Item `
                -LiteralPath $Path `
                -Force `
                -ErrorAction Stop

            if (-not (Test-Path -LiteralPath $Path)) {
                Write-OK "Removed $Path"
                return $true
            }
        }
        catch {

            Write-Warn "Attempt ${i}/${Attempts}: could not remove $Path"

            try {
                $item = Get-Item `
                    -LiteralPath $Path `
                    -Force `
                    -ErrorAction SilentlyContinue

                if ($null -ne $item) {
                    $item.IsReadOnly = $false
                }
            }
            catch {
            }
        }

        Start-Sleep -Seconds 2
    }

    return $false
}

# ============================================================
# STOP DSTerminal PROCESSES
# ============================================================

function Stop-DSTerminalProcesses {

    Write-Host "  Stopping running DSTerminal processes..." `
        -ForegroundColor $DarkGray

    $processes = Get-Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.ProcessName -like "DSTerminal*" -or
            $_.ProcessName -like "pyinstaller*"
        }

    if (-not $processes) {
        Write-Host `
            "  No matching processes found." `
            -ForegroundColor $DarkGray

        return
    }

    foreach ($process in $processes) {

        try {

            Stop-Process `
                -Id $process.Id `
                -Force `
                -ErrorAction Stop

            Write-Host `
                "  Stopped process: $($process.ProcessName) [$($process.Id)]" `
                -ForegroundColor $Green
        }
        catch {

            Write-Warn `
                "Could not stop $($process.ProcessName) [$($process.Id)]"
        }
    }

    Start-Sleep -Seconds 3
}

# ============================================================
# ENVIRONMENT VALIDATION
# ============================================================

function Test-Environment {

    Write-Section "ENVIRONMENT VALIDATION"

    Write-Host "  Project root:" -ForegroundColor $DarkGray
    Write-Host "    $ProjectRoot" -ForegroundColor $White

    Write-Host "  Python:" -ForegroundColor $DarkGray
    Write-Host "    $PythonExe" -ForegroundColor $White

    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    if (-not (Test-Path -LiteralPath $PythonExe)) {
        throw "Virtual environment Python was not found: $PythonExe"
    }

    Write-OK "Virtual environment Python found."

    # --------------------------------------------------------
    # Main application
    # --------------------------------------------------------

    if (-not (Test-Path -LiteralPath $MainScript)) {
        throw "Main application not found: $MainScript"
    }

    Write-OK "Found main application: dsterminal.py"

    # --------------------------------------------------------
    # Full PyInstaller spec
    # --------------------------------------------------------

    if (-not (Test-Path -LiteralPath $SpecFile)) {
        throw "Required PyInstaller spec not found: $SpecFile"
    }

    Write-OK "Found PyInstaller spec: dsterminal_console.spec"

    # --------------------------------------------------------
    # Verify Python
    # --------------------------------------------------------

    Write-Host ""
    Write-Host "  Python environment:" -ForegroundColor $DarkGray

    $pythonInfo = & $PythonExe -c `
        "import sys; print(sys.executable); print(sys.prefix); print(sys.base_prefix)"

    if ($LASTEXITCODE -ne 0) {
        throw "Unable to execute Python from the project virtual environment."
    }

    foreach ($line in $pythonInfo) {
        Write-Host "    $line" -ForegroundColor $White
    }

    # --------------------------------------------------------
    # Check that venv is actually being used
    # --------------------------------------------------------

    $venvCheck = & $PythonExe -c `
        "import sys; print('VENV_ACTIVE=' + str(sys.prefix != sys.base_prefix))"

    if ($LASTEXITCODE -eq 0) {

        if ($venvCheck -match "VENV_ACTIVE=True") {
            Write-OK "Project virtual environment is active."
        }
        else {
            Write-Warn "Python does not appear to be running inside a virtual environment."
        }
    }

    # --------------------------------------------------------
    # Verify PyInstaller
    # --------------------------------------------------------

    Write-Host ""
    Write-Host "  Checking PyInstaller..." -ForegroundColor $DarkGray

    & $PythonExe -m PyInstaller --version

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller is not working inside the project virtual environment."
    }

    Write-OK "PyInstaller is available."

    # --------------------------------------------------------
    # Verify direct PyInstaller executable
    # --------------------------------------------------------

    if (Test-Path -LiteralPath $PyInstallerExe) {
        Write-OK "venv PyInstaller executable found."
    }
    else {
        Write-Warn "venv PyInstaller executable was not found directly."
        Write-Warn "Using python -m PyInstaller instead."
    }

    # --------------------------------------------------------
    # Spec timestamp
    # --------------------------------------------------------

    $specInfo = Get-Item -LiteralPath $SpecFile

    Write-Host ""
    Write-Host "  Full spec:" -ForegroundColor $DarkGray
    Write-Host "    $($specInfo.FullName)" -ForegroundColor $White
    Write-Host "    Modified: $($specInfo.LastWriteTime)" -ForegroundColor $White
}

# ============================================================
# CLEAN
# ============================================================

function Invoke-Clean {

    Write-Section "1/5 - CLEAN BUILD ARTIFACTS"

    Stop-DSTerminalProcesses

    # --------------------------------------------------------
    # Remove build directories
    # --------------------------------------------------------

    Write-Host `
        "  Removing build artifacts..." `
        -ForegroundColor $DarkGray

    foreach ($dir in @($DistDir, $BuildDir, $InstallerDir)) {

        if (Test-Path -LiteralPath $dir) {

            $removed = Remove-DirectorySafe -Path $dir

            if (-not $removed) {

                Write-Warn `
                    "Could not completely remove: $dir"

                if ($dir -eq $DistDir -and
                    (Test-Path -LiteralPath $ExePath)) {

                    Write-Warn "DSTerminal.exe is still locked."

                    Write-Host ""
                    Write-Host `
                        "  The executable is still being used by Windows or another process." `
                        -ForegroundColor $Yellow

                    Write-Host `
                        "  Close all DSTerminal console windows and retry." `
                        -ForegroundColor $Yellow

                    Write-Host ""
                }
            }
        }
    }

    # --------------------------------------------------------
    # Remove generated WiX files
    # --------------------------------------------------------

    foreach ($file in @($WixSource, $WixObj)) {

        if (Test-Path -LiteralPath $file) {
            Remove-FileSafe -Path $file | Out-Null
        }
    }

    # --------------------------------------------------------
    # IMPORTANT:
    # NEVER DELETE THE EXISTING SPEC
    # --------------------------------------------------------

    Write-Host ""
    Write-Host `
        "  Preserving full PyInstaller specification:" `
        -ForegroundColor $DarkGray

    Write-Host `
        "    dsterminal_console.spec" `
        -ForegroundColor $Green

    # --------------------------------------------------------
    # Python cache directories
    # --------------------------------------------------------

    Write-Host ""
    Write-Host `
        "  Cleaning Python cache directories..." `
        -ForegroundColor $DarkGray

    Get-ChildItem `
        -LiteralPath $ProjectRoot `
        -Recurse `
        -Directory `
        -Filter "__pycache__" `
        -ErrorAction SilentlyContinue |
        ForEach-Object {

            try {

                Remove-Item `
                    -LiteralPath $_.FullName `
                    -Recurse `
                    -Force `
                    -ErrorAction Stop
            }
            catch {

                Write-Warn `
                    "Could not remove cache: $($_.FullName)"
            }
        }

    # --------------------------------------------------------
    # PYC files
    # --------------------------------------------------------

    Write-Host `
        "  Cleaning .pyc files..." `
        -ForegroundColor $DarkGray

    Get-ChildItem `
        -LiteralPath $ProjectRoot `
        -Recurse `
        -File `
        -Filter "*.pyc" `
        -ErrorAction SilentlyContinue |
        ForEach-Object {

            try {

                Remove-Item `
                    -LiteralPath $_.FullName `
                    -Force `
                    -ErrorAction Stop
            }
            catch {

                Write-Warn `
                    "Could not remove: $($_.FullName)"
            }
        }

    Write-Host ""
    Write-OK "Clean phase completed."
}

# ============================================================
# BUILD PYINSTALLER
# ============================================================

function Invoke-PyInstallerBuild {

    Write-Section "3/5 - BUILD CONSOLE EXECUTABLE"

    if (-not (Test-Path -LiteralPath $SpecFile)) {
        throw "Full spec file does not exist: $SpecFile"
    }

    if (-not (Test-Path -LiteralPath $MainScript)) {
        throw "Main application does not exist: $MainScript"
    }

    Write-Host `
        "  Using EXISTING FULL PyInstaller spec:" `
        -ForegroundColor $DarkGray

    Write-Host `
        "    dsterminal_console.spec" `
        -ForegroundColor $Cyan

    Write-Host ""
    Write-Host `
        "  Build configuration:" `
        -ForegroundColor $DarkGray

    Write-Host `
        "    Python:       $PythonExe" `
        -ForegroundColor $White

    Write-Host `
        "    Spec:         dsterminal_console.spec" `
        -ForegroundColor $White

    Write-Host `
        "    Console:      controlled by spec" `
        -ForegroundColor $White

    Write-Host `
        "    Socket.IO:    controlled by spec" `
        -ForegroundColor $White

    Write-Host `
        "    WebSocket:    controlled by spec" `
        -ForegroundColor $White

    Write-Host `
        "    Shield_Core:  controlled by spec" `
        -ForegroundColor $White

    Write-Host ""
    Write-Host `
        "  Running PyInstaller..." `
        -ForegroundColor $Cyan

    Write-Host ""

    & $PythonExe -m PyInstaller `
        --clean `
        --noconfirm `
        $SpecFile

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE."
    }

    if (-not (Test-Path -LiteralPath $ExePath)) {
        throw `
            "PyInstaller reported success but DSTerminal.exe was not created at $ExePath."
    }

    $exe = Get-Item -LiteralPath $ExePath
    $sizeMB = [math]::Round($exe.Length / 1MB, 2)

    Write-Host ""
    Write-OK "Executable built successfully."

    Write-Host `
        "  Output: $ExePath" `
        -ForegroundColor $Cyan

    Write-Host `
        "  Size:   $sizeMB MB" `
        -ForegroundColor $Cyan

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    Write-Host ""
    Write-Host `
        "  Executable metadata:" `
        -ForegroundColor $DarkGray

    try {

        $versionInfo = $exe.VersionInfo

        Write-Host `
            "    File version:    $($versionInfo.FileVersion)" `
            -ForegroundColor $White

        Write-Host `
            "    Product version: $($versionInfo.ProductVersion)" `
            -ForegroundColor $White

        Write-Host `
            "    Description:     $($versionInfo.FileDescription)" `
            -ForegroundColor $White
    }
    catch {

        Write-Warn "Could not read executable version metadata."
    }
}

# ============================================================
# TEST EXECUTABLE
# ============================================================

function Test-BuiltExecutable {

    Write-Section "EXECUTABLE VALIDATION"

    if (-not (Test-Path -LiteralPath $ExePath)) {
        throw "DSTerminal.exe does not exist."
    }

    Write-Host "  Executable:" -ForegroundColor $DarkGray
    Write-Host "    $ExePath" -ForegroundColor $White

    Write-Host ""
    Write-Host `
        "  Running executable smoke test..." `
        -ForegroundColor $DarkGray

    try {

        $output = & $ExePath --version 2>&1

        $exitCode = $LASTEXITCODE

        if ($output) {

            $output |
                ForEach-Object {
                    Write-Host `
                        "    $_" `
                        -ForegroundColor $White
                }
        }

        if ($exitCode -eq 0) {

            Write-OK `
                "Executable launched and returned successfully."
        }
        else {

            Write-Warn `
                "Executable launched but returned exit code $exitCode."

            Write-Warn `
                "This can occur if DSTerminal does not implement --version."
        }
    }
    catch {

        Write-Warn `
            "Executable smoke test encountered an error."

        Write-Warn `
            "This does not necessarily mean the executable is broken."

        Write-Warn `
            "DSTerminal may not implement a --version command."
    }
}

# ============================================================
# FIND WIX
# ============================================================

function Find-Wix {

    $candidates = @(
        "C:\Program Files (x86)\WiX Toolset v3.14\bin",
        "C:\Program Files\WiX Toolset v3.14\bin",
        "C:\Program Files (x86)\WiX Toolset v3.11\bin",
        "C:\Program Files\WiX Toolset v3.11\bin",
        "C:\ProgramData\chocolatey\lib\wixtoolset\tools\bin",
        "C:\ProgramData\chocolatey\lib\wixtoolset\tools"
    )

    foreach ($path in $candidates) {

        $candle = Join-Path $path "candle.exe"
        $light = Join-Path $path "light.exe"

        if (
            (Test-Path -LiteralPath $candle) -and
            (Test-Path -LiteralPath $light)
        ) {
            return $path
        }
    }

    # Also check PATH.
    $candleCommand = Get-Command candle.exe `
        -ErrorAction SilentlyContinue

    $lightCommand = Get-Command light.exe `
        -ErrorAction SilentlyContinue

    if ($candleCommand -and $lightCommand) {
        return (Split-Path -Parent $candleCommand.Source)
    }

    return $null
}

# ============================================================
# BUILD MSI
# ============================================================

function Invoke-InstallerBuild {

    Write-Section "4/5 - BUILD MSI INSTALLER"

    if (-not (Test-Path -LiteralPath $ExePath)) {
        throw `
            "DSTerminal.exe is missing. Build the executable first."
    }

    $wixPath = Find-Wix

    if (-not $wixPath) {

        Write-Warn "WiX Toolset was not found."

        Write-Host ""
        Write-Host `
            "  MSI creation skipped." `
            -ForegroundColor $Yellow

        Write-Host `
            "  Install WiX Toolset if MSI generation is required." `
            -ForegroundColor $Yellow

        return
    }

    Write-OK "Found WiX Toolset."

    Write-Host `
        "    $wixPath" `
        -ForegroundColor $Cyan

    New-Item `
        -ItemType Directory `
        -Path $InstallerDir `
        -Force |
        Out-Null

    # --------------------------------------------------------
    # WiX XML
    # --------------------------------------------------------

    $wixXml = @"
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">

    <Product
        Id="*"
        Name="DSTerminal"
        Language="1033"
        Version="$Version"
        Manufacturer="Stark Expo Tech Exchange LTD"
        UpgradeCode="8A9C8B1E-2F3D-4A5B-8C7D-9E0F1A2B3C4D">

        <Package
            InstallerVersion="200"
            Compressed="yes"
            InstallScope="perMachine"
            Platform="x64"
            Description="DSTerminal Defensive Security Terminal"/>

        <MajorUpgrade
            DowngradeErrorMessage="A newer version of DSTerminal is already installed."
            AllowSameVersionUpgrades="yes"/>

        <MediaTemplate EmbedCab="yes"/>

        <Feature
            Id="ProductFeature"
            Title="DSTerminal"
            Level="1">

            <ComponentRef Id="MainComponent"/>

        </Feature>

        <Directory Id="TARGETDIR" Name="SourceDir">

            <Directory Id="ProgramFiles64Folder">

                <Directory
                    Id="INSTALLFOLDER"
                    Name="DSTerminal"/>

            </Directory>

            <Directory Id="ProgramMenuFolder">

                <Directory
                    Id="ApplicationProgramsFolder"
                    Name="DSTerminal"/>

            </Directory>

            <Directory Id="DesktopFolder"/>

        </Directory>

        <DirectoryRef Id="INSTALLFOLDER">

            <Component
                Id="MainComponent"
                Guid="*"
                Win64="yes">

                <File
                    Id="DSTerminalExe"
                    Name="DSTerminal.exe"
                    Source="dist\DSTerminal.exe"
                    KeyPath="yes"
                    Checksum="yes">

                    <Shortcut
                        Id="StartMenuShortcut"
                        Directory="ApplicationProgramsFolder"
                        Name="DSTerminal"
                        WorkingDirectory="INSTALLFOLDER"/>

                    <Shortcut
                        Id="DesktopShortcut"
                        Directory="DesktopFolder"
                        Name="DSTerminal"
                        WorkingDirectory="INSTALLFOLDER"/>

                </File>

            </Component>

        </DirectoryRef>

    </Product>

</Wix>
"@

    $wixXml |
        Out-File `
            -LiteralPath $WixSource `
            -Encoding UTF8 `
            -Force

    Write-OK "Created DSTerminal.wxs"

    # --------------------------------------------------------
    # Candle
    # --------------------------------------------------------

    Write-Host ""
    Write-Host `
        "  Compiling WiX source..." `
        -ForegroundColor $Yellow

    & (Join-Path $wixPath "candle.exe") `
        $WixSource `
        -out $WixObj

    if ($LASTEXITCODE -ne 0) {
        throw "WiX candle.exe failed."
    }

    Write-OK "WiX compilation successful."

    # --------------------------------------------------------
    # Light
    # --------------------------------------------------------

    Write-Host ""
    Write-Host `
        "  Linking MSI..." `
        -ForegroundColor $Yellow

    & (Join-Path $wixPath "light.exe") `
        $WixObj `
        -out $MsiPath

    if ($LASTEXITCODE -ne 0) {
        throw "WiX light.exe failed."
    }

    if (-not (Test-Path -LiteralPath $MsiPath)) {
        throw `
            "WiX reported success but MSI was not created."
    }

    $msi = Get-Item -LiteralPath $MsiPath
    $sizeMB = [math]::Round($msi.Length / 1MB, 2)

    Write-OK "MSI created."

    Write-Host `
        "  Output: $MsiPath" `
        -ForegroundColor $Cyan

    Write-Host `
        "  Size:   $sizeMB MB" `
        -ForegroundColor $Cyan
}

# ============================================================
# PORTABLE BUILD
# ============================================================

function Invoke-PortableBuild {

    Write-Section "5/5 - CREATE PORTABLE VERSION"

    if (-not (Test-Path -LiteralPath $ExePath)) {
        throw "DSTerminal.exe is missing."
    }

    $portableDir = Join-Path `
        $ProjectRoot `
        "DSTerminal_Portable_v$Version"

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

    if (Test-Path -LiteralPath $portableDir) {

        $removed = Remove-DirectorySafe `
            -Path $portableDir

        if (-not $removed) {
            throw `
                "Unable to remove existing portable directory: $portableDir"
        }
    }

    New-Item `
        -ItemType Directory `
        -Path $portableDir `
        -Force |
        Out-Null

    Write-OK "Created portable directory."

    # --------------------------------------------------------
    # EXE
    # --------------------------------------------------------

    Copy-Item `
        -LiteralPath $ExePath `
        -Destination (Join-Path $portableDir "DSTerminal.exe") `
        -Force

    Write-OK "Copied DSTerminal.exe"

    # --------------------------------------------------------
    # Launcher
    # --------------------------------------------------------

    $batContent = @"
@echo off
title DSTerminal Console v$Version

echo.
echo ============================================================
echo              DSTERMINAL CONSOLE v$Version
echo ============================================================
echo.
echo Starting DSTerminal...
echo.
echo Type 'help' for available commands.
echo.
echo ============================================================
echo.

DSTerminal.exe

echo.
echo DSTerminal has exited.
pause
"@

    $batPath = Join-Path `
        $portableDir `
        "launch_dsterminal.bat"

    $batContent |
        Out-File `
            -LiteralPath $batPath `
            -Encoding ASCII `
            -Force

    Write-OK "Created launch_dsterminal.bat"

    # --------------------------------------------------------
    # README
    # --------------------------------------------------------

    $readme = @"
DSTERMINAL® CONSOLE
Version $Version
========================================

Defensive Security Terminal

PORTABLE BUILD
--------------

This is the portable Windows console build of DSTerminal.

HOW TO START
------------

1. Double-click:

   launch_dsterminal.bat

OR:

2. Run:

   DSTerminal.exe

REQUIREMENTS
------------

- Windows 10 / Windows 11
- x64 processor
- 2 GB RAM recommended
- Network access for network-dependent features

FEATURES
--------

- Defensive security operations
- System security monitoring
- Network monitoring
- Threat detection
- Shield_Core analysis
- Flask-SocketIO realtime services
- Console-based interface

NOTES
-----

This package is self-contained.

Python does not need to be installed separately.

For full DSTerminal functionality, some operations may require
appropriate Windows permissions.

VERSION
-------

$Version

"@

    $readmePath = Join-Path `
        $portableDir `
        "README.txt"

    $readme |
        Out-File `
            -LiteralPath $readmePath `
            -Encoding UTF8 `
            -Force

    Write-OK "Created README.txt"

    # --------------------------------------------------------
    # ZIP
    # --------------------------------------------------------

    $zipName = "DSTerminal_Console_v${Version}_${timestamp}.zip"
    $zipPath = Join-Path $ProjectRoot $zipName

    if (Test-Path -LiteralPath $zipPath) {

        Remove-FileSafe `
            -Path $zipPath |
            Out-Null
    }

    Compress-Archive `
        -Path (Join-Path $portableDir "*") `
        -DestinationPath $zipPath `
        -Force

    if (-not (Test-Path -LiteralPath $zipPath)) {
        throw "Portable ZIP was not created."
    }

    $zip = Get-Item -LiteralPath $zipPath
    $sizeMB = [math]::Round($zip.Length / 1MB, 2)

    Write-OK "Portable ZIP created."

    Write-Host `
        "  Output: $zipPath" `
        -ForegroundColor $Cyan

    Write-Host `
        "  Size:   $sizeMB MB" `
        -ForegroundColor $Cyan
}

# ============================================================
# SUMMARY
# ============================================================

function Show-Summary {

    Write-Section "BUILD COMPLETE"

    Write-Host `
        "DSTerminal Console Build Outputs:" `
        -ForegroundColor $Cyan

    Write-Host ""

    if (Test-Path -LiteralPath $ExePath) {

        $exe = Get-Item -LiteralPath $ExePath
        $sizeMB = [math]::Round($exe.Length / 1MB, 2)

        Write-Host `
            "  [OK] Executable:" `
            -ForegroundColor $Green

        Write-Host `
            "       $ExePath" `
            -ForegroundColor $White

        Write-Host `
            "       $sizeMB MB" `
            -ForegroundColor $DarkGray
    }

    if (Test-Path -LiteralPath $MsiPath) {

        $msi = Get-Item -LiteralPath $MsiPath
        $sizeMB = [math]::Round($msi.Length / 1MB, 2)

        Write-Host ""
        Write-Host `
            "  [OK] MSI Installer:" `
            -ForegroundColor $Green

        Write-Host `
            "       $MsiPath" `
            -ForegroundColor $White

        Write-Host `
            "       $sizeMB MB" `
            -ForegroundColor $DarkGray
    }

    $zipFiles = Get-ChildItem `
        -LiteralPath $ProjectRoot `
        -Filter "DSTerminal_Console_*.zip" `
        -File `
        -ErrorAction SilentlyContinue

    if ($zipFiles) {

        Write-Host ""

        foreach ($zip in $zipFiles) {

            $sizeMB = [math]::Round($zip.Length / 1MB, 2)

            Write-Host `
                "  [OK] Portable ZIP:" `
                -ForegroundColor $Green

            Write-Host `
                "       $($zip.FullName)" `
                -ForegroundColor $White

            Write-Host `
                "       $sizeMB MB" `
                -ForegroundColor $DarkGray
        }
    }

    Write-Host ""
    Write-Host "Quick Start:" -ForegroundColor $Cyan
    Write-Host "  .\dist\DSTerminal.exe" -ForegroundColor $White

    Write-Host ""
    Write-Host "Full Build:" -ForegroundColor $Cyan
    Write-Host `
        "  .\build.ps1 -Full -Version $Version" `
        -ForegroundColor $White

    Write-Host ""
}

# ============================================================
# MAIN
# ============================================================

try {

    Write-Host ""
    Write-Host `
        "============================================================" `
        -ForegroundColor $Cyan

    Write-Host `
        "       DSTERMINAL® CONSOLE BUILD ORCHESTRATOR" `
        -ForegroundColor $Green

    Write-Host `
        "                    v$Version" `
        -ForegroundColor $Green

    Write-Host `
        "============================================================" `
        -ForegroundColor $Cyan

    Write-Host ""

    # --------------------------------------------------------
    # Default behavior
    # --------------------------------------------------------

    if (
        -not $Clean -and
        -not $BuildPy -and
        -not $BuildInstaller -and
        -not $BuildPortable -and
        -not $Full
    ) {

        Write-Host "Usage:" -ForegroundColor $Yellow
        Write-Host ""

        Write-Host `
            "  .\build.ps1 -Full" `
            -ForegroundColor $White

        Write-Host `
            "  .\build.ps1 -BuildPy" `
            -ForegroundColor $White

        Write-Host `
            "  .\build.ps1 -BuildInstaller" `
            -ForegroundColor $White

        Write-Host `
            "  .\build.ps1 -BuildPortable" `
            -ForegroundColor $White

        Write-Host `
            "  .\build.ps1 -Clean" `
            -ForegroundColor $White

        Write-Host ""
        Write-Host "Examples:" -ForegroundColor $Yellow
        Write-Host ""

        Write-Host `
            "  .\build.ps1 -Full -Version 5.0.0" `
            -ForegroundColor $White

        Write-Host `
            "  .\build.ps1 -Clean -BuildPy" `
            -ForegroundColor $White

        Write-Host ""

        exit 0
    }

    # --------------------------------------------------------
    # Full build
    # --------------------------------------------------------

    if ($Full) {

        $Clean = $true
        $BuildPy = $true
        $BuildInstaller = $true
        $BuildPortable = $true
    }

    # --------------------------------------------------------
    # Environment
    # --------------------------------------------------------

    Test-Environment

    # --------------------------------------------------------
    # Clean
    # --------------------------------------------------------

    if ($Clean) {
        Invoke-Clean
    }

    # --------------------------------------------------------
    # Build executable
    # --------------------------------------------------------

    if ($BuildPy) {

        Write-Section "2/5 - PREPARE BUILD"

        Write-OK `
            "Using existing dsterminal_console.spec."

        Write-Host ""

        Write-Host `
            "  The build orchestrator will NOT generate or replace the spec." `
            -ForegroundColor $DarkGray

        Write-Host `
            "  Full Flask/Socket.IO/threading configuration remains intact." `
            -ForegroundColor $DarkGray

        Write-Host `
            "  Shield_Core and hidden imports remain controlled by the spec." `
            -ForegroundColor $DarkGray

        Invoke-PyInstallerBuild

        Test-BuiltExecutable
    }

    # --------------------------------------------------------
    # Installer
    # --------------------------------------------------------

    if ($BuildInstaller) {
        Invoke-InstallerBuild
    }

    # --------------------------------------------------------
    # Portable
    # --------------------------------------------------------

    if ($BuildPortable) {
        Invoke-PortableBuild
    }

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    Show-Summary
}
catch {

    Write-Host ""
    Write-Host `
        "============================================================" `
        -ForegroundColor $Red

    Write-Host `
        "                 BUILD FAILED" `
        -ForegroundColor $Red

    Write-Host `
        "============================================================" `
        -ForegroundColor $Red

    Write-Host ""

    Write-Host `
        "Error:" `
        -ForegroundColor $Red

    Write-Host `
        $_.Exception.Message `
        -ForegroundColor $White

    Write-Host ""

    Write-Host `
        "Location:" `
        -ForegroundColor $DarkGray

    Write-Host `
        $ProjectRoot `
        -ForegroundColor $White

    Write-Host ""

    Write-Host `
        "Recommended action:" `
        -ForegroundColor $Yellow

    if (Test-Path -LiteralPath $ExePath) {

        Write-Host `
            "  DSTerminal.exe may still be locked by Windows." `
            -ForegroundColor $Yellow

        Write-Host `
            "  Close all running DSTerminal windows and retry." `
            -ForegroundColor $Yellow
    }
    else {

        Write-Host `
            "  Review the error above and rerun the failed build stage." `
            -ForegroundColor $Yellow
    }

    Write-Host ""

    exit 1
}