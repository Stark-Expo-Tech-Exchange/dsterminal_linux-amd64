# DSTerminal Update Helper Script
param(
    [switch],
    [switch],
    [switch],
    [string]
)

$ErrorActionPreference = "Stop"
$repo = "Stark-Expo-Tech-Exchange/DSTerminal_releases_latest"
$apiUrl = "https://api.github.com/repos/$repo/releases/latest"
$versionFile = "$env:APPDATA\DSTerminal_Workspace\version.txt"

Write-Host "DSTerminal Update Helper v1.0" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path $versionFile) {
    $currentVer = (Get-Content $versionFile -Raw).Trim()
} else {
    $currentVer = "2.0.59"
}
Write-Host "Current version: $currentVer"

try {
    $release = Invoke-RestMethod -Uri $apiUrl -Headers @{ "User-Agent" = "DSTerminal-Updater" }
    $latestVer = $release.tag_name -replace "v", ""
    Write-Host "Latest version:  $latestVer"
    Write-Host ""
    
    if ([version]$currentVer -lt [version]$latestVer) {
        Write-Host "UPDATE AVAILABLE!" -ForegroundColor Green
        Write-Host ""
        $choice = Read-Host "Download now? (Y/N)"
        if ($choice -eq "Y" -or $choice -eq "y") {
            $asset = $release.assets | Where-Object { $_.name -like "*Setup*.exe" } | Select-Object -First 1
            if ($asset) {
                Write-Host "Downloading $($asset.name)..."
                Invoke-WebRequest -Uri $asset.browser_download_url -OutFile "$env:TEMP\DSTerminal_Update.exe"
                Write-Host "Download complete!" -ForegroundColor Green
                Start-Process "$env:TEMP\DSTerminal_Update.exe" -Wait
            }
        }
    } else {
        Write-Host "You have the latest version." -ForegroundColor Green
    }
} catch {
    Write-Host "Update check failed: $_" -ForegroundColor Red
}

pause
