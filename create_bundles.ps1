# ============================================================================
# DSTERMINAL BUNDLE CREATOR - PowerShell Version
# Version: 2.1.328
# Description: Creates bundled packages from downloaded installers
# ============================================================================

#Requires -Version 5.1

param(
    [switch]$Clean,
    [string]$SourceDir,
    [switch]$SkipNikto,
    [switch]$SkipNmap,
    [switch]$SkipNpcap
)

# ============================================================================
# COLOR CODES
# ============================================================================
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-SectionHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor White
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

# ============================================================================
# CREATE ZIP WITH EXCLUSIONS
# ============================================================================
function Create-ZipWithExclusions {
    param(
        [string]$SourcePath,
        [string]$DestinationPath,
        [string[]]$ExcludePatterns
    )
    
    try {
        # Create temp directory for filtered files
        $tempFilterDir = Join-Path $env:TEMP "nikto_filter_$(Get-Random)"
        New-Item -ItemType Directory -Path $tempFilterDir -Force | Out-Null
        
        # Copy files excluding problematic ones
        $files = Get-ChildItem -Path $SourcePath -File -Recurse
        $excludedCount = 0
        
        foreach ($file in $files) {
            $exclude = $false
            $relativePath = $file.FullName.Substring($SourcePath.Length + 1)
            
            foreach ($pattern in $ExcludePatterns) {
                if ($relativePath -match $pattern) {
                    $exclude = $true
                    $excludedCount++
                    Write-ColorOutput "      Excluding: $relativePath" Yellow
                    break
                }
            }
            
            if (-not $exclude) {
                $destFile = Join-Path $tempFilterDir $relativePath
                $destDir = Split-Path $destFile -Parent
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Copy-Item -Path $file.FullName -Destination $destFile -Force
            }
        }
        
        Write-ColorOutput "      Excluded $excludedCount files" Yellow
        
        # Create zip from filtered directory
        if ((Get-ChildItem -Path $tempFilterDir -File -Recurse).Count -gt 0) {
            Compress-Archive -Path "$tempFilterDir\*" -DestinationPath $DestinationPath -Force
            Write-ColorOutput "      Created zip with filtered content" Green
            
            # Clean up temp directory
            Remove-Item -Recurse -Force $tempFilterDir -ErrorAction SilentlyContinue
            return $true
        } else {
            Write-ColorOutput "      No files to zip after filtering" Yellow
            Remove-Item -Recurse -Force $tempFilterDir -ErrorAction SilentlyContinue
            return $false
        }
    } catch {
        Write-ColorOutput "      Error creating zip: $_" Red
        return $false
    }
}

