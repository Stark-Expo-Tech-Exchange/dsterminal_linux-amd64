# ============================================================================
# DSTERMINAL SMART INSTALLER - PowerShell Version
# Version: 2.1.327
# ============================================================================

param(
    [switch]$InstallAll,
    [string]$Tool = "",
    [switch]$Help
)

# ============================================================================
# COLOR CODES
# ============================================================================
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-SectionHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor White
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================
$global:InstallDir = Join-Path $HOME "DSTerminal"
$global:BinDir = Join-Path $global:InstallDir "bin"
$global:ToolsDir = Join-Path $global:InstallDir "tools"
$global:ConfigDir = Join-Path $global:InstallDir "config"
$global:DownloadDir = Join-Path $global:InstallDir "downloads"
$global:IsAdmin = $false

# ============================================================================
# CHECK ADMIN
# ============================================================================
function CheckAdmin {
    try {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        $global:IsAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        return $global:IsAdmin
    } catch {
        $global:IsAdmin = $false
        return $false
    }
}

# ============================================================================
# CHECK INTERNET
# ============================================================================
function CheckInternet {
    try {
        $request = [System.Net.WebRequest]::Create('https://github.com')
        $request.Timeout = 5000
        $response = $request.GetResponse()
        $response.Close()
        return $true
    } catch {
        return $false
    }
}

# ============================================================================
# CHECK TOOLS
# ============================================================================
function CheckPip {
    try { return (python -m pip --version 2>&1) -ne $null } catch { return $false }
}

function CheckGit {
    return (Get-Command git -ErrorAction SilentlyContinue) -ne $null
}

function CheckNpcapInstalled {
    $npcapPaths = @(
        'C:\Windows\System32\Npcap',
        'C:\Program Files\Npcap',
        'C:\Windows\SysWOW64\Npcap'
    )
    foreach ($path in $npcapPaths) {
        if (Test-Path $path) { return $true }
    }
    return $false
}

# ============================================================================
# DOWNLOAD FILE
# ============================================================================
function DownloadFile {
    param($url, $destPath, $showProgress = $true)
    try {
        $webClient = New-Object System.Net.WebClient
        if ($showProgress) {
            Write-ColorOutput "  Downloading: $([System.IO.Path]::GetFileName($url))" Cyan
            $webClient.DownloadFile($url, $destPath)
        } else {
            $webClient.DownloadFile($url, $destPath)
        }
        return $true
    } catch {
        Write-ColorOutput "  Download error: $_" Red
        return $false
    }
}

# ============================================================================
# CREATE DIRECTORIES
# ============================================================================
function SetupDirectories {
    $dirs = @($global:InstallDir, $global:BinDir, $global:ToolsDir, $global:ConfigDir, $global:DownloadDir)
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
}

# ============================================================================
# INSTALL Npcap
# ============================================================================
function InstallNpcap {
    Write-ColorOutput "`n  Installing Npcap (required for Nmap)..." Yellow
    
    if (CheckNpcapInstalled) {
        Write-ColorOutput "  Npcap is already installed" Green
        return $true
    }
    
    if (-not (Test-Path $global:DownloadDir)) {
        New-Item -ItemType Directory -Path $global:DownloadDir -Force | Out-Null
    }
    
    $npcapUrl = 'https://npcap.com/dist/npcap-1.79.exe'
    $filename = [System.IO.Path]::GetFileName($npcapUrl)
    $downloadPath = Join-Path $global:DownloadDir $filename
    
    if (-not (Test-Path $downloadPath)) {
        Write-ColorOutput "  Downloading Npcap installer..." Cyan
        if (-not (DownloadFile $npcapUrl $downloadPath)) {
            Write-ColorOutput "  Failed to download Npcap" Red
            return $false
        }
    }
    
    Write-ColorOutput "  Installing Npcap silently..." Cyan
    try {
        $args = ' /npcap_silent_install /npcap_winpcap_mode /npcap_loopback_support'
        
        if ($global:IsAdmin) {
            $process = Start-Process -FilePath $downloadPath -ArgumentList $args -Wait -PassThru
            if ($process.ExitCode -eq 0) {
                Write-ColorOutput "  Npcap installation completed" Green
                return $true
            }
        } else {
            Write-ColorOutput "  Attempting to run as administrator..." Yellow
            Start-Process -FilePath $downloadPath -ArgumentList $args -Verb RunAs -Wait
            Write-ColorOutput "  Npcap installer started with admin privileges" Green
            Start-Sleep -Seconds 10
            return $true
        }
    } catch {
        Write-ColorOutput "  Npcap installation error: $_" Red
    }
    return $false
}

