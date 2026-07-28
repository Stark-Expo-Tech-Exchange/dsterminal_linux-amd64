@echo off
title DSTERMINAL Dependency Installer
color 0A

echo ========================================
echo   DSTERMINAL Dependency Installer
echo ========================================
echo.

:: Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] This installer needs Administrator privileges for some tools.
    echo [*] Requesting elevation...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [*] Running with Administrator privileges.
echo.

:: ============================================
:: Install Chocolatey (if missing)
:: ============================================
echo [1/4] Checking Chocolatey...
where choco >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Installing Chocolatey...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    echo [*] Refreshing environment...
    refreshenv >nul 2>nul
) else (
    echo [*] Chocolatey already installed.
)

echo.

:: ============================================
:: Install Nmap
:: ============================================
echo [2/4] Installing Nmap...
where nmap >nul 2>nul
if %errorlevel% neq 0 (
    choco install nmap -y --no-progress
) else (
    echo [*] Nmap already installed.
)

echo.

:: ============================================
:: Install SQLMap (via pip)
:: ============================================
echo [3/4] Installing SQLMap...
where sqlmap >nul 2>nul
if %errorlevel% neq 0 (
    pip install sqlmap --quiet
) else (
    echo [*] SQLMap already installed.
)

echo.

:: ============================================
:: Install Python packages
:: ============================================
echo [4/4] Installing Python packages...
pip install colorama requests folium plotly reportlab --quiet

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Installed:
echo   - Chocolatey (package manager)
echo   - Nmap (network scanner)
echo   - SQLMap (SQL injection tool)
echo   - Python packages (colorama, requests, folium, plotly, reportlab)
echo.
echo [*] You may need to restart your terminal for changes to take effect.
echo.
pause