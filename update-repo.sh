#!/bin/bash
# Update the DSTerminal APT repository

REPO_DIR="/var/www/html/apt-repo"  # Change to your web server path

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Copy the latest .deb file to the repository
cp dsterminal_*.deb "$REPO_DIR/pool/main/d/dsterminal/"

# Update Packages files
cd "$REPO_DIR"
dpkg-scanpackages --arch amd64 pool/ > dists/stable/main/binary-amd64/Packages
dpkg-scanpackages --arch all pool/ > dists/stable/main/binary-all/Packages

# Compress Packages files
gzip -k -9 dists/stable/main/binary-amd64/Packages
gzip -k -9 dists/stable/main/binary-all/Packages

# Update Release file
cat > dists/stable/Release <<EOC
Origin: Stark Expo Tech Exchange
Label: DSTerminal
Suite: stable
Codename: stable
Version: $(cat ../VERSION 2>/dev/null || echo "4.0.0.113")
Date: $(date -R)
Architectures: amd64 all
Components: main
Description: DSTerminal Defensive Security Terminal Repository
EOC

# Sign the Release file
gpg --armor --detach-sign --output dists/stable/Release.gpg dists/stable/Release
gpg --clearsign --output dists/stable/InRelease dists/stable/Release

echo "Repository updated successfully!"
