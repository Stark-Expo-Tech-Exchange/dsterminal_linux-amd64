# patch_version.ps1
# Run this script to update version 4.0.0.113 to 4.0.0.113 across the project.

$OldVersion = "4.0.0.113"
$NewVersion = "4.0.0.113"

# Define the exact files to patch. We exclude .git, .vs, dist, build folders.
$Files = Get-ChildItem -Path . -Recurse -File -Exclude "*.exe","*.dll","*.pyc","*.idx","*.db","*.bin","*.vsidx","*.wsuo","*.bak" | Where-Object {
    $_.FullName -notmatch "\\.git\\" -and 
    $_.FullName -notmatch "\\.vs\\" -and 
    $_.FullName -notmatch "\\dist\\" -and 
    $_.FullName -notmatch "\\build\\" -and
    $_.FullName -notmatch "\\venv\\" -and
    $_.Name -notmatch "package-lock.json"
}

Write-Host "Starting version patch from $OldVersion to $NewVersion..." -ForegroundColor Cyan

foreach ($File in $Files) {
    try {
        # Read the current content
        $Content = Get-Content -Path $File.FullName -Raw -ErrorAction Stop
        
        # Ensure there is something to replace first
        if ($Content -match [regex]::Escape($OldVersion)) {
            
            # 1. Replace standard versions (4.0.0.113 -> 4.0.0.113)
            $NewContent = $Content -replace [regex]::Escape($OldVersion), $NewVersion
            
            # 2. Fix Display Names in .iss specifically (DSTerminal v4.0.0.113 -> DSTerminal v4.0.0.113)
            if ($File.Extension -eq ".iss") {
                $NewContent = $NewContent -replace "DSTerminal v$OldVersion", "DSTerminal v$NewVersion"
            }

            # 3. Write the changes back to the file
            # We use UTF8 encoding without BOM to match standard Python/Inno files
            [System.IO.File]::WriteAllLines($File.FullName, $NewContent)
            
            Write-Host "PATCHED: $($File.FullName)" -ForegroundColor Green
        }
    } catch {
        Write-Host "SKIPPED: $($File.FullName) (Could not read)" -ForegroundColor Yellow
    }
}

Write-Host "Version patch complete! Please review changes in Git." -ForegroundColor Cyan