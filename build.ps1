<<<<<<< HEAD
﻿# build.ps1 - Complete build script with all dependencies
param(
    [switch]$Clean,
    [switch]$BuildPy,
    [switch]$BuildInstaller,
    [switch]$BuildPortable,
    [switch]$Full
)

$ErrorActionPreference = "Continue"

Write-Host "DSTerminal Build Script v3.1.113" -ForegroundColor Cyan
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
    
    # ONLY delete auto-generated spec files, preserve your custom one!
    Get-ChildItem "*.spec" | Where-Object { $_.Name -ne "dsterminal_win-3.1.113_x64-amd64.spec" } | Remove-Item -Force -ErrorAction SilentlyContinue
    
    # Clean up __pycache__
    Get-ChildItem -Path "." -Directory -Filter "__pycache__" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "Clean complete! (Preserved custom .spec file)" -ForegroundColor Green
    Write-Host ""
}

if ($BuildPy) {
    Write-Host "[2/4] Building Python executable..." -ForegroundColor Yellow

    # Ensure all dependencies are installed
    Write-Host "Installing all dependencies from requirements.txt..." -ForegroundColor Yellow
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt --upgrade
    } else {
        Write-Host "⚠️ requirements.txt not found! Installing common dependencies..." -ForegroundColor Yellow
        pip install requests beautifulsoup4 rich colorama tqdm psutil pyfiglet reportlab Pillow qrcode opencv-python-headless numpy cryptography pycryptodome folium plotly geopy netifaces whois GitPython pytz matplotlib prompt-toolkit
    }

    # Ensure netifaces is specifically installed
    Write-Host "Ensuring netifaces is installed..." -ForegroundColor Yellow
    pip install netifaces --upgrade

=======
# build.ps1
param(
    [switch]$Clean,
    [switch]$BuildPy,
    [switch]$BuildInstaller
)

$ErrorActionPreference = "Stop"

Write-Host "DSTerminal Build Script" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

# Clean build artifacts
if ($Clean) {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue }
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue }
    if (Test-Path "*.exe") { Remove-Item -Force "*.exe" -ErrorAction SilentlyContinue }
    Write-Host "Clean complete!" -ForegroundColor Green
}

