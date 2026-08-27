@echo off
REM DSTerminal Launcher - Sets working directory to fix icon display
cd /d "%~dp0"
start "" "%~dp0dsterminal.exe" %*
