@echo off
echo DSTerminal Dependency Check
echo ==========================
echo.

set MISSING=

:: Check nmap
where nmap >nul 2>nul
if %errorlevel%==0 (
    echo   [OK] nmap is installed
) else (
    echo   [X] nmap is NOT installed
    set MISSING=!MISSING! nmap
)

:: Check whois
where whois >nul 2>nul
if %errorlevel%==0 (
    echo   [OK] whois is installed
) else (
    echo   [X] whois is NOT installed
    set MISSING=!MISSING! whois
)

:: Check sqlmap
where sqlmap >nul 2>nul
if %errorlevel%==0 (
    echo   [OK] sqlmap is installed
) else (
    echo   [X] sqlmap is NOT installed
    set MISSING=!MISSING! sqlmap
)

:: Check python
where python >nul 2>nul
if %errorlevel%==0 (
    echo   [OK] python is installed
) else (
    where python3 >nul 2>nul
    if %errorlevel%==0 (
        echo   [OK] python3 is installed
    ) else (
        echo   [X] python is NOT installed
        set MISSING=!MISSING! python
    )
)

echo.
echo Summary:
if "%MISSING%"=="" (
    echo   All dependencies satisfied
    exit /b 0
) else (
    echo   Missing dependencies: %MISSING%
    exit /b 1
)