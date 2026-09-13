Step 1: Clean Everything
# Go to your project directory
cd ~/Documents/stark/DSTerminal_releases_latest

# Clean all previous builds
rm -rf build dist debian-package
rm -f dsterminal_*.deb
rm -f dsterminal_*.deb.asc
rm -f dsterminal_*.deb.sha256
rm -f *.tar.gz

# Verify everything is clean
echo "=== Clean directory ==="
ls -la | grep -E "(build|dist|debian-package|dsterminal_.*\.deb)" || echo "✅ All clean!"


<!--  -->
Step 2: Build PyInstaller Executable
# Activate virtual environment
source venv/bin/activate

# Clean PyInstaller cache and build
pyinstaller --clean --noconfirm dsterminal_linux.spec

# Verify the executable
echo "=== Executable created ==="
ls -lh dist/dsterminal
file dist/dsterminal


<!--  -->
Step 3: Create Debian Package Structure
# Set version (clean, no spaces or newlines)
VERSION="4.0.0.113"

# Create directory structure
mkdir -p debian-package/DEBIAN
mkdir -p debian-package/opt/dsterminal
mkdir -p debian-package/usr/bin
mkdir -p debian-package/usr/share/applications
mkdir -p debian-package/usr/share/doc/dsterminal

# Copy the executable
cp dist/dsterminal debian-package/opt/dsterminal/dsterminal
chmod 755 debian-package/opt/dsterminal/dsterminal

# Verify
echo "=== Executable in package ==="
ls -lh debian-package/opt/dsterminal/dsterminal

<!-- -->
Step 4: Create the Launcher Script (CRITICAL!)
# Create the wrapper script that goes in /usr/bin/
cat > debian-package/usr/bin/dsterminal <<'EOF'
#!/bin/sh
exec /opt/dsterminal/dsterminal "$@"
EOF
chmod 755 debian-package/usr/bin/dsterminal

# Verify
echo "=== Launcher script ==="
ls -lh debian-package/usr/bin/dsterminal
cat debian-package/usr/bin/dsterminal

<!--  -->
Step 5: Create DEBIAN/control File
# Create the control file
cat > debian-package/DEBIAN/control <<EOF
Package: dsterminal
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Stark Expo Tech Exchange <support@starkexpo.tech>
Description: DSTerminal Defensive Security Terminal
 AI-assisted defensive cybersecurity monitoring, security analysis,
 threat detection and SOC operations terminal platform.
Depends: nmap, openssl, iproute2
EOF

# Verify
echo "=== Control file ==="
cat debian-package/DEBIAN/control

<!--  -->
Step 6: Create Desktop Entry
# Create .desktop file
cat > debian-package/usr/share/applications/dsterminal.desktop <<'EOF'
[Desktop Entry]
Name=DSTerminal
GenericName=Defensive Security Terminal
Comment=AI-assisted defensive cybersecurity monitoring and SOC platform
Exec=/usr/bin/dsterminal
Terminal=true
Type=Application
Categories=System;Security;Utility;
StartupNotify=true
Icon=dsterminal
EOF

# Verify
echo "=== Desktop file ==="
cat debian-package/usr/share/applications/dsterminal.desktop

<!--  -->
Step 7: Create Post-Installation Script
# Create post-install script
cat > debian-package/DEBIAN/postinst <<'EOF'
#!/bin/sh
set -e

# Create configuration directory
mkdir -p /etc/dsterminal

# Set proper permissions
chmod 755 /opt/dsterminal/dsterminal
chmod 755 /usr/bin/dsterminal

# Update desktop database if available
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database
fi

echo ""
echo "==================================================="
echo "   DSTERMINAL INSTALLED SUCCESSFULLY!"
echo "==================================================="
echo "   Run 'dsterminal' to start the security terminal"
echo "==================================================="
echo ""
EOF
chmod 755 debian-package/DEBIAN/postinst

# Verify
echo "=== Post-install script ==="
cat debian-package/DEBIAN/postinst

<!--  -->
Step 8: Add Documentation
# Create copyright file
cat > debian-package/usr/share/doc/dsterminal/copyright <<'EOF'
DSTerminal - Defensive Security Terminal
Copyright (c) 2024-2026 Stark Expo Tech Exchange
All rights reserved.
EOF

# Create changelog
cat > debian-package/usr/share/doc/dsterminal/changelog <<EOF
DSTerminal (${VERSION}) stable; urgency=medium

  * Initial release with PyInstaller standalone build
  * Real-time threat monitoring and ransomware detection
  * Web dashboard and security scanning tools

 -- Stark Expo Tech Exchange <support@starkexpo.tech>  $(date -R)
