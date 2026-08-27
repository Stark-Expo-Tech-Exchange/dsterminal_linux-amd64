# Check Python (No admin required)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Checking Python Installation" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = & python --version 2>$null
    Write-Host "Python is already installed" -ForegroundColor Green
    Write-Host "Version: $pythonVersion" -ForegroundColor Cyan
    pause
    exit 0
}

if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonVersion = & python3 --version 2>$null
    Write-Host "Python is already installed" -ForegroundColor Green
    Write-Host "Version: $pythonVersion" -ForegroundColor Cyan
    pause
    exit 0
}

Write-Host "Python is not installed." -ForegroundColor Red
Write-Host ""
Write-Host "To install Python without admin rights:" -ForegroundColor Cyan
Write-Host ""

Write-Host "Option 1: Download from Microsoft Store (Recommended)" -ForegroundColor Green
Write-Host "  - Open Microsoft Store" -ForegroundColor White
Write-Host "  - Search for 'Python 3.11'" -ForegroundColor White
Write-Host "  - Click Install" -ForegroundColor White
Write-Host ""

Write-Host "Option 2: Download from python.org" -ForegroundColor Green
Write-Host "  - Visit: https://python.org/downloads" -ForegroundColor White
Write-Host "  - Download Windows installer" -ForegroundColor White
Write-Host "  - Check 'Add Python to PATH' during installation" -ForegroundColor White
Write-Host ""

Write-Host "Option 3: Install via winget (if available)" -ForegroundColor Green
Write-Host "  - Run: winget install Python.Python.3.11" -ForegroundColor White
Write-Host ""

$openBrowser = Read-Host "Open Python download page? (y/n)"
if ($openBrowser -eq 'y') {
    Start-Process "https://python.org/downloads"
}

Write-Host ""
Write-Host "After installing Python, re-run this installer." -ForegroundColor Yellow
pause
exit 1