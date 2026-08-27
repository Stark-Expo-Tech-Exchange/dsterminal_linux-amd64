@echo off
title DSTERMINAL - Install Remaining Dependencies
color 0A

echo ========================================
echo   DSTERMINAL - Installing Remaining Dependencies
echo ========================================
echo.

echo [1/2] Installing SQLMap...
echo.
pip install sqlmap
if %errorlevel%==0 (
    echo   [OK] SQLMap installed successfully
) else (
    echo   [X] SQLMap installation failed
)
echo.

echo [2/2] Installing WHOIS...
echo.
where choco >nul 2>nul
if %errorlevel%==0 (
    echo Installing via Chocolatey...
    choco install whois -y --no-progress
) else (
    where winget >nul 2>nul
    if %errorlevel%==0 (
        echo Installing via winget...
        winget install Microsoft.Sysinternals.Whois --silent --accept-package-agreements
    ) else (
        echo [WARN] No package manager found. Please install WHOIS manually:
        echo        https://docs.microsoft.com/en-us/sysinternals/downloads/whois
    )
)
echo.

echo ========================================
echo   Installation Summary
echo ========================================
echo.
echo Verifying installations...
echo.

where sqlmap >nul 2>nul
if %errorlevel%==0 (
    echo   [OK] SQLMap is installed
) else (
    echo   [X] SQLMap is NOT installed
)

where whois >nul 2>nul
if %errorlevel%==0 (
    echo   [OK] WHOIS is installed
) else (
    echo   [WARN] WHOIS is NOT installed (optional)
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo DSTERMINAL Cyber-OPs is ready to use!
echo.
echo To start DSTERMINAL:
echo   ...
echo   Right click DSTerminal Cyber-Ops as an Admin
echo.
pause