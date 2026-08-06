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
    
    $pyinstaller = Get-Command "pyinstaller" -ErrorAction SilentlyContinue
    if (-not $pyinstaller) {
        pip install pyinstaller
    }
    
    $specFile = "dsterminal_win-4.0.0.113_x64-amd64.spec"
    if (-not (Test-Path $specFile)) {
        Write-Host "ERROR: Spec file not found!" -ForegroundColor Red
        exit 1
    }
    
    pyinstaller $specFile --clean --noconfirm
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Executable built successfully!" -ForegroundColor Green
        Write-Host "Location: dist\dsterminal_win-4.0.0.113_x64-amd64.exe" -ForegroundColor Green
        
        if (Test-Path "dist\dsterminal_win-4.0.0.113_x64-amd64.exe") {
            $exeSize = [math]::Round((Get-Item "dist\dsterminal_win-4.0.0.113_x64-amd64.exe").Length / 1MB, 2)
            Write-Host "File size: $exeSize MB" -ForegroundColor Green
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
            "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
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
    }
    
    $batContent = '@echo off
title DSTerminal Portable v' + $version + '
echo ========================================
echo   DSTERMINAL PORTABLE v' + $version + '
echo ========================================
echo.
echo Starting DSTerminal...
echo.
dsterminal.exe
pause'
    $batContent | Out-File -FilePath "$portableDir\launch_dsterminal.bat" -Encoding ASCII
    
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
