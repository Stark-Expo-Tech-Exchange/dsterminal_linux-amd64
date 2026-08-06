@echo off
echo ====================================================================
echo            DSTERMINAL TEST INSTALLER v1.0.0
echo            Testing Update Feature
echo ====================================================================
echo.
echo [INFO] Installing DSTerminal...
echo.
echo [1/3] Extracting files...
timeout /t 1 /nobreak > nul 2>&1
echo [2/3] Copying files to destination...
timeout /t 1 /nobreak > nul 2>&1
echo [3/3] Configuring settings...
timeout /t 1 /nobreak > nul 2>&1
echo.
echo ====================================================================
echo [SUCCESS] Installation Complete!
echo ====================================================================
echo.
echo Version: 1.0.0
echo Location: %CD%
echo Date: %DATE% %TIME%
echo.
echo Thank you for installing DSTerminal!
echo.
pause