# ============================================================================
# CREATE WRAPPER
# ============================================================================
function CreateWrapper {
    param($toolName, $toolConfig)
    
    $wrapperExt = '.bat'
    if ($toolConfig.ContainsKey('wrapper_ext')) {
        $wrapperExt = $toolConfig['wrapper_ext']
    }
    
    $wrapperName = "$toolName$wrapperExt"
    $wrapperPath = Join-Path $global:BinDir $wrapperName
    New-Item -ItemType Directory -Path $global:BinDir -Force | Out-Null
    
    $executable = $toolConfig['executable']
    if ($toolConfig.ContainsKey('executable_name')) {
        $executable = $toolConfig['executable_name']
    }
    
    $toolPath = Join-Path $global:ToolsDir $toolName
    $execPath = $null
    
    if ($toolConfig.ContainsKey('install_paths')) {
        foreach ($installPath in $toolConfig['install_paths']) {
            $testPath = Join-Path $installPath $executable
            if (Test-Path $testPath) { $execPath = $testPath; break }
        }
    }
    
    if (-not $execPath) {
        $extensions = @('', '.py', '.pl', '.ps1', '.exe', '.sh', '.bat')
        foreach ($ext in $extensions) {
            $testPath = Join-Path $toolPath "$executable$ext"
            if (Test-Path $testPath) { $execPath = $testPath; break }
        }
        if (-not $execPath -and (Test-Path $toolPath)) {
            $files = Get-ChildItem $toolPath -File | Where-Object { $_.Extension -notin @('.txt', '.md', '.json') }
            if ($files.Count -gt 0) { $execPath = $files[0].FullName }
        }
    }
    
    $cmd = "echo `"$toolName not found. See $toolPath\README.txt for instructions`""
    
    if ($execPath) {
        $cmd = $execPath
        if ([System.IO.Path]::GetExtension($execPath) -eq '.py') {
            $cmd = "python3 `"$execPath`""
        } elseif ([System.IO.Path]::GetExtension($execPath) -eq '.pl') {
            $cmd = "perl `"$execPath`""
        } elseif ([System.IO.Path]::GetExtension($execPath) -eq '.ps1') {
            $cmd = "powershell -ExecutionPolicy Bypass -File `"$execPath`""
        } elseif ([System.IO.Path]::GetExtension($execPath) -eq '.sh') {
            $cmd = "bash `"$execPath`""
        }
    } else {
        if (Get-Command $toolName -ErrorAction SilentlyContinue) {
            $cmd = (Get-Command $toolName).Source
        }
    }
    
    $content = "@echo off`r`n$cmd %*`r`n"
    Set-Content -Path $wrapperPath -Value $content
    return $true
}

# ============================================================================
# ADD TO PATH
# ============================================================================
function AddToolToPath {
    param($toolName, $toolConfig)
    
    if (-not $toolConfig.ContainsKey('install_paths')) { return }
    
    Write-ColorOutput "  Adding $toolName to PATH..." Cyan
    
    $foundPath = $null
    foreach ($installPath in $toolConfig['install_paths']) {
        if (Test-Path $installPath) { $foundPath = $installPath; break }
    }
    
    if ($toolName -eq 'whois' -and -not $foundPath) {
        $whoisPath = Join-Path $global:ToolsDir "whois"
        if (Test-Path $whoisPath) { $foundPath = $whoisPath }
    }
    
    if ($foundPath) {
        try {
            $currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
            if ($currentPath -notlike "*$foundPath*") {
                $newPath = "$currentPath;$foundPath"
                [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
                Write-ColorOutput "  Added $foundPath to PATH" Green
            } else {
                Write-ColorOutput "  $foundPath already in PATH" Green
            }
        } catch {
            Write-ColorOutput "  Could not add to PATH: $_" Yellow
        }
    }
}

# ============================================================================
# INSTALL METHODS
# ============================================================================
function InstallViaPip {
    param($toolName, $toolConfig)
    
    if (-not $toolConfig.ContainsKey('pip_package')) { return $false }
    if (-not (CheckPip)) { return $false }
    
    try {
        Write-ColorOutput "  Installing via pip: $($toolConfig['pip_package'])" Cyan
        python -m pip install $($toolConfig['pip_package'])
        return (CreateWrapper $toolName $toolConfig)
    } catch {
        Write-ColorOutput "  Pip error: $_" Red
        return $false
    }
}

function InstallViaGit {
    param($toolName, $toolConfig)
    
    if (-not $toolConfig.ContainsKey('git_url')) { return $false }
    if (-not (CheckGit)) { return $false }
    
    $toolPath = Join-Path $global:ToolsDir $toolName
    try {
        if (Test-Path $toolPath) {
            Remove-Item -Recurse -Force $toolPath -ErrorAction SilentlyContinue
        }
        Write-ColorOutput "  Cloning from: $($toolConfig['git_url'])" Cyan
        git clone --depth 1 $toolConfig['git_url'] $toolPath
        return (CreateWrapper $toolName $toolConfig)
    } catch {
        Write-ColorOutput "  Git error: $_" Red
        return $false
    }
}

function InstallViaInstaller {
    param($toolName, $toolConfig)
    
    if (-not $toolConfig.ContainsKey('installer_url')) { return $false }
    
    if (-not (Test-Path $global:DownloadDir)) {
        New-Item -ItemType Directory -Path $global:DownloadDir -Force | Out-Null
    }
    
    $filename = [System.IO.Path]::GetFileName($toolConfig['installer_url'])
    $downloadPath = Join-Path $global:DownloadDir $filename
    
    if (-not (Test-Path $downloadPath)) {
        Write-ColorOutput "  Downloading installer: $filename" Cyan
        if (-not (DownloadFile $toolConfig['installer_url'] $downloadPath)) {
            return $false
        }
    }
    
    if ($toolName -eq 'nmap') {
        Write-ColorOutput "`n  Nmap requires Npcap for packet capture functionality" Yellow
        InstallNpcap
    }
    
    $silentArgs = '/S'
    if ($toolConfig.ContainsKey('silent_args')) {
        $silentArgs = $toolConfig['silent_args']
    }
    
    Write-ColorOutput "  Running installer..." Cyan
    
    try {
        if ($global:IsAdmin) {
            Write-ColorOutput "  Waiting for installation to complete..." Yellow
            Start-Process -FilePath $downloadPath -ArgumentList $silentArgs -Wait
            Start-Sleep -Seconds 5
        } else {
            Start-Process -FilePath $downloadPath -ArgumentList $silentArgs -Verb RunAs -Wait
            Start-Sleep -Seconds 5
        }
        
        AddToolToPath $toolName $toolConfig
        return (CreateWrapper $toolName $toolConfig)
    } catch {
        Write-ColorOutput "  Installer error: $_" Red
        return $false
    }
}

