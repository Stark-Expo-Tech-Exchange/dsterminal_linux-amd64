# install_all_dependencies.ps1 - SIMPLIFIED VERSION
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DSTERMINAL - Dependency Installer" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$failed = @()
$installed = @()

# Check if in virtual environment
$inVenv = ($env:VIRTUAL_ENV -ne $null)
if ($inVenv) {
    Write-Host "NOTE: Running in virtual environment" -ForegroundColor Yellow
    Write-Host ""
}

# ============================================
# Check Python
# ============================================
Write-Host "[1/3] Checking Python..." -ForegroundColor Yellow

$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
    $pythonVersion = & python --version 2>$null
    Write-Host "  [OK] Python: $pythonVersion" -ForegroundColor Green
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
    $pythonVersion = & python3 --version 2>$null
    Write-Host "  [OK] Python3: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  [X] Python not found" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""

# ============================================
# Install SQLMap (skip if already installed)
# ============================================
Write-Host "[2/3] Installing SQLMap..." -ForegroundColor Yellow

if (Get-Command sqlmap -ErrorAction SilentlyContinue) {
    Write-Host "  [OK] SQLMap already installed" -ForegroundColor Green
} else {
    Write-Host "  Installing SQLMap via pip..." -ForegroundColor Cyan
    if ($inVenv) {
        & $pythonCmd -m pip install sqlmap --quiet
    } else {
        & $pythonCmd -m pip install sqlmap --user --quiet
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] SQLMap installed" -ForegroundColor Green
    } else {
        Write-Host "  [X] SQLMap installation failed" -ForegroundColor Red
        $failed += "sqlmap"
    }
}

Write-Host ""

# ============================================
# Install WHOIS (if missing)
# ============================================
Write-Host "[3/3] Installing WHOIS..." -ForegroundColor Yellow

if (Get-Command whois -ErrorAction SilentlyContinue) {
    Write-Host "  [OK] WHOIS already installed" -ForegroundColor Green
} else {
    Write-Host "  WHOIS not found. Installing via winget..." -ForegroundColor Cyan
    
    # Try winget first (no admin needed for download)
    $wingetCheck = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetCheck) {
        winget install Microsoft.Sysinternals.Whois --silent --accept-package-agreements 2>$null
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (Get-Command whois -ErrorAction SilentlyContinue) {
            Write-Host "  [OK] WHOIS installed" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] WHOIS installation may need PATH refresh" -ForegroundColor Yellow
            Write-Host "  Please restart your terminal and run: whois --version" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  [WARN] winget not available. Please install WHOIS manually:" -ForegroundColor Yellow
        Write-Host "  https://docs.microsoft.com/en-us/sysinternals/downloads/whois" -ForegroundColor Cyan
        $failed += "whois"
    }
}

Write-Host ""

# ============================================
# Refresh PATH
# ============================================
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# ============================================
# Summary
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($failed.Count -eq 0) {
    Write-Host "All dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Some dependencies need manual installation:" -ForegroundColor Yellow
    foreach ($item in $failed) {
        Write-Host "  [!] $item" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Press any key to continue..."
pause