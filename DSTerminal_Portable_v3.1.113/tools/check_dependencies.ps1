# Simple dependency checker - No complex quotes
Write-Host "DSTerminal Dependency Check" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

$missing = @()

# Check nmap
$nmapCheck = Get-Command nmap -ErrorAction SilentlyContinue
if ($nmapCheck) {
    Write-Host "  [OK] nmap is installed" -ForegroundColor Green
} else {
    Write-Host "  [X] nmap is NOT installed" -ForegroundColor Red
    $missing += "nmap"
}

# Check whois
$whoisCheck = Get-Command whois -ErrorAction SilentlyContinue
if ($whoisCheck) {
    Write-Host "  [OK] whois is installed" -ForegroundColor Green
} else {
    Write-Host "  [X] whois is NOT installed" -ForegroundColor Red
    $missing += "whois"
}

# Check sqlmap
$sqlmapCheck = Get-Command sqlmap -ErrorAction SilentlyContinue
if ($sqlmapCheck) {
    Write-Host "  [OK] sqlmap is installed" -ForegroundColor Green
} else {
    Write-Host "  [X] sqlmap is NOT installed" -ForegroundColor Red
    $missing += "sqlmap"
}

# Check Python
$pythonCmd = $null
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCheck) {
    $pythonCmd = "python"
    Write-Host "  [OK] python is installed" -ForegroundColor Green
} else {
    $pythonCheck3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($pythonCheck3) {
        $pythonCmd = "python3"
        Write-Host "  [OK] python3 is installed" -ForegroundColor Green
    } else {
        Write-Host "  [X] python is NOT installed" -ForegroundColor Red
        $missing += "python"
    }
}

# Check Python packages
if ($pythonCmd) {
    Write-Host ""
    Write-Host "Checking Python packages..." -ForegroundColor Cyan
    
    $packages = @("colorama", "requests", "folium", "plotly", "reportlab")
    foreach ($pkg in $packages) {
        $checkCommand = "$pythonCmd -c `"import $pkg`""
        Invoke-Expression $checkCommand 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] $pkg" -ForegroundColor Green
        } else {
            Write-Host "  [X] $pkg" -ForegroundColor Red
            $missing += $pkg
        }
    }
}

# ===================================
# In check_dependencies.ps1, add this check
Write-Host "Checking SQLMap..." -ForegroundColor Yellow
$sqlmapCheck = Get-Command sqlmap -ErrorAction SilentlyContinue
if ($sqlmapCheck) {
    Write-Host "  [OK] sqlmap is installed" -ForegroundColor Green
} else {
    # Check if SQLMap is in the bundled location
    $sqlmapPath = "$env:USERPROFILE\DSTerminal\tools\sqlmap\sqlmap.py"
    if (Test-Path $sqlmapPath) {
        Write-Host "  [OK] sqlmap is installed (bundled)" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] sqlmap is not installed" -ForegroundColor Red
    }
}
# ===================================
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
if ($missing.Count -eq 0) {
    Write-Host "  All dependencies satisfied" -ForegroundColor Green
    exit 0
} else {
    $missingText = $missing -join ", "
    Write-Host "  Missing dependencies: $missingText" -ForegroundColor Yellow
    exit 1
}