@echo off
echo Installing Nmap...
echo.

:: Check if nmap is already installed
where nmap >nul 2>nul
if %errorlevel%==0 (
    echo Nmap is already installed
    exit /b 0
)

:: Check if Chocolatey is installed
where choco >nul 2>nul
if %errorlevel%==0 (
    echo Installing Nmap via Chocolatey...
    choco install nmap -y --no-progress
    echo Nmap installed successfully!
    exit /b 0
)

:: If no Chocolatey, try direct download
echo Chocolatey not found. Downloading Nmap directly...

:: Download Nmap installer
powershell -Command "Invoke-WebRequest -Uri 'https://nmap.org/dist/nmap-7.95-setup.exe' -OutFile '%TEMP%\nmap-setup.exe'"

:: Run installer silently
echo Running Nmap installer...
start /wait %TEMP%\nmap-setup.exe /S

echo Nmap installation complete!
pause