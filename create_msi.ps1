# create_msi.ps1 - Build MSI for DSTerminal
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    DSTerminal MSI Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Set WiX path
$wixPath = "C:\Program Files (x86)\WiX Toolset v3.14\bin"
Write-Host "Using WiX at: $wixPath" -ForegroundColor Green

# Check if executable exists
if (-not (Test-Path "dist\dsterminal_complete.exe")) {
    Write-Host "ERROR: dsterminal_complete.exe not found in dist folder!" -ForegroundColor Red
    Write-Host "Build the executable first using auto-py-to-exe" -ForegroundColor Yellow
    exit 1
}

Write-Host "Creating WiX XML file..." -ForegroundColor Yellow

# Create WiX XML file
@'
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*" 
             Name="DSTerminal" 
             Language="1033" 
             Version="1.0.0" 
             Manufacturer="Your Company" 
             UpgradeCode="8A9C8B1E-2F3D-4A5B-8C7D-9E0F1A2B3C4D">
        
        <Package InstallerVersion="200" 
                 Compressed="yes" 
                 InstallScope="perMachine" 
                 Platform="x64"
                 Description="DSTerminal - Advanced Terminal Tool"/>
        
        <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." 
                      AllowSameVersionUpgrades="yes"/>
        
        <MediaTemplate EmbedCab="yes" />
        
        <Feature Id="ProductFeature" Title="DSTerminal" Level="1">
            <ComponentGroupRef Id="ProductComponents" />
        </Feature>
        
        <Property Id="ARPPRODUCTICON" Value="DSTerminal.exe" />
        <Icon Id="DSTerminal.exe" SourceFile="dist\dsterminal_complete.exe" />
        
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFiles64Folder">
                <Directory Id="INSTALLFOLDER" Name="DSTerminal" />
            </Directory>
            <Directory Id="ProgramMenuFolder">
                <Directory Id="ApplicationProgramsFolder" Name="DSTerminal" />
            </Directory>
            <Directory Id="DesktopFolder" Name="Desktop" />
        </Directory>
        
        <Fragment>
            <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
                <Component Id="DSTerminalExe" Guid="*" Win64="yes">
                    <File Id="DSTerminalExe" 
                          Name="DSTerminal.exe" 
                          Source="dist\dsterminal_complete.exe" 
                          KeyPath="yes" 
                          Checksum="yes">
                        <Shortcut Id="StartMenuShortcut" 
                                  Directory="ApplicationProgramsFolder" 
                                  Name="DSTerminal" 
                                  WorkingDirectory="INSTALLFOLDER" 
                                  Icon="DSTerminal.exe" 
                                  IconIndex="0" />
                        <Shortcut Id="DesktopShortcut" 
                                  Directory="DesktopFolder" 
                                  Name="DSTerminal" 
                                  WorkingDirectory="INSTALLFOLDER" 
                                  Icon="DSTerminal.exe" 
                                  IconIndex="0" />
                    </File>
                </Component>
                <Component Id="UninstallRegistry" Guid="*" Win64="yes">
                    <RegistryValue Root="HKCU" 
                                   Key="Software\DSTerminal" 
                                   Name="Installed" 
                                   Type="integer" 
                                   Value="1" 
                                   KeyPath="yes" />
                    <RemoveFolder Id="RemoveProgramMenuFolder" 
                                  Directory="ApplicationProgramsFolder" 
                                  On="uninstall" />
                    <RemoveFolder Id="RemoveDesktopFolder" 
                                  Directory="DesktopFolder" 
                                  On="uninstall" />
                </Component>
            </ComponentGroup>
        </Fragment>
    </Product>
</Wix>
'@ | Out-File DSTerminal.wxs -Encoding UTF8

Write-Host "Created DSTerminal.wxs" -ForegroundColor Green

# Compile with candle.exe
Write-Host "Compiling with candle.exe..." -ForegroundColor Yellow
& "$wixPath\candle.exe" DSTerminal.wxs -out DSTerminal.wixobj

if ($LASTEXITCODE -ne 0 -or -not (Test-Path "DSTerminal.wixobj")) {
    Write-Host "Compilation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Compilation successful!" -ForegroundColor Green

# Link with light.exe
Write-Host "Linking with light.exe..." -ForegroundColor Yellow
& "$wixPath\light.exe" DSTerminal.wixobj -out DSTerminal_Setup.msi

if ($LASTEXITCODE -ne 0 -or -not (Test-Path "DSTerminal_Setup.msi")) {
    Write-Host "Linking failed!" -ForegroundColor Red
    exit 1
}

# Success!
$fileSize = (Get-Item "DSTerminal_Setup.msi").Length
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    MSI Created Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "File: DSTerminal_Setup.msi" -ForegroundColor Cyan
Write-Host "Size: $([math]::Round($fileSize/1MB, 2)) MB" -ForegroundColor Cyan
Write-Host "Location: $PWD\DSTerminal_Setup.msi" -ForegroundColor Cyan
Write-Host ""
Write-Host "To install:" -ForegroundColor Green
Write-Host "  msiexec /i DSTerminal_Setup.msi" -ForegroundColor Cyan
Write-Host ""
Write-Host "To install silently:" -ForegroundColor Green
Write-Host "  msiexec /i DSTerminal_Setup.msi /quiet /norestart" -ForegroundColor Cyan
Write-Host ""