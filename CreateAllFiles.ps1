# CreateAllFiles.ps1 - Fixed version
Write-Host "Creating all required files for DSTerminal installer..." -ForegroundColor Cyan

# Create directories
$dirs = @(
    "tools",
    "docs",
    "templates",
    "config",
    "installer_assets",
    "redist\ffmpeg"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Write-Host "  ✓ Created directory: $dir" -ForegroundColor Green
}

# Create update-helper.ps1 in tools directory
$updateHelper = @'
# DSTerminal Update Helper Script
param(
    [switch]$Check,
    [switch]$Download,
    [switch]$Install,
    [string]$Version
)

$ErrorActionPreference = "Stop"
$repo = "Stark-Expo-Tech-Exchange/DSTerminal_releases_latest"
$apiUrl = "https://api.github.com/repos/$repo/releases/latest"
$versionFile = "$env:APPDATA\DSTerminal_Workspace\version.txt"

function Write-Color {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Get-CurrentVersion {
    if (Test-Path $versionFile) {
        return (Get-Content $versionFile -Raw).Trim()
    }
    return "2.0.59"
}

function Get-LatestVersion {
    try {
        $release = Invoke-RestMethod -Uri $apiUrl -Headers @{ "User-Agent" = "DSTerminal-Updater" }
        return @{
            Version = $release.tag_name -replace "v", ""
            URL = $release.html_url
            Assets = $release.assets
            Notes = $release.body
        }
    }
    catch {
        Write-Color "Failed to check for updates: $_" -Color Red
        return $null
    }
}

function Compare-Versions {
    param([string]$v1, [string]$v2)
    try {
        return ([version]$v1 -lt [version]$v2)
    }
    catch {
        return $false
    }
}

function Download-Update {
    param([string]$Version)
    
    $release = Get-LatestVersion
    if (-not $release) { return $false }
    
    $asset = $release.Assets | Where-Object { $_.name -like "*Setup*.exe" } | Select-Object -First 1
    if (-not $asset) {
        Write-Color "No installer found in latest release" -Color Red
        return $false
    }
    
    $downloadUrl = $asset.browser_download_url
    $outputFile = "$env:TEMP\DSTerminal_Update_$Version.exe"
    
    Write-Color "Downloading version $Version..." -Color Yellow
    Write-Color "URL: $downloadUrl" -Color Gray
    
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $outputFile -ProgressBar
        Write-Color "Download complete: $outputFile" -Color Green
        return $outputFile
    }
    catch {
        Write-Color "Download failed: $_" -Color Red
        return $false
    }
}

function Install-Update {
    param([string]$InstallerPath)
    
    if (-not (Test-Path $InstallerPath)) {
        Write-Color "Installer not found: $InstallerPath" -Color Red
        return $false
    }
    
    Write-Color "Launching installer..." -Color Cyan
    Write-Color "The installer will guide you through the update process." -Color Yellow
    
    try {
        $process = Start-Process -FilePath $InstallerPath -ArgumentList "/VERYSILENT /SUPPRESSMSGBOXES /UPDATE" -Wait -PassThru
        if ($process.ExitCode -eq 0) {
            Write-Color "Update installed successfully!" -Color Green
            return $true
        }
        else {
            Write-Color "Installer exited with code: $($process.ExitCode)" -Color Red
            return $false
        }
    }
    catch {
        Write-Color "Failed to launch installer: $_" -Color Red
        return $false
    }
}

# Main logic
Write-Color "╔════════════════════════════════════════╗" -Color Cyan
Write-Color "║     DSTerminal Update Helper v1.0      ║" -Color Cyan
Write-Color "╚════════════════════════════════════════╝" -Color Cyan
Write-Host ""

$currentVer = Get-CurrentVersion
Write-Color "Current version: $currentVer" -Color White

$release = Get-LatestVersion
if (-not $release) {
    Write-Color "Update check failed. Please check your internet connection." -Color Red
    exit 1
}

$latestVer = $release.Version
Write-Color "Latest version:  $latestVer" -Color White
Write-Host ""

if (Compare-Versions $currentVer $latestVer) {
    Write-Color "✓ UPDATE AVAILABLE!" -Color Green
    Write-Host ""
    Write-Color "Release notes:" -Color Yellow
    Write-Color "$($release.Notes)" -Color Gray
    Write-Host ""
    
    $choice = Read-Host "Download and install now? (Y/N)"
    if ($choice -eq "Y" -or $choice -eq "y") {
        $installer = Download-Update -Version $latestVer
        if ($installer) {
            Install-Update -InstallerPath $installer
        }
    }
}
else {
    Write-Color "✓ You have the latest version." -Color Green
}

