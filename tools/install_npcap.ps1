# install_npcap.ps1 - Modified to show GUI installation
# Npcap Installation Script for DSTerminal

param(
    [switch]$Silent,
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installing Npcap Packet Capture" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
$npcapPaths = @(
    'C:\Windows\System32\Npcap',
    'C:\Program Files\Npcap'
)

$installed = $false
foreach ($path in $npcapPaths) {
    if (Test-Path $path) {
        $installed = $true
        break
    }
}

if ($installed -and -not $Force) {
    Write-Host "Npcap is already installed" -ForegroundColor Green
    Write-Host ""
    Write-Host "To reinstall, use: .\install_npcap.ps1 -Force" -ForegroundColor Yellow
    pause
    exit 0
}

# Check for bundled installer
$bundledNpcap = Join-Path $PSScriptRoot "bundled\npcap\npcap-1.79.exe"
$downloadPath = $bundledNpcap

if (-not (Test-Path $bundledNpcap)) {
    Write-Host "Bundled Npcap installer not found!" -ForegroundColor Yellow
    Write-Host "Downloading Npcap installer..." -ForegroundColor Cyan
    
    $downloadPath = Join-Path $env:TEMP "npcap-1.79.exe"
    $npcapUrl = "https://npcap.com/dist/npcap-1.79.exe"
    
    try {
        $webClient = New-Object System.Net.WebClient
        Write-Host "Downloading from: $npcapUrl" -ForegroundColor Gray
        $webClient.DownloadFile($npcapUrl, $downloadPath)
        Write-Host "Download complete!" -ForegroundColor Green
    } catch {
        Write-Host "Failed to download Npcap installer!" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please download manually from: https://npcap.com/" -ForegroundColor Yellow
        pause
        exit 1
    }
} else {
    Write-Host "Using bundled Npcap installer" -ForegroundColor Green
}

Write-Host ""
Write-Host "Npcap Installation Wizard will now open." -ForegroundColor Cyan
Write-Host "Please follow the on-screen instructions." -ForegroundColor Yellow
Write-Host ""

# Run Npcap installer with GUI (no silent flags)
try {
    $process = Start-Process -FilePath $downloadPath -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "Npcap installed successfully!" -ForegroundColor Green
        Write-Host "You may need to restart your computer for changes to take effect." -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "Npcap installation failed with exit code: $($process.ExitCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "Error launching Npcap installer: $_" -ForegroundColor Red
}

Write-Host ""
pause
exit $process.ExitCode