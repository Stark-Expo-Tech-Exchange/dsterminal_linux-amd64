@echo off
echo ========================================
echo DSTERMINAL - Dependency Installation
echo ========================================
echo.
echo This will launch installers for:
echo   - Nmap (Network Scanner)
echo   - Npcap (Packet Capture Library)
echo   - SQLMap (SQL Injection Tool)
echo   - Nikto (Web Vulnerability Scanner)
echo.
echo Please follow the installation wizards.
echo The installers will open in separate windows.
echo.
pause

echo.
echo [1/4] Launching Nmap installer...
start /wait "" "%CD%\bundled\nmap\nmap-7.95-setup.exe"
echo Nmap installation completed.

echo.
echo [2/4] Launching Npcap installer...
start /wait "" "%CD%\bundled\npcap\npcap-1.79.exe"
echo Npcap installation completed.

echo.
echo [3/4] Extracting SQLMap...
powershell -Command "Expand-Archive -Path '%CD%\bundled\sqlmap\sqlmap.zip' -DestinationPath '%CD%\tools\sqlmap' -Force"
echo SQLMap extracted.

echo.
echo [4/4] Extracting Nikto...
powershell -Command "Expand-Archive -Path '%CD%\bundled\nikto\nikto.zip' -DestinationPath '%CD%\tools\nikto' -Force"
echo Nikto extracted.

echo.
echo ========================================
echo All dependencies installed!
echo ========================================
pause