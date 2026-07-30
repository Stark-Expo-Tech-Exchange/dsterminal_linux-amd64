# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import site

# Fix the path - update to your actual path
BASE_PATH = 'C:\\Users\\stark\\Documents\\DSTerminal_releases_latest'

# ====================================================================
# DATA FILES - Define FIRST
# ====================================================================
datas = [
    ('vt_scan.py', '.'),
    ('recon.py', '.'),
    ('recon_full.py', '.'),
    ('web_security_analyzer.py', '.'),
    ('edu_typing_engine.py', '.'),
    ('crypto_engine.py', '.'),
    ('deletion_protection.py', '.'),
    ('financial_forensics.py', '.'),
    ('hardening_dashboard.py', '.'),
    ('integrity_monitor.py', '.'),
    ('ransomware_monitor.py', '.'),
    ('soc_nmap_dashboard.py', '.'),
    ('sqlmap_scanner.py', '.'),
    ('sqlmap_advanced.py', '.'),
    ('soc_automated_lab.py', '.'),
    ('soc_enhanced_modules.py', '.'),
    ('telemetry_engine.py', '.'),
    ('update.py', '.'),
    ('dst_footer.py', '.'),
    ('wifi_audit.py', '.'),
    ('config', 'config'),
    ('templates', 'templates'),
    ('logo_path', 'logo_path'),
    ('footer_logo_path', 'footer_logo_path'),
    ('docs', 'docs'),
    ('data', 'data'),
    ('logs', 'logs'),
    ('scans', 'scans'),
    ('tools', 'tools'),
    ('licenses', 'licenses'),
    ('redist', 'redist'),
    ('photos', 'photos'),
    ('update', 'update'),
]

if os.path.exists('license.txt'): datas.append(('license.txt', '.'))
if os.path.exists('README.md'): datas.append(('README.md', '.'))
if os.path.exists('CHANGELOG.txt'): datas.append(('CHANGELOG.txt', '.'))
if os.path.exists('VERSION'): datas.append(('VERSION', '.'))

# ====================================================================
# BINARIES - Define SECOND
# ====================================================================
binaries = []

# ====================================================================
# Generic function to add any package
# ====================================================================
def add_package(package_name, folder_name=None):
    """Add a package from site-packages to the build"""
    if folder_name is None:
        folder_name = package_name
    
    print(f"Looking for {package_name}...")
    package_path = None
    possible_paths = [
        os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', folder_name),
        os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', folder_name),
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            package_path = path
            print(f"✅ Found {package_name} at: {package_path}")
            break
    
    if package_path and os.path.exists(package_path):
        datas.append((package_path, folder_name))
        print(f"✅ Added {package_name} directory to data")
        
        # Add any subdirectories that might contain libs
        for subdir in ['libs', 'include', 'bin']:
            sub_path = os.path.join(package_path, subdir)
            if os.path.exists(sub_path) and os.path.isdir(sub_path):
                datas.append((sub_path, f'{folder_name}.{subdir}'))
                print(f"✅ Added {folder_name}.{subdir} directory to data")
        
        for file in os.listdir(package_path):
            full_path = os.path.join(package_path, file)
            if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
                binaries.append((full_path, folder_name))
                print(f"  Added {package_name} binary: {file}")
        return True
    else:
        print(f"⚠️ Could not find {package_name} directory")
        return False

# Add packages
add_package('numpy')
add_package('PIL', 'PIL')
add_package('cv2')
add_package('qrcode')
add_package('pyfiglet')

# ====================================================================
# Add netifaces as a binary
# ====================================================================
print("=" * 60)
print("Looking for netifaces...")

netifaces_pyd_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'netifaces.cp311-win_amd64.pyd'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'netifaces.cp311-win_amd64.pyd'),
    os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'netifaces.cp311-win_amd64.pyd'),
]

netifaces_pyd = None
for path in netifaces_pyd_paths:
    if os.path.exists(path):
        netifaces_pyd = path
        print(f"✅ Found netifaces at: {netifaces_pyd}")
        break

if netifaces_pyd:
    binaries.append((netifaces_pyd, '.'))
    print(f"✅ Added netifaces .pyd to binaries (root)")
    datas.append((netifaces_pyd, '.'))
    print(f"✅ Added netifaces .pyd to data (root)")
