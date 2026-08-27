#!/bin/bash
# Generate clean requirements.txt for Linux

source venv/bin/activate

# Generate requirements and filter out Windows-only packages
pip freeze | grep -v -E \
    -e "auto-py-to-exe" \
    -e "pywin32" \
    -e "pefile" \
    -e "altgraph" \
    -e "pyinstaller" \
    -e "Eel" \
    -e "opencv-python" \
    -e "pyzbar" \
    -e "steg-analyzer" \
    -e "dataclasses" \
    -e "importlib" \
    -e "ipaddress" \
    -e "distro" \
    -e "dotenv" \
    -e "docx" \
    -e "flatbuffers" \
    -e "fpdf" \
> requirements_linux.txt

echo "✅ Generated requirements_linux.txt"
echo "📊 Total packages: $(wc -l < requirements_linux.txt)"
echo ""
echo "First 10 packages:"
head -10 requirements_linux.txt
