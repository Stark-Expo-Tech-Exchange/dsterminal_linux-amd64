# build.ps1 - Simplified Build Script
param(
    [switch]$Clean,
    [switch]$BuildPy,
    [switch]$BuildInstaller,
    [switch]$BuildPortable,
    [switch]$Full
)

$ErrorActionPreference = "Continue"

Write-Host "DSTerminal Build Script v4.0.0.113" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

if ($Full) {
    $Clean = $true
    $BuildPy = $true
    $BuildInstaller = $true
    $BuildPortable = $true
}

if ($Clean) {
    Write-Host "[1/4] Cleaning build artifacts..." -ForegroundColor Yellow
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue }
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue }
    if (Test-Path "installer_output") { Remove-Item -Recurse -Force "installer_output" -ErrorAction SilentlyContinue }
    Get-ChildItem "*.spec" | Where-Object { $_.Name -ne "dsterminal_win-4.0.0.113_x64-amd64.spec" } | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path "." -Directory -Filter "__pycache__" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Clean complete!" -ForegroundColor Green
    Write-Host ""
}

if ($BuildPy) {
    Write-Host "[2/4] Building Python executable..." -ForegroundColor Yellow
    
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt --upgrade
    }
    
    pip install netifaces --upgrade
    pip install flask flask-socketio python-socketio psutil --upgrade
    
    $pyinstaller = Get-Command "pyinstaller" -ErrorAction SilentlyContinue
    if (-not $pyinstaller) {
        pip install pyinstaller
    }
    
    # Build with proper flags to bundle all dependencies
    Write-Host "Building with PyInstaller..." -ForegroundColor Cyan
    
    pyinstaller --onefile --windowed `
        --name "dsterminal_win-4.0.0.113_x64-amd64" `
        --add-data "static;static" `
        --add-data "3486-removebg-preview.ico;." `
        --hidden-import psutil `
        --hidden-import netifaces `
        --hidden-import flask `
        --hidden-import flask_socketio `
        --hidden-import socketio `
        --hidden-import engineio `
        --hidden-import werkzeug `
        --hidden-import werkzeug.wsgi `
        --hidden-import jinja2 `
        --hidden-import markupsafe `
        --hidden-import datetime `
        --hidden-import json `
        --hidden-import hashlib `
        --hidden-import threading `
        --hidden-import subprocess `
        --hidden-import shutil `
        --hidden-import platform `
        --hidden-import webbrowser `
        --hidden-import random `
        --hidden-import time `
        --hidden-import os `
        --hidden-import sys `
        --hidden-import logging `
        --hidden-import contextlib `
        --hidden-import io `
        --hidden-import colorama `
        --hidden-import colorama.ansitowin32 `
        --hidden-import colorama.win32 `
        --hidden-import colorama.initialise `
        --collect-all flask `
        --collect-all flask_socketio `
        --collect-all werkzeug `
        --collect-all jinja2 `
        --collect-all markupsafe `
        --collect-all python_socketio `
        --collect-all python_engineio `
        --exclude-module pandas `
        --exclude-module opencv-python `
        --exclude-module cv2 `
        --exclude-module torch `
        --exclude-module tensorflow `
        --exclude-module scipy `
        --exclude-module sklearn `
        --exclude-module PyQt5 `
        --exclude-module PyQt6 `
        --exclude-module tkinter `
        --exclude-module test `
        --exclude-module pytest `
        --exclude-module setuptools `
        --exclude-module pip `
        --exclude-module _tkinter `
        --exclude-module tkinter `
        --exclude-module distutils `
        --exclude-module wheel `
        --log-level ERROR `
        dsterminal.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Executable built successfully!" -ForegroundColor Green
        Write-Host "Location: dist\dsterminal_win-4.0.0.113_x64-amd64.exe" -ForegroundColor Green
        
        if (Test-Path "dist\dsterminal_win-4.0.0.113_x64-amd64.exe") {
            $exeSize = [math]::Round((Get-Item "dist\dsterminal_win-4.0.0.113_x64-amd64.exe").Length / 1MB, 2)
            Write-Host "File size: $exeSize MB" -ForegroundColor Green
            
            # Test the executable
            Write-Host "Testing executable..." -ForegroundColor Cyan
            $testResult = & "dist\dsterminal_win-4.0.0.113_x64-amd64.exe" --help 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Executable test passed!" -ForegroundColor Green
            } else {
                Write-Host "Executable test failed (this is normal for GUI apps)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "Failed to build executable!" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

if ($BuildInstaller) {
    Write-Host "[3/4] Building Inno Setup installer..." -ForegroundColor Yellow
    
    if (-not (Test-Path "dist\dsterminal_win-4.0.0.113_x64-amd64.exe")) {
        Write-Host "ERROR: Executable not found!" -ForegroundColor Red
        exit 1
    }
    
    $iscc = Get-Command "iscc" -ErrorAction SilentlyContinue
    if (-not $iscc) {
        $paths = @(
            "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
            "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
            "${env:ProgramFiles}\Inno Setup 5\ISCC.exe",
            "${env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe"
        )
        foreach ($path in $paths) {
            if (Test-Path $path) {
                $iscc = $path
                break
            }
        }
    }
    
    if (-not $iscc) {
        Write-Host "Inno Setup not found! Skipping installer." -ForegroundColor Yellow
        Write-Host "Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    } else {
        if (-not (Test-Path "dsterminal_installer.iss")) {
            Write-Host "ERROR: Installer script not found!" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "Using ISCC: $iscc" -ForegroundColor Cyan
        & $iscc "dsterminal_installer.iss"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Installer built successfully!" -ForegroundColor Green
            $installer = Get-ChildItem -Path "installer_output" -Filter "*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($installer) {
                $size = [math]::Round($installer.Length / 1MB, 2)
                Write-Host "Location: installer_output\$($installer.Name) ($size MB)" -ForegroundColor Green
            }
        } else {
            Write-Host "Failed to build installer!" -ForegroundColor Red
        }
    }
    Write-Host ""
}

if ($BuildPortable) {
    Write-Host "[4/4] Creating portable version..." -ForegroundColor Yellow
    
    $version = "4.0.0.113"
    $portableDir = "DSTerminal_Portable_v$version"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    
    if (Test-Path $portableDir) { Remove-Item -Recurse -Force $portableDir -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Path $portableDir -Force | Out-Null
    
    if (Test-Path "dist\dsterminal_win-4.0.0.113_x64-amd64.exe") {
        Copy-Item "dist\dsterminal_win-4.0.0.113_x64-amd64.exe" "$portableDir\dsterminal.exe" -Force
        Write-Host "Copied executable" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Executable not found!" -ForegroundColor Red
        exit 1
    }
    
    # Create launcher batch file
    $batContent = '@echo off
title DSTerminal Portable v' + $version + '
echo ========================================
echo   DSTERMINAL PORTABLE v' + $version + '
echo ========================================
echo.
echo Starting DSTerminal...
echo.
echo Workspace will be created in: %APPDATA%\DSTerminal\workspace
echo.
dsterminal.exe
pause'
    $batContent | Out-File -FilePath "$portableDir\launch_dsterminal.bat" -Encoding ASCII
    
    # Copy icon
    if (Test-Path "3486-removebg-preview.ico") {
        Copy-Item "3486-removebg-preview.ico" "$portableDir\" -Force
    }
    
    # Create README
    $readme = @"
DSTERMINAL PORTABLE v$version
========================================

This is the portable version of DSTerminal.

HOW TO USE:
1. Run launch_dsterminal.bat
2. The dashboard will open in your browser
3. Workspace data is stored in: %APPDATA%\DSTerminal\workspace

SYSTEM REQUIREMENTS:
- Windows 10 or later
- 4GB RAM recommended
- 200MB free disk space

NOTES:
- No installation required
- No admin privileges needed (except for some security features)
- All data is saved in your user profile

SUPPORT:
https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest/issues

"@
    $readme | Out-File -FilePath "$portableDir\README.txt" -Encoding ASCII
    
    if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
        $zipName = "DSTerminal_Portable_v${version}_${timestamp}.zip"
        Compress-Archive -Path "$portableDir\*" -DestinationPath $zipName -Force
        $zipSize = [math]::Round((Get-Item $zipName).Length / 1MB, 2)
        Write-Host "ZIP created: $zipName ($zipSize MB)" -ForegroundColor Green
    }
    
    Write-Host "Portable version created in: $portableDir" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build complete!" -ForegroundColor Green
Write-Host ""

if (-not $Clean -and -not $BuildPy -and -not $BuildInstaller -and -not $BuildPortable -and -not $Full) {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\build.ps1 -Full              # Build everything" -ForegroundColor White
    Write-Host "  .\build.ps1 -BuildPy           # Build executable only" -ForegroundColor White
    Write-Host "  .\build.ps1 -BuildInstaller    # Build installer only" -ForegroundColor White
    Write-Host "  .\build.ps1 -BuildPortable     # Build portable only" -ForegroundColor White
    Write-Host "  .\build.ps1 -Clean             # Clean only" -ForegroundColor White
    Write-Host ""
}

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run the installer or portable version" -ForegroundColor White
Write-Host "  2. Open http://localhost:5000 in your browser" -ForegroundColor White
Write-Host "  3. Start using DSTerminal!" -ForegroundColor White
Write-Host ""