else:
    print("❌ Could not find netifaces .pyd file!")

# ====================================================================
# Add tqdm - Using file system search (no import)
# ====================================================================
print("Looking for tqdm...")
tqdm_path = None
possible_tqdm_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'tqdm'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'tqdm'),
    os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'tqdm'),
]

for path in possible_tqdm_paths:
    if os.path.exists(path) and os.path.isdir(path):
        tqdm_path = path
        print(f"✅ Found tqdm at: {tqdm_path}")
        break

if tqdm_path and os.path.exists(tqdm_path):
    # Add the entire tqdm directory as data
    datas.append((tqdm_path, 'tqdm'))
    print(f"✅ Added tqdm directory to data")
    
    # Add any .pyd files as binaries
    for file in os.listdir(tqdm_path):
        full_path = os.path.join(tqdm_path, file)
        if os.path.isfile(full_path):
            if file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib'):
                binaries.append((full_path, 'tqdm'))
                print(f"  Added tqdm binary: {file}")
else:
    print("⚠️ Could not find tqdm directory in site-packages")
    # Try to find tqdm anywhere in site-packages
    site_packages = os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages')
    if os.path.exists(site_packages):
        for item in os.listdir(site_packages):
            if 'tqdm' in item.lower() and os.path.isdir(os.path.join(site_packages, item)):
                tqdm_path = os.path.join(site_packages, item)
                print(f"✅ Found tqdm at: {tqdm_path}")
                datas.append((tqdm_path, 'tqdm'))
                break

print("=" * 60)

# ====================================================================
# Add fpdf - Using file system search (no import)
# ====================================================================
print("Looking for fpdf...")
fpdf_path = None
possible_fpdf_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'fpdf'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'fpdf'),
    os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'fpdf'),
]

for path in possible_fpdf_paths:
    if os.path.exists(path) and os.path.isdir(path):
        fpdf_path = path
        print(f"✅ Found fpdf at: {fpdf_path}")
        break

if fpdf_path and os.path.exists(fpdf_path):
    # Add the entire fpdf directory as data
    datas.append((fpdf_path, 'fpdf'))
    print(f"✅ Added fpdf directory to data")
    
    # Add any .pyd files as binaries
    for file in os.listdir(fpdf_path):
        full_path = os.path.join(fpdf_path, file)
        if os.path.isfile(full_path):
            if file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib'):
                binaries.append((full_path, 'fpdf'))
                print(f"  Added fpdf binary: {file}")
else:
    print("⚠️ Could not find fpdf directory in site-packages")
    # Try to find fpdf anywhere in site-packages
    site_packages = os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages')
    if os.path.exists(site_packages):
        for item in os.listdir(site_packages):
            if 'fpdf' in item.lower() and os.path.isdir(os.path.join(site_packages, item)):
                fpdf_path = os.path.join(site_packages, item)
                print(f"✅ Found fpdf at: {fpdf_path}")
                datas.append((fpdf_path, 'fpdf'))
                break

print("=" * 60)

# ====================================================================
# Add pyfiglet - Using file system search
# ====================================================================
print("Looking for pyfiglet...")
pyfiglet_path = None
possible_pyfiglet_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'pyfiglet'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'pyfiglet'),
]

for path in possible_pyfiglet_paths:
    if os.path.exists(path) and os.path.isdir(path):
        pyfiglet_path = path
        print(f"✅ Found pyfiglet at: {pyfiglet_path}")
        break

if pyfiglet_path and os.path.exists(pyfiglet_path):
    datas.append((pyfiglet_path, 'pyfiglet'))
    print(f"✅ Added pyfiglet directory to data")
    
    for file in os.listdir(pyfiglet_path):
        full_path = os.path.join(pyfiglet_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'pyfiglet'))
            print(f"  Added pyfiglet binary: {file}")
else:
    print("⚠️ Could not find pyfiglet directory")

# ====================================================================
# Add timezonefinder - Using file system search
# ====================================================================
print("Looking for timezonefinder...")
timezonefinder_path = None
possible_timezonefinder_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'timezonefinder'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'timezonefinder'),
]

