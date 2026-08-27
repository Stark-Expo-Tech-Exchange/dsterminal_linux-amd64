# Install Chocolatey Package Manager - With Admin Elevation & Alternatives
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installing Chocolatey Package Manager" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
$chocoCheck = Get-Command choco -ErrorAction SilentlyContinue
if ($chocoCheck) {
    $chocoVersion = & choco --version 2>$null
    Write-Host "Chocolatey is already installed" -ForegroundColor Green
    Write-Host "Version: $chocoVersion" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 0
}

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "Chocolatey requires Administrator privileges." -ForegroundColor Yellow
    Write-Host "Attempting to elevate to Administrator..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $scriptPath = $MyInvocation.MyCommand.Path
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "powershell.exe"
        $psi.Arguments = "-ExecutionPolicy Bypass -File `"$scriptPath`""
        $psi.Verb = "runas"
        $psi.WindowStyle = "Normal"
        
        [System.Diagnostics.Process]::Start($psi)
        exit
    } catch {
        Write-Host "Failed to elevate. Please run PowerShell as Administrator manually." -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host "Running with Administrator privileges." -ForegroundColor Green
Write-Host ""

# ============================================
# Method 1: Try official Chocolatey install
# ============================================
Write-Host "[Method 1] Trying official Chocolatey installation..." -ForegroundColor Yellow

try {
    # Use the official install script with alternative download method
    $installScript = @'
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072

# Try multiple download URLs
$urls = @(
    'https://community.chocolatey.org/install.ps1',
    'https://chocolatey.org/install.ps1',
    'https://raw.githubusercontent.com/chocolatey/choco/master/redirects/install.ps1'
)

$downloaded = $false
foreach ($url in $urls) {
    try {
        Write-Host "Trying: $url"
        $scriptContent = (New-Object System.Net.WebClient).DownloadString($url)
        $downloaded = $true
        break
    } catch {
        Write-Host "Failed: $url"
    }
}

if ($downloaded) {
    Invoke-Expression $scriptContent
    exit 0
} else {
    Write-Host "All download methods failed."
    exit 1
}
'@
    
    # Execute the install script
    powershell -ExecutionPolicy Bypass -Command $installScript
    
    # Refresh environment
    foreach($level in "Machine", "User") {
        [Environment]::GetEnvironmentVariables($level).GetEnumerator() | ForEach-Object {
            Set-Content "env:$($_.Key)" $_.Value
        }
    }
    
    # Verify
    $chocoVersion = & choco --version 2>$null
    if ($chocoVersion) {
        Write-Host ""
        Write-Host "SUCCESS: Chocolatey installed!" -ForegroundColor Green
        Write-Host "Version: $chocoVersion" -ForegroundColor Cyan
        pause
        exit 0
    }
} catch {
    Write-Host "Method 1 failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# ============================================
# Method 2: Manual download instructions
# ============================================
Write-Host "[Method 2] Manual installation required" -ForegroundColor Yellow
Write-Host ""
Write-Host "The automated Chocolatey installation is currently blocked." -ForegroundColor Red
Write-Host ""
Write-Host "Please install Chocolatey manually using one of these methods:" -ForegroundColor Cyan
Write-Host ""

Write-Host "Option A - Download installer script manually:" -ForegroundColor Green
Write-Host "  1. Open browser to: https://chocolatey.org/install" -ForegroundColor White
Write-Host "  2. Copy the installation command" -ForegroundColor White
Write-Host "  3. Run in Administrator PowerShell:" -ForegroundColor White
Write-Host "     Set-ExecutionPolicy Bypass -Scope Process -Force;" -ForegroundColor Yellow
Write-Host "     [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072;" -ForegroundColor Yellow
Write-Host "     iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" -ForegroundColor Yellow
Write-Host ""

Write-Host "Option B - Download and run locally:" -ForegroundColor Green
Write-Host "  1. Download install.ps1 from: https://chocolatey.org/install.ps1" -ForegroundColor White
Write-Host "  2. Run in Administrator PowerShell: .\install.ps1" -ForegroundColor White
Write-Host ""

Write-Host "Option C - Skip Chocolatey (Recommended for DSTERMINAL):" -ForegroundColor Green
Write-Host "  Most DSTERMINAL dependencies can be installed via pip without Chocolatey." -ForegroundColor White
Write-Host "  Run: .\install_all_dependencies.ps1" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Choose option (A/B/C)"
Write-Host ""

if ($choice -eq 'A' -or $choice -eq 'a') {
    Start-Process "https://chocolatey.org/install"
    Write-Host "Installation page opened. Follow the instructions there." -ForegroundColor Cyan
} elseif ($choice -eq 'B' -or $choice -eq 'b') {
    $downloadUrl = "https://chocolatey.org/install.ps1"
    $outputPath = "$env:TEMP\install-choco.ps1"
    
    Write-Host "Downloading install script..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath -UseBasicParsing
        Write-Host "Downloaded to: $outputPath" -ForegroundColor Green
        Write-Host ""
        Write-Host "Now run in Administrator PowerShell: $outputPath" -ForegroundColor Yellow
    } catch {
        Write-Host "Download failed. Please download manually." -ForegroundColor Red
        Start-Process "https://chocolatey.org/install.ps1"
    }
} else {
    Write-Host "Skipping Chocolatey installation." -ForegroundColor Yellow
    Write-Host "Continue with pip-based installations using: .\install_all_dependencies.ps1" -ForegroundColor Cyan
}

Write-Host ""
pause