# Build Python executable
if ($BuildPy) {
    Write-Host "Building Python executable..." -ForegroundColor Yellow

    # Check if PyInstaller is installed
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    $pyinstaller = Get-Command "pyinstaller" -ErrorAction SilentlyContinue
    if (-not $pyinstaller) {
        Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
        pip install pyinstaller
    }

<<<<<<< HEAD
    $specFile = "dsterminal_win-3.1.113_x64-amd64.spec"
    if (-not (Test-Path $specFile)) {
        Write-Host "ERROR: Spec file not found: $specFile" -ForegroundColor Red
        exit 1
    }

    Write-Host "Using spec file: $specFile" -ForegroundColor Cyan
    Write-Host "Running PyInstaller..." -ForegroundColor Gray
    
    # Run PyInstaller with the spec file
    pyinstaller $specFile --clean --noconfirm

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Executable built successfully!" -ForegroundColor Green
        Write-Host "Location: dist\dsterminal_win-3.1.113_x64-amd64.exe" -ForegroundColor Green
        
        # Verify the executable exists
        if (Test-Path "dist\dsterminal_win-3.1.113_x64-amd64.exe") {
            $exeSize = [math]::Round((Get-Item "dist\dsterminal_win-3.1.113_x64-amd64.exe").Length / 1MB, 2)
            Write-Host "File size: $exeSize MB" -ForegroundColor Green
            
            # Copy dependencies to dist as fallback
            Write-Host "Copying dependencies to dist directory (fallback)..." -ForegroundColor Yellow
            
            $distDir = "dist\dsterminal_win-3.1.113_x64-amd64"
            
            # Copy netifaces
            try {
                $netifacesPath = & python -c "import netifaces; import os; print(os.path.dirname(netifaces.__file__))" 2>$null
                if ($netifacesPath -and (Test-Path $netifacesPath)) {
                    $distNetifacesDir = Join-Path $distDir "netifaces"
                    if (-not (Test-Path $distNetifacesDir)) {
                        New-Item -ItemType Directory -Path $distNetifacesDir -Force | Out-Null
                    }
                    Copy-Item -Path "$netifacesPath\*" -Destination $distNetifacesDir -Recurse -Force -ErrorAction SilentlyContinue
                    Write-Host "  ✓ Copied netifaces" -ForegroundColor Green
                } else {
                    Write-Host "  ⚠️ netifaces not found" -ForegroundColor Yellow
                }
            } catch {
                Write-Host ("  ⚠️ Error copying netifaces: {0}" -f $_.Exception.Message) -ForegroundColor Yellow
            }
            
            # Copy tqdm
            try {
                $tqdmPath = & python -c "import tqdm; import os; print(os.path.dirname(tqdm.__file__))" 2>$null
                if ($tqdmPath -and (Test-Path $tqdmPath)) {
                    $distTqdmDir = Join-Path $distDir "tqdm"
                    if (-not (Test-Path $distTqdmDir)) {
                        New-Item -ItemType Directory -Path $distTqdmDir -Force | Out-Null
                    }
                    Copy-Item -Path "$tqdmPath\*" -Destination $distTqdmDir -Recurse -Force -ErrorAction SilentlyContinue
                    Write-Host "  ✓ Copied tqdm" -ForegroundColor Green
                } else {
                    Write-Host "  ⚠️ tqdm not found" -ForegroundColor Yellow
                }
            } catch {
                Write-Host ("  ⚠️ Error copying tqdm: {0}" -f $_.Exception.Message) -ForegroundColor Yellow
            }
            
            # Copy critical packages
            $criticalPackages = @('requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna', 'rich', 'colorama')
            foreach ($pkg in $criticalPackages) {
                try {
                    $pkgPath = & python -c "import $pkg; import os; print(os.path.dirname($pkg.__file__))" 2>$null
                    if ($pkgPath -and (Test-Path $pkgPath)) {
                        $distPkgDir = Join-Path $distDir $pkg
                        if (-not (Test-Path $distPkgDir)) {
                            New-Item -ItemType Directory -Path $distPkgDir -Force | Out-Null
                        }
                        Copy-Item -Path "$pkgPath\*" -Destination $distPkgDir -Recurse -Force -ErrorAction SilentlyContinue
                        Write-Host "  ✓ Copied $pkg" -ForegroundColor Green
                    } else {
                        Write-Host "  ⚠️ $pkg not found" -ForegroundColor Yellow
                    }
                } catch {
                    Write-Host ("  ⚠️ Error copying {0}: {1}" -f $pkg, $_.Exception.Message) -ForegroundColor Yellow
                }
            }
            
            # Copy any .pyd files from site-packages root
            try {
                $sitePackages = & python -c "import site; print(site.getsitepackages()[0])" 2>$null
                if ($sitePackages -and (Test-Path $sitePackages)) {
                    Copy-Item -Path "$sitePackages\*.pyd" -Destination $distDir -Force -ErrorAction SilentlyContinue
                    Write-Host "  ✓ Copied .pyd files" -ForegroundColor Green
                }
            } catch {
                Write-Host ("  ⚠️ Error copying .pyd files: {0}" -f $_.Exception.Message) -ForegroundColor Yellow
            }
            
            Write-Host "✅ Dependency copy complete" -ForegroundColor Green
        }
=======
    # Ensure required directories exist
    if (-not (Test-Path "installer_assets")) { New-Item -ItemType Directory -Path "installer_assets" -Force }
    if (-not (Test-Path "docs")) { New-Item -ItemType Directory -Path "docs" -Force }
    if (-not (Test-Path "templates")) { New-Item -ItemType Directory -Path "templates" -Force }

    # Build with PyInstaller
    pyinstaller --onefile --name "dsterminal_win-2.0.59_x64-amd64" `
        --add-data "docs;docs" `
        --add-data "templates;templates" `
        --icon "installer_assets\icon.ico" `
        --version-file "version_info.txt" `
        --noconfirm `
        dsterminal.py

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Executable built successfully!" -ForegroundColor Green
        Write-Host "Location: dist\dsterminal_win-2.0.59_x64-amd64.exe" -ForegroundColor Green
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    } else {
        Write-Host "Failed to build executable!" -ForegroundColor Red
        exit 1
    }