for path in possible_timezonefinder_paths:
    if os.path.exists(path) and os.path.isdir(path):
        timezonefinder_path = path
        print(f"✅ Found timezonefinder at: {timezonefinder_path}")
        break

if timezonefinder_path and os.path.exists(timezonefinder_path):
    datas.append((timezonefinder_path, 'timezonefinder'))
    print(f"✅ Added timezonefinder directory to data")
    
    for file in os.listdir(timezonefinder_path):
        full_path = os.path.join(timezonefinder_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'timezonefinder'))
            print(f"  Added timezonefinder binary: {file}")
else:
    print("⚠️ Could not find timezonefinder directory")


print("Looking for cryptography...")
cryptography_path = None
possible_cryptography_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'cryptography'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'cryptography'),
]

for path in possible_cryptography_paths:
    if os.path.exists(path) and os.path.isdir(path):
        cryptography_path = path
        print(f"✅ Found cryptography at: {cryptography_path}")
        break

if cryptography_path and os.path.exists(cryptography_path):
    datas.append((cryptography_path, 'cryptography'))
    print(f"✅ Added cryptography directory to data")
    
    for file in os.listdir(cryptography_path):
        full_path = os.path.join(cryptography_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'cryptography'))
            print(f"  Added cryptography binary: {file}")
else:
    print("⚠️ Could not find cryptography directory")


print("Looking for python_dotenv...")
python_dotenv_path = None
possible_python_dotenv_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'python_dotenv'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'python_dotenv'),
]

for path in possible_python_dotenv_paths:
    if os.path.exists(path) and os.path.isdir(path):
        python_dotenv_path = path
        print(f"✅ Found python_dotenv at: {python_dotenv_path}")
        break

if python_dotenv_path and os.path.exists(python_dotenv_path):
    datas.append((python_dotenv_path, 'python_dotenv'))
    print(f"✅ Added python_dotenv directory to data")
    
    for file in os.listdir(python_dotenv_path):
        full_path = os.path.join(python_dotenv_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'python_dotenv'))
            print(f"  Added python_dotenv binary: {file}")
else:
    print("⚠️ Could not find python_dotenv directory")



# ==============================================
# ====================================================================
# Add psutil - Using file system search
# ====================================================================
print("Looking for psutil...")
psutil_path = None
possible_psutil_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'psutil'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'psutil'),
]

for path in possible_psutil_paths:
    if os.path.exists(path) and os.path.isdir(path):
        psutil_path = path
        print(f"✅ Found psutil at: {psutil_path}")
        break

if psutil_path and os.path.exists(psutil_path):
    datas.append((psutil_path, 'psutil'))
    print(f"✅ Added psutil directory to data")
    
    for file in os.listdir(psutil_path):
        full_path = os.path.join(psutil_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'psutil'))
            print(f"  Added psutil binary: {file}")
else:
    print("⚠️ Could not find psutil directory")

# ====================================================================
# Add reportlab - Using file system search
# ====================================================================
print("Looking for reportlab...")
reportlab_path = None
possible_reportlab_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'reportlab'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'reportlab'),
]

for path in possible_reportlab_paths:
    if os.path.exists(path) and os.path.isdir(path):
        reportlab_path = path
        print(f"✅ Found reportlab at: {reportlab_path}")
        break

if reportlab_path and os.path.exists(reportlab_path):
    datas.append((reportlab_path, 'reportlab'))
    print(f"✅ Added reportlab directory to data")
    
    for file in os.listdir(reportlab_path):
        full_path = os.path.join(reportlab_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'reportlab'))
            print(f"  Added reportlab binary: {file}")
else:
    print("⚠️ Could not find reportlab directory")

# ====================================================================
# Add geopy - Using file system search
# ====================================================================
print("Looking for geopy...")
geopy_path = None
possible_geopy_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'geopy'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'geopy'),
]

for path in possible_geopy_paths:
    if os.path.exists(path) and os.path.isdir(path):
        geopy_path = path
        print(f"✅ Found geopy at: {geopy_path}")
        break

if geopy_path and os.path.exists(geopy_path):
    datas.append((geopy_path, 'geopy'))
    print(f"✅ Added geopy directory to data")
    
    for file in os.listdir(geopy_path):
        full_path = os.path.join(geopy_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'geopy'))
            print(f"  Added geopy binary: {file}")