EOF
gzip -9 -n debian-package/usr/share/doc/dsterminal/changelog

<!--  -->
Step 9: Verify Package Structure
# Check the complete structure
echo "=== Package Structure ==="
find debian-package -type f -exec ls -lh {} \;
echo ""
echo "=== Directory Structure ==="
tree debian-package 2>/dev/null || find debian-package -type d | sort

<!--  -->
Step 10: Build the .deb Package

# Build the package
dpkg-deb --build debian-package "dsterminal_${VERSION}_amd64.deb"

# Check if created
echo "=== Package Created ==="
ls -lh dsterminal_*.deb

<!--  -->
Step 11: Verify the Package
# Show package info
echo "=== Package Info ==="
dpkg-deb --info "dsterminal_${VERSION}_amd64.deb"

# Show contents
echo "=== Package Contents ==="
dpkg-deb --contents "dsterminal_${VERSION}_amd64.deb"

# Check dependencies
echo "=== Dependencies ==="
dpkg-deb -I "dsterminal_${VERSION}_amd64.deb" | grep -E "(Package|Version|Depends)"


<!--  -->
Step 12: Install and Test
# Install the package
sudo apt install "./dsterminal_${VERSION}_amd64.deb"

# Verify installation
echo "=== Installation Verification ==="
which dsterminal
dpkg -L dsterminal | head -20

# Test it (exit venv first)
deactivate
echo "=== Testing DSTerminal ==="
dsterminal --version 2>/dev/null || dsterminal -h 2>/dev/null || echo "Run 'dsterminal' to start the terminal"

<!--  -->
Step 13: Create Checksums (Optional)

# Create SHA256 checksum
sha256sum "dsterminal_${VERSION}_amd64.deb" > "dsterminal_${VERSION}_amd64.deb.sha256"

# Create GPG signature (if you have a GPG key)
gpg --detach-sign --armor "dsterminal_${VERSION}_amd64.deb" 2>/dev/null || echo "No GPG key found, skipping signature"

# Show checksums
echo "=== Checksums ==="
cat "dsterminal_${VERSION}_amd64.deb.sha256"

<!--  -->
Step 14: Create Distribution Archive
# Create distribution folder
mkdir -p ~/Desktop/DSTerminal-Distribution

# Copy files
cp "dsterminal_${VERSION}_amd64.deb" ~/Desktop/DSTerminal-Distribution/
cp "dsterminal_${VERSION}_amd64.deb.sha256" ~/Desktop/DSTerminal-Distribution/ 2>/dev/null || true
cp "dsterminal_${VERSION}_amd64.deb.asc" ~/Desktop/DSTerminal-Distribution/ 2>/dev/null || true

# Create simple install script
cat > ~/Desktop/DSTerminal-Distribution/install.sh <<'EOF'
#!/bin/bash
echo "==================================================="
echo "   DSTERMINAL - Quick Install"
echo "==================================================="
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run with sudo: sudo ./install.sh"
    exit 1
fi
apt install ./dsterminal_*.deb
echo "✅ Installation complete! Run 'dsterminal' to start."
EOF
chmod +x ~/Desktop/DSTerminal-Distribution/install.sh

# Create README
cat > ~/Desktop/DSTerminal-Distribution/README.txt <<'EOF'
DSTERMINAL SECURITY TERMINAL v4.0.0.113

Installation:
  sudo ./install.sh

Or manually:
  sudo apt install ./dsterminal_4.0.0.113_amd64.deb

After installation:
  dsterminal

For help:
  dsterminal --help
  Type 'help' inside the terminal
EOF

# Compress for distribution
cd ~/Desktop
tar -czf "DSTerminal-${VERSION}-distribution.tar.gz" DSTerminal-Distribution/

echo "=== Distribution Archive ==="
ls -lh "DSTerminal-${VERSION}-distribution.tar.gz"

<!--  -->
📚 Adding the Man Page
Step 1: Create the Man Page Directory Structure
# Create man page directory in the package
cd ~/Documents/stark/DSTerminal_releases_latest
mkdir -p debian-package/usr/share/man/man1



<!--  -->
Step 2: Create the Man Page
# Create the man page file
cat > debian-package/usr/share/man/man1/dsterminal.1 <<'EOF'
.\" DSTerminal Man Page
.\" Copyright (c) 2024-2026 Stark Expo Tech Exchange
.TH DSTERMINAL 1 "September 2026" "4.0.0.113" "User Commands"
.SH NAME
dsterminal \- Defensive Security Terminal \- AI-assisted cybersecurity monitoring and SOC platform

