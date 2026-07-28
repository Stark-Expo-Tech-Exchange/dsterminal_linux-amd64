# Python Packages Installer
Write-Host "Installing Python packages..." -ForegroundColor Cyan
Write-Host ""

# Find Python executable
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "ERROR: Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python from: https://python.org/downloads" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using: $pythonCmd" -ForegroundColor Cyan
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
& $pythonCmd -m pip install --upgrade pip --quiet

# Install packages
$packages = @(
    # ===== Core System Packages =====
    "colorama", 
    "requests", 
    "folium", 
    "plotly", 
    "reportlab",
    "psutil",
    "watchdog",
    "netifaces",
    "click",
    "rich",
    
    # ===== Web & Scraping =====
    "beautifulsoup4",
    "soupsieve",
    "urllib3",
    "certifi",
    "charset-normalizer",
    "idna",
    "defusedxml",
    "lxml",
    
    # ===== Data Processing =====
    "numpy",
    "pandas",
    "matplotlib",
    "pillow",
    "h3",
    "timezonefinder",
    
    # ===== PDF & Document =====
    "reportlab",
    "PyPDF2",
    "mistune",
    "tinycss2",
    "webencodings",
    
    # ===== Terminal & UI =====
    "rich",
    "click",
    "colorama",
    "prompt_toolkit",
    "pygments",
    "wcwidth",
    
    # ===== Jupyter & Notebook =====
    "ipython",
    "jupyter_client",
    "jupyter_core",
    "nbformat",
    "nbclient",
    "nbconvert",
    "notebook",
    "jupyterlab_pygments",
    
    # ===== JavaScript/JSON =====
    "jsonschema",
    "jsonschema-specifications",
    "referencing",
    "rpds-py",
    "fastjsonschema",
    "json5",
    
    # ===== Build & Packaging =====
    "build",
    "packaging",
    "pyinstaller",
    "pyinstaller-hooks-contrib",
    "pyproject_hooks",
    "pip-tools",
    "pipreqs",
    "stdeb",
    "docopt",
    "yarg",
    
    # ===== Templates & Markup =====
    "Jinja2",
    "MarkupSafe",
    "markdown-it-py",
    "mdurl",
    "pandocfilters",
    
    # ===== Async & Networking =====
    "aiohttp",
    "httpx",
    "tornado",
    "pyzmq",
    "socket",
    
    # ===== Database =====
    "sqlalchemy",
    "sqlite3",
    
    # ===== Security & Crypto =====
    "cryptography",
    "pyOpenSSL",
    "paramiko",
    "bcrypt",
    "pycryptodome",
    "cffi",
    "pycparser",
    
    # ===== Forensic & Analysis =====
    "pefile",
    "volatility",
    "pyforensics",
    "scapy",
    "dnspython",
    "whois",
    
    # ===== Threat Intelligence =====
    "virustotal",
    "shodan",
    "theharvester",
    
    # ===== Recon & OSINT =====
    "recon-ng",
    "splunk-sdk",
    
    # ===== Windows-Specific =====
    "pywin32-ctypes",
    
    # ===== Utilities =====
    "python-dateutil",
    "pytz",
    "six",
    "traitlets",
    "decorator",
    "backcall",
    "executing",
    "pure_eval",
    "stack-data",
    "asttokens",
    "parso",
    "jedi",
    "pickleshare",
    "matplotlib-inline",
    "typing_extensions",
    "attrs",
    "bleach",
    "defusedxml",
    "flatbuffers",
    
    # ===== Data Visualization =====
    "folium",
    "plotly",
    "matplotlib",
    "seaborn",
    
    # ===== Geospatial =====
    "geopy",
    "geocoder",
    "folium",
    "h3",
    
    # ===== Machine Learning (Optional) =====
    "scikit-learn",
    "tensorflow",
    "torch"
)

$failed = @()

foreach ($package in $packages) {
    Write-Host "Installing: $package..." -ForegroundColor Cyan
    try {
        python -m pip install --upgrade $package
        Write-Host "✅ $package installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install: $package" -ForegroundColor Red
        $failed += $package
    }
}

Write-Host ""
if ($failed.Count -gt 0) {
    Write-Host "`n⚠️ Failed packages:" -ForegroundColor Yellow
    foreach ($pkg in $failed) {
        Write-Host "  - $pkg" -ForegroundColor Red
    }
} else {
    Write-Host "`n✅ All packages installed successfully!" -ForegroundColor Green
}