else:
    print("⚠️ Could not find geopy directory")

# ====================================================================
# Add folium - Using file system search
# ====================================================================
print("Looking for folium...")
folium_path = None
possible_folium_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'folium'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'folium'),
]

for path in possible_folium_paths:
    if os.path.exists(path) and os.path.isdir(path):
        folium_path = path
        print(f"✅ Found folium at: {folium_path}")
        break

if folium_path and os.path.exists(folium_path):
    datas.append((folium_path, 'folium'))
    print(f"✅ Added folium directory to data")
    
    for file in os.listdir(folium_path):
        full_path = os.path.join(folium_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'folium'))
            print(f"  Added folium binary: {file}")
else:
    print("⚠️ Could not find folium directory")

# ====================================================================
# Add pyOpenSSL - Using file system search
# ====================================================================
print("Looking for pyOpenSSL...")
pyOpenSSL_path = None
possible_pyOpenSSL_paths = [  # <-- FIX THIS LINE
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'pyOpenSSL'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'pyOpenSSL'),
]

for path in possible_pyOpenSSL_paths:
    if os.path.exists(path) and os.path.isdir(path):
        pyOpenSSL_path = path
        print(f"✅ Found pyOpenSSL at: {pyOpenSSL_path}")
        break

if pyOpenSSL_path and os.path.exists(pyOpenSSL_path):
    datas.append((pyOpenSSL_path, 'pyopenssl'))
    print(f"✅ Added pyopenssl directory to data")
    
    for file in os.listdir(pyopenssl_path):
        full_path = os.path.join(pyopenssl_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'pyopenssl'))
            print(f"  Added pyopenssl binary: {file}")
else:
    print("⚠️ Could not find pyopenssl directory")
# ====================================================================
# Add pyzbar - Using file system search
# ====================================================================
print("Looking for pyzbar...")
pyzbar_path = None
possible_pyzbar_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'pyzbar'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'pyzbar'),
]

for path in possible_pyzbar_paths:
    if os.path.exists(path) and os.path.isdir(path):
        pyzbar_path = path
        print(f"✅ Found pyzbar at: {pyzbar_path}")
        break

if pyzbar_path and os.path.exists(pyzbar_path):
    datas.append((pyzbar_path, 'pyzbar'))
    print(f"✅ Added pyzbar directory to data")
    
    for file in os.listdir(pyzbar_path):
        full_path = os.path.join(pyzbar_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'pyzbar'))
            print(f"  Added pyzbar binary: {file}")
else:
    print("⚠️ Could not find pyzbar directory")

# ====================================================================
# Add qrcode - Using file system search
# ====================================================================
print("Looking for qrcode...")
qrcode_path = None
possible_qrcode_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'qrcode'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'qrcode'),
]

for path in possible_qrcode_paths:
    if os.path.exists(path) and os.path.isdir(path):
        qrcode_path = path
        print(f"✅ Found qrcode at: {qrcode_path}")
        break

if qrcode_path and os.path.exists(qrcode_path):
    datas.append((qrcode_path, 'qrcode'))
    print(f"✅ Added qrcode directory to data")
    
    for file in os.listdir(qrcode_path):
        full_path = os.path.join(qrcode_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'qrcode'))
            print(f"  Added qrcode binary: {file}")
else:
    print("⚠️ Could not find qrcode directory")

# ====================================================================
# Add PIL (Pillow) - Using file system search
# ====================================================================
print("Looking for PIL...")
pil_path = None
possible_pil_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'PIL'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'PIL'),
]

for path in possible_pil_paths:
    if os.path.exists(path) and os.path.isdir(path):
        pil_path = path
        print(f"✅ Found PIL at: {pil_path}")
        break

if pil_path and os.path.exists(pil_path):
    datas.append((pil_path, 'PIL'))
    print(f"✅ Added PIL directory to data")
    
    for file in os.listdir(pil_path):
        full_path = os.path.join(pil_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'PIL'))
            print(f"  Added PIL binary: {file}")
else:
    print("⚠️ Could not find PIL directory")