# ============================================================================
# MAIN FUNCTION
# ============================================================================
function Create-Bundles {
    Write-SectionHeader "DSTerminal Bundle Creator"
    
    # Setup paths
    $scriptDir = Get-Location
    $bundleDir = Join-Path $scriptDir "bundled"
    $homeDir = $HOME
    
    # Determine source directory
    if ($SourceDir) {
        $sourceDir = $SourceDir
        Write-ColorOutput "Using source directory from parameter: $sourceDir" Cyan
    } elseif (Test-Path (Join-Path $scriptDir "downloads")) {
        $sourceDir = Join-Path $scriptDir "downloads"
        Write-ColorOutput "Using source directory: $sourceDir (current directory)" Cyan
    } else {
        $sourceDir = Join-Path $scriptDir "installers"
        if (-not (Test-Path $sourceDir)) {
            $sourceDir = Join-Path $homeDir "DSTerminal"
            $sourceDir = Join-Path $sourceDir "downloads"
        }
        Write-ColorOutput "Using source directory: $sourceDir" Cyan
    }
    
    $tempDir = Join-Path $scriptDir "temp"
    
    Write-ColorOutput "Script directory: $scriptDir" Cyan
    Write-ColorOutput "Bundle directory: $bundleDir" Cyan
    Write-ColorOutput "Source directory: $sourceDir" Cyan
    Write-ColorOutput "Temp directory: $tempDir" Cyan
    
    # Create directories if they don't exist
    if (-not (Test-Path $bundleDir)) {
        New-Item -ItemType Directory -Path $bundleDir -Force | Out-Null
        Write-ColorOutput "Created bundle directory: $bundleDir" Green
    }
    if (-not (Test-Path $tempDir)) {
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
        Write-ColorOutput "Created temp directory: $tempDir" Green
    }
    
    # Clean temp directory
    Write-ColorOutput "`n  Cleaning temp directory: $tempDir" Yellow
    try {
        if (Test-Path $tempDir) {
            Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 500
        }
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
        Write-ColorOutput "    Temp directory cleaned" Green
    } catch {
        Write-ColorOutput "    Could not clean temp directory: $_" Yellow
    }
    
    # Define packages
    $packages = @{
        'whois' = @{
            'file' = 'whois.ps1'
            'description' = 'Whois lookup script'
            'create_script' = $true
        }
        'nikto' = @{
            'file' = 'nikto.zip'
            'description' = 'Web server scanner'
            'create_from_git' = 'https://github.com/sullo/nikto.git'
            'skip' = $SkipNikto
        }
        'sqlmap' = @{
            'file' = 'sqlmap.zip'
            'description' = 'SQL injection tool'
            'create_from_git' = 'https://github.com/sqlmapproject/sqlmap.git'
        }
        'npcap' = @{
            'file' = 'npcap-1.79.exe'
            'description' = 'Npcap packet capture library'
            'download_url' = 'https://npcap.com/dist/npcap-1.79.exe'
            'skip' = $SkipNpcap
        }
        'nmap' = @{
            'file' = 'nmap-7.95-setup.exe'
            'description' = 'Nmap network scanner'
            'download_url' = 'https://nmap.org/dist/nmap-7.95-setup.exe'
            'skip' = $SkipNmap
        }
    }
    
    # Bundle each package
    foreach ($packageName in $packages.Keys) {
        $info = $packages[$packageName]
        
        # Check if package should be skipped
        if ($info.ContainsKey('skip') -and $info['skip']) {
            Write-ColorOutput "`n  Skipping $packageName ($($info['description']))..." Yellow
            continue
        }
        
        Write-ColorOutput "`n  Processing $packageName ($($info['description']))..." Cyan
        
        # Create package directory
        $packageDir = Join-Path $bundleDir $packageName
        if (-not (Test-Path $packageDir)) {
            New-Item -ItemType Directory -Path $packageDir -Force | Out-Null
        }
        
        # Handle different package types
        if ($info.ContainsKey('create_script') -and $info['create_script']) {
            # Create whois script
            if ($packageName -eq 'whois') {
                $scriptContent = @"
param(
    [Parameter(Mandatory=`$true)]
    [string]`$Domain
)

`$whoisServer = "whois.internic.net"
try {
    `$tcp = New-Object System.Net.Sockets.TcpClient(`$whoisServer, 43)
    `$stream = `$tcp.GetStream()
    `$writer = New-Object System.IO.StreamWriter(`$stream)
    `$writer.WriteLine(`$Domain)
    `$writer.Flush()
    
    `$reader = New-Object System.IO.StreamReader(`$stream)
    while (`$line = `$reader.ReadLine()) {
        if (`$line -match "^>") { continue }
        Write-Host `$line
    }
    
    `$reader.Close()
    `$writer.Close()
    `$tcp.Close()
} catch {
    Write-Error "Error querying WHOIS: `$_"
}
"@
                $destFile = Join-Path $packageDir 'whois.ps1'
                Set-Content -Path $destFile -Value $scriptContent -Encoding UTF8
                Write-ColorOutput "    Created whois script" Green
                
                # Create checksum
                $checksum = Get-FileHash -Path $destFile -Algorithm SHA256
                $checksumFile = Join-Path $packageDir "$packageName.sha256"
                Set-Content -Path $checksumFile -Value $checksum.Hash
                Write-ColorOutput "    Created checksum for whois" Green
            }
        }
        elseif ($info.ContainsKey('create_from_git')) {
            # Clone from git and create zip
            Write-ColorOutput "    Cloning from: $($info['create_from_git'])" Yellow
            
            # Check if git is available
            $gitCmd = Get-Command git -ErrorAction SilentlyContinue
            if (-not $gitCmd) {
                Write-ColorOutput "    Git not found! Please install Git to bundle $packageName" Red
                Write-ColorOutput "    Download from: https://git-scm.com/download/win" Yellow
                continue
            }
            
            $repoUrl = $info['create_from_git']
            $repoName = Split-Path $repoUrl -Leaf
            $repoName = $repoName -replace '\.git$', ''
            $repoDir = Join-Path $tempDir $repoName
            
            # Remove existing directory
            if (Test-Path $repoDir) {
                Write-ColorOutput "    Removing existing directory: $repoDir" Yellow
                try {
                    Remove-Item -Recurse -Force $repoDir -ErrorAction SilentlyContinue
                    Start-Sleep -Milliseconds 500
                } catch {
                    Write-ColorOutput "    Could not remove directory: $_" Yellow
                }
            }
            
            # Clone repository
            try {
                Write-ColorOutput "    Cloning into: $repoDir" Cyan
                $result = git clone --depth 1 $repoUrl $repoDir 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "    Clone completed" Green
                } else {
                    Write-ColorOutput "    Clone failed: $result" Red
                    continue
                }
            } catch {
                Write-ColorOutput "    Clone error: $_" Red
                continue
            }
            
            if (Test-Path $repoDir) {
                # Create zip
                $zipPath = Join-Path $packageDir $info['file']
                Write-ColorOutput "    Creating zip: $zipPath" Cyan
                
                try {
                    # Check if directory has content
                    $files = Get-ChildItem -Path $repoDir -File -Recurse
                    if ($files.Count -eq 0) {
                        Write-ColorOutput "    No files found in repository" Yellow
                        continue
                    }
                    
                    # Special handling for nikto - exclude problematic files
                    if ($packageName -eq 'nikto') {
                        Write-ColorOutput "    Nikto detected - excluding problematic files" Yellow
                        $success = Create-ZipWithExclusions -SourcePath $repoDir -DestinationPath $zipPath -ExcludePatterns @(
                            'program\\nikto\.pl$',
                            'program\\nikto\.pl\.original$'
                        )
                        if ($success) {
                            Write-ColorOutput "    Created zip with exclusions" Green
                            $checksum = Get-FileHash -Path $zipPath -Algorithm SHA256
                            $checksumFile = Join-Path $packageDir "$packageName.sha256"
                            Set-Content -Path $checksumFile -Value $checksum.Hash
                            Write-ColorOutput "    Created checksum for $packageName" Green
                        } else {
                            Write-ColorOutput "    Failed to create zip" Red
                        }
                    } else {
                        # Regular zip creation
                        Compress-Archive -Path "$repoDir\*" -DestinationPath $zipPath -Force
                        
                        if ((Test-Path $zipPath) -and ((Get-Item $zipPath).Length -gt 0)) {
                            Write-ColorOutput "    Created zip from git" Green
                            
                            # Create checksum
                            $checksum = Get-FileHash -Path $zipPath -Algorithm SHA256
                            $checksumFile = Join-Path $packageDir "$packageName.sha256"
                            Set-Content -Path $checksumFile -Value $checksum.Hash
                            Write-ColorOutput "    Created checksum for $packageName" Green
                        } else {
                            Write-ColorOutput "    Failed to create zip (empty or missing)" Red
                        }
                    }
                    
                } catch {
                    Write-ColorOutput "    Failed to create zip: $_" Red
                    continue
                }
            }
        }
        else {
            # Copy from source directory
            $srcFile = Join-Path $sourceDir $info['file']
            $destFile = Join-Path $packageDir $info['file']
            
            if (Test-Path $srcFile) {
                # Copy file
                Copy-Item -Path $srcFile -Destination $destFile -Force
                Write-ColorOutput "    Copied: $($info['file'])" Green
                
                # Create checksum
                $checksum = Get-FileHash -Path $srcFile -Algorithm SHA256
                $checksumFile = Join-Path $packageDir "$packageName.sha256"
                Set-Content -Path $checksumFile -Value $checksum.Hash
                Write-ColorOutput "    Created checksum for $packageName" Green
            } else {
                Write-ColorOutput "    Source file not found: $srcFile" Yellow
                if ($info.ContainsKey('download_url')) {
                    Write-ColorOutput "    Please download from: $($info['download_url'])" Cyan
                    Write-ColorOutput "    Or place it in: $sourceDir" Yellow
                }
            }
        }
    }
    
    # Create bundle manifest
    $manifestPath = Join-Path $bundleDir "manifest.json"
    $manifest = @{
        'created' = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        'version' = '4.0.0.113'
        'packages' = @{}
    }
    
    foreach ($packageName in $packages.Keys) {
        $packageDir = Join-Path $bundleDir $packageName
        if (Test-Path $packageDir) {
            $files = Get-ChildItem -Path $packageDir -File | Where-Object { $_.Name -notlike '*.sha256' } | Select-Object -ExpandProperty Name
            if ($files) {
                $manifest['packages'][$packageName] = @{
                    'bundled' = $true
                    'path' = $packageDir
                    'files' = $files
                }
            }
        }
    }
    
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $manifestPath -Encoding UTF8
    Write-ColorOutput "`n  Created bundle manifest: $manifestPath" Green
    
    Write-SectionHeader "Bundle creation complete!"
    Write-ColorOutput "  Bundles are in: $bundleDir" Cyan
    
    Write-ColorOutput "`n  Next steps:" Yellow
    Write-ColorOutput "  1. The 'bundled' folder is now ready" White
    Write-ColorOutput "  2. Run DSTerminal - it will use bundled packages first" White
    
    # Display bundle sizes
    Write-ColorOutput "`n  Bundle Summary:" Cyan
    $totalSize = 0
    $hasContent = $false
    foreach ($packageName in $packages.Keys) {
        $packageDir = Join-Path $bundleDir $packageName
        if (Test-Path $packageDir) {
            $files = Get-ChildItem -Path $packageDir -File -Recurse | Where-Object { $_.Name -notlike '*.sha256' }
            $size = ($files | Measure-Object -Property Length -Sum).Sum
            if ($size -and $size -gt 0) {
                $sizeMB = $size / (1024 * 1024)
                Write-ColorOutput "    $packageName : $('{0:F2}' -f $sizeMB) MB ($($files.Count) files)" White
                $totalSize += $size
                $hasContent = $true
            } else {
                Write-ColorOutput "    $packageName : 0.00 MB (No files - check source)" Yellow
            }
        }
    }
    $totalMB = $totalSize / (1024 * 1024)
    Write-ColorOutput "`n    Total bundled size: $('{0:F2}' -f $totalMB) MB" Cyan
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
$scriptDir = Get-Location

if ($Clean) {
    Write-ColorOutput "Cleaning bundled directory..." Yellow
    $bundleDir = Join-Path $scriptDir "bundled"
    if (Test-Path $bundleDir) {
        Remove-Item -Recurse -Force $bundleDir
        Write-ColorOutput "  Removed: $bundleDir" Green
    } else {
        Write-ColorOutput "  No bundled directory found" Yellow
    }
    $tempDir = Join-Path $scriptDir "temp"
    if (Test-Path $tempDir) {
        Remove-Item -Recurse -Force $tempDir
        Write-ColorOutput "  Removed: $tempDir" Green
    }
}

# Run the main function
Create-Bundles