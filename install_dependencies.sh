#!/bin/bash

echo "[+] Installing DSTERMINAL Dependencies..."

# Update package manager
sudo apt update

# Install core tools
sudo apt install -y nmap
sudo apt install -y whois
sudo apt install -y sqlmap

# Install Metasploit (Ubuntu/Debian)
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
sudo ./msfinstall

# Install Python dependencies
pip install colorama
pip install requests
pip install folium plotly
pip install reportlab

# Install additional tools
sudo apt install -y net-tools
sudo apt install -y curl wget

echo "[+] All dependencies installed successfully!"