<<<<<<< HEAD
    Write-Host ""
}

if ($BuildInstaller) {
    Write-Host "[3/4] Building Inno Setup installer..." -ForegroundColor Yellow

    if (-not (Test-Path "dist\dsterminal_win-3.1.113_x64-amd64.exe")) {
        Write-Host "ERROR: Executable not found! Build it first with -BuildPy" -ForegroundColor Red
        exit 1
    }

    $iscc = Get-Command "iscc" -ErrorAction SilentlyContinue
    if (-not $iscc) {
=======
}

# Build Inno Setup installer
if ($BuildInstaller) {
    Write-Host "Building Inno Setup installer..." -ForegroundColor Yellow

    # Check if ISCC is in PATH
    $iscc = Get-Command "iscc" -ErrorAction SilentlyContinue
    if (-not $iscc) {
        # Try common installation paths
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        $paths = @(
            "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
            "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
            "${env:ProgramFiles}\Inno Setup 5\ISCC.exe",
            "${env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe"
        )
<<<<<<< HEAD
=======

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        foreach ($path in $paths) {
            if (Test-Path $path) {
                $iscc = $path
                break
            }
        }
    }

    if (-not $iscc) {
<<<<<<< HEAD
        Write-Host "Inno Setup not found! Skipping installer." -ForegroundColor Yellow
        Write-Host "Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    } else {
        $installerScript = "dsterminal_installer.iss"
        
        if (-not (Test-Path $installerScript)) {
            Write-Host "ERROR: Installer script not found!" -ForegroundColor Red
            exit 1
        }

        Write-Host "Compiling installer..." -ForegroundColor Gray
        & $iscc $installerScript

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
    
    $version = "3.1.113"
    $portableDir = "DSTerminal_Portable_v$version"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    
    # Clean up old portable directory if it exists
    if (Test-Path $portableDir) { Remove-Item -Recurse -Force $portableDir -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Path $portableDir -Force | Out-Null
    
    # Copy executable
    if (Test-Path "dist\dsterminal_win-3.1.113_x64-amd64.exe") {
        Copy-Item "dist\dsterminal_win-3.1.113_x64-amd64.exe" "$portableDir\dsterminal.exe" -Force
        Write-Host "Copied executable" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Executable not found in dist folder!" -ForegroundColor Yellow
    }
    
    # Copy all dependency folders from dist to portable
    $distDir = "dist\dsterminal_win-3.1.113_x64-amd64"
    $dependencyFolders = @("netifaces", "tqdm", "requests", "urllib3", "certifi", "charset_normalizer", "idna", "rich", "colorama")
    
    foreach ($folder in $dependencyFolders) {
        $srcPath = Join-Path $distDir $folder
        if (Test-Path $srcPath) {
            Copy-Item -Path $srcPath -Destination "$portableDir\$folder" -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "Copied $folder" -ForegroundColor Green
        }
    }
    
    # Copy any .pyd files from dist root
    Get-ChildItem -Path $distDir -Filter "*.pyd" -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination "$portableDir\" -Force -ErrorAction SilentlyContinue
        Write-Host "Copied $($_.Name)" -ForegroundColor Green
    }
    
    # Copy Python files
    $pythonFiles = @(
        "vt_scan.py", "recon.py", "recon_full.py", "web_security_analyzer.py",
        "edu_typing_engine.py", "ai_ml_detection.py", "ai_threat_intelligence.py",
        "crypto_engine.py", "deletion_protection.py", "financial_forensics.py",
        "financial_forensic_back.py", "hardening_dashboard.py", "immigration_integration.py",
        "integrity_monitor.py", "operator_session.py", "passport_protection.py",
        "post_dst.py", "ransomware_monitor.py", "soc_nmap_dashboard.py",
        "sqlmap_scanner.py", "ssl_backupcode.py", "telemetry_engine.py",
        "test_integrity.py", "test_vtscan.py", "user_guide.py", "wifi_audit.py",
        "fix_and_run.py", "quick_sqlite_fix.py", "generate_license_pdf.py",
        "setup_immigration.py", "dst_footer.py"
    )
    
    foreach ($file in $pythonFiles) {
        if (Test-Path $file) {
            Copy-Item $file "$portableDir\" -Force -ErrorAction SilentlyContinue
            Write-Host "Copied $file" -ForegroundColor Green
        }
    }
    
    # Copy directories
    $directories = @(
        "config", "templates", "logo_path", "footer_logo_path", 
        "docs", "biometrics", "data", "logs", "scans", "update", 
        "tools", "licenses", "redist", "test_integrity_env", "photos", "backup"
    )
    
    foreach ($dir in $directories) {
        if (Test-Path $dir) {
            Copy-Item -Path $dir -Destination "$portableDir\$dir" -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "Copied $dir" -ForegroundColor Green
        }
    }
    
    # Copy icon files
    $iconFiles = @("icon-removebg-preview.ico", "3486-removebg-preview.ico")
    foreach ($icon in $iconFiles) {
        if (Test-Path $icon) {
            Copy-Item $icon "$portableDir\" -Force -ErrorAction SilentlyContinue
            Write-Host "Copied icon: $icon" -ForegroundColor Green
            break
        }
    }
    
    # Copy documentation
    @("license.txt", "README.md", "CHANGELOG.txt", "VERSION") | ForEach-Object {
        if (Test-Path $_) {
            Copy-Item $_ "$portableDir\" -Force -ErrorAction SilentlyContinue
            Write-Host "Copied $_" -ForegroundColor Green
        }
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
dsterminal.exe
pause'
    $batContent | Out-File -FilePath "$portableDir\launch_dsterminal.bat" -Encoding ASCII
    
    # Create README
    $readmeContent = 'DSTERMINAL PORTABLE VERSION v' + $version + '
=====================================

This is the portable version of DSTerminal - no installation required!

QUICK START:
-----------
1. Double-click launch_dsterminal.bat or dsterminal.exe
2. Type vt-scan or vt for VirusTotal module
3. Type help for available commands

REQUIREMENTS:
------------
- Windows 10 or later
- Internet connection for VirusTotal API

TROUBLESHOOTING:
---------------
- If vt-scan fails, check your API key
- Run as administrator for full features

Version: ' + $version + '
Build Date: ' + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    $readmeContent | Out-File -FilePath "$portableDir\README.txt" -Encoding UTF8
    
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
=======
        Write-Host "Inno Setup Compiler (ISCC.exe) not found!" -ForegroundColor Red
        Write-Host "Please install Inno Setup from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
        exit 1
    }

    # Check if installer script exists
    if (-not (Test-Path "dsterminal_installer.iss")) {
        Write-Host "Installer script dsterminal_installer.iss not found!" -ForegroundColor Red
        exit 1
    }

    # Run ISCC
    Write-Host "Compiling installer with: $iscc" -ForegroundColor Gray
    if ($iscc -is [string]) {
        & $iscc "dsterminal_installer.iss"
    } else {
        & iscc "dsterminal_installer.iss"
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installer built successfully!" -ForegroundColor Green
        # Find the generated installer
        $installer = Get-ChildItem -Path . -Filter "DSTerminal_Setup_*.exe" | Select-Object -First 1
        if ($installer) {
            Write-Host "Location: $($installer.FullName)" -ForegroundColor Green
        }
    } else {
        Write-Host "Failed to build installer!" -ForegroundColor Red
        exit 1
    }
}

if (-not $BuildPy -and -not $BuildInstaller -and -not $Clean) {
    Write-Host "`nNo build actions specified. Available options:" -ForegroundColor Yellow
    Write-Host "  .\build.ps1 -Clean         # Clean build artifacts" -ForegroundColor White
    Write-Host "  .\build.ps1 -BuildPy       # Build Python executable" -ForegroundColor White
    Write-Host "  .\build.ps1 -BuildInstaller # Build Inno Setup installer" -ForegroundColor White
    Write-Host "  .\build.ps1 -Clean -BuildPy -BuildInstaller # Do everything" -ForegroundColor White
}

Write-Host "`nBuild complete!" -ForegroundColor Green
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
