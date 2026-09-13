#!/bin/bash
# build-deb.sh - Complete DSTerminal .deb Builder with Desktop Copy
# Usage: ./build-deb.sh

set -e

# ============================================================
# CONFIGURATION
# ============================================================
VERSION=${VERSION:-"4.0.0.113"}
PROJECT_DIR="$HOME/Documents/stark/DSTerminal_releases_latest"
DESKTOP_DIR="$HOME/Desktop"

# ============================================================
# COLORS
# ============================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Building DSTerminal .deb Package ===${NC}"
echo -e "${BLUE}Version: ${VERSION}${NC}"
echo -e "${BLUE}Project: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}Desktop: ${DESKTOP_DIR}${NC}"

# ============================================================
# STEP 1: CLEAN EVERYTHING
# ============================================================
echo -e "\n${YELLOW}Step 1: Cleaning...${NC}"
cd "$PROJECT_DIR"
rm -rf build dist debian-package
rm -f dsterminal_*.deb dsterminal_*.deb.asc dsterminal_*.deb.sha256 *.tar.gz
# Also clean Desktop distribution folder
rm -rf "$DESKTOP_DIR/DSTerminal-Distribution"
rm -f "$DESKTOP_DIR/DSTerminal-*.tar.gz"
echo -e "${GREEN}✅ Clean complete${NC}"

# ============================================================
# STEP 2: BUILD PYINSTALLER EXECUTABLE
# ============================================================
echo -e "\n${YELLOW}Step 2: Building PyInstaller executable...${NC}"
source venv/bin/activate
pyinstaller --clean --noconfirm dsterminal_linux.spec
echo -e "${GREEN}✅ PyInstaller build complete${NC}"

# Verify executable
if [ ! -f "dist/dsterminal" ]; then
    echo -e "${RED}❌ Executable not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Executable: $(ls -lh dist/dsterminal | awk '{print $5}')${NC}"

# ============================================================
# STEP 3: CREATE DEBIAN PACKAGE STRUCTURE
# ============================================================
echo -e "\n${YELLOW}Step 3: Creating package structure...${NC}"
mkdir -p debian-package/DEBIAN
mkdir -p debian-package/opt/dsterminal
mkdir -p debian-package/usr/bin
mkdir -p debian-package/usr/share/applications
mkdir -p debian-package/usr/share/doc/dsterminal
mkdir -p debian-package/usr/share/man/man1
mkdir -p debian-package/usr/share/icons/hicolor/256x256/apps

cp dist/dsterminal debian-package/opt/dsterminal/dsterminal
chmod 755 debian-package/opt/dsterminal/dsterminal

# ============================================================
# STEP 4: CREATE LAUNCHER SCRIPT
# ============================================================
echo -e "\n${YELLOW}Step 4: Creating launcher script...${NC}"
cat > debian-package/usr/bin/dsterminal <<'EOF'
#!/bin/sh
exec /opt/dsterminal/dsterminal "$@"
EOF
chmod 755 debian-package/usr/bin/dsterminal

# ============================================================
# STEP 5: CREATE CONTROL FILE
# ============================================================
echo -e "\n${YELLOW}Step 5: Creating control file...${NC}"
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
Depends: nmap, openssl, iproute2, python3, python3-requests
Recommends: python3-rich, python3-colorama
EOF

# ============================================================
# STEP 6: CREATE DESKTOP ENTRY
# ============================================================
echo -e "\n${YELLOW}Step 6: Creating desktop entry...${NC}"
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

# ============================================================
# STEP 7: CREATE POST-INSTALL SCRIPT
# ============================================================
echo -e "\n${YELLOW}Step 7: Creating post-install script...${NC}"
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

# ============================================================
# STEP 8: ADD DOCUMENTATION
# ============================================================
echo -e "\n${YELLOW}Step 8: Adding documentation...${NC}"
cat > debian-package/usr/share/doc/dsterminal/copyright <<'EOF'
DSTerminal - Defensive Security Terminal
Copyright (c) 2024-2026 Stark Expo Tech Exchange
All rights reserved.
EOF

cat > debian-package/usr/share/doc/dsterminal/changelog <<EOF
DSTerminal (${VERSION}) stable; urgency=medium

  * Initial release with PyInstaller standalone build
  * Real-time threat monitoring and ransomware detection
  * Web dashboard and security scanning tools
  * Man page documentation

 -- Stark Expo Tech Exchange <support@starkexpo.tech>  $(date -R)
EOF
gzip -9 -n debian-package/usr/share/doc/dsterminal/changelog

# ============================================================
# STEP 9: CREATE MAN PAGE
# ============================================================
echo -e "\n${YELLOW}Step 9: Creating man page...${NC}"
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

gzip -9 -n debian-package/usr/share/man/man1/dsterminal.1

# ============================================================
# STEP 10: VERIFY PACKAGE STRUCTURE
# ============================================================
echo -e "\n${YELLOW}Step 10: Verifying package structure...${NC}"
echo -e "${BLUE}Files in package:${NC}"
find debian-package -type f -exec ls -lh {} \; | awk '{print "  " $9 " (" $5 ")"}' | head -20

# ============================================================
# STEP 11: BUILD THE .DEB
# ============================================================
echo -e "\n${YELLOW}Step 11: Building .deb package...${NC}"
dpkg-deb --build debian-package "dsterminal_${VERSION}_amd64.deb"

if [ -f "dsterminal_${VERSION}_amd64.deb" ]; then
    echo -e "${GREEN}✅ Package built: $(ls -lh dsterminal_${VERSION}_amd64.deb | awk '{print $5}')${NC}"
