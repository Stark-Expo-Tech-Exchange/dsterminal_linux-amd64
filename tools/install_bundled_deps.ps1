# install_bundled_deps.ps1
# This runs after installation to install bundled tools with GUI wizards

param(
    [string]$AppPath = (Split-Path -Parent $MyInvocation.MyCommand.Path)
)

# ============================================================
# COLOR CODES
# ============================================================
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

# ============================================================
# MAIN INSTALLATION FUNCTION
# ============================================================
function Install-BundledDependencies {
    Write-ColorOutput "========================================" Cyan
    Write-ColorOutput "  DSTERMINAL - Dependency Installation" Cyan
    Write-ColorOutput "========================================" Cyan
    Write-ColorOutput ""
    Write-ColorOutput "This will launch installers for:" Yellow
    Write-ColorOutput "  • Nmap (Network Scanner) - GUI Wizard" White
    Write-ColorOutput "  • Npcap (Packet Capture Library) - GUI Wizard" White
    Write-ColorOutput "  • SQLMap (SQL Injection Tool)" White
    Write-ColorOutput "  • Nikto (Web Vulnerability Scanner)" White
    Write-ColorOutput "  • WHOIS Domain Lookup Tool" White
    Write-ColorOutput ""
    
    # Check if running as administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-ColorOutput "⚠️  WARNING: Some installers may require administrator privileges!" Red
        Write-ColorOutput "   If prompted, please click 'Yes' to allow administrative access." Yellow
        Write-ColorOutput ""
    }
    
    Write-ColorOutput "Press any key to start dependency installation..." Yellow
    Read-Host
    
    # ============================================================
    # 1. INSTALL Nmap (GUI Wizard)
    # ============================================================
    $nmapPath = Join-Path $AppPath "bundled\nmap\nmap-7.95-setup.exe"
    if (Test-Path $nmapPath) {
        Write-ColorOutput "`n[1/5] Launching Nmap GUI installer..." Cyan
        Write-ColorOutput "   Path: $nmapPath" Gray
        
        try {
            # Launch Nmap installer with GUI (no /S parameter)
            $process = Start-Process -FilePath $nmapPath -Wait -PassThru
            if ($process.ExitCode -eq 0) {
                Write-ColorOutput "   ✅ Nmap GUI installation completed successfully!" Green
            } else {
                Write-ColorOutput "   ⚠️  Nmap installation may have been cancelled or had issues." Yellow
            }
        } catch {
            Write-ColorOutput "   ❌ Failed to launch Nmap installer: $_" Red
        }
    } else {
        Write-ColorOutput "`n[1/5] ❌ Nmap installer not found: $nmapPath" Red
        Write-ColorOutput "   Please download from: https://nmap.org/dist/nmap-7.95-setup.exe" Yellow
    }
    
    # ============================================================
    # 2. INSTALL Npcap (GUI Wizard)
    # ============================================================
    $npcapPath = Join-Path $AppPath "bundled\npcap\npcap-1.79.exe"
    if (Test-Path $npcapPath) {
        Write-ColorOutput "`n[2/5] Launching Npcap GUI installer..." Cyan
        Write-ColorOutput "   Path: $npcapPath" Gray
        Write-ColorOutput "   ⚠️  During Npcap installation, check 'Install in WinPcap API-compatible Mode'" Yellow
        
        try {
            # Launch Npcap installer with GUI (no /S parameter)
            $process = Start-Process -FilePath $npcapPath -Wait -PassThru
            if ($process.ExitCode -eq 0) {
                Write-ColorOutput "   ✅ Npcap GUI installation completed successfully!" Green
            } else {
                Write-ColorOutput "   ⚠️  Npcap installation may have been cancelled or had issues." Yellow
            }
        } catch {
            Write-ColorOutput "   ❌ Failed to launch Npcap installer: $_" Red
        }
    } else {
        Write-ColorOutput "`n[2/5] ❌ Npcap installer not found: $npcapPath" Red
        Write-ColorOutput "   Please download from: https://npcap.com/dist/npcap-1.79.exe" Yellow
    }
    
    # ============================================================
    # 3. EXTRACT SQLMap
    # ============================================================
    $sqlmapZip = Join-Path $AppPath "bundled\sqlmap\sqlmap.zip"
    $sqlmapDest = Join-Path $AppPath "tools\sqlmap"
    if (Test-Path $sqlmapZip) {
        Write-ColorOutput "`n[3/5] Extracting SQLMap..." Cyan
        Write-ColorOutput "   Source: $sqlmapZip" Gray
        Write-ColorOutput "   Destination: $sqlmapDest" Gray
        
        try {
            # Remove existing directory if it exists
            if (Test-Path $sqlmapDest) {
                Remove-Item -Recurse -Force $sqlmapDest -ErrorAction SilentlyContinue
            }
            
            # Create destination directory
            New-Item -ItemType Directory -Path $sqlmapDest -Force | Out-Null
            
            # Extract zip
            Expand-Archive -Path $sqlmapZip -DestinationPath $sqlmapDest -Force
            Write-ColorOutput "   ✅ SQLMap extracted successfully!" Green
        } catch {
            Write-ColorOutput "   ❌ Failed to extract SQLMap: $_" Red
        }
    } else {
        Write-ColorOutput "`n[3/5] ❌ SQLMap zip not found: $sqlmapZip" Red
    }
    
    # ============================================================
    # 4. EXTRACT Nikto
    # ============================================================
    $niktoZip = Join-Path $AppPath "bundled\nikto\nikto.zip"
    $niktoDest = Join-Path $AppPath "tools\nikto"
    if (Test-Path $niktoZip) {
        Write-ColorOutput "`n[4/5] Extracting Nikto..." Cyan
        Write-ColorOutput "   Source: $niktoZip" Gray
        Write-ColorOutput "   Destination: $niktoDest" Gray
        
        try {
            # Remove existing directory if it exists
            if (Test-Path $niktoDest) {
                Remove-Item -Recurse -Force $niktoDest -ErrorAction SilentlyContinue
            }
            
            # Create destination directory
            New-Item -ItemType Directory -Path $niktoDest -Force | Out-Null
            
            # Extract zip
            Expand-Archive -Path $niktoZip -DestinationPath $niktoDest -Force
            Write-ColorOutput "   ✅ Nikto extracted successfully!" Green
        } catch {
            Write-ColorOutput "   ❌ Failed to extract Nikto: $_" Red
        }
    } else {
        Write-ColorOutput "`n[4/5] ❌ Nikto zip not found: $niktoZip" Red
    }
    
    # ============================================================
    # 5. INSTALL WHOIS Script
    # ============================================================
    $whoisSource = Join-Path $AppPath "bundled\whois\whois.ps1"
    $whoisDest = Join-Path $AppPath "tools\whois.ps1"
    if (Test-Path $whoisSource) {
        Write-ColorOutput "`n[5/5] Installing WHOIS tool..." Cyan
        Write-ColorOutput "   Source: $whoisSource" Gray
        Write-ColorOutput "   Destination: $whoisDest" Gray
        
        try {
            Copy-Item -Path $whoisSource -Destination $whoisDest -Force
            Write-ColorOutput "   ✅ WHOIS tool installed successfully!" Green
        } catch {
            Write-ColorOutput "   ❌ Failed to install WHOIS tool: $_" Red
        }
    } else {
        Write-ColorOutput "`n[5/5] ❌ WHOIS script not found: $whoisSource" Red
    }
    
    # ============================================================
    # 6. SUMMARY
    # ============================================================
    Write-ColorOutput "`n========================================" Green
    Write-ColorOutput "  INSTALLATION SUMMARY" Green
    Write-ColorOutput "========================================" Green
    
    Write-ColorOutput "`n✅ Installed Tools:" Yellow
    Write-ColorOutput "  • Nmap: $(if (Test-Path $nmapPath) {'Installed'} else {'Not Found'})" White
    Write-ColorOutput "  • Npcap: $(if (Test-Path $npcapPath) {'Installed'} else {'Not Found'})" White
    Write-ColorOutput "  • SQLMap: $(if (Test-Path $sqlmapDest) {'Extracted'} else {'Not Found'})" White
    Write-ColorOutput "  • Nikto: $(if (Test-Path $niktoDest) {'Extracted'} else {'Not Found'})" White
    Write-ColorOutput "  • WHOIS: $(if (Test-Path $whoisDest) {'Installed'} else {'Not Found'})" White
    
    Write-ColorOutput "`n📁 Installation Locations:" Yellow
    Write-ColorOutput "  • Nmap: C:\Program Files\Nmap (or user selected)" Gray
    Write-ColorOutput "  • Npcap: C:\Program Files\Npcap (or user selected)" Gray
    Write-ColorOutput "  • SQLMap: $sqlmapDest" Gray
    Write-ColorOutput "  • Nikto: $niktoDest" Gray
    Write-ColorOutput "  • WHOIS: $whoisDest" Gray
    
    Write-ColorOutput "`n⚠️  IMPORTANT NOTES:" Yellow
    Write-ColorOutput "  • If Nmap or Npcap didn't install, run the installers manually from:" Red
    Write-ColorOutput "    $AppPath\bundled\nmap\nmap-7.95-setup.exe" Red
    Write-ColorOutput "    $AppPath\bundled\npcap\npcap-1.79.exe" Red
    Write-ColorOutput "  • For Npcap, select 'Install in WinPcap API-compatible Mode' for best compatibility" Yellow
    
    Write-ColorOutput "`nPress any key to exit..." Yellow
    Read-Host
}

# ============================================================
# RUN THE INSTALLATION
# ============================================================
Install-BundledDependencies