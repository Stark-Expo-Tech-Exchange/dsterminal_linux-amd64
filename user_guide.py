# generate_user_guide.py
# Run this script to create user_guide.pdf in the docs folder

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Preformatted
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ============================================================
# CONFIGURATION
# ============================================================
DOCS_FOLDER = "docs"
PDF_FILENAME = "user_guide.pdf"
PDF_PATH = os.path.join(DOCS_FOLDER, PDF_FILENAME)

# Create docs folder if it doesn't exist
os.makedirs(DOCS_FOLDER, exist_ok=True)

# ============================================================
# PDF DOCUMENT GENERATION
# ============================================================
def generate_pdf():
    """Generate the complete user guide PDF"""
    
    # Document setup
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        title="DSTerminal User Guide",
        author="Stark Expo Tech Exchange"
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CyberTitle',
        parent=styles['Heading1'],
        textColor=colors.Color(0, 1, 0.6),
        fontSize=28,
        alignment=TA_CENTER,
        spaceAfter=30,
        backColor=colors.Color(0.1, 0.1, 0.1, alpha=0.5)
    ))
    
    styles.add(ParagraphStyle(
        name='CyberHeading1',
        parent=styles['Heading1'],
        textColor=colors.Color(0, 1, 0.6),
        fontSize=20,
        spaceBefore=20,
        spaceAfter=10,
        borderWidth=1,
        borderColor=colors.Color(0, 1, 0.6, alpha=0.3)
    ))
    
    styles.add(ParagraphStyle(
        name='CyberHeading2',
        parent=styles['Heading2'],
        textColor=colors.Color(0, 0.8, 1),
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='CyberHeading3',
        parent=styles['Heading3'],
        textColor=colors.white,
        fontSize=14,
        spaceBefore=10,
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        name='CyberBody',
        parent=styles['Normal'],
        textColor=colors.Color(0.9, 0.9, 0.9),
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='CyberCode',
        parent=styles['Code'],
        textColor=colors.Color(0, 1, 0.6),
        fontSize=9,
        backColor=colors.Color(0.1, 0.1, 0.1),
        borderPadding=5,
        borderWidth=1,
        borderColor=colors.Color(0, 1, 0.6, alpha=0.3)
    ))
    
    styles.add(ParagraphStyle(
        name='Warning',
        parent=styles['Normal'],
        textColor=colors.Color(1, 0.5, 0),
        fontSize=10,
        backColor=colors.Color(0.2, 0.1, 0, alpha=0.5),
        borderPadding=5,
        borderWidth=1,
        borderColor=colors.Color(1, 0.5, 0, alpha=0.5)
    ))
    
    # Story (content) list
    story = []
    
    # ============================================================
    # COVER PAGE
    # ============================================================
    story.append(Paragraph("DSTERMINAL", styles['CyberTitle']))
    story.append(Paragraph("SECURITY OPERATIONS CENTER", styles['CyberTitle']))
    story.append(Spacer(1, 30))
    
    story.append(Paragraph(
        '<font size=14 color="#00ff9d">Version 4.0.0.113</font>',
        styles['Normal']
    ))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph(
        f'<font size=10 color="#808080">Document Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC</font>',
        styles['Normal']
    ))
    story.append(Spacer(1, 50))
    
    # ASCII Art
    ascii_art = """
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║     ██████╗ ███████╗████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗ ║
    ║     ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║ ║
    ║     ██║  ██║███████╗   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║ ║
    ║     ██║  ██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║ ║
    ║     ██████╔╝███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║██║ ║
    ║     ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝ ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    story.append(Preformatted(ascii_art, styles['CyberCode']))
    story.append(Spacer(1, 30))
    
    story.append(Paragraph(
        "⚠️ FOR AUTHORIZED SECURITY PERSONNEL ONLY ⚠️",
        styles['Warning']
    ))
    
    story.append(PageBreak())
    
    # ============================================================
    # TABLE OF CONTENTS
    # ============================================================
    story.append(Paragraph("TABLE OF CONTENTS", styles['CyberHeading1']))
    story.append(Spacer(1, 10))
    
    toc_items = [
        ("1. INTRODUCTION TO DSTERMINAL", 1),
        ("2. SYSTEM REQUIREMENTS", 2),
        ("3. INSTALLATION GUIDE", 3),
        ("4. GETTING STARTED", 4),
        ("5. CORE COMMANDS", 5),
        ("6. SECURITY MODULES", 6),
        ("7. NETWORK OPERATIONS", 7),
        ("8. CRYPTOGRAPHY", 8),
        ("9. FORENSICS", 9),
        ("10. SYSTEM HARDENING", 10),
        ("11. INCIDENT RESPONSE", 11),
        ("12. REPORTING", 12),
        ("13. TROUBLESHOOTING", 13),
        ("14. APPENDIX", 14)
    ]
    
    for title, page in toc_items:
        story.append(Paragraph(
            f'<font color="#00ccff">{title}</font><font color="#808080">{"." * (50 - len(title))}{page}</font>',
            styles['Normal']
        ))
    
    story.append(PageBreak())
    
    # ============================================================
    # 1. INTRODUCTION TO DSTERMINAL
    # ============================================================
    story.append(Paragraph("1. INTRODUCTION TO DSTERMINAL", styles['CyberHeading1']))
    
    story.append(Paragraph(
        "DSTerminal is a comprehensive Security Operations Center (SOC) platform designed "
        "for defensive security professionals. It provides a unified terminal interface for "
        "threat detection, incident response, forensics, and system hardening operations.",
        styles['CyberBody']
    ))
    
    story.append(Paragraph("Key Features:", styles['CyberHeading2']))
    
    features = [
        "• Real-time network monitoring with threat detection and geolocation",
        "• AES-256 encryption for file protection and secure key management",
        "• Memory forensics and volatile data analysis",
        "• System hardening and vulnerability assessment",
        "• Steganography detection in images and files",
        "• Integration with VirusTotal API for hash lookups",
        "• Metasploit Framework integration for penetration testing",
        "• Automated PDF report generation for compliance",
        "• SSL/TLS certificate analysis and security auditing",
        "• SQL injection scanning with sqlmap integration"
    ]
    
    for feature in features:
        story.append(Paragraph(feature, styles['CyberBody']))
    
    story.append(Spacer(1, 10))
    
    # Status Table
    status_data = [
        ["COMPONENT", "STATUS", "VERSION"],
        ["DSTerminal Core", "● ONLINE", "4.0.0.113"],
        ["Network Monitor", "● ACTIVE", "4.0.0.113"],
        ["Encryption Module", "● READY", "4.0.0.113"],
        ["Forensics Engine", "● LOADED", "4.0.0.113"],
        ["API Gateway", "● CONNECTED", "4.0.0.113"]
    ]
    
    status_table = Table(status_data, colWidths=[150, 100, 100])
    status_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(0, 1, 0.6)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.1, 0.1, 0.1)),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0, 1, 0.6, alpha=0.3))
    ]))
    story.append(status_table)
    
    story.append(PageBreak())
    
    # ============================================================
    # 2. SYSTEM REQUIREMENTS
    # ============================================================
    story.append(Paragraph("2. SYSTEM REQUIREMENTS", styles['CyberHeading1']))
    
    story.append(Paragraph("Hardware Requirements:", styles['CyberHeading2']))
    
    hardware = [
        ["Component", "Minimum", "Recommended"],
        ["Processor", "Dual-core 2.0 GHz", "Quad-core 3.0 GHz"],
        ["RAM", "4 GB", "16 GB"],
        ["Storage", "500 MB", "10 GB"],
        ["Network", "100 Mbps", "1 Gbps"]
    ]
    
    hardware_table = Table(hardware, colWidths=[120, 150, 150])
    hardware_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(0, 1, 0.6)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.1, 0.1, 0.1)),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0, 1, 0.6, alpha=0.3))
    ]))
    story.append(hardware_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Software Requirements:", styles['CyberHeading2']))
    
    software = [
        ["Operating System", "Version"],
        ["Windows", "10/11 (64-bit)"],
        ["Linux", "Ubuntu 20.04+, Debian 11+, Kali Linux"],
        ["macOS", "12+ (Monterey+)"],
        ["Python", "3.8 or higher"],
        ["Git", "Latest version"],
        ["Nmap", "7.80+ (optional)"],
        ["Metasploit", "6.0+ (optional)"],
        ["sqlmap", "1.6+ (optional)"]
    ]
    
    software_table = Table(software, colWidths=[200, 250])
    software_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(0, 1, 0.6)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.1, 0.1, 0.1)),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0, 1, 0.6, alpha=0.3))
    ]))
    story.append(software_table)
    
    story.append(PageBreak())
    
    # ============================================================
    # 3. INSTALLATION GUIDE
    # ============================================================
    story.append(Paragraph("3. INSTALLATION GUIDE", styles['CyberHeading1']))
    
    story.append(Paragraph("3.1 Windows Installation", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "# DSTerminal Windows Installer\n\n"
        "1. Download DSTerminal_Installer_v4.0.0.113.exe from GitHub\n"
        "2. Run the installer (no administrator rights required)\n"
        "3. Follow the setup wizard to choose installation options\n"
        "4. Select components to install (Core, Documentation, Tools)\n"
        "5. Choose update channel (Stable/Beta/Nightly)\n"
        "6. Launch DSTerminal from Start Menu or Desktop shortcut\n\n"
        "# Installation path\n"
        "C:\\Users\\[USERNAME]\\AppData\\Roaming\\DSTerminal\\\n"
        "C:\\Users\\[USERNAME]\\AppData\\Roaming\\DSTerminal_Workspace\\",
        styles['CyberCode']
    ))
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("3.2 Linux Installation", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "# Clone the DSTerminal repository\n"
        "git clone https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest.git\n"
        "cd DSTerminal_releases_latest\n\n"
        "# Install Python dependencies\n"
        "pip install -r requirements.txt\n\n"
        "# Optional: Install additional tools\n"
        "sudo apt update\n"
        "sudo apt install nmap sqlmap ffmpeg\n\n"
        "# Run DSTerminal\n"
        "python dsterminal.py\n\n"
        "# Create desktop shortcut (optional)\n"
        "chmod +x dsterminal.desktop\n"
        "cp dsterminal.desktop ~/.local/share/applications/",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("3.3 macOS Installation", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "# Install using Homebrew\n"
        "brew install dsterminal\n\n"
        "# Or from source\n"
        "git clone https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest.git\n"
        "cd DSTerminal_releases_latest\n"
        "pip3 install -r requirements.txt\n"
        "python3 dsterminal.py",
        styles['CyberCode']
    ))
    
    story.append(PageBreak())
    
    # ============================================================
    # 4. GETTING STARTED
    # ============================================================
    story.append(Paragraph("4. GETTING STARTED", styles['CyberHeading1']))
    
    story.append(Paragraph("4.1 First Launch", styles['CyberHeading2']))
    
    story.append(Paragraph(
        "When you first launch DSTerminal, you'll see the SOC banner and be assigned "
        "a unique operator ID. All your activities are logged for audit purposes in "
        "the workspace/operators directory.",
        styles['CyberBody']
    ))
    
    story.append(Preformatted(
        "[22:41:49] WILSON-SON [PROD] NORMAL [SOC-5BD39]\n"
        "🔹 OP-189EA9 @ soc-terminal : ~$ help\n\n"
        "╔═══════════════════════════════════════════════════════════════════════════════╗\n"
        "║           DSTERMINAL HELP MENU                    ║\n"
        "╚═══════════════════════════════════════════════════════════════════════════════╝",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("4.2 Workspace Initialization", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "# Navigate to DSTerminal workspace\n"
        "cd ~/DSTerminal_Workspace\n\n"
        "# Create standard directories\n"
        "mkdir operators\n"
        "mkdir scans\n"
        "mkdir reports\n"
        "mkdir exploits\n"
        "mkdir sandbox\n"
        "mkdir quarantine\n\n"
        "# Verify workspace structure\n"
        "ls -la",
        styles['CyberCode']
    ))
    
    story.append(PageBreak())
    
    # ============================================================
    # 5. CORE COMMANDS
    # ============================================================
    story.append(Paragraph("5. CORE COMMANDS", styles['CyberHeading1']))
    
    story.append(Paragraph("5.1 File Operations", styles['CyberHeading2']))
    
    file_commands = [
        ("ls [path]", "List directory contents"),
        ("cd <directory>", "Change working directory"),
        ("pwd", "Print current working directory"),
        ("mkdir <name>", "Create new directory"),
        ("touch <file>", "Create empty file"),
        ("cat <file>", "Display file contents"),
        ("echo <text>", "Display text"),
        ("echo <text> > <file>", "Write text to file"),
        ("echo <text> >> <file>", "Append text to file")
    ]
    
    file_table = Table(file_commands, colWidths=[180, 320])
    file_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0, 1, 0.6)),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0, 1, 0.6, alpha=0.3))
    ]))
    story.append(file_table)
    
    story.append(Paragraph("5.2 System Commands", styles['CyberHeading2']))
    
    system_commands = [
        ("sysinfo", "Display detailed system information"),
        ("killproc <PID>", "Terminate a process by ID"),
        ("update", "Check for DSTerminal updates"),
        ("clear", "Clear the terminal screen"),
        ("exit", "Exit DSTerminal"),
        ("help", "Show comprehensive help menu"),
        ("status", "Display DSTerminal system status")
    ]
    
    system_table = Table(system_commands, colWidths=[180, 320])
    system_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0, 1, 0.6)),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0, 1, 0.6, alpha=0.3))
    ]))
    story.append(system_table)
    
    story.append(PageBreak())
    
    # ============================================================
    # 6. SECURITY MODULES
    # ============================================================
    story.append(Paragraph("6. SECURITY MODULES", styles['CyberHeading1']))
    
    story.append(Paragraph("6.1 System Security Scan", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "system scan -All [--quick] [--deep] [--output <file>]\n\n"
        "Performs comprehensive DSTerminal security scan including:\n"
        "• Memory analysis and process inspection\n"
        "• File integrity verification\n"
        "• Network connection monitoring\n"
        "• Registry analysis (Windows systems)\n"
        "• Scheduled tasks and services review\n"
        "• Malware persistence mechanism detection",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("6.2 Exploit Detection", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "exploitcheck\n\n"
        "Checks for critical vulnerabilities:\n"
        "• CVE-2021-44228 - Log4j Remote Code Execution\n"
        "• CVE-2017-0144 - EternalBlue SMB Exploit\n"
        "• CVE-2021-3156 - Sudo Buffer Overflow\n"
        "• Local privilege escalation vectors\n"
        "• Kernel exploit detection",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("6.3 Integrity Verification", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "check integrity\n\n"
        "Verifies critical system files:\n"
        "• Windows: kernel32.dll, cmd.exe, powershell.exe\n"
        "• Linux: /bin/bash, /usr/bin/sudo, /bin/ls\n"
        "• macOS: /bin/bash, /usr/bin/sudo\n"
        "• Checks file sizes, modification times, and hashes",
        styles['CyberCode']
    ))
    
    story.append(PageBreak())
    
    # ============================================================
    # 7. NETWORK OPERATIONS
    # ============================================================
    story.append(Paragraph("7. NETWORK OPERATIONS", styles['CyberHeading1']))
    
    story.append(Paragraph("7.1 Real-time Network Monitor", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "net -n mon [--duration <sec>] [--export <file>] [--geoip]\n\n"
        "DSTerminal Network Monitoring Features:\n"
        "• Live connection tracking with ESTABLISHED/LISTEN states\n"
        "• Bandwidth usage monitoring (upload/download)\n"
        "• Geolocation of remote IP addresses\n"
        "• Threat scoring system (LOW/MEDIUM/HIGH)\n"
        "• Automated PDF forensic report generation\n"
        "• Intrusion detection alerts for port scans\n"
        "• ISP and country information for connections",
        styles['CyberCode']
    ))
    
    story.append(Spacer(1, 10))
    
    threat_data = [
        ["Threat Score", "Risk Level", "Indicator"],
        ["0-3 points", "LOW", "✓ (Green)"],
        ["4-6 points", "MEDIUM", "⚠ (Yellow)"],
        ["7+ points", "HIGH", "✖ (Red)"]
    ]
    
    threat_table = Table(threat_data, colWidths=[120, 120, 120])
    threat_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(0, 1, 0.6)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (1, 1), (1, 1), colors.Color(0, 1, 0, alpha=0.2)),
        ('BACKGROUND', (1, 2), (1, 2), colors.Color(1, 1, 0, alpha=0.2)),
        ('BACKGROUND', (1, 3), (1, 3), colors.Color(1, 0, 0, alpha=0.2)),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0, 1, 0.6, alpha=0.3))
    ]))
    story.append(threat_table)
    
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("7.2 Port Scanning", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "portsweep <target> [--ports range]\n\n"
        "DSTerminal port scanner scans:\n"
        "• Common ports: 21,22,23,25,53,80,110,135,139,143\n"
        "• Additional ports: 443,445,3389,8080,8443\n"
        "• Custom port ranges (e.g., --ports 1-1024)\n"
        "• Service identification when possible",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("7.3 Traceroute", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "traceroute <target>\n\n"
        "Network path analysis:\n"
        "• Traces route to target destination\n"
        "• Shows intermediate hops\n"
        "• Response time measurements",
        styles['CyberCode']
    ))
    
    story.append(PageBreak())
    
    # ============================================================
    # 8. CRYPTOGRAPHY
    # ============================================================
    story.append(Paragraph("8. CRYPTOGRAPHY", styles['CyberHeading1']))
    
    story.append(Paragraph("8.1 DSTerminal Encryption System", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "# Initialize encryption (first time only)\n"
        "encrypt-setup\n\n"
        "# Encrypt a file\n"
        "encrypt <filename>\n\n"
        "# Decrypt a file\n"
        "decrypt <filename.enc> [key]\n\n"
        "# List encrypted files\n"
        "crypto-list\n\n"
        "# Show encryption information\n"
        "crypto-info <file.enc>\n\n"
        "# Verify encryption system\n"
        "crypto-verify\n\n"
        "# Backup encryption key\n"
        "crypto-backup\n\n"
        "# Test encryption system\n"
        "encrypt-test",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("8.2 Encryption Features", styles['CyberHeading3']))
    
    crypto_features = [
        "• AES-256 encryption using Fernet implementation",
        "• Automatic key generation and secure storage (~/.dsterminal_key)",
        "• Secure file deletion with multiple overwrite passes",
        "• File integrity verification with SHA-256 hashing",
        "• QR code key backup for offline storage",
        "• Encrypted file inventory management",
        "• Key ID tracking for multiple keys"
    ]
    
    for feature in crypto_features:
        story.append(Paragraph(f"  • {feature}", styles['CyberBody']))
    
    story.append(PageBreak())
    
    # ============================================================
    # 9. FORENSICS
    # ============================================================
    story.append(Paragraph("9. FORENSICS", styles['CyberHeading1']))
    
    story.append(Paragraph("9.1 Memory Forensics", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "memdump [--output <file>]\n\n"
        "DSTerminal Memory Forensics captures:\n"
        "• Running processes and their memory maps\n"
        "• Active network connections\n"
        "• Open file handles\n"
        "• Loaded kernel modules\n"
        "• Windows registry hives\n"
        "• Process environment variables",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("9.2 Steganography Detection", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "stegcheck <image_path>\n\n"
        "DSTerminal Steganalysis includes:\n"
        "• Least Significant Bit (LSB) analysis\n"
        "• Entropy calculation and evaluation\n"
        "• Known steganography tool signatures\n"
        "• EXIF metadata examination\n"
        "• File structure anomaly detection",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("9.3 Ransomware Detection", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "ransomwatch\n\n"
        "DSTerminal Ransomware Scanner detects:\n"
        "• Suspicious file extensions (.encrypted, .locked, .crypt)\n"
        "• Mass file encryption patterns\n"
        "• Ransom note creation\n"
        "• Bitcoin wallet address generation\n"
        "• Process behavior anomalies",
        styles['CyberCode']
    ))
    
    story.append(PageBreak())
    
    # ============================================================
    # 10. SYSTEM HARDENING
    # ============================================================
    story.append(Paragraph("10. SYSTEM HARDENING", styles['CyberHeading1']))
    
    story.append(Paragraph("10.1 DSTerminal Hardening", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "harden -t sys [--dry-run]\n\n"
        "DSTerminal Hardening applies:\n"
        "• Windows: Disables SMB1 protocol\n"
        "• Windows: Configures firewall rules\n"
        "• Linux: Enables UFW firewall\n"
        "• Linux: Secures SSH configuration\n"
        "• Disables unnecessary services\n"
        "• Applies CIS benchmark recommendations\n"
        "• Configures system auditing",
        styles['CyberCode']
    ))
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("10.2 MAC Address Spoofing", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "macspoof [interface]\n\n"
        "DSTerminal MAC Changer:\n"
        "• Generates random valid MAC addresses\n"
        "• Auto-detects active network interface\n"
        "• Supports Linux, Windows, and macOS\n"
        "• Verifies MAC change success\n"
        "• Progress animation during spoofing",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("10.3 Log Management", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "clearlogs\n\n"
        "DSTerminal Log Cleaner:\n"
        "• Windows: Application, System, Security event logs\n"
        "• Linux: /var/log/* files\n"
        "• Systemd journal (journalctl)\n"
        "• Shell history files\n"
        "• Application-specific logs",
        styles['CyberCode']
    ))
    
    story.append(PageBreak())
    
    # ============================================================
    # 11. INCIDENT RESPONSE
    # ============================================================
    story.append(Paragraph("11. INCIDENT RESPONSE", styles['CyberHeading1']))
    
    story.append(Paragraph("11.1 Financial Attack Simulator", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "transfertrace\n"
        "extract -money\n\n"
        "DSTerminal Financial Simulator:\n"
        "• SWIFT network transaction simulation\n"
        "• Cryptocurrency exchange monitoring\n"
        "• Payment processor analysis\n"
        "• Money laundering pattern detection\n"
        "• Transaction visualization\n"
        "• Suspicious activity reporting",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("11.2 Emergency Procedures", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "shutdown\n\n"
        "DSTerminal Emergency Shutdown:\n"
        "• Requires explicit confirmation ('YES')\n"
        "• 15-second countdown with visual indicator\n"
        "• Forces system shutdown\n"
        "• Supports Windows and Linux",
        styles['CyberCode']
    ))
    
    story.append(PageBreak())
    
    # ============================================================
    # 12. REPORTING
    # ============================================================
    story.append(Paragraph("12. REPORTING", styles['CyberHeading1']))
    
    report_formats = [
        ["Report Type", "DSTerminal Command", "Output Format"],
        ["System Security Scan", "system scan -All --output report.txt", "TXT"],
        ["Network Analysis", "net -n mon --export report.pdf", "PDF"],
        ["SSL Certificate Audit", "certcheck example.com", "PDF/JSON"],
        ["Encrypted Files Inventory", "crypto-list", "TXT"],
        ["Memory Dump", "memdump --output memory.dmp", "DMP"],
        ["Forensic Report", "network_monitor()", "PDF"],
        ["CVE Scan", "exploitcheck", "TXT"]
    ]
    
    report_table = Table(report_formats, colWidths=[120, 250, 80])
    report_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(0, 1, 0.6)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.1, 0.1, 0.1)),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0, 1, 0.6, alpha=0.3))
    ]))
    story.append(report_table)
    
    story.append(PageBreak())
    
    # ============================================================
    # 13. TROUBLESHOOTING
    # ============================================================
    story.append(Paragraph("13. TROUBLESHOOTING", styles['CyberHeading1']))
    
    issues = [
        ["Issue", "Solution"],
        ["Permission denied", "Run DSTerminal with administrator privileges"],
        ["Module not found", "Run: pip install -r requirements.txt"],
        ["Connection timeout", "Check firewall settings for DSTerminal"],
        ["Encryption failed", "Run 'encrypt-setup' first"],
        ["Update failed", "Check internet connection and GitHub access"],
        ["Workspace error", "Delete ~/.dsterminal_vfs and restart DSTerminal"],
        ["Nmap not found", "Install nmap and ensure it's in PATH"],
        ["Metasploit not found", "Install Metasploit or use WSL on Windows"],
        ["PDF generation failed", "Install reportlab: pip install reportlab"]
    ]
    
    issues_table = Table(issues, colWidths=[150, 350])
    issues_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(0, 1, 0.6)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.1, 0.1, 0.1)),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0, 1, 0.6, alpha=0.3))
    ]))
    story.append(issues_table)
    
    story.append(PageBreak())
    
    # ============================================================
    # 14. APPENDIX
    # ============================================================
    story.append(Paragraph("14. APPENDIX", styles['CyberHeading1']))
    
    story.append(Paragraph("14.1 DSTerminal Directory Structure", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "DSTerminal Installation Directory:\n"
        "├── dsterminal.exe (Main executable)\n"
        "├── config/ (Configuration files)\n"
        "├── docs/ (Documentation)\n"
        "├── tools/ (Helper utilities)\n"
        "├── templates/ (Report templates)\n"
        "├── logs/ (Application logs)\n"
        "└── updates/ (Downloaded updates)\n\n"
        "DSTerminal Workspace:\n"
        "├── operators/ (Session logs)\n"
        "├── scans/ (Scan results)\n"
        "├── reports/ (Generated reports)\n"
        "├── exploits/ (Safe exploit storage)\n"
        "├── sandbox/ (Testing environment)\n"
        "└── quarantine/ (Isolated threats)",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("14.2 API Keys Configuration", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "# VirusTotal API Key (optional)\n"
        "DSTerminal supports VirusTotal integration:\n"
        "1. Get API key from virustotal.com\n"
        "2. Edit CONFIG in dsterminal.py\n"
        "3. Use 'vt-scan' command for hash lookups\n\n"
        "# GitHub Token (for updates)\n"
        "Configure in CONFIG['UPDATE_URL']",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("14.3 Update Channels", styles['CyberHeading2']))
    
    story.append(Preformatted(
        "DSTerminal Update Channels:\n\n"
        "• Stable Channel: Production-ready releases\n"
        "• Beta Channel: Early access to new features\n"
        "• Nightly Channel: Daily development builds\n\n"
        "Select during installation or in config/update_channel.conf",
        styles['CyberCode']
    ))
    
    story.append(Paragraph("14.4 Support and Community", styles['CyberHeading2']))
    
    support_info = [
        ["GitHub Repository", "https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest"],
        ["Documentation", "https://starkexpotechexchange-mw.com/docs"],
        ["Issue Tracker", "https://github.com/Stark-Expo-Tech-Exchange/DSTerminal_releases_latest/issues"],
        ["Email Support", "support@starkexpotechexchange-mw.com"]
    ]
    
    support_table = Table(support_info, colWidths=[150, 350])
    support_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0, 1, 0.6)),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0, 1, 0.6, alpha=0.3))
    ]))
    story.append(support_table)
    
    # Build PDF
    doc.build(story)
    print(f"[✓] DSTerminal User Guide PDF generated successfully: {PDF_PATH}")
    print(f"[✓] File size: {os.path.getsize(PDF_PATH) / 1024:.2f} KB")

# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("DSTerminal User Guide Generator v4.0.0.113")
    print("=" * 60)
    
    try:
        generate_pdf()
        print("\n" + "=" * 60)
        print("✅ DSTerminal Documentation Complete!")
        print("📄 PDF Location: docs/user_guide.pdf")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error generating DSTerminal user guide: {e}")
        import traceback
        traceback.print_exc()