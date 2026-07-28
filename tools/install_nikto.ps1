# install_nikto.ps1
# Nikto Installation Script for DSTerminal

param(
    [switch]$Silent,
    [switch]$Force
)

Write-Host "[*] Nikto installation script" -ForegroundColor Cyan
Write-Host "[*] Nikto is bundled with DSTerminal" -ForegroundColor Yellow
Write-Host "[*] No additional installation required" -ForegroundColor Green
exit 0