# ====================================================================
# Add opencv-python-headless (cv2) - Using file system search
# ====================================================================
print("Looking for cv2...")
cv2_path = None
possible_cv2_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'cv2'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'cv2'),
]

for path in possible_cv2_paths:
    if os.path.exists(path) and os.path.isdir(path):
        cv2_path = path
        print(f"✅ Found cv2 at: {cv2_path}")
        break

if cv2_path and os.path.exists(cv2_path):
    datas.append((cv2_path, 'cv2'))
    print(f"✅ Added cv2 directory to data")
    
    for file in os.listdir(cv2_path):
        full_path = os.path.join(cv2_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'cv2'))
            print(f"  Added cv2 binary: {file}")
else:
    print("⚠️ Could not find cv2 directory")
# ====================================================================
# EXCLUDES - Define BEFORE hiddenimports
# ====================================================================
excludes = [
    'jupyter', 'jupyter_client', 'jupyter_core', 'jupyterlab',
    'jupyterlab_server', 'jupyter_server', 'jupyter_events',
    'jupyter_lsp', 'jupyter_server_terminals', 'notebook',
    'notebook_shim', 'ipykernel', 'ipywidgets', 'widgetsnbextension',
    'jupyterlab_widgets', 'nbconvert', 'nbformat', 'nbclient',
    'ipython', 'ipython_genutils', 'traitlets', 'testpath',
    'terminado', 'jedi', 'parso', 'pexpect', 'ptyprocess',
    'pickleshare', 'decorator', 'backcall', 'matplotlib_inline',
    'appnope', 'stack_data', 'asttokens', 'executing', 'pure_eval',
    'tkinter',  # Exclude tkinter if not needed
]

# ====================================================================
# Add numpy - Using file system search
# ====================================================================
print("Looking for numpy...")
numpy_path = None
possible_numpy_paths = [
    os.path.join(BASE_PATH, 'venv', 'Lib', 'site-packages', 'numpy'),
    os.path.join(BASE_PATH, 'venv', 'lib', 'site-packages', 'numpy'),
]

for path in possible_numpy_paths:
    if os.path.exists(path) and os.path.isdir(path):
        numpy_path = path
        print(f"✅ Found numpy at: {numpy_path}")
        break

if numpy_path and os.path.exists(numpy_path):
    datas.append((numpy_path, 'numpy'))
    print(f"✅ Added numpy directory to data")
    
    # Add numpy.libs if it exists
    numpy_libs_path = os.path.join(numpy_path, 'libs')
    if os.path.exists(numpy_libs_path):
        datas.append((numpy_libs_path, 'numpy.libs'))
        print(f"✅ Added numpy.libs directory to data")
    
    for file in os.listdir(numpy_path):
        full_path = os.path.join(numpy_path, file)
        if os.path.isfile(full_path) and (file.endswith('.pyd') or file.endswith('.so') or file.endswith('.dylib')):
            binaries.append((full_path, 'numpy'))
            print(f"  Added numpy binary: {file}")
else:
    print("⚠️ Could not find numpy directory")
