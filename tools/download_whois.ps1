# download_whois.ps1
# Download WHOIS from Microsoft Sysinternals and bundle it for offline installation

param(
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Downloading WHOIS from Sysinternals" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set paths
$currentDir = Get-Location
$bundledDir = Join-Path $currentDir "bundled\whois"
$whoisExePath = Join-Path $bundledDir "whois.exe"

# Check if already exists
if ((Test-Path $whoisExePath) -and (-not $Force)) {
    Write-Host "WHOIS.exe already exists in bundled directory!" -ForegroundColor Yellow
    Write-Host "Location: $whoisExePath" -ForegroundColor Cyan
    
    $fileSize = (Get-Item $whoisExePath).Length / 1KB
    Write-Host "Size: $([math]::Round($fileSize, 2)) KB" -ForegroundColor Gray
    
    $version = & $whoisExePath --version 2>&1 | Select-Object -First 1
    Write-Host "Version: $version" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "To re-download, use: .\download_whois.ps1 -Force" -ForegroundColor Yellow
    pause
    exit 0
}

# Create bundled directory if it doesn't exist
if (-not (Test-Path $bundledDir)) {
    Write-Host "Creating directory: $bundledDir" -ForegroundColor Gray
    New-Item -ItemType Directory -Path $bundledDir -Force | Out-Null
}

# Download WHOIS.exe from Microsoft Sysinternals
$whoisUrl = "https://live.sysinternals.com/whois.exe"

Write-Host "Downloading WHOIS.exe from:" -ForegroundColor Cyan
Write-Host "  $whoisUrl" -ForegroundColor Gray
Write-Host ""

try {
    $webClient = New-Object System.Net.WebClient
    
    # Add a user-agent to avoid blocking
    $webClient.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    Write-Host "Downloading..." -ForegroundColor Yellow
    $webClient.DownloadFile($whoisUrl, $whoisExePath)
    
    Write-Host "Download complete!" -ForegroundColor Green
    
    # Verify the download
    if (Test-Path $whoisExePath) {
        $fileSize = (Get-Item $whoisExePath).Length / 1KB
        Write-Host "File saved to: $whoisExePath" -ForegroundColor Cyan
        Write-Host "File size: $([math]::Round($fileSize, 2)) KB" -ForegroundColor Cyan
        
        # Test the executable
        Write-Host ""
        Write-Host "Verifying WHOIS.exe..." -ForegroundColor Yellow
        $version = & $whoisExePath --version 2>&1 | Select-Object -First 1
        Write-Host "âœ… $version" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "WHOIS bundled successfully!" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Failed to download WHOIS.exe" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual download options:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://live.sysinternals.com/whois.exe" -ForegroundColor Cyan
    Write-Host "  2. Download and save to: $whoisExePath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Alternative: Download from Microsoft Docs" -ForegroundColor Yellow
    Write-Host "  https://docs.microsoft.com/en-us/sysinternals/downloads/whois" -ForegroundColor Cyan
    pause
    exit 1
}

Write-Host ""
Write-Host "To use WHOIS offline, it will be copied from:" -ForegroundColor Cyan
Write-Host "  $whoisExePath" -ForegroundColor Gray
Write-Host "To: %USERPROFILE%\DSTerminal\tools\whois\whois.exe" -ForegroundColor Gray
Write-Host ""
pause
exit 0