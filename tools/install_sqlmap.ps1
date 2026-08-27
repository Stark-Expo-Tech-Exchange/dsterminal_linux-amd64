<<<<<<< HEAD
# install_sqlmap.ps1 - Extract bundled SQLMap (No Python required)
# SQLMap Installation Script for DSTerminal

param(
    [switch]$Silent,
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installing SQLMap" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Define installation paths
$sqlmapDir = "$env:USERPROFILE\DSTerminal\tools\sqlmap"
$bundledZip = Join-Path $PSScriptRoot "bundled\sqlmap\sqlmap.zip"

# FIXED: Proper PowerShell syntax
if ((Test-Path $sqlmapDir) -and (-not $Force)) {
    Write-Host "SQLMap is already installed" -ForegroundColor Green
    Write-Host "Location: $sqlmapDir" -ForegroundColor Cyan
    
    # Check if sqlmap.py exists
    if (Test-Path "$sqlmapDir\sqlmap.py") {
        Write-Host "âœ… sqlmap.py found" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "To reinstall, use: .\install_sqlmap.ps1 -Force" -ForegroundColor Yellow
    pause
    exit 0
}

# Check if bundled zip exists
if (-not (Test-Path $bundledZip)) {
    Write-Host "ERROR: Bundled SQLMap zip not found!" -ForegroundColor Red
    Write-Host "Expected: $bundledZip" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Falling back to pip installation..." -ForegroundColor Yellow
    
    # Try pip as fallback
    try {
        $pythonCmd = $null
        if (Get-Command python -ErrorAction SilentlyContinue) {
            $pythonCmd = "python"
        } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
            $pythonCmd = "python3"
        }
        
        if ($pythonCmd) {
            Write-Host "Installing SQLMap via pip..." -ForegroundColor Cyan
            & $pythonCmd -m pip install sqlmap --user
            if ($LASTEXITCODE -eq 0) {
                Write-Host "SQLMap installed successfully via pip!" -ForegroundColor Green
                pause
                exit 0
            }
        }
    } catch {
        Write-Host "Pip installation failed!" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Please download SQLMap manually from: https://sqlmap.org/" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Extracting SQLMap from bundled zip..." -ForegroundColor Cyan
Write-Host "  Source: $bundledZip" -ForegroundColor Gray
Write-Host "  Destination: $sqlmapDir" -ForegroundColor Gray
Write-Host ""

# Remove existing directory if forcing reinstall
if ($Force -and (Test-Path $sqlmapDir)) {
    Write-Host "Removing existing SQLMap installation..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $sqlmapDir -ErrorAction SilentlyContinue
}

# Create the sqlmap directory
if (-not (Test-Path $sqlmapDir)) {
    New-Item -ItemType Directory -Path $sqlmapDir -Force | Out-Null
}

# Extract the zip file
try {
    # Use PowerShell's built-in Expand-Archive (available in PowerShell 5+)
    if ($PSVersionTable.PSVersion.Major -ge 5) {
        Write-Host "Extracting using Expand-Archive..." -ForegroundColor Gray
        Expand-Archive -Path $bundledZip -DestinationPath $sqlmapDir -Force
        
        # Move contents up one level if they're in a subfolder
        $subFolders = Get-ChildItem -Path $sqlmapDir -Directory -ErrorAction SilentlyContinue
        if ($subFolders.Count -eq 1) {
            $subFolder = $subFolders[0]
            Write-Host "Moving contents from subfolder: $($subFolder.Name)" -ForegroundColor Gray
            Get-ChildItem -Path $subFolder.FullName | Move-Item -Destination $sqlmapDir -Force
            Remove-Item -Path $subFolder.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
    } else {
        # Fallback for older PowerShell versions
        Write-Host "Using COM object for extraction..." -ForegroundColor Gray
        $shell = New-Object -ComObject Shell.Application
        $zip = $shell.NameSpace($bundledZip)
        $dest = $shell.NameSpace($sqlmapDir)
        $dest.CopyHere($zip.Items(), 16)  # 16 = "No progress dialog"
        Start-Sleep -Seconds 2
    }
    
    Write-Host "SQLMap extracted successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to extract SQLMap: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please extract manually from: $bundledZip" -ForegroundColor Yellow
    Write-Host "To: $sqlmapDir" -ForegroundColor Yellow
    pause
    exit 1
}

# Create a wrapper script for easy execution
$wrapperDir = "$env:USERPROFILE\DSTerminal\bin"
if (-not (Test-Path $wrapperDir)) {
    New-Item -ItemType Directory -Path $wrapperDir -Force | Out-Null
}

$wrapperPath = Join-Path $wrapperDir "sqlmap.bat"

# Check if sqlmap.py exists
$sqlmapPy = Join-Path $sqlmapDir "sqlmap.py"
if (-not (Test-Path $sqlmapPy)) {
    Write-Host "WARNING: sqlmap.py not found in extracted files!" -ForegroundColor Yellow
    Write-Host "Looking for sqlmap.py in subdirectories..." -ForegroundColor Yellow
    
    # Search for sqlmap.py
    $found = Get-ChildItem -Path $sqlmapDir -Filter "sqlmap.py" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $sqlmapPy = $found.FullName
        Write-Host "Found: $sqlmapPy" -ForegroundColor Green
    }
}

# Create the wrapper
if (Test-Path $sqlmapPy) {
    Write-Host "Creating wrapper: $wrapperPath" -ForegroundColor Cyan
    
    # Determine Python command
    $pythonCmd = "python"
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3"
    }
    
    $wrapperContent = @"
@echo off
REM SQLMap wrapper for DSTerminal
if not exist "$sqlmapPy" (
    echo SQLMap not found at: $sqlmapPy
    echo Please reinstall SQLMap using: install_sqlmap.ps1 -Force
    pause
    exit /b 1
)
$pythonCmd "$sqlmapPy" %*
"@
    Set-Content -Path $wrapperPath -Value $wrapperContent
    
    # Add to PATH if not already there
    $currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($currentPath -notlike "*$wrapperDir*") {
        $newPath = "$currentPath;$wrapperDir"
        [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        Write-Host "Added $wrapperDir to user PATH" -ForegroundColor Green
    }
    
    Write-Host "Wrapper created successfully!" -ForegroundColor Green
} else {
    Write-Host "WARNING: Could not find sqlmap.py" -ForegroundColor Yellow
    Write-Host "The SQLMap files were extracted but sqlmap.py was not found." -ForegroundColor Yellow
    Write-Host "Location: $sqlmapDir" -ForegroundColor Cyan
}

# Verify installation
Write-Host ""
Write-Host "Verifying SQLMap installation..." -ForegroundColor Cyan
=======
# install_sqlmap.ps1 - Updated for virtual environments
Write-Host "Installing SQLMap..." -ForegroundColor Cyan
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

<<<<<<< HEAD
# Test SQLMap
if (Get-Command sqlmap -ErrorAction SilentlyContinue) {
    $version = & sqlmap --version 2>&1 | Select-Object -First 1
    Write-Host "âœ… SQLMap installed successfully!" -ForegroundColor Green
    Write-Host "   Version: $version" -ForegroundColor Gray
    Write-Host "   Location: $wrapperPath" -ForegroundColor Gray
} else {
    Write-Host "âš ï¸ SQLMap installed but not in PATH" -ForegroundColor Yellow
    Write-Host "   You can run it manually from: $sqlmapDir" -ForegroundColor Yellow
    Write-Host "   Or restart your terminal and try again." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "SQLMap installation complete!" -ForegroundColor Green
pause
exit 0
=======
# Find Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
}

if (-not $pythonCmd) {
    Write-Host "Python not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $pythonCmd" -ForegroundColor Green

# Check if in virtual environment
$inVenv = ($pythonCmd -eq "python" -and (Get-Command python).Source -like "*venv*")
if ($inVenv) {
    Write-Host "Detected virtual environment. Installing without --user flag..." -ForegroundColor Yellow
    & $pythonCmd -m pip install sqlmap
} else {
    Write-Host "Installing SQLMap via pip..." -ForegroundColor Yellow
    & $pythonCmd -m pip install sqlmap --user
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "SQLMap installed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "SQLMap installation failed!" -ForegroundColor Red
    exit 1
}
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
