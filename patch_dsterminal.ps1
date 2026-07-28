<#
.SYNOPSIS
    Fix ALL DSTerminal indentation errors
.DESCRIPTION
    Finds and fixes all unexpected indent errors in dsterminal.py
#>

$filePath = "dsterminal.py"

# Create backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "backups\dsterminal_all_fix_${timestamp}.py"
New-Item -ItemType Directory -Path "backups" -Force | Out-Null
Copy-Item $filePath $backupPath -Force
Write-Host "Backup created: $backupPath" -ForegroundColor Green

# Read the file
$lines = Get-Content $filePath -Encoding UTF8
Write-Host "Total lines: $($lines.Count)" -ForegroundColor Cyan

# Function to check if a line is likely a top-level statement
function Is-TopLevel {
    param($Line)
    $trimmed = $Line.Trim()
    return $trimmed -match '^(import|from|def|class|if|elif|else|for|while|try|except|finally|with|async|await|return|pass|break|continue|raise|yield|global|nonlocal|print|raise|assert|del)\s' -or
           $trimmed -match '^[A-Z_][A-Z0-9_]*\s*=' -or
           $trimmed -match '^#\s*===' -or
           $trimmed -match '^"""' -or
           $trimmed -match "^'''" -or
           $trimmed -eq '' -or
           $trimmed -match '^#'
}

# Find and fix all unexpected indent errors
Write-Host ""
Write-Host "Scanning for indentation errors..." -ForegroundColor Magenta

$fixedCount = 0
$i = 0
$inMultilineString = $false
$inTripleQuote = $false
$inFunction = $false
$functionIndent = 0
$classIndent = 0

while ($i -lt $lines.Count) {
    $line = $lines[$i]
    $trimmed = $line.Trim()
    
    # Skip if empty or comment
    if ($trimmed -eq '' -or $trimmed -match '^#') {
        $i++
        continue
    }
    
    # Check if line has leading spaces but is a top-level statement
    if ($line -match '^[ ]+' -and (Is-TopLevel -Line $trimmed)) {
        # This is likely an indentation error - fix it
        $lineNum = $i + 1
        Write-Host "  Fixing line $lineNum: '$line'" -ForegroundColor Yellow
        $lines[$i] = $trimmed
        $fixedCount++
        $i++
        continue
    }
    
    # Check for tabs and replace with spaces
    if ($line -match '^\t') {
        $lineNum = $i + 1
        Write-Host "  Fixing tab at line $lineNum" -ForegroundColor Yellow
        $lines[$i] = $line -replace "`t", "    "
        $fixedCount++
        $i++
        continue
    }
    
    # Check for inconsistent indentation (mix of spaces and tabs)
    if ($line -match '^[ ]+\t' -or $line -match '^\t[ ]+') {
        $lineNum = $i + 1
        Write-Host "  Fixing mixed indentation at line $lineNum" -ForegroundColor Yellow
        $lines[$i] = $line -replace "`t", "    "
        $fixedCount++
        $i++
        continue
    }
    
    $i++
}

Write-Host ""
Write-Host "Fixed $fixedCount indentation issues." -ForegroundColor Green

# Write the fixed file
Set-Content $filePath -Value $lines -Encoding UTF8 -NoNewline
Write-Host "File updated: $filePath" -ForegroundColor Green

# Verify syntax
Write-Host ""
Write-Host "Verifying Python syntax..." -ForegroundColor Magenta
$result = python -m py_compile $filePath 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Syntax check passed!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Still has issues:" -ForegroundColor Yellow
    Write-Host $result -ForegroundColor Cyan
    
    # Try to find the specific line
    if ($result -match 'line (\d+)') {
        $lineNum = [int]$matches[1] - 1
        Write-Host ""
        Write-Host "Error at line $($matches[1]):" -ForegroundColor Red
        Write-Host "  $($lines[$lineNum])" -ForegroundColor Red
        Write-Host ""
        Write-Host "Lines around this:" -ForegroundColor Cyan
        $start = [Math]::Max(0, $lineNum - 3)
        $end = [Math]::Min($lines.Count - 1, $lineNum + 3)
        for ($j = $start; $j -le $end; $j++) {
            $num = $j + 1
            if ($num -eq $matches[1]) {
                Write-Host "  $num ->>> $($lines[$j])" -ForegroundColor Red
            } else {
                Write-Host "  $num - $($lines[$j])" -ForegroundColor Gray
            }
        }
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  FIX COMPLETED" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backup saved to: $backupPath" -ForegroundColor Cyan
Write-Host "Fixes applied: $fixedCount" -ForegroundColor Cyan
Write-Host ""