function InstallEmbeddedScript {
    param($toolName, $toolConfig)
    
    $toolPath = Join-Path $global:ToolsDir $toolName
    New-Item -ItemType Directory -Path $toolPath -Force | Out-Null
    
    if ($toolName -eq 'whois') {
        $scriptPath = Join-Path $toolPath "whois.ps1"
        $scriptContent = @'
param(
    [Parameter(Mandatory=$true)]
    [string]$Domain
)

$whoisServer = "whois.internic.net"
try {
    $tcp = New-Object System.Net.Sockets.TcpClient($whoisServer, 43)
    $stream = $tcp.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $writer.WriteLine($Domain)
    $writer.Flush()
    
    $reader = New-Object System.IO.StreamReader($stream)
    while ($line = $reader.ReadLine()) {
        if ($line -match "^>") { continue }
        Write-Host $line
    }
    
    $reader.Close()
    $writer.Close()
    $tcp.Close()
} catch {
    Write-Error "Error querying WHOIS: $_"
}
'@
        Set-Content -Path $scriptPath -Value $scriptContent
        
        AddToolToPath $toolName $toolConfig
        return (CreateWrapper $toolName $toolConfig)
    }
    return $false
}

# ============================================================================
# SMART INSTALL
# ============================================================================
function SmartInstall {
    param($toolName)
    
    $toolDefinitions = @{
        'sqlmap' = @{
            'priority' = @('python_pip', 'git_clone')
            'pip_package' = 'sqlmap'
            'git_url' = 'https://github.com/sqlmapproject/sqlmap.git'
            'executable' = 'sqlmap.py'
            'wrapper_ext' = '.bat'
        }
        'nmap' = @{
            'priority' = @('installer_gui')
            'installer_url' = 'https://nmap.org/dist/nmap-7.95-setup.exe'
            'executable' = 'nmap.exe'
            'wrapper_ext' = '.bat'
            'silent_args' = ''
            'install_paths' = @('C:\Program Files\Nmap', 'C:\Program Files (x86)\Nmap')
            'executable_name' = 'nmap.exe'
        }
        'whois' = @{
            'priority' = @('embedded_script')
            'executable' = 'whois.ps1'
            'wrapper_ext' = '.bat'
            'install_paths' = @(Join-Path $global:ToolsDir "whois")
            'executable_name' = 'whois.ps1'
        }
    }
    
    if (-not $toolDefinitions.ContainsKey($toolName)) {
        Write-ColorOutput "  Unknown tool: $toolName" Yellow
        return $false
    }
    
    $toolConfig = $toolDefinitions[$toolName]
    Write-ColorOutput "`nInstalling $toolName..." Cyan
    
    foreach ($strategy in $toolConfig['priority']) {
        Write-ColorOutput "  Trying: $strategy" Cyan
        try {
            $result = $false
            switch ($strategy) {
                'python_pip' { $result = InstallViaPip $toolName $toolConfig }
                'git_clone' { $result = InstallViaGit $toolName $toolConfig }
                'installer' { $result = InstallViaInstaller $toolName $toolConfig }
                'embedded_script' { $result = InstallEmbeddedScript $toolName $toolConfig }
             }
            if ($result) {
                Write-ColorOutput "  $toolName installed successfully" Green
                return $true
            }
        } catch {
            Write-ColorOutput "  Error: $_" Red
        }
    }
    
    Write-ColorOutput "  Could not install $toolName" Yellow
    return $false
}

