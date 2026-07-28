<<<<<<< HEAD
# install_whois.ps1 - Uses bundled whois.exe (offline)
# WHOIS Installation Script for DSTerminal

param(
    [switch]$Silent,
    [switch]$Force
)

=======
# Install WHOIS - User-level installation (no admin required)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installing WHOIS Domain Lookup Tool" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

<<<<<<< HEAD
# Define paths
$whoisDir = "$env:USERPROFILE\DSTerminal\tools\whois"
$bundledWhois = Join-Path $PSScriptRoot "bundled\whois\whois.exe"
$wrapperDir = "$env:USERPROFILE\DSTerminal\bin"
$wrapperPath = Join-Path $wrapperDir "whois.bat"

# Check if already installed
if ((Get-Command whois -ErrorAction SilentlyContinue) -and (-not $Force)) {
    Write-Host "WHOIS is already installed" -ForegroundColor Green
    $whoisPath = (Get-Command whois).Source
    Write-Host "Location: $whoisPath" -ForegroundColor Cyan
    
    $version = & whois --version 2>&1 | Select-Object -First 1
    Write-Host "Version: $version" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To reinstall, use: .\install_whois.ps1 -Force" -ForegroundColor Yellow
=======
# Check if already installed
$whoisCheck = Get-Command whois -ErrorAction SilentlyContinue
if ($whoisCheck) {
    Write-Host "WHOIS is already installed" -ForegroundColor Green
    $whoisPath = (Get-Command whois).Source
    Write-Host "Location: $whoisPath" -ForegroundColor Cyan
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    pause
    exit 0
}

<<<<<<< HEAD
# Check if bundled whois.exe exists
if (-not (Test-Path $bundledWhois)) {
    Write-Host "ERROR: Bundled WHOIS.exe not found!" -ForegroundColor Red
    Write-Host "Expected: $bundledWhois" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please run: .\download_whois.ps1" -ForegroundColor Cyan
    Write-Host "Or download manually from: https://live.sysinternals.com/whois.exe" -ForegroundColor Cyan
    pause
    exit 1
}

Write-Host "Found bundled WHOIS.exe" -ForegroundColor Green
Write-Host "  Source: $bundledWhois" -ForegroundColor Gray

# Create tools directory if needed
if (-not (Test-Path $whoisDir)) {
    Write-Host "Creating directory: $whoisDir" -ForegroundColor Gray
    New-Item -ItemType Directory -Path $whoisDir -Force | Out-Null
}

# Copy whois.exe to tools directory
Write-Host "Copying whois.exe to: $whoisDir" -ForegroundColor Cyan
Copy-Item -Path $bundledWhois -Destination $whoisDir -Force

$whoisExe = Join-Path $whoisDir "whois.exe"

# Create wrapper for PATH access
if (-not (Test-Path $wrapperDir)) {
    New-Item -ItemType Directory -Path $wrapperDir -Force | Out-Null
}

$wrapperContent = @"
@echo off
REM WHOIS wrapper for DSTerminal
if not exist "$whoisExe" (
    echo WHOIS not found at: $whoisExe
    echo Please reinstall WHOIS using: install_whois.ps1 -Force
    pause
    exit /b 1
)
"$whoisExe" %*
"@
Set-Content -Path $wrapperPath -Value $wrapperContent
Write-Host "Created wrapper: $wrapperPath" -ForegroundColor Green

# Add to PATH if not already there
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike "*$wrapperDir*") {
    $newPath = "$currentPath;$wrapperDir"
    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
    Write-Host "Added $wrapperDir to user PATH" -ForegroundColor Green
}

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify installation
Write-Host ""
Write-Host "Verifying WHOIS installation..." -ForegroundColor Cyan

if (Get-Command whois -ErrorAction SilentlyContinue) {
    $version = & whois --version 2>&1 | Select-Object -First 1
    Write-Host "✅ WHOIS installed successfully!" -ForegroundColor Green
    Write-Host "   $version" -ForegroundColor Gray
    Write-Host "   Location: $wrapperPath" -ForegroundColor Gray
} else {
    Write-Host "⚠️ WHOIS not in PATH. Please restart your terminal." -ForegroundColor Yellow
    Write-Host "   You can run it manually from: $whoisExe" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "WHOIS installation complete!" -ForegroundColor Green
pause
exit 0
=======
Write-Host "NOTE: WHOIS installation may require Administrator privileges." -ForegroundColor Yellow
Write-Host ""

Write-Host "Options for WHOIS:" -ForegroundColor Cyan
Write-Host "  1. Skip WHOIS (DSTerminal works fine without it)" -ForegroundColor White
Write-Host "  2. Use online WHOIS via web browser" -ForegroundColor White
Write-Host "  3. Install manually (download and extract)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Choose option (1/2/3)"
Write-Host ""

if ($choice -eq "1") {
    Write-Host "Skipping WHOIS installation." -ForegroundColor Yellow
    Write-Host "You can use web-based WHOIS at: https://whois.domaintools.com" -ForegroundColor Cyan
    exit 0
} elseif ($choice -eq "2") {
    Write-Host "Opening online WHOIS service..." -ForegroundColor Cyan
    Start-Process "https://whois.domaintools.com"
    exit 0
} else {
    Write-Host "Manual installation instructions:" -ForegroundColor Green
    Write-Host ""
    Write-Host "1. Download WhoIs.zip from:" -ForegroundColor White
    Write-Host "   https://docs.microsoft.com/en-us/sysinternals/downloads/whois" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Extract the zip file" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Create a folder: %USERPROFILE%\tools\" -ForegroundColor White
    Write-Host "   mkdir %USERPROFILE%\tools" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Copy whois.exe to that folder" -ForegroundColor White
    Write-Host ""
    Write-Host "5. Add to PATH (no admin required):" -ForegroundColor White
    Write-Host "   [Environment]::SetEnvironmentVariable('Path', " -ForegroundColor Cyan
    Write-Host "     '$env:Path;%USERPROFILE%\tools', 'User')" -ForegroundColor Cyan
    Write-Host ""
    
    $openBrowser = Read-Host "Open download page? (y/n)"
    if ($openBrowser -eq 'y') {
        Start-Process "https://docs.microsoft.com/en-us/sysinternals/downloads/whois"
    }
    exit 0
}
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