# ====================================================================
# HIDDEN IMPORTS - Define AFTER binaries and datas
# ====================================================================
hiddenimports = [
    'vt_scan',
    'recon',
    'recon_full',
    'web_security_analyzer',
    'edu_typing_engine',
    'crypto_engine',
    'deletion_protection',
    'financial_forensics',
    'hardening_dashboard',
    'integrity_monitor',
    'ransomware_monitor',
    'soc_nmap_dashboard',
    'sqlmap_scanner',
    'sqlmap_advanced',
    'telemetry_engine',
    'soc_automated_lab',
    'soc_enhanced_modules',
    'soc_ai_threat_hunter',
    'dst_footer',
    'update',
    'wifi_audit',
    'colorama',
    'rich',
    'rich.console',
    'rich.live',
    'rich.panel',
    'rich.progress',
    'rich.table',
    'rich.layout',
    'rich.align',
    'rich.box',
    'rich.prompt',
    'rich.syntax',
    'rich.tree',
    'prompt_toolkit',
    'cryptography',
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.backends',
    'requests',
    'psutil',
    'pyfiglet',
    'pillow',
    'plotly',
    'tqdm',
    'tqdm.auto',
    'tqdm.notebook',
    'tqdm.contrib',
    'reportlab',
    'reportlab.lib',
    'reportlab.platypus',
    'reportlab.lib.pagesizes',
    'reportlab.lib.styles',
    'reportlab.lib.colors',
    'reportlab.lib.units',
    'PIL',
    'PIL.Image',
    'qrcode',
    'cv2',
    'numpy',
    'numpy.core',
    'numpy.core.multiarray',
    'numpy.random',
    'numpy.lib',
    'numpy.linalg',
    'numpy.fft',
    'numpy.polynomial',
    'numpy.ma',
    'numpy.ctypeslib',
    'numpy.testing',
    'folium',
    'plotly',
    'geopy',
    'netifaces',
    'whois',
    'OpenSSL',
    'pytz',
    'matplotlib',
    'sqlite3',
    'json',
    'os',
    'sys',
    'subprocess',
    'datetime',
    'time',
    'logging',
    'glob',
    'shutil',
    'pathlib',
    'importlib',
    'importlib.util',
    'importlib.metadata',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'yaml',
    'argparse',
    'socket',
    'ssl',
    'threading',
    'queue',
    'http',
    'http.client',
    'http.server',
    'urllib',
    'urllib.parse',
    'xml',
    'xml.etree',
    'xml.etree.ElementTree',
    'zipfile',
    'tarfile',
    'tempfile',
    'hashlib',
    'base64',
    'hmac',
    'secrets',
    'random',
    'math',
    're',
    'struct',
    'pickle',
    'io',
    'types',
    'typing',
    'enum',
    'collections',
    'dataclasses',
    'functools',
    'itertools',
    'contextlib',
    'asyncio',
    'signal',
    'platform',
    'webbrowser',
    'ctypes',
    'winreg',
    # Add these common packages that might be missing
    'six',
    'packaging',
    'setuptools',
    'pip',
    'wheel',
    'click',
    'prettytable',
    'wcwidth',
    'decorator',
    'backcall',
    'parso',
    'jedi',
    'tornado',
    'pyzmq',
    'traitlets',
    'bleach',
    'defusedxml',
    'webencodings',
    'tinycss2',
    'mistune',
    'pandocfilters',
    'fastjsonschema',
    'jsonschema',
    'referencing',
    'rpds_py',
    'fpdf',
    'attrs',
]

# ====================================================================
# Auto-add all installed packages from site-packages
# ====================================================================
def get_installed_packages():
    """Get all installed packages from site-packages"""
    packages = []
    try:
        import pkg_resources
        for dist in pkg_resources.working_set:
            packages.append(dist.project_name)
    except:
        # Fallback: parse site-packages directories
        try:
            for site_dir in site.getsitepackages():
                if os.path.exists(site_dir):
                    for item in os.listdir(site_dir):
                        if item.endswith('.dist-info') or item.endswith('.egg-info'):
                            pkg_name = item.split('-')[0]
                            if pkg_name and pkg_name not in packages:
                                packages.append(pkg_name)
        except:
            pass
    return packages

# Add all installed packages to hidden imports
installed_packages = get_installed_packages()
if installed_packages:
    print(f"✅ Adding {len(installed_packages)} installed packages to hidden imports")
    hiddenimports.extend(installed_packages)
    # Remove duplicates
    hiddenimports = list(dict.fromkeys(hiddenimports))

print(f"Total hidden imports: {len(hiddenimports)}")

# ====================================================================
# Create the PyInstaller Analysis
# ====================================================================
a = Analysis(
    ['dsterminal.py'],
    pathex=[BASE_PATH],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# ====================================================================
# Create the executable
# ====================================================================
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dsterminal_win-3.1.113_x64-amd64',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['installer_assets\\3486-removebg-preview.ico'] if os.path.exists('installer_assets\\3486-removebg-preview.ico') else None,
)

# ====================================================================
# Add COLLECT for better organization
# ====================================================================
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dsterminal_win-3.1.113_x64-amd64'
)

print("=" * 60)
print("✅ Build configuration complete!")
print(f"   Data files: {len(datas)}")
print(f"   Binaries: {len(binaries)}")
print(f"   Hidden imports: {len(hiddenimports)}")
print(f"   Excludes: {len(excludes)}")
print("=" * 60)
