#!/bin/bash
# Complete repository setup script

set -e

echo "=== Setting up DSTerminal APT Repository ==="

# Variables
VERSION=$(cat VERSION 2>/dev/null || echo "4.0.0.113")
GPG_KEY_ID="41505F4CA0180402"  # Replace with your key ID

# Create repository structure
mkdir -p apt-repo/pool/main/d/dsterminal
mkdir -p apt-repo/dists/stable/main/binary-amd64
mkdir -p apt-repo/dists/stable/main/binary-all

# Copy package
cp dsterminal_${VERSION}_amd64.deb apt-repo/pool/main/d/dsterminal/

# Export GPG key
gpg --armor --export ${GPG_KEY_ID} > apt-repo/dsterminal-repo-key.asc

# Generate Packages files
cd apt-repo
dpkg-scanpackages --arch amd64 pool/ > dists/stable/main/binary-amd64/Packages
dpkg-scanpackages --arch all pool/ > dists/stable/main/binary-all/Packages

# Compress Packages files
gzip -k -9 dists/stable/main/binary-amd64/Packages
gzip -k -9 dists/stable/main/binary-all/Packages

# Generate Release file
cat > dists/stable/Release <<EOC
Origin: Stark Expo Tech Exchange
Label: DSTerminal
Suite: stable
Codename: stable
Version: ${VERSION}
Date: $(date -R)
Architectures: amd64 all
Components: main
Description: DSTerminal Defensive Security Terminal Repository
EOC

# Sign Release file
gpg --armor --detach-sign --output dists/stable/Release.gpg dists/stable/Release
gpg --clearsign --output dists/stable/InRelease dists/stable/Release

cd ..

echo "=== Repository setup complete! ==="
echo ""
echo "Repository location: ./apt-repo"
echo ""
echo "To use this repository, add this line to /etc/apt/sources.list.d/dsterminal.list:"
echo "  deb [trusted=yes] file://$(pwd)/apt-repo stable main"
echo ""
echo "Or serve it with a web server:"
echo "  sudo cp -r apt-repo /var/www/html/"
echo "  deb [trusted=yes] http://your-server/apt-repo stable main"
