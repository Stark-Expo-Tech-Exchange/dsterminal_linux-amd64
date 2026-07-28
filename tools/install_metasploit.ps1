# Install Metasploit Framework - Requires Administrator
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installing Metasploit Framework" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: Metasploit installation requires Administrator privileges" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "Or re-run the DSTERMINAL installer as Administrator" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 1
}

# Check if already installed
if (Get-Command msfconsole -ErrorAction SilentlyContinue) {
    $msfVersion = & msfconsole --version 2>$null
    Write-Host "Metasploit is already installed" -ForegroundColor Green
    Write-Host "Version: $msfVersion" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 0
}

Write-Host "NOTE: Metasploit is a large framework (800MB+ download)" -ForegroundColor Yellow
Write-Host "Installation may take 10-30 minutes depending on your connection." -ForegroundColor Cyan
Write-Host ""

$confirm = Read-Host "Continue with Metasploit installation? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Metasploit installation cancelled." -ForegroundColor Yellow
    pause
    exit 0
}

Write-Host ""
$installed = $false

# Method 1: Install via Chocolatey (Recommended)
Write-Host "[Method 1] Trying Chocolatey..." -ForegroundColor Yellow

$chocoCheck = Get-Command choco -ErrorAction SilentlyContinue
if ($chocoCheck) {
    Write-Host "Chocolatey found. Installing Metasploit..." -ForegroundColor Cyan
    Write-Host "This may take a while. Please be patient..." -ForegroundColor DarkYellow
    
    try {
        choco install metasploit -y --no-progress --timeout=2700
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Verify
        if (Get-Command msfconsole -ErrorAction SilentlyContinue) {
            Write-Host "SUCCESS: Metasploit installed via Chocolatey" -ForegroundColor Green
            $installed = $true
        } else {
            Write-Host "Metasploit installed but not found in PATH" -ForegroundColor Yellow
            Write-Host "Please restart your terminal" -ForegroundColor Cyan
            $installed = $true
        }
    } catch {
        Write-Host "Chocolatey installation failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Chocolatey not available" -ForegroundColor DarkYellow
}

# Method 2: Direct download from Rapid7
if (-not $installed) {
    Write-Host ""
    Write-Host "[Method 2] Downloading from Rapid7..." -ForegroundColor Yellow
    
    $downloadUrl = "https://github.com/rapid7/metasploit-framework/releases/latest/download/metasploit-framework-installer.exe"
    $installerPath = "$env:TEMP\metasploit-installer.exe"
    
    Write-Host "Downloading Metasploit installer (may take several minutes)..." -ForegroundColor Cyan
    
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Host "Running installer..." -ForegroundColor Cyan
        Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait -NoNewWindow
        
        # Clean up
        Remove-Item $installerPath -ErrorAction SilentlyContinue
        
        # Verify
        if (Get-Command msfconsole -ErrorAction SilentlyContinue) {
            Write-Host "SUCCESS: Metasploit installed via Rapid7 installer" -ForegroundColor Green
            $installed = $true
        } else {
            Write-Host "Installation completed but verification failed" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Direct download failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Method 3: Manual installation instructions
if (-not $installed) {
    Write-Host ""
    Write-Host "[Method 3] Manual installation required" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please install Metasploit manually:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Option A - Via installer:" -ForegroundColor Green
    Write-Host "  1. Download from: https://www.metasploit.com/download" -ForegroundColor White
    Write-Host "  2. Run the installer as Administrator" -ForegroundColor White
    Write-Host "  3. Follow the installation wizard" -ForegroundColor White
    Write-Host ""
    Write-Host "Option B - Via Chocolatey (as Admin):" -ForegroundColor Green
    Write-Host "  choco install metasploit -y" -ForegroundColor White
    Write-Host ""
    Write-Host "Option C - Via Windows Subsystem for Linux (WSL):" -ForegroundColor Green
    Write-Host "  wsl --install" -ForegroundColor White
    Write-Host "  wsl sudo apt update && sudo apt install metasploit-framework -y" -ForegroundColor White
    Write-Host ""
    
    $openBrowser = Read-Host "Open Metasploit download page? (y/n)"
    if ($openBrowser -eq 'y') {
        Start-Process "https://www.metasploit.com/download"
    }
}

# Final verification
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Cyan
$finalCheck = Get-Command msfconsole -ErrorAction SilentlyContinue
if ($finalCheck) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS: Metasploit is ready to use!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Test with: msfconsole --version" -ForegroundColor Yellow
    Write-Host "Launch with: msfconsole" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "  Metasploit installation needs attention" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please follow the manual installation steps above." -ForegroundColor Cyan
}

Write-Host ""
pause