# ==============================gui installation function================================
# =============================================================
function InstallViaInstallerGUI {
    param($toolName, $toolConfig)
    
    if (-not $toolConfig.ContainsKey('installer_url')) { return $false }
    
    if (-not (Test-Path $global:DownloadDir)) {
        New-Item -ItemType Directory -Path $global:DownloadDir -Force | Out-Null
    }
    
    $filename = [System.IO.Path]::GetFileName($toolConfig['installer_url'])
    $downloadPath = Join-Path $global:DownloadDir $filename
    
    if (-not (Test-Path $downloadPath)) {
        Write-ColorOutput "  Downloading installer: $filename" Cyan
        if (-not (DownloadFile $toolConfig['installer_url'] $downloadPath)) {
            return $false
        }
    }
    
    Write-ColorOutput "  Launching installer (GUI mode)..." Cyan
    Write-ColorOutput "  Please follow the on-screen instructions" Yellow
    
    try {
        # NO silent args - show full GUI
        Start-Process -FilePath $downloadPath -Wait
        
        AddToolToPath $toolName $toolConfig
        return (CreateWrapper $toolName $toolConfig)
    } catch {
        Write-ColorOutput "  Installer error: $_" Red
        return $false
    }
}
# ============================================================================
# ADD ALL TO PATH
# ============================================================================
function AddToPath {
    $binPath = $global:BinDir
    try {
        $currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
        if ($currentPath -notlike "*$binPath*") {
            $newPath = "$currentPath;$binPath"
            [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
            Write-ColorOutput "`nAdded $binPath to user PATH" Green
            Write-ColorOutput "   Please restart your terminal for changes to take effect" Yellow
        } else {
            Write-ColorOutput "`n$binPath already in PATH" Green
        }
    } catch {
        Write-ColorOutput "`nCould not update PATH: $_" Yellow
        Write-ColorOutput "   Please manually add this to your PATH:" Yellow
        Write-ColorOutput "   $binPath" Cyan
    }
}

# ============================================================================
# DETECT ENVIRONMENT
# ============================================================================
function DetectEnvironment {
    $pkgManagers = @{}
    if (Get-Command apt-get -ErrorAction SilentlyContinue) { $pkgManagers['apt'] = $true }
    if (Get-Command yum -ErrorAction SilentlyContinue) { $pkgManagers['yum'] = $true }
    if (Get-Command dnf -ErrorAction SilentlyContinue) { $pkgManagers['dnf'] = $true }
    if (Get-Command brew -ErrorAction SilentlyContinue) { $pkgManagers['brew'] = $true }
    if (Get-Command choco -ErrorAction SilentlyContinue) { $pkgManagers['choco'] = $true }
    if (Get-Command winget -ErrorAction SilentlyContinue) { $pkgManagers['winget'] = $true }
    
    return @{
        'has_internet' = (CheckInternet)
        'is_admin' = $global:IsAdmin
        'os' = 'windows'
        'arch' = [System.Environment]::GetEnvironmentVariable('PROCESSOR_ARCHITECTURE')
        'python_version' = (python --version 2>&1) -replace 'Python ', ''
        'package_managers' = $pkgManagers
    }
}

# ============================================================================
# PRINT USAGE
# ============================================================================
function PrintUsageInstructions {
    param($results)
    
    Write-ColorOutput "`nUsage Instructions:" Cyan
    Write-ColorOutput ("-" * 40) Cyan
    
    foreach ($tool in $results.Keys) {
        if ($results[$tool]) {
            switch ($tool) {
                'sqlmap' { Write-ColorOutput "  sqlmap: sqlmap --help" White }
                'nmap' { Write-ColorOutput "  nmap: nmap -A <target>" White }
                'whois' { Write-ColorOutput "  whois: whois <domain>" White }
            }
        }
    }
}

# ============================================================================
# PRINT POST INSTALL NOTES
# ============================================================================
function PrintPostInstallNotes {
    param($results)
    
    Write-ColorOutput "`nPost-Installation Notes:" Cyan
    Write-ColorOutput ("-" * 40) Cyan
    
    if (-not $global:IsAdmin) {
        Write-ColorOutput "  Some tools may have triggered UAC prompts" Yellow
        Write-ColorOutput "  Please check if any installation wizards are still open" Yellow
        if (-not $results['nmap']) {
            Write-ColorOutput "    - Nmap installer: $($global:DownloadDir)\nmap-7.95-setup.exe" Yellow
        }
    }
    
    if (-not (CheckNpcapInstalled)) {
        Write-ColorOutput "`n  Npcap is not installed (required for Nmap scanning)" Yellow
        Write-ColorOutput "  Download from: https://npcap.com/" Yellow
    }
    
    Write-ColorOutput "`n  To add tools to PATH permanently:" Cyan
    Write-ColorOutput "    [Environment]::SetEnvironmentVariable('Path', `$env:Path + ';$($global:BinDir)', 'User')" Cyan
}

# ============================================================================
# MAIN - INSTALL ALL
# ============================================================================
function InstallAll {
    Write-SectionHeader "DSTerminal Smart Installer - Windows"
    
    CheckAdmin
    
    $env = DetectEnvironment
    Write-ColorOutput "`nEnvironment Detection:" Cyan
    Write-ColorOutput "  has_internet: $($env['has_internet'])" White
    Write-ColorOutput "  is_admin: $($env['is_admin'])" White
    Write-ColorOutput "  os: $($env['os'])" White
    Write-ColorOutput "  arch: $($env['arch'])" White
    Write-ColorOutput "  python_version: $($env['python_version'])" White
    
    if (-not $global:IsAdmin) {
        Write-ColorOutput "`nRunning without administrator privileges" Yellow
        Write-ColorOutput "   The installer will attempt to auto-elevate when needed" Yellow
    }
    
    SetupDirectories
    
    $tools = @('sqlmap', 'nmap', 'whois')
    $results = @{}
    
    foreach ($tool in $tools) {
        $results[$tool] = SmartInstall $tool
    }
    
    Write-SectionHeader "Installation Summary"
    foreach ($tool in $results.Keys) {
        $status = if ($results[$tool]) { "[OK]" } else { "[FAIL]" }
        $color = if ($results[$tool]) { "Green" } else { "Red" }
        Write-ColorOutput "  $status $tool" $color
    }
    
    Write-ColorOutput "`nInstallation Directory:" Cyan
    Write-ColorOutput "  $($global:InstallDir)" White
    Write-ColorOutput "  Binaries: $($global:BinDir)" White
    
    AddToPath
    PrintUsageInstructions $results
    PrintPostInstallNotes $results
    
    Write-SectionHeader "Installation Complete!"
    return $results
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if ($Help) {
    Write-ColorOutput @"
DSTERMINAL SMART INSTALLER - PowerShell Version

Usage:
  .\dsterminal_smart_installer.ps1 [options]

Options:
  -InstallAll   Install all tools
  -Tool <name>  Install specific tool (e.g., -Tool nmap)
  -Help         Show this help message

Examples:
  .\dsterminal_smart_installer.ps1 -InstallAll
  .\dsterminal_smart_installer.ps1 -Tool nmap
"@ Cyan
    exit
}

if ($Tool) {
    SmartInstall $Tool
} else {
    InstallAll
}