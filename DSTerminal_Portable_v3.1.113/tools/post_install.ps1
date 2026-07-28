# post_install.ps1 - DSTERMINAL Post-Installation Script
# Runs after installer completes to install missing dependencies

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DSTERMINAL Post-Installation Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Wait for system to settle
Start-Sleep -Seconds 2

# Refresh PATH in current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

$installed = @()
$failed = @()

# ============================================
# 1. Install SQLMap
# ============================================
Write-Host "[1/3] Installing SQLMap..." -ForegroundColor Yellow

$sqlmapCheck = Get-Command sqlmap -ErrorAction SilentlyContinue
if ($sqlmapCheck) {
    Write-Host "  SQLMap is already installed" -ForegroundColor Green
    $installed += "sqlmap"
} else {
    # Find Python
    $pythonCmd = $null
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
    } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3"
    } else {
        Write-Host "  Python not found! Cannot install SQLMap." -ForegroundColor Red
        $failed += "sqlmap"
    }
    
    if ($pythonCmd) {
        Write-Host "  Installing SQLMap via pip..." -ForegroundColor Cyan
        & $pythonCmd -m pip install sqlmap --user --quiet
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  SQLMap installed successfully!" -ForegroundColor Green
            $installed += "sqlmap"
        } else {
            Write-Host "  SQLMap installation failed!" -ForegroundColor Red
            $failed += "sqlmap"
        }
    }
}

Write-Host ""

# ============================================
# 2. Install WHOIS
# ============================================
Write-Host "[2/3] Installing WHOIS..." -ForegroundColor Yellow

$whoisCheck = Get-Command whois -ErrorAction SilentlyContinue
if ($whoisCheck) {
    Write-Host "  WHOIS is already installed" -ForegroundColor Green
    $installed += "whois"
} else {
    $whoisInstalled = $false
    
    # Method 1: Try Chocolatey
    $chocoCheck = Get-Command choco -ErrorAction SilentlyContinue
    if ($chocoCheck) {
        Write-Host "  Installing WHOIS via Chocolatey..." -ForegroundColor Cyan
        choco install whois -y --no-progress --limit-output 2>$null
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        $whoisCheck2 = Get-Command whois -ErrorAction SilentlyContinue
        if ($whoisCheck2) {
            Write-Host "  WHOIS installed successfully via Chocolatey!" -ForegroundColor Green
            $installed += "whois"
            $whoisInstalled = $true
        }
    }
    
    # Method 2: Try winget
    if (-not $whoisInstalled) {
        $wingetCheck = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCheck) {
            Write-Host "  Installing WHOIS via winget..." -ForegroundColor Cyan
            winget install Microsoft.Sysinternals.Whois --silent --accept-package-agreements 2>$null
            
            $whoisCheck2 = Get-Command whois -ErrorAction SilentlyContinue
            if ($whoisCheck2) {
                Write-Host "  WHOIS installed successfully via winget!" -ForegroundColor Green
                $installed += "whois"
                $whoisInstalled = $true
            }
        }
    }
    
    # Method 3: Download manually
    if (-not $whoisInstalled) {
        Write-Host "  Automatic WHOIS installation not available." -ForegroundColor Yellow
        Write-Host "  Downloading WHOIS manually..." -ForegroundColor Cyan
        
        $downloadUrl = "https://download.sysinternals.com/files/WhoIs.zip"
        $zipPath = "$env:TEMP\whois.zip"
        $extractPath = "$env:TEMP\whois"
        
        try {
            # Create temp directory
            if (-not (Test-Path $extractPath)) {
                New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
            }
            
            # Download WhoIs.zip
            Write-Host "  Downloading WhoIs.zip..." -ForegroundColor DarkYellow
            Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
            
            # Extract zip
            Write-Host "  Extracting..." -ForegroundColor DarkYellow
            Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
            
            # Find whois.exe
            $whoisExe = Get-ChildItem -Path $extractPath -Filter "whois.exe" -Recurse | Select-Object -First 1
            
            if ($whoisExe) {
                # Copy to user's local bin or System32 (requires admin)
                $userBinPath = "$env:USERPROFILE\bin"
                if (-not (Test-Path $userBinPath)) {
                    New-Item -ItemType Directory -Path $userBinPath -Force | Out-Null
                }
                
                Copy-Item -Path $whoisExe.FullName -Destination "$userBinPath\whois.exe" -Force
                
                # Add to user PATH
                $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
                if ($currentPath -notlike "*$userBinPath*") {
                    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$userBinPath", "User")
                }
                
                # Refresh PATH
                $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
                
                Write-Host "  WHOIS installed to: $userBinPath\whois.exe" -ForegroundColor Green
                $installed += "whois"
                $whoisInstalled = $true
            } else {
                Write-Host "  Could not find whois.exe in downloaded package" -ForegroundColor Red
                $failed += "whois"
            }
            
            # Clean up
            Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
            Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
            
        } catch {
            Write-Host "  Manual download failed: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "  You can download manually from: https://docs.microsoft.com/en-us/sysinternals/downloads/whois" -ForegroundColor Yellow
            $failed += "whois"
        }
    }
}

Write-Host ""

# ============================================
# 3. Verify Python Packages
# ============================================
Write-Host "[3/3] Verifying Python packages..." -ForegroundColor Yellow

$packages = @("colorama", "requests", "folium", "plotly", "reportlab")
$missingPackages = @()

foreach ($pkg in $packages) {
    $result = python -c "import $pkg" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $pkg" -ForegroundColor Green
        $installed += $pkg
    } else {
        Write-Host "  [X] $pkg - Installing..." -ForegroundColor Yellow
        pip install $pkg --user --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] $pkg installed" -ForegroundColor Green
            $installed += $pkg
        } else {
            Write-Host "  [X] $pkg failed" -ForegroundColor Red
            $missingPackages += $pkg
        }
    }
}

Write-Host ""

# ============================================
# Summary
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  POST-INSTALLATION SUMMARY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($installed.Count -gt 0) {
    Write-Host "Successfully installed/verified:" -ForegroundColor Green
    foreach ($item in $installed | Select-Object -Unique) {
        Write-Host "  [OK] $item" -ForegroundColor Green
    }
}

if ($failed.Count -gt 0 -or $missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "The following components need manual installation:" -ForegroundColor Yellow
    foreach ($item in $failed) {
        Write-Host "  [!] $item" -ForegroundColor Yellow
    }
    foreach ($item in $missingPackages) {
        Write-Host "  [!] $item (pip install $item)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DSTERMINAL is ready to use!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Wait a moment before exiting
Start-Sleep -Seconds 3