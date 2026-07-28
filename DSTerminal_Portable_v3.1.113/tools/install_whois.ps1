# install_whois.ps1 - Uses bundled whois.exe (offline)
# WHOIS Installation Script for DSTerminal

param(
    [switch]$Silent,
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installing WHOIS Domain Lookup Tool" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

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
    pause
    exit 0
}

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