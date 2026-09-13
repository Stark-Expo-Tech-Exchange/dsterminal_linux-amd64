#!/bin/bash
# Quick install script for DSTerminal

echo "=== DSTerminal Quick Install ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Install the package
apt install ./dsterminal_4.0.0.113_amd64.deb

echo ""
echo "=== Installation Complete ==="
echo "Run 'dsterminal' to start the security terminal"