.SH SYNOPSIS
.B dsterminal
[\fIOPTIONS\fR]

.SH DESCRIPTION
DSTerminal is a comprehensive defensive security terminal that provides:
.IP \(bu 2
Real-time threat monitoring and alerting
.IP \(bu
AI-assisted ransomware detection with auto-quarantine
.IP \(bu
MITRE ATT&CK technique mapping and tracking
.IP \(bu
Network security scanning and vulnerability assessment
.IP \(bu
Web application security analysis
.IP \(bu
Financial fraud investigation tools
.IP \(bu
System hardening and integrity checking

.SH OPTIONS
.TP
.B \-h, \-\-help
Display this help message and exit.
.TP
.B \-v, \-\-version
Display version information and exit.
.TP
.B \-\-workspace \fIDIR\fR
Set custom workspace directory.
.TP
.B \-\-no-dashboard
Disable dashboard server startup.
.TP
.B \-\-port \fIPORT\fR
Set dashboard port (default: 5000).

.SH COMMANDS
Inside DSTerminal, type \fBhelp\fR for a complete list of available commands.

.SH EXAMPLES
.TP
\fBdsterminal\fR
Launch DSTerminal with default settings.
.TP
\fBdsterminal \-\-port 8080\fR
Launch DSTerminal with dashboard on port 8080.
.TP
\fBdsterminal \-\-workspace ~/my-workspace\fR
Launch with custom workspace directory.

.SH FILES
.TP
\fI/opt/dsterminal/dsterminal\fR
Main executable.
.TP
\fI/etc/dsterminal/\fR
System-wide configuration directory.
.TP
\fI~/.config/DSTerminal/\fR
User workspace and configuration.

.SH ENVIRONMENT
.TP
\fBDSTERMINAL_WORKSPACE\fR
Override the default workspace directory.

.SH AUTHOR
Developed by Spark Wilson Spink (c) 2024-2026

.SH REPORTING BUGS
Report bugs to: support@starkexpo.tech

.SH COPYRIGHT
Copyright (c) 2024-2026 Stark Expo Tech Exchange
All rights reserved.

.SH SEE ALSO
.BR nmap(1),
.BR openssl(1),
.BR ip(8)
EOF

# Verify the man page was created
echo "=== Man Page ==="
cat debian-package/usr/share/man/man1/dsterminal.1


<!--  -->
# Update the post-install script to update the man database
cat > debian-package/DEBIAN/postinst <<'EOF'
#!/bin/sh
set -e

# Create configuration directory
mkdir -p /etc/dsterminal

# Set proper permissions
chmod 755 /opt/dsterminal/dsterminal
chmod 755 /usr/bin/dsterminal

# Update desktop database if available
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database
fi

# Update man database if available
if command -v mandb >/dev/null 2>&1; then
    mandb -q
fi

echo ""
echo "==================================================="
echo "   DSTERMINAL INSTALLED SUCCESSFULLY!"
echo "==================================================="
echo "   Run 'dsterminal' to start the security terminal"
echo "   Type 'man dsterminal' for documentation"
echo "==================================================="
echo ""
EOF
chmod 755 debian-package/DEBIAN/postinst

<!--  -->
# Check the man page file
echo "=== Man Page in Package ==="
file debian-package/usr/share/man/man1/dsterminal.1.gz
gunzip -c debian-package/usr/share/man/man1/dsterminal.1.gz | head -20

<!--  -->
Step 6: Rebuild the Package
# Rebuild with man page included
dpkg-deb --build debian-package "dsterminal_${VERSION}_amd64.deb"

# Verify man page is included
echo "=== Package Contents with Man Page ==="
dpkg-deb --contents "dsterminal_${VERSION}_amd64.deb" | grep man

<!--  -->
Step 7: Install and Test Man Page
# Install the updated package
sudo apt install "./dsterminal_${VERSION}_amd64.deb"

# Test the man page
man dsterminal

<!--  -->
# Copy to Desktop distribution folder
mkdir -p ~/Desktop/DSTerminal-Distribution
cp "dsterminal_${VERSION}_amd64.deb" ~/Desktop/DSTerminal-Distribution/
cp "dsterminal_${VERSION}_amd64.deb.sha256" ~/Desktop/DSTerminal-Distribution/ 2>/dev/null || true

# Create distribution archive
cd ~/Desktop
tar -czf "DSTerminal-${VERSION}-distribution.tar.gz" DSTerminal-Distribution/

echo "=== Final Package ==="
ls -lh "DSTerminal-${VERSION}-distribution.tar.gz"