else
    echo -e "${RED}❌ Package build failed!${NC}"
    exit 1
fi

# ============================================================
# STEP 12: VERIFY THE PACKAGE
# ============================================================
echo -e "\n${YELLOW}Step 12: Verifying package...${NC}"
echo -e "${BLUE}Package Info:${NC}"
dpkg-deb --info "dsterminal_${VERSION}_amd64.deb" | head -15

echo -e "${BLUE}Contents:${NC}"
dpkg-deb --contents "dsterminal_${VERSION}_amd64.deb" | head -15

# ============================================================
# STEP 13: CREATE CHECKSUMS
# ============================================================
echo -e "\n${YELLOW}Step 13: Creating checksums...${NC}"
sha256sum "dsterminal_${VERSION}_amd64.deb" > "dsterminal_${VERSION}_amd64.deb.sha256"
echo -e "${GREEN}✅ SHA256 created${NC}"

# ============================================================
# STEP 14: COPY TO DESKTOP
# ============================================================
echo -e "\n${YELLOW}Step 14: Copying to Desktop...${NC}"

# Create distribution folder on Desktop
mkdir -p "$DESKTOP_DIR/DSTerminal-Distribution"

# Copy the main .deb file
cp "dsterminal_${VERSION}_amd64.deb" "$DESKTOP_DIR/DSTerminal-Distribution/"
echo -e "${GREEN}✅ Copied .deb to Desktop${NC}"

# Copy checksum
cp "dsterminal_${VERSION}_amd64.deb.sha256" "$DESKTOP_DIR/DSTerminal-Distribution/"
echo -e "${GREEN}✅ Copied checksum${NC}"

# Copy man page
cp -r debian-package/usr/share/man "$DESKTOP_DIR/DSTerminal-Distribution/" 2>/dev/null || true

# Create install script for Desktop
cat > "$DESKTOP_DIR/DSTerminal-Distribution/install.sh" <<'EOF'
#!/bin/bash
echo "==================================================="
echo "   DSTERMINAL - Quick Install"
echo "==================================================="
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run with sudo: sudo ./install.sh"
    exit 1
fi
apt install ./dsterminal_*.deb
echo ""
echo "✅ Installation complete!"
echo "   Run 'dsterminal' to start the security terminal"
echo "   Type 'man dsterminal' for documentation"
EOF
chmod +x "$DESKTOP_DIR/DSTerminal-Distribution/install.sh"
echo -e "${GREEN}✅ Created install script${NC}"

# Create README
cat > "$DESKTOP_DIR/DSTerminal-Distribution/README.txt" <<EOF
DSTERMINAL SECURITY TERMINAL v${VERSION}

===================================================
QUICK INSTALL
===================================================
sudo ./install.sh

OR manually:
sudo apt install ./dsterminal_${VERSION}_amd64.deb

===================================================
AFTER INSTALLATION
===================================================
dsterminal           - Start the terminal
man dsterminal       - View documentation
dsterminal-update    - Check for updates (if available)

===================================================
VERIFY INSTALLATION
===================================================
which dsterminal     # Should show /usr/bin/dsterminal
dpkg -l dsterminal   # Should show the package

===================================================
FILES INCLUDED
===================================================
dsterminal_${VERSION}_amd64.deb  - Main installer
dsterminal_*.deb.sha256          - SHA256 checksum
install.sh                       - Quick install script
README.txt                       - This file
man/                             - Man page documentation

===================================================
SUPPORT
===================================================
Email: support@starkexpo.tech
GitHub: https://github.com/Stark-Expo-Tech-Exchange

© 2024-2026 Stark Expo Tech Exchange
EOF
echo -e "${GREEN}✅ Created README${NC}"

# ============================================================
# STEP 15: CREATE DISTRIBUTION ARCHIVE ON DESKTOP
# ============================================================
echo -e "\n${YELLOW}Step 15: Creating distribution archive...${NC}"
cd "$DESKTOP_DIR"
tar -czf "DSTerminal-${VERSION}-distribution.tar.gz" DSTerminal-Distribution/
echo -e "${GREEN}✅ Archive created: $(ls -lh DSTerminal-${VERSION}-distribution.tar.gz | awk '{print $5}')${NC}"

# ============================================================
# STEP 16: SHOW SUMMARY
# ============================================================
echo -e "\n${GREEN}=== BUILD COMPLETE! ===${NC}"
echo ""
echo -e "${BLUE}📦 Package:${NC}"
echo "  $PROJECT_DIR/dsterminal_${VERSION}_amd64.deb ($(ls -lh dsterminal_${VERSION}_amd64.deb | awk '{print $5}'))"
echo ""
echo -e "${BLUE}📂 Desktop Distribution Folder:${NC}"
echo "  $DESKTOP_DIR/DSTerminal-Distribution/"
ls -lh "$DESKTOP_DIR/DSTerminal-Distribution/" | awk '{print "    " $9 " (" $5 ")"}'
echo ""
echo -e "${BLUE}📦 Desktop Distribution Archive:${NC}"
echo "  $DESKTOP_DIR/DSTerminal-${VERSION}-distribution.tar.gz ($(ls -lh "$DESKTOP_DIR/DSTerminal-${VERSION}-distribution.tar.gz" | awk '{print $5}'))"
echo ""
echo -e "${YELLOW}To install:${NC}"
echo "  cd ~/Desktop/DSTerminal-Distribution && sudo ./install.sh"
echo ""
echo -e "${YELLOW}To distribute:${NC}"
echo "  Share: ~/Desktop/DSTerminal-${VERSION}-distribution.tar.gz"
echo ""
echo -e "${GREEN}✅ Done!${NC}"