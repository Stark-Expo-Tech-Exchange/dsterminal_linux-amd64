# install_nmap.ps1 - Fixed version
# Nmap Installer Script with GUI Prompt

param(
    [switch]$Silent,
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installing Nmap Network Scanner" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if already installed via Chocolatey or system
$nmapCheck = Get-Command nmap -ErrorAction SilentlyContinue
if ($nmapCheck -and -not $Force) {
    Write-Host "Nmap is already installed" -ForegroundColor Green
    $nmapPath = (Get-Command nmap).Source
    Write-Host "Location: $nmapPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To reinstall, use: .\install_nmap.ps1 -Force" -ForegroundColor Yellow
    pause
    exit 0
}

# Check for bundled installer
$bundledNmap = Join-Path $PSScriptRoot "bundled\nmap\nmap-7.95-setup.exe"
$downloadPath = $bundledNmap

if (-not (Test-Path $bundledNmap)) {
    Write-Host "Bundled Nmap installer not found!" -ForegroundColor Yellow
    Write-Host "Downloading Nmap installer..." -ForegroundColor Cyan
    
    $downloadPath = Join-Path $env:TEMP "nmap-7.95-setup.exe"
    $nmapUrl = "https://nmap.org/dist/nmap-7.95-setup.exe"
    
    try {
        $webClient = New-Object System.Net.WebClient
        Write-Host "Downloading from: $nmapUrl" -ForegroundColor Gray
        $webClient.DownloadFile($nmapUrl, $downloadPath)
        Write-Host "Download complete!" -ForegroundColor Green
    } catch {
        Write-Host "Failed to download Nmap installer!" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please download manually from: https://nmap.org/download.html" -ForegroundColor Yellow
        pause
        exit 1
    }
} else {
    Write-Host "Using bundled Nmap installer" -ForegroundColor Green
}

Write-Host ""
Write-Host "Nmap Installation Wizard will now open." -ForegroundColor Cyan
Write-Host "Please follow the on-screen instructions." -ForegroundColor Yellow
Write-Host ""
Write-Host "NOTE: Nmap requires Npcap for packet capture." -ForegroundColor Yellow
Write-Host "      The installer will check for Npcap." -ForegroundColor Yellow
Write-Host ""

# FIXED: Proper PowerShell syntax for checking Npcap
$npcapPaths = @(
    'C:\Windows\System32\Npcap',
    'C:\Program Files\Npcap',
    'C:\Program Files (x86)\Npcap'
)
$npcapInstalled = $false
foreach ($path in $npcapPaths) {
    if (Test-Path $path) {
        $npcapInstalled = $true
        break
    }
}

if (-not $npcapInstalled) {
    Write-Host "WARNING: Npcap not found!" -ForegroundColor Red
    Write-Host "Nmap requires Npcap for network scanning." -ForegroundColor Yellow
    Write-Host ""
    $installNpcap = Read-Host "Install Npcap now? (y/n)"
    if ($installNpcap -eq 'y') {
        Write-Host "Launching Npcap installer..." -ForegroundColor Cyan
        $npcapInstaller = Join-Path $PSScriptRoot "bundled\npcap\npcap-1.79.exe"
        if (-not (Test-Path $npcapInstaller)) {
            $npcapInstaller = Join-Path $env:TEMP "npcap-1.79.exe"
            $npcapUrl = "https://npcap.com/dist/npcap-1.79.exe"
            try {
                $webClient = New-Object System.Net.WebClient
                $webClient.DownloadFile($npcapUrl, $npcapInstaller)
            } catch {
                Write-Host "Failed to download Npcap!" -ForegroundColor Red
                exit 1
            }
        }
        Start-Process -FilePath $npcapInstaller -Wait
        Write-Host "Npcap installation completed." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Launching Nmap installer..." -ForegroundColor Cyan
Write-Host ""

# Run Nmap installer with GUI
try {
    $process = Start-Process -FilePath $downloadPath -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "Nmap installed successfully!" -ForegroundColor Green
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # FIXED: Check both system paths and our bin directory
        $nmapFound = $false
        
        # Check if nmap is in the system PATH
        if (Get-Command nmap -ErrorAction SilentlyContinue) {
            $nmapFound = $true
            $version = & nmap --version 2>&1 | Select-Object -First 1
            Write-Host "Version: $version" -ForegroundColor Cyan
            Write-Host "Location: $(Get-Command nmap).Source" -ForegroundColor Cyan
        }
        
        # Check common installation paths
        if (-not $nmapFound) {
            $commonPaths = @(
                'C:\Program Files\Nmap\nmap.exe',
                'C:\Program Files (x86)\Nmap\nmap.exe'
            )
            foreach ($path in $commonPaths) {
                if (Test-Path $path) {
                    Write-Host "Nmap installed at: $path" -ForegroundColor Green
                    $nmapFound = $true
                    break
                }
            }
        }
        
        if (-not $nmapFound) {
            Write-Host "Nmap installed but not found in PATH." -ForegroundColor Yellow
            Write-Host "You may need to restart your terminal." -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "Nmap installation failed with exit code: $($process.ExitCode)" -ForegroundColor Red
        Write-Host "Please try installing manually from: https://nmap.org/download.html" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error launching Nmap installer: $_" -ForegroundColor Red
}

Write-Host ""
pause
exit $process.ExitCode