Write-Host ""
pause
'@

Set-Content -Path "tools\update-helper.ps1" -Value $updateHelper -Encoding UTF8
Write-Host "  ✓ Created: tools\update-helper.ps1" -ForegroundColor Green

# Create docs\index.html using here-string
$docIndex = @'
<!DOCTYPE html>
<html>
<head>
    <title>DSTerminal Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #0a0e14; color: #e0e0e0; }
        h1 { color: #00ff9d; border-bottom: 2px solid #00ff9d; }
        h2 { color: #00ccff; }
        code { background: #1a1f2a; padding: 2px 5px; border-radius: 3px; }
        .container { max-width: 800px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DSTerminal Documentation</h1>
        <p>Version 2.0.59 | © 2024 Stark Expo Tech Exchange</p>
        
        <h2>Quick Start</h2>
        <p>Type <code>help</code> in the terminal to see all available commands.</p>
        
        <h2>Basic Commands</h2>
        <ul>
            <li><code>system scan -All</code> - Full system security scan</li>
            <li><code>net -n mon</code> - Network monitoring</li>
            <li><code>encrypt &lt;file&gt;</code> - Encrypt a file</li>
            <li><code>decrypt &lt;file&gt;</code> - Decrypt a file</li>
            <li><code>update</code> - Check for updates</li>
        </ul>
        
        <h2>Workspace</h2>
        <p>Your workspace is located at: <code>%APPDATA%\DSTerminal_Workspace</code></p>
        
        <h2>Support</h2>
        <p>For more information, visit: <a href="https://starkexpotechexchange-mw.com">starkexpotechexchange-mw.com</a></p>
    </div>
</body>
</html>
'@

Set-Content -Path "docs\index.html" -Value $docIndex -Encoding UTF8
Write-Host "  ✓ Created: docs\index.html" -ForegroundColor Green

# Create templates\report_template.txt
$reportTemplate = @'
DSTerminal Security Report
==========================
Generated: {DATE}
User: {USER}
Version: 2.0.59

Scan Results:
------------
{SCAN_RESULTS}

Threat Assessment:
-----------------
{THREAT_ASSESSMENT}

Recommendations:
---------------
{RECOMMENDATIONS}

---
This report was generated by DSTerminal v2.0.59
© 2024 Stark Expo Tech Exchange
'@

Set-Content -Path "templates\report_template.txt" -Value $reportTemplate -Encoding UTF8
Write-Host "  ✓ Created: templates\report_template.txt" -ForegroundColor Green

# Create config\config.ini
$configIni = @'
[DSTerminal]
version=2.0.59
workspace=%APPDATA%\DSTerminal_Workspace
log_level=INFO
auto_update=true
update_interval=7

[Network]
timeout=30
user_agent=DSTerminal/2.0.59

[Security]
encryption_key_file=%APPDATA%\.dsterminal_key
secure_delete_passes=3
'@

Set-Content -Path "config\config.ini" -Value $configIni -Encoding UTF8
Write-Host "  ✓ Created: config\config.ini" -ForegroundColor Green

# Create redist\ffmpeg\README.txt
$ffmpegReadme = @'
FFmpeg for DSTerminal
=====================

This directory is for FFmpeg binaries if needed for video analysis features.

To install FFmpeg:
1. Download from: https://ffmpeg.org/download.html
2. Extract the binaries here
3. Ensure ffmpeg.exe is in this directory

Current version: Not installed (placeholder only)
'@

Set-Content -Path "redist\ffmpeg\README.txt" -Value $ffmpegReadme -Encoding UTF8
Write-Host "  ✓ Created: redist\ffmpeg\README.txt" -ForegroundColor Green

# Create tools\README.txt
$toolsReadme = @'
DSTerminal Additional Tools
===========================

This directory contains additional security tools and utilities.

Available Tools:
- update-helper.ps1 - Auto-update helper script

To add more tools, place them in this directory and they will be included in the installation.
'@

Set-Content -Path "tools\README.txt" -Value $toolsReadme -Encoding UTF8
Write-Host "  ✓ Created: tools\README.txt" -ForegroundColor Green

# Create empty placeholder files to ensure directories aren't empty
"# DSTerminal Templates" | Out-File -FilePath "templates\README.txt" -Encoding UTF8
"# DSTerminal Configuration" | Out-File -FilePath "config\README.txt" -Encoding UTF8

Write-Host ""
Write-Host "✅ All files created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Now you can run the build again:" -ForegroundColor Yellow
Write-Host "  .\build.ps1 -BuildInstaller" -ForegroundColor White