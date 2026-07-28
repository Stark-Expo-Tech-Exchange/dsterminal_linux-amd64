# Convert DSTERMINAL icon to BMP for Inno Setup
Add-Type -AssemblyName System.Drawing

 = "installer_assets\3486-removebg-preview.ico"
 = "installer_assets\wizard-image.bmp"
 = "installer_assets\wizard-small.bmp"

# Check if source icon exists
if (Test-Path ) {
    Write-Host "Found icon: " -ForegroundColor Green
    
    # Load the icon
     = [System.Drawing.Image]::FromFile()
    
    # Create large image (164x314)
     = New-Object System.Drawing.Bitmap(, 164, 314)
    .Save(, [System.Drawing.Imaging.ImageFormat]::Bmp)
    .Dispose()
    Write-Host "Created: " -ForegroundColor Green
    
    # Create small image (55x55)
     = New-Object System.Drawing.Bitmap(, 55, 55)
    .Save(, [System.Drawing.Imaging.ImageFormat]::Bmp)
    .Dispose()
    Write-Host "Created: " -ForegroundColor Green
    
    .Dispose()
    
    # Verify files
    Get-ChildItem installer_assets\*.bmp
} else {
    Write-Host "Icon not found at: " -ForegroundColor Red
}
