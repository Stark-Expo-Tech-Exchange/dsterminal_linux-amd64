# Install Remaining Dependencies for DSTERMINAL
# This installs sqlmap and whois

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DSTERMINAL - Installing Remaining Dependencies" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$failed = @()
$installed = @()

# ============================================
# Install SQLMap
# ============================================
Write-Host "[1/2] Installing SQLMap..." -ForegroundColor Yellow
Write-Host ""

# Check if already installed
$sqlmapCheck = Get-Command sqlmap -ErrorAction SilentlyContinue
if ($sqlmapCheck) {
    Write-Host "  SQLMap is already installed" -ForegroundColor Green
    $installed += "sqlmap (already had)"
} else {
    # Try pip install
    Write-Host "  Installing via pip..." -ForegroundColor Cyan
    pip install sqlmap
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] SQLMap installed successfully" -ForegroundColor Green
        $installed += "sqlmap"
    } else {
        Write-Host "  [X] Failed to install SQLMap via pip" -ForegroundColor Red
        $failed += "sqlmap"
    }
}

Write-Host ""

# ============================================
# Install WHOIS
# ============================================
Write-Host "[2/2] Installing WHOIS..." -ForegroundColor Yellow
Write-Host ""

# Check if already installed
$whoisCheck = Get-Command whois -ErrorAction SilentlyContinue
if ($whoisCheck) {
    Write-Host "  WHOIS is already installed" -ForegroundColor Green
    $installed += "whois (already had)"
} else {
    $whoisInstalled = $false
    
    # Try Chocolatey first
    $chocoCheck = Get-Command choco -ErrorAction SilentlyContinue
    if ($chocoCheck) {
        Write-Host "  Installing via Chocolatey..." -ForegroundColor Cyan
        choco install whois -y --no-progress
        
        # Refresh environment
        refreshenv 2>$null
        
        # Check again
        $whoisCheck2 = Get-Command whois -ErrorAction SilentlyContinue
        if ($whoisCheck2) {
            Write-Host "  [OK] WHOIS installed via Chocolatey" -ForegroundColor Green
            $installed += "whois"
            $whoisInstalled = $true
        } else {
            Write-Host "  [X] Chocolatey installation failed" -ForegroundColor Red
        }
    }
    
    # Try winget if Chocolatey failed
    if (-not $whoisInstalled) {
        $wingetCheck = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCheck) {
            Write-Host "  Installing via winget..." -ForegroundColor Cyan
            winget install Microsoft.Sysinternals.Whois --silent --accept-package-agreements
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] WHOIS installed via winget" -ForegroundColor Green
                $installed += "whois"
                $whoisInstalled = $true
            } else {
                Write-Host "  [X] winget installation failed" -ForegroundColor Red
            }
        }
    }
    
    # Provide manual instructions if both methods failed
    if (-not $whoisInstalled) {
        Write-Host ""
        Write-Host "  [WARN] Could not install WHOIS automatically" -ForegroundColor Yellow
        Write-Host "  Manual installation required:" -ForegroundColor Cyan
        Write-Host "    1. Download from: https://docs.microsoft.com/en-us/sysinternals/downloads/whois" -ForegroundColor White
        Write-Host "    2. Extract whois.exe to C:\Windows\System32\" -ForegroundColor White
        Write-Host "    3. Or add the extracted folder to your PATH" -ForegroundColor White
        $failed += "whois (manual)"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION SUMMARY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($installed.Count -gt 0) {
    Write-Host "Successfully installed:" -ForegroundColor Green
    foreach ($item in $installed) {
        Write-Host "  [OK] $item" -ForegroundColor Green
    }
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "Failed to install:" -ForegroundColor Red
    foreach ($item in $failed) {
        Write-Host "  [X] $item" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# Run verification
Write-Host ""
Write-Host "Verifying installations..." -ForegroundColor Cyan
Write-Host ""

# Verify SQLMap
$sqlmapFinal = Get-Command sqlmap -ErrorAction SilentlyContinue
if ($sqlmapFinal) {
    $version = & sqlmap --version 2>$null | Select-Object -First 1
    Write-Host "  SQLMap: $version" -ForegroundColor Green
} else {
    Write-Host "  SQLMap: NOT FOUND" -ForegroundColor Red
}

# Verify WHOIS
$whoisFinal = Get-Command whois -ErrorAction SilentlyContinue
if ($whoisFinal) {
    Write-Host "  WHOIS: Installed" -ForegroundColor Green
} else {
    Write-Host "  WHOIS: NOT FOUND (optional, DSTERMINAL will still work)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($failed.Count -eq 0 -or ($failed.Count -eq 1 -and $failed[0] -like "*whois*")) {
    Write-Host "DSTERMINAL Cyber-OPs is ready to use!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start DSTERMINAL:" -ForegroundColor Cyan
    Write-Host "  ..." -ForegroundColor White
    Write-Host "  Right click DSTerminal Cyber-Ops as an Admin" -ForegroundColor White
} else {
    Write-Host "Please install the failed dependencies manually." -ForegroundColor Yellow
}

Write-Host ""
pause