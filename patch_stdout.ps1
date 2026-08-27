# patch_stdout.ps1 - Automatically patch Python files with safe stdout/stderr handling
param(
    [string]$RootDir = ".",
    [switch]$DryRun,
    [switch]$Backup
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DSTERMINAL STDOUT/STDERR PATCHER" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Directories to exclude
$excludeDirs = @(
    "venv",
    ".venv",
    "env",
    ".env",
    "virtualenv",
    "pyenv",
    "site-packages",
    "dist-packages",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "build",
    "dist",
    "installer_output",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".tox"
)

# Patterns to exclude
$excludePatterns = @(
    "test_",
    "_test",
    ".test",
    "setup.py",
    "conftest.py"
)

# The patch code to insert
$PATCH_CODE = @"
# ============================================================
# FIX UNICODE ENCODING ISSUES FOR WINDOWS CONSOLE
# ============================================================
import sys
import io
import os

# Safe stdout/stderr handling for GUI executables
if sys.platform == 'win32':
    try:
        # Set console code page to UTF-8 (only if console exists)
        if sys.stdout is not None:
            os.system('chcp 65001 > nul')
    except:
        pass
    
    # Replace stdout/stderr with UTF-8 wrappers (only if they exist)
    if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
        except:
            pass
    if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
        try:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')
        except:
            pass

def safe_print_unicode(message):
    """Safely print unicode/emoji characters on Windows"""
    try:
        # Check if stdout exists before printing
        if sys.stdout is not None:
            print(message)
        # If stdout is None (windowed mode), log to file instead
        else:
            try:
                log_path = os.path.join(os.path.dirname(sys.executable), 'dsterminal.log')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(message + '\n')
            except:
                pass
    except UnicodeEncodeError:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        if sys.stdout is not None:
            print(clean_message)
        else:
            try:
                log_path = os.path.join(os.path.dirname(sys.executable), 'dsterminal.log')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(clean_message + '\n')
            except:
                pass
    except:
        pass  # Silent fail for GUI mode

"@

# Get all Python files, excluding specified directories
$allFiles = Get-ChildItem -Path $RootDir -Filter "*.py" -Recurse -File

# Filter files
$pythonFiles = @()
foreach ($file in $allFiles) {
    $skip = $false
    
    # Check if file is in excluded directory
    $relativePath = $file.FullName.Substring($RootDir.Length).TrimStart('\', '/')
    $pathParts = $relativePath -split '[\\/]'
    
    foreach ($excludeDir in $excludeDirs) {
        if ($relativePath -match "\\$excludeDir\\" -or $relativePath -match "^$excludeDir\\" -or $pathParts -contains $excludeDir) {
            $skip = $true
            break
        }
    }
    
    # Check if file matches exclude patterns
    if (-not $skip) {
        foreach ($pattern in $excludePatterns) {
            if ($file.Name -like "$pattern*" -or $file.Name -like "*$pattern*") {
                $skip = $true
                break
            }
        }
    }
    
    if (-not $skip) {
        $pythonFiles += $file
    }
}

Write-Host "Found $($pythonFiles.Count) Python files to process (excluding venv and test files)" -ForegroundColor Green
Write-Host ""

$processedCount = 0
$skippedCount = 0
$alreadyPatchedCount = 0

foreach ($file in $pythonFiles) {
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    
    if (-not $content) {
        Write-Host "⚠️  Skipping $($file.Name) - Could not read file" -ForegroundColor Yellow
        $skippedCount++
        continue
    }
    
    # Check if file already has the patch
    if ($content -match "safe_print_unicode" -or $content -match "sys.stdout is not None") {
        Write-Host "⏭️  Skipping $($file.Name) - Already patched" -ForegroundColor Gray
        $alreadyPatchedCount++
        continue
    }
    
    # Check if file has the old problematic code
    $hasOldCode = $content -match "sys.stdout = io.TextIOWrapper\(sys.stdout\.buffer"
    
    if ($hasOldCode) {
        Write-Host "🔧 Patching $($file.Name) - Found old stdout code" -ForegroundColor Yellow
        
        if ($DryRun) {
            Write-Host "    [DRY RUN] Would replace old stdout code with new safe version" -ForegroundColor Cyan
            $processedCount++
            continue
        }
        
        if ($Backup) {
            $backupPath = $file.FullName + ".backup"
            Copy-Item -Path $file.FullName -Destination $backupPath -Force
            Write-Host "    📁 Backup created: $backupPath" -ForegroundColor Green
        }
        
        # Find the old code block and replace it
        $pattern = '(?s)(# ============================================================\s*# FIX UNICODE ENCODING ISSUES FOR WINDOWS CONSOLE\s*# ============================================================.*?)(?=\s*# Now proceed with the rest of your imports|\s*import time|\s*import os(?!\.)|\s*if __name__)'
        
        if ($content -match $pattern) {
            $newContent = $content -replace $pattern, $PATCH_CODE
            Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8 -NoNewline
            Write-Host "    ✅ Patched $($file.Name) (replaced old section)" -ForegroundColor Green
            $processedCount++
        } else {
            # Try alternative pattern - just find the problematic line
            $oldLinePattern = 'sys\.stdout = io\.TextIOWrapper\(sys\.stdout\.buffer'
            if ($content -match $oldLinePattern) {
                # Remove the old code and insert patch at top
                $importPattern = '(?m)^(import sys\s*import io\s*import os)'
                if ($content -match $importPattern) {
                    $newContent = $content -replace $importPattern, $PATCH_CODE
                    Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8 -NoNewline
                    Write-Host "    ✅ Patched $($file.Name) (inserted at top)" -ForegroundColor Green
                    $processedCount++
                } else {
                    Write-Host "    ⚠️  Could not patch $($file.Name) - pattern not found" -ForegroundColor Red
                    $skippedCount++
                }
            } else {
                Write-Host "    ⚠️  Could not patch $($file.Name) - pattern not found" -ForegroundColor Red
                $skippedCount++
            }
        }
    } else {
        # Check if the file has imports and should get the patch
        if ($content -match '^import sys' -or $content -match '^import os' -or $content -match '^import io' -or $content -match '^import') {
            # Skip if it's a small utility file that doesn't need the patch
            $lineCount = $content.Split("`n").Count
            if ($lineCount -lt 20) {
                Write-Host "⏭️  Skipping $($file.Name) - Small utility file" -ForegroundColor Gray
                $skippedCount++
                continue
            }
            
            Write-Host "➕ Adding patch to $($file.Name) - No existing stdout code" -ForegroundColor Yellow
            
            if ($DryRun) {
                Write-Host "    [DRY RUN] Would add patch to file" -ForegroundColor Cyan
                $processedCount++
                continue
            }
            
            if ($Backup) {
                $backupPath = $file.FullName + ".backup"
                Copy-Item -Path $file.FullName -Destination $backupPath -Force
                Write-Host "    📁 Backup created: $backupPath" -ForegroundColor Green
            }
            
            # Insert patch after the shebang or at the top
            if ($content -match '^#!.*?python') {
                $newContent = $content -replace '(^#!.*?python\s*)', "`$1`n$PATCH_CODE`n"
            } else {
                $newContent = $PATCH_CODE + "`n" + $content
            }
            
            Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8 -NoNewline
            Write-Host "    ✅ Added patch to $($file.Name)" -ForegroundColor Green
            $processedCount++
        } else {
            Write-Host "⏭️  Skipping $($file.Name) - No imports found" -ForegroundColor Gray
            $skippedCount++
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PATCH COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Processed: $processedCount files" -ForegroundColor Green
Write-Host "Already patched: $alreadyPatchedCount files" -ForegroundColor Yellow
Write-Host "Skipped: $skippedCount files" -ForegroundColor Yellow
Write-Host ""

if ($DryRun) {
    Write-Host "This was a DRY RUN. Remove -DryRun to apply changes." -ForegroundColor Yellow
} else {
    Write-Host "✅ All files have been patched!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Rebuild the executable: .\build.ps1 -Clean -BuildPy" -ForegroundColor White
    Write-Host "  2. Test the new executable" -ForegroundColor White
}

Write-Host ""