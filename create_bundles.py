# create_bundles.py - Complete Fixed Version
import os
import sys
import shutil
import hashlib
from pathlib import Path
import zipfile
import subprocess
import time
import json  # <-- Added missing import

def create_bundles():
    """Create bundled packages from downloaded installers"""
    print("=" * 60)
    print("ðŸ“¦ DSTerminal Bundle Creator")
    print("=" * 60)
    
    # Setup paths
    bundle_dir = Path(__file__).parent / "bundled"
    source_dir = Path.home() / "DSTerminal" / "downloads"
    temp_dir = Path.home() / "DSTerminal" / "temp"
    
    bundle_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    if not source_dir.exists():
        print(f"âŒ Source directory not found: {source_dir}")
        print("Please run the installer first to download the files.")
        return
    
    # Clean up temp directory
    print(f"\nðŸ§¹ Cleaning temp directory: {temp_dir}")
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
        time.sleep(1)
        temp_dir.mkdir(parents=True, exist_ok=True)
        print("  âœ… Temp directory cleaned")
    except Exception as e:
        print(f"  âš ï¸ Could not clean temp directory: {e}")
    
    # Create bundle structure
    packages = {
        'nmap': {
            'file': 'nmap-7.95-setup.exe',
            'dest': 'nmap/nmap-7.95-setup.exe',
            'description': 'Nmap network scanner'
        },
        'npcap': {
            'file': 'npcap-1.79.exe',
            'dest': 'npcap/npcap-1.79.exe',
            'description': 'Npcap packet capture library'
        },
        'metasploit': {
            'file': 'metasploit-latest-windows-x64-installer.exe',
            'dest': 'metasploit/metasploit-latest-windows-x64-installer.exe',
            'description': 'Metasploit Framework'
        },
        'sqlmap': {
            'file': 'sqlmap.zip',
            'dest': 'sqlmap/sqlmap.zip',
            'description': 'SQL injection tool',
            'create_from_git': 'https://github.com/sqlmapproject/sqlmap.git'
        },
        'nikto': {
            'file': 'nikto.zip',
            'dest': 'nikto/nikto.zip',
            'description': 'Web server scanner',
            'create_from_git': 'https://github.com/sullo/nikto.git'
        },
        'whois': {
            'file': 'whois.ps1',
            'dest': 'whois/whois.ps1',
            'description': 'Whois lookup script',
            'create_script': True
        }
    }
    
    # Bundle each package
    for package_name, info in packages.items():
        print(f"\nðŸ“¦ Processing {package_name} ({info['description']})...")
        
        # Create package directory
        package_dir = bundle_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # Handle different package types
        if info.get('create_script'):
            # Create whois script
            if package_name == 'whois':
                script_content = '''param(
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
'''
                dest_file = package_dir / 'whois.ps1'
                with open(dest_file, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                print(f"  âœ… Created whois script")
                
                # Create checksum
                sha256_hash = hashlib.sha256()
                with open(dest_file, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                checksum = sha256_hash.hexdigest()
                
                checksum_file = package_dir / f"{package_name}.sha256"
                with open(checksum_file, 'w') as f:
                    f.write(checksum)
                print(f"  âœ… Created checksum for whois")
        
        elif info.get('create_from_git'):
            # Clone from git and create zip
            print(f"  Cloning from: {info['create_from_git']}")
            
            repo_name = info['create_from_git'].split('/')[-1].replace('.git', '')
            repo_dir = temp_dir / repo_name
            
            # Remove existing directory if it exists
            if repo_dir.exists():
                print(f"  Removing existing directory: {repo_dir}")
                try:
                    shutil.rmtree(repo_dir, ignore_errors=True)
                    time.sleep(1)
                except Exception as e:
                    print(f"  âš ï¸ Could not remove directory: {e}")
                    # Try using system command
                    try:
                        if sys.platform == 'win32':
                            subprocess.run(['rmdir', '/s', '/q', str(repo_dir)], shell=True, check=False)
                        else:
                            subprocess.run(['rm', '-rf', str(repo_dir)], check=False)
                        time.sleep(1)
                    except:
                        pass
            
            # Clone repository
            try:
                print(f"  Cloning into: {repo_dir}")
                result = subprocess.run(
                    ['git', 'clone', '--depth', '1', info['create_from_git'], str(repo_dir)],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    print(f"  âœ… Clone completed")
                else:
                    print(f"  âŒ Clone failed: {result.stderr}")
                    continue
            except Exception as e:
                print(f"  âŒ Clone error: {e}")
                continue
            
            if repo_dir.exists():
                # Create zip with proper handling
                zip_path = package_dir / info['file']
                print(f"  Creating zip: {zip_path}")
                
                try:
                    # Check if directory has content
                    files_count = sum(1 for _ in repo_dir.rglob('*') if _.is_file())
                    if files_count == 0:
                        print(f"  âš ï¸ No files found in repository")
                        continue
                    
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        # Walk through the directory
                        for root, dirs, files in os.walk(repo_dir):
                            for file in files:
                                file_path = Path(root) / file
                                try:
                                    # Get relative path
                                    rel_path = file_path.relative_to(repo_dir.parent)
                                    # Write file to zip
                                    zipf.write(file_path, str(rel_path))
                                except Exception as e:
                                    # Skip problematic files
                                    continue
                    
                    if zip_path.exists() and zip_path.stat().st_size > 0:
                        print(f"  âœ… Created zip from git: {info['file']}")
                        
                        # Create checksum
                        sha256_hash = hashlib.sha256()
                        with open(zip_path, "rb") as f:
                            for byte_block in iter(lambda: f.read(4096), b""):
                                sha256_hash.update(byte_block)
                        checksum = sha256_hash.hexdigest()
                        
                        checksum_file = package_dir / f"{package_name}.sha256"
                        with open(checksum_file, 'w') as f:
                            f.write(checksum)
                        print(f"  âœ… Created checksum for {package_name}")
                    else:
                        print(f"  âŒ Failed to create zip (empty or missing)")
                        
                except Exception as e:
                    print(f"  âŒ Failed to create zip: {e}")
                    continue
        
        else:
            # Copy from downloads
            src_file = source_dir / info['file']
            dest_file = package_dir / info['file']
            
            if src_file.exists():
                # Copy file
                shutil.copy2(src_file, dest_file)
                print(f"  âœ… Copied: {info['file']}")
                
                # Create checksum
                sha256_hash = hashlib.sha256()
                with open(src_file, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                checksum = sha256_hash.hexdigest()
                
                checksum_file = package_dir / f"{package_name}.sha256"
                with open(checksum_file, 'w') as f:
                    f.write(checksum)
                print(f"  âœ… Created checksum for {package_name}")
            else:
                print(f"  âš ï¸ Source file not found: {src_file}")
                print(f"     Please download {info['file']} first.")
    
    # Also create a bundle manifest
    manifest_path = bundle_dir / "manifest.json"
    manifest = {
        'created': time.strftime('%Y-%m-%d %H:%M:%S'),
        'packages': {}
    }
    
    for package_name in packages:
        package_dir = bundle_dir / package_name
        if package_dir.exists():
            manifest['packages'][package_name] = {
                'bundled': True,
                'path': str(package_dir)
            }
            # Add file list
            files = []
            for file in package_dir.iterdir():
                if file.is_file() and not file.name.endswith('.sha256'):
                    files.append(file.name)
            manifest['packages'][package_name]['files'] = files
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nâœ… Created bundle manifest: {manifest_path}")
    
    print("\n" + "=" * 60)
    print("ðŸŽ‰ Bundle creation complete!")
    print(f"ðŸ“ Bundles are in: {bundle_dir}")
    print("=" * 60)
    print("\nðŸ“‹ Next steps:")
    print("1. The 'bundled' folder is now ready")
    print("2. Run DSTerminal - it will use bundled packages first")
    print("3. To force using bundles: python dsterminal.py --install-all")
    
    # Display bundle sizes
    print("\nðŸ“Š Bundle Summary:")
    total_size = 0
    for package_name in packages:
        package_dir = bundle_dir / package_name
        if package_dir.exists():
            size = sum(f.stat().st_size for f in package_dir.glob('**/*') if f.is_file())
            size_mb = size / (1024 * 1024)
            print(f"  {package_name}: {size_mb:.2f} MB")
            total_size += size
    total_mb = total_size / (1024 * 1024)
    print(f"\n  Total bundled size: {total_mb:.2f} MB")

if __name__ == "__main__":
    create_bundles()