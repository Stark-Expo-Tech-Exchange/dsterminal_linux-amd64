# build_all.ps1
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Building Exploit Scanner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Build executable
Write-Host "Building executable..." -ForegroundColor Yellow
python -m pip install pyinstaller
pyinstaller --onefile exploit_scanner.py

if (-not (Test-Path "dist\exploit_scanner.exe")) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Executable built successfully!" -ForegroundColor Green

# 2. Create portable ZIP
Write-Host "Creating portable ZIP..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "portable" -Force | Out-Null
Copy-Item "dist\exploit_scanner.exe" "portable\"
Copy-Item "*.json" "portable\" -ErrorAction SilentlyContinue
Compress-Archive -Path "portable\*" -DestinationPath "ExploitScanner_Portable.zip" -Force
Remove-Item "portable" -Recurse -Force
Write-Host "Portable ZIP created: ExploitScanner_Portable.zip" -ForegroundColor Green

# 3. Create installer
Write-Host "Creating installer script..." -ForegroundColor Yellow
@"
@echo off
echo Installing Exploit Scanner...
mkdir "%ProgramFiles%\ExploitScanner" 2>nul
copy "dist\exploit_scanner.exe" "%ProgramFiles%\ExploitScanner\"
powershell -command " = New-Object -comObject WScript.Shell;  = .CreateShortcut('%UserProfile%\Desktop\Exploit Scanner.lnk'); .TargetPath = '%ProgramFiles%\ExploitScanner\exploit_scanner.exe'; .Save()"
echo Installation complete!
pause
