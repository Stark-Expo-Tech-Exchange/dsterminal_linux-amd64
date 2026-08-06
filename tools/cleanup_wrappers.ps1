# cleanup_wrappers.ps1
Write-Host "Cleaning up old wrappers..." -ForegroundColor Cyan

$wrapperDirs = @(
    "$env:USERPROFILE\DSTerminal\bin",
    "$env:USERPROFILE\DSTerminal\tools"
)

foreach ($dir in $wrapperDirs) {
    if (Test-Path $dir) {
        $wrappers = Get-ChildItem -Path $dir -Filter "*.bat" -ErrorAction SilentlyContinue
        foreach ($wrapper in $wrappers) {
            Write-Host "Removing old wrapper: $($wrapper.FullName)" -ForegroundColor Gray
            Remove-Item $wrapper.FullName -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "Cleanup complete!" -ForegroundColor Green