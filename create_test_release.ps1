# create_test_release.ps1
Write-Host "Creating test release files for DSTerminal update feature..." -ForegroundColor Cyan

# Create test installer batch file
@"
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
"@ | Out-File -FilePath "DSTerminal-Installer.bat" -Encoding ASCII

# Create config.json
@"
{
  "version": "1.0.0",
  "name": "DSTerminal Test",
  "description": "Test repository for update feature",
  "release_date": "2026-07-30",
  "author": "Stark-Expo-Tech-Exchange"
}
"@ | Out-File -FilePath "config.json" -Encoding ASCII

# Create version.txt
"1.0.0" | Out-File -FilePath "version.txt" -Encoding ASCII

# Create README.md
@"
# DSTerminal Updates Test Repository

This is a public test repository for the DSTerminal automatic update feature.

## Latest Version
- **Version:** v1.0.0
- **Release Date:** 2026-07-30

## Features Tested
- âœ… GitHub API integration
- âœ… Automatic update detection
- âœ… Download progress tracking
- âœ… Installer execution

## Installation
Download the latest release from the [releases page](https://github.com/Stark-Expo-Tech-Exchange/DSTerminal-Updates-Test/releases).

## Testing
This repository is used to test the automatic update feature of DSTerminal.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| v1.0.0  | 2026-07-30 | Initial test release |
"@ | Out-File -FilePath "README.md" -Encoding ASCII

# Create RELEASE_NOTES.md
@"
# Release Notes - DSTerminal v1.0.0

## Release Date: 2026-07-30

### ðŸš€ New Features
- Initial test release
- Automatic update detection
- GitHub API integration

### ðŸ“¦ Installer
- File: DSTerminal-v1.0.0.zip
- Size: ~1 MB
- Platform: Windows/Linux/MacOS

### âš™ï¸ Configuration
- Version: 1.0.0

### ðŸ“ Notes
This is a test release for the update feature.
"@ | Out-File -FilePath "RELEASE_NOTES.md" -Encoding ASCII

# Create the ZIP file
Write-Host "Creating ZIP file..." -ForegroundColor Yellow
$files = @(
    "DSTerminal-Installer.bat",
    "config.json",
    "version.txt",
    "README.md",
    "RELEASE_NOTES.md"
)
Compress-Archive -Path $files -DestinationPath "DSTerminal-v1.0.0.zip" -Force

Write-Host "âœ“ Created DSTerminal-v1.0.0.zip" -ForegroundColor Green

# Initialize git repository
Write-Host "Initializing git repository..." -ForegroundColor Yellow
git init
git add .
git commit -m "Initial commit: Test release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0"

Write-Host ""
Write-Host "âœ… Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create a repository on GitHub called: DSTerminal-Updates-Test (PUBLIC)" -ForegroundColor White
Write-Host "2. Run these commands:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/Stark-Expo-Tech-Exchange/DSTerminal-Updates-Test.git" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor Yellow
Write-Host "   git push --tags" -ForegroundColor Yellow
Write-Host "3. Go to GitHub and create a release from the v1.0.0 tag" -ForegroundColor White
Write-Host "4. Upload DSTerminal-v1.0.0.zip as an asset" -ForegroundColor White
Write-Host "5. Run the test!" -ForegroundColor White