# fix_nmap_wrapper.ps1
Write-Host "Fixing Nmap wrapper..." -ForegroundColor Cyan

# Find actual Nmap installation
$nmapPaths = @(
    'C:\Program Files\Nmap\nmap.exe',
    'C:\Program Files (x86)\Nmap\nmap.exe',
    'C:\ProgramData\chocolatey\bin\nmap.exe'
)

$nmapExe = $null
foreach ($path in $nmapPaths) {
    if (Test-Path $path) {
        $nmapExe = $path
        break
    }
}

if ($nmapExe) {
    Write-Host "Found Nmap at: $nmapExe" -ForegroundColor Green
    
    # Create correct wrapper in user's PATH
    $wrapperDir = "$env:USERPROFILE\DSTerminal\bin"
    if (-not (Test-Path $wrapperDir)) {
        New-Item -ItemType Directory -Path $wrapperDir -Force | Out-Null
    }
    
    $wrapperPath = Join-Path $wrapperDir "nmap.bat"
    $wrapperContent = "@echo off`r`n`"$nmapExe`" %*`r`n"
    Set-Content -Path $wrapperPath -Value $wrapperContent
    
    Write-Host "Created wrapper: $wrapperPath" -ForegroundColor Green
    
    # Add to PATH if not already there
    $currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($currentPath -notlike "*$wrapperDir*") {
        $newPath = "$currentPath;$wrapperDir"
        [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        Write-Host "Added $wrapperDir to user PATH" -ForegroundColor Green
        Write-Host "Please restart your terminal for changes to take effect" -ForegroundColor Yellow
    }
} else {
    Write-Host "Nmap not found! Please run install_nmap.ps1 -Force" -ForegroundColor Red
}