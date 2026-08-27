# -*- coding: utf-8 -*-
"""
Steganography Analyzer Module - Independent Module for DSTerminal
Performs comprehensive steganalysis with full extraction and report generation.
"""

import os
import sys
import re
import time
import math
import zlib
import struct
import shutil
import platform
import tempfile
import subprocess
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Fix Windows console encoding
if platform.system() == "Windows":
    try:
        os.system('chcp 65001 > nul')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
    except:
        pass

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback color codes
    class Fore:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
        WHITE = '\033[97m'; RESET = '\033[0m'; DIM = '\033[2m'
        LIGHTRED_EX = '\033[91m'; LIGHTGREEN_EX = '\033[92m'
        LIGHTYELLOW_EX = '\033[93m'; LIGHTCYAN_EX = '\033[96m'
        LIGHTMAGENTA_EX = '\033[95m'
    
    class Style:
        BRIGHT = '\033[1m'; DIM = '\033[2m'; NORMAL = '\033[22m'
        RESET_ALL = '\033[0m'


class StegAnalyzer:
    """Steganography Analyzer - Independent module for DSTerminal"""
    
    def __init__(self, workspace_root=None):
        if workspace_root is None:
            self.workspace_root = os.path.expanduser("~/dsterminal_workspace")
        else:
            self.workspace_root = workspace_root
        
        self.reports_dir = os.path.join(self.workspace_root, 'reports', 'steg_reports')
        os.makedirs(self.reports_dir, exist_ok=True)
        
        self.EMOJI_SUPPORT = True
        try:
            test_str = "🔍"
            test_str.encode(sys.stdout.encoding)
        except:
            self.EMOJI_SUPPORT = False
    
    def get_emoji(self, emoji, fallback):
        return emoji if self.EMOJI_SUPPORT else fallback
    
    def center_text(self, text, term_width):
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\[[0-9;]*m')
        clean_text = ansi_escape.sub('', text)
        padding = max(0, (term_width - len(clean_text)) // 2)
        return ' ' * padding + text
    
    def print_centered(self, text, color=Fore.WHITE, bold=False, term_width=100):
        if bold:
            text = f"{Style.BRIGHT}{text}{Style.RESET_ALL}"
        print(self.center_text(f"{color}{text}{Style.RESET_ALL}", term_width))
    
    def print_box(self, title, content_lines, border_color=Fore.CYAN, term_width=100):
        box_width = min(60, term_width - 10)
        if box_width < 30:
            box_width = 30
        padding = max(0, (term_width - box_width - 2) // 2)
        
        print(" " * padding + f"{border_color}┌{'─' * box_width}┐{Style.RESET_ALL}")
        
        title_line = f" {title} "
        if len(title_line) > box_width:
            title_line = title_line[:box_width-3] + "..."
        title_padding = (box_width - len(title_line)) // 2
        if title_padding < 0:
            title_padding = 0
        print(" " * padding + f"{border_color}│{Style.RESET_ALL}{' ' * title_padding}{Fore.YELLOW}{Style.BRIGHT}{title_line}{Style.RESET_ALL}{' ' * (box_width - len(title_line) - title_padding)}{border_color}│{Style.RESET_ALL}")
        
        print(" " * padding + f"{border_color}├{'─' * box_width}┤{Style.RESET_ALL}")
        
        for line in content_lines:
            ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\[[0-9;]*m')
            clean_len = len(ansi_escape.sub('', line))
            
            if clean_len > box_width - 2:
                if len(line) > box_width - 5:
                    line = line[:box_width-5] + "..."
            
            padding_needed = max(0, box_width - len(ansi_escape.sub('', line)) - 2)
            
            print(" " * padding + f"{border_color}│{Style.RESET_ALL} {line}{' ' * padding_needed} {border_color}│{Style.RESET_ALL}")
        
        print(" " * padding + f"{border_color}└{'─' * box_width}┘{Style.RESET_ALL}")
    
    def scan_bar(self, label, duration=0.4, width=25, term_width=100):
        sys.stdout.write(f"{Fore.CYAN}    └─{Fore.WHITE} {label}: {Style.RESET_ALL}")
        sys.stdout.flush()
        
        steps = 20
        for i in range(steps):
            progress = i / steps
            if progress < 0.3:
                color = Fore.YELLOW
            elif progress < 0.7:
                color = Fore.CYAN
            else:
                color = Fore.GREEN
            
            sys.stdout.write(f"{color}█{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(duration / steps)
        
        try:
            sys.stdout.write(f" {Fore.GREEN}✅{Style.RESET_ALL}\n")
        except UnicodeEncodeError:
            sys.stdout.write(f" {Fore.GREEN}[OK]{Style.RESET_ALL}\n")
        sys.stdout.flush()
    
    # ============================================================
    # FILE TYPE DETECTION
    # ============================================================
    
    def detect_file_type(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                header = f.read(100)
            
            if header[:8] == b'\x89PNG\r\n\x1a\n':
                return {'type': 'PNG Image', 'extension': '.png', 'mime': 'image/png', 'category': 'image'}
            elif header[:2] == b'\xff\xd8':
                return {'type': 'JPEG Image', 'extension': '.jpg', 'mime': 'image/jpeg', 'category': 'image'}
            elif header[:6] in (b'GIF89a', b'GIF87a'):
                return {'type': 'GIF Image', 'extension': '.gif', 'mime': 'image/gif', 'category': 'image'}
            elif header[:2] == b'BM':
                return {'type': 'BMP Image', 'extension': '.bmp', 'mime': 'image/bmp', 'category': 'image'}
            elif header[:4] == b'RIFF' and header[8:12] == b'WEBP':
                return {'type': 'WebP Image', 'extension': '.webp', 'mime': 'image/webp', 'category': 'image'}
            elif header[:4] == b'%PDF':
                return {'type': 'PDF Document', 'extension': '.pdf', 'mime': 'application/pdf', 'category': 'document'}
            elif header[:4] == b'PK\x03\x04':
                return {'type': 'ZIP Archive', 'extension': '.zip', 'mime': 'application/zip', 'category': 'archive'}
            elif header[:4] == b'Rar!':
                return {'type': 'RAR Archive', 'extension': '.rar', 'mime': 'application/x-rar-compressed', 'category': 'archive'}
            elif header[:6] == b'7z\xbc\xaf\x27\x1c':
                return {'type': '7-Zip Archive', 'extension': '.7z', 'mime': 'application/x-7z-compressed', 'category': 'archive'}
            elif header[:2] == b'MZ':
                return {'type': 'Windows Executable', 'extension': '.exe', 'mime': 'application/x-msdownload', 'category': 'executable'}
            elif header[:4] == b'\x7fELF':
                return {'type': 'Linux Executable', 'extension': '', 'mime': 'application/x-elf', 'category': 'executable'}
            elif all(b < 128 and b != 0 for b in header[:100]):
                return {'type': 'Text File', 'extension': '.txt', 'mime': 'text/plain', 'category': 'text'}
            else:
                return {'type': 'Unknown', 'extension': '', 'mime': 'application/octet-stream', 'category': 'unknown'}
        except:
            return {'type': 'Unknown', 'extension': '', 'mime': 'application/octet-stream', 'category': 'unknown'}
    
    def detect_file_type_from_data(self, data):
        if data[:4] == b'PK\x03\x04':
            return 'ZIP Archive'
        if data[:4] == b'Rar!':
            return 'RAR Archive'
        if data[:6] == b'7z\xbc\xaf\x27\x1c':
            return '7-Zip Archive'
        if data[:2] == b'MZ':
            return 'EXE/DLL File'
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return 'PNG Image'
        if data[:2] == b'\xff\xd8':
            return 'JPEG Image'
        if data[:4] == b'%PDF':
            return 'PDF Document'
        return 'Unknown'
    
    # ============================================================
    # REAL DATA EXTRACTION FUNCTIONS
    # ============================================================
    
    def extract_text_from_png(self, data):
        """Extract actual readable text from PNG data"""
        results = {'text': [], 'metadata': [], 'strings': []}
        
        # Try to extract text from PNG chunks
        pos = 8
        while pos < len(data) - 12:
            chunk_len = struct.unpack('>I', data[pos:pos+4])[0]
            chunk_type = data[pos+4:pos+8]
            chunk_data = data[pos+8:pos+8+chunk_len]
            
            if chunk_type == b'tEXt':
                try:
                    text = chunk_data.decode('latin-1', errors='ignore')
                    # Filter out binary noise, keep readable text
                    clean = re.sub(r'[^\x20-\x7E\n\r]', '', text)
                    if len(clean) > 3:
                        results['text'].append(clean)
                except:
                    pass
            elif chunk_type == b'zTXt':
                try:
                    idx = chunk_data.find(b'\x00')
                    if idx > 0:
                        keyword = chunk_data[:idx].decode('latin-1', errors='ignore')
                        compressed = chunk_data[idx+2:]
                        decompressed = zlib.decompress(compressed)
                        text = decompressed.decode('latin-1', errors='ignore')
                        clean = re.sub(r'[^\x20-\x7E\n\r]', '', text)
                        if len(clean) > 3:
                            results['text'].append(f"{keyword}: {clean}")
                except:
                    pass
            elif chunk_type == b'iTXt':
                try:
                    parts = chunk_data.split(b'\x00')
                    if len(parts) >= 4:
                        keyword = parts[0].decode('latin-1', errors='ignore')
                        text = parts[3].decode('utf-8', errors='ignore')
                        clean = re.sub(r'[^\x20-\x7E\n\r]', '', text)
                        if len(clean) > 3:
                            results['text'].append(f"{keyword}: {clean}")
                except:
                    pass
            
            pos += 4 + 4 + chunk_len + 4
        
        # Extract readable strings from entire file
        pattern = re.compile(b'[\\x20-\\x7E]{4,}')
        matches = pattern.findall(data)
        for m in matches:
            try:
                s = m.decode('ascii', errors='ignore')
                # Filter out common PNG headers
                if len(s) > 3 and not s.startswith(('IHDR', 'IDAT', 'IEND', 'sRGB', 'gAMA', 'PLTE')):
                    results['strings'].append(s)
            except:
                pass
        
        return results
    
    def extract_text_from_pdf(self, file_path):
        """Extract actual readable text from PDF"""
        results = {'text': [], 'metadata': {}}
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Extract text between parentheses
            text_matches = re.findall(rb'\(([^)]*)\)', data)
            for match in text_matches:
                try:
                    text = match.decode('latin-1', errors='ignore')
                    # Clean up and keep readable text
                    clean = re.sub(r'[^\x20-\x7E\n\r]', '', text)
                    if len(clean) > 3 and any(c.isalnum() for c in clean):
                        results['text'].append(clean)
                except:
                    pass
            
            # Extract metadata
            meta_patterns = {
                'Title': rb'/Title\s*\(([^)]*)\)',
                'Author': rb'/Author\s*\(([^)]*)\)',
                'Subject': rb'/Subject\s*\(([^)]*)\)',
                'Keywords': rb'/Keywords\s*\(([^)]*)\)',
                'Creator': rb'/Creator\s*\(([^)]*)\)',
                'Producer': rb'/Producer\s*\(([^)]*)\)',
            }
            
            for key, pattern in meta_patterns.items():
                match = re.search(pattern, data)
                if match:
                    try:
                        text = match.group(1).decode('latin-1', errors='ignore')
                        clean = re.sub(r'[^\x20-\x7E]', '', text)
                        if clean:
                            results['metadata'][key] = clean
                    except:
                        pass
        except:
            pass
        
        return results
    
    def extract_text_from_image(self, file_path):
        """Extract text from image using OCR or embedded text"""
        results = {'text': [], 'metadata': []}
        
        # Try to extract EXIF data
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            img = Image.open(file_path)
            exifdata = img.getexif()
            
            for tag_id, value in exifdata.items():
                tag = TAGS.get(tag_id, tag_id)
                if isinstance(value, str) and len(value) > 3:
                    results['metadata'].append(f"{tag}: {value}")
        except ImportError:
            pass
        except:
            pass
        
        return results
    
    def extract_all_data(self, file_path, file_type):
        """Extract all meaningful data from file"""
        results = {'text': [], 'strings': [], 'metadata': [], 'appended_data': None}
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Check for appended data
            if file_type == 'PNG Image':
                iend_pos = data.rfind(b'IEND')
                if iend_pos > 0 and iend_pos + 8 < len(data):
                    appended = data[iend_pos + 8:]
                    if len(appended) > 100:
                        # Try to decode appended data
                        try:
                            text = appended.decode('latin-1', errors='ignore')
                            clean = re.sub(r'[^\x20-\x7E\n\r]', '', text)
                            if len(clean) > 10:
                                results['appended_data'] = {
                                    'size': len(appended),
                                    'text': clean[:500]
                                }
                        except:
                            results['appended_data'] = {
                                'size': len(appended),
                                'text': '[Binary data - cannot display]'
                            }
            
            # Extract text based on file type
            if file_type == 'PNG Image':
                png_text = self.extract_text_from_png(data)
                results['text'].extend(png_text.get('text', []))
                results['strings'].extend(png_text.get('strings', []))
                
                # Also try image metadata
                img_text = self.extract_text_from_image(file_path)
                results['metadata'].extend(img_text.get('metadata', []))
                
            elif file_type == 'PDF Document':
                pdf_text = self.extract_text_from_pdf(file_path)
                results['text'].extend(pdf_text.get('text', []))
                for key, value in pdf_text.get('metadata', {}).items():
                    results['metadata'].append(f"{key}: {value}")
            
            else:
                # Generic text extraction
                pattern = re.compile(b'[\\x20-\\x7E]{4,}')
                matches = pattern.findall(data)
                for m in matches[:100]:
                    try:
                        s = m.decode('ascii', errors='ignore')
                        if len(s) > 3:
                            results['strings'].append(s)
                    except:
                        pass
            
            # Deduplicate and clean
            results['text'] = list(dict.fromkeys(results['text']))
            results['strings'] = list(dict.fromkeys(results['strings']))
            results['metadata'] = list(dict.fromkeys(results['metadata']))
            
        except Exception as e:
            pass
        
        return results
    
    # ============================================================
    # DISPLAY FUNCTIONS WITH NICE BOXES
    # ============================================================
    
    def display_analysis_results(self, results, extracted_data, term_width=100):
        """Display analysis results in a well-designed box"""
        print()
        
        # Determine status
        if results and results.get('analysis', {}).get('has_anomalies'):
            status = "⚠️ ANOMALIES DETECTED"
            status_color = Fore.RED
            border_color = Fore.RED
        else:
            status = "✅ ANALYSIS COMPLETE"
            status_color = Fore.GREEN
            border_color = Fore.GREEN
        
        # Build content lines
        content_lines = []
        content_lines.append(f"{status_color}{status}{Style.RESET_ALL}")
        content_lines.append("")
        
        if results:
            content_lines.append(f"  {Fore.CYAN}Report ID:{Style.RESET_ALL} {results.get('report_id', 'N/A')}")
            content_lines.append(f"  {Fore.CYAN}File:{Style.RESET_ALL} {results.get('file', {}).get('name', 'N/A')}")
            content_lines.append(f"  {Fore.CYAN}File Type:{Style.RESET_ALL} {results.get('file', {}).get('type', 'N/A')}")
            content_lines.append(f"  {Fore.CYAN}Entropy Score:{Style.RESET_ALL} {results.get('analysis', {}).get('entropy', 0.0):.2f}/8.0")
            
            anomalies = results.get('analysis', {}).get('anomalies', [])
            if anomalies:
                content_lines.append(f"  {Fore.CYAN}Anomalies:{Style.RESET_ALL} {len(anomalies)} found")
                for a in anomalies[:3]:
                    content_lines.append(f"    {Fore.YELLOW}▸{Style.RESET_ALL} {a}")
                if len(anomalies) > 3:
                    content_lines.append(f"    {Fore.YELLOW}▸{Style.RESET_ALL} ... and {len(anomalies) - 3} more")
            else:
                content_lines.append(f"  {Fore.CYAN}Anomalies:{Style.RESET_ALL} {Fore.GREEN}None detected{Style.RESET_ALL}")
        
        content_lines.append("")
        
        # Extracted text data
        if extracted_data:
            text_data = extracted_data.get('text', [])
            strings = extracted_data.get('strings', [])
            metadata = extracted_data.get('metadata', [])
            appended = extracted_data.get('appended_data')
            
            if text_data:
                content_lines.append(f"  {Fore.CYAN}📝 Embedded Text Found:{Style.RESET_ALL} {len(text_data)} items")
                for t in text_data[:3]:
                    content_lines.append(f"    {Fore.WHITE}• {t[:100]}{Style.RESET_ALL}")
                if len(text_data) > 3:
                    content_lines.append(f"    {Fore.DIM}... and {len(text_data) - 3} more{Style.RESET_ALL}")
                content_lines.append("")
            
            if strings:
                content_lines.append(f"  {Fore.CYAN}📊 Readable Strings:{Style.RESET_ALL} {len(strings)} found")
                for s in strings[:3]:
                    content_lines.append(f"    {Fore.WHITE}• {s[:100]}{Style.RESET_ALL}")
                if len(strings) > 3:
                    content_lines.append(f"    {Fore.DIM}... and {len(strings) - 3} more{Style.RESET_ALL}")
                content_lines.append("")
            
            if metadata:
                content_lines.append(f"  {Fore.CYAN}📋 Metadata:{Style.RESET_ALL} {len(metadata)} items")
                for m in metadata[:3]:
                    content_lines.append(f"    {Fore.WHITE}• {m[:100]}{Style.RESET_ALL}")
                if len(metadata) > 3:
                    content_lines.append(f"    {Fore.DIM}... and {len(metadata) - 3} more{Style.RESET_ALL}")
                content_lines.append("")
            
            if appended:
                content_lines.append(f"  {Fore.CYAN}📦 Appended Data:{Style.RESET_ALL} {appended.get('size', 0)} bytes")
                if appended.get('text'):
                    content_lines.append(f"    {Fore.WHITE}• {appended['text'][:200]}{Style.RESET_ALL}")
                content_lines.append("")
        
        self.print_box("📊 ANALYSIS RESULTS", content_lines, border_color, term_width)
    
    def display_report_generation(self, html_path, pdf_path, term_width=100):
        """Display report generation status in a nice box"""
        content_lines = []
        content_lines.append(f"{Fore.GREEN}✅ Reports Generated Successfully{Style.RESET_ALL}")
        content_lines.append("")
        
        if html_path:
            content_lines.append(f"  {Fore.CYAN}📄 HTML Report:{Style.RESET_ALL}")
            content_lines.append(f"    {Fore.WHITE}{html_path}{Style.RESET_ALL}")
        
        if pdf_path:
            content_lines.append(f"  {Fore.CYAN}📄 PDF Report:{Style.RESET_ALL}")
            content_lines.append(f"    {Fore.WHITE}{pdf_path}{Style.RESET_ALL}")
        else:
            content_lines.append(f"  {Fore.YELLOW}⚠️ PDF Report: Skipped (ReportLab not installed){Style.RESET_ALL}")
        
        self.print_box("📄 REPORT GENERATION", content_lines, Fore.CYAN, term_width)
    
    # ============================================================
    # MAIN ANALYSIS METHOD
    # ============================================================
    
    def analyze(self, file_path, verbose=False):
        """Perform comprehensive steganalysis on a file"""
        try:
            term_width = shutil.get_terminal_size().columns
            if term_width < 80:
                term_width = 80
            if term_width > 200:
                term_width = 200
        except:
            term_width = 100
        
        if not file_path:
            self.print_centered("❌ No file path provided", Fore.RED, bold=True, term_width=term_width)
            return None
        
        if not os.path.exists(file_path):
            self.print_centered(f"❌ File not found: {file_path}", Fore.RED, bold=True, term_width=term_width)
            return None

        try:
            # Detect File Type
            file_info = self.detect_file_type(file_path)
            file_name = os.path.basename(file_path)
            
            # Safe emojis
            search_emoji = self.get_emoji("🔍", "[SEARCH]")
            folder_emoji = self.get_emoji("📁", "[FOLDER]")
            loading_emoji = self.get_emoji("📂", "[LOADING]")
            chart_emoji = self.get_emoji("📊", "[CHART]")
            microscope_emoji = self.get_emoji("🔬", "[MICROSCOPE]")
            checkmark = self.get_emoji("✅", "[OK]")
            warning = self.get_emoji("⚠️", "[!]")
            file_type_emoji = "🖼️" if file_info['category'] == 'image' else "📄" if file_info['category'] == 'document' else "📦" if file_info['category'] == 'archive' else "📁"
            
            # Print Header
            content_lines = [
                f"{file_type_emoji} {file_name}",
                f"📋 Type: {file_info['type']}",
                f"📏 Size: {os.path.getsize(file_path) / 1024:.2f} KB"
            ]
            self.print_box("🔍 STEGANOGRAPHY ANALYSIS", content_lines, Fore.CYAN, term_width)
            print()
            
            # Loading animation
            self.print_centered(f"{loading_emoji} Loading file...", Fore.CYAN, term_width=term_width)
            time.sleep(0.2)

            with open(file_path, "rb") as f:
                content = f.read()

            self.print_centered(f"{microscope_emoji} Analyzing...", Fore.CYAN, term_width=term_width)
            time.sleep(0.1)
            print()

            # Animated scan stages
            scan_stages = [
                ("Structure", folder_emoji),
                ("Signatures", search_emoji),
                ("Entropy", chart_emoji),
                ("Extraction", microscope_emoji)
            ]
            
            for stage, icon in scan_stages:
                self.scan_bar(f"{icon} {stage}", duration=0.3, width=25, term_width=term_width)
                time.sleep(0.05)

            anomalies = []
            extracted_data = {}

            # Known steganography signatures
            steg_signatures = {
                b"STEGO": "Generic steganography marker",
                b"Steghide": "Steghide tool reference",
                b"outguess": "OutGuess tool reference",
                b"JPHIDE": "JP Hide and Seek",
                b"JPSEEK": "JP Seek"
            }

            content_lower = content.lower()
            for sig, desc in steg_signatures.items():
                if sig.lower() in content_lower:
                    anomalies.append(f"Possible {desc}")

            # Entropy check
            entropy = 0.0
            if len(content) > 0:
                byte_counts = Counter(content)
                for count in byte_counts.values():
                    p = count / len(content)
                    if p > 0:
                        entropy -= p * math.log2(p)
                entropy = round(entropy, 2)

                if entropy > 7.5:
                    anomalies.append(f"High entropy ({entropy:.2f}) - possible embedded data")
                elif entropy > 6.5:
                    anomalies.append(f"Elevated entropy ({entropy:.2f}) - potential hidden content")

            # Extract real data
            extracted_data = self.extract_all_data(file_path, file_info['type'])

            time.sleep(0.1)

            # Result output
            has_true_positive = False
            
            if anomalies:
                has_high_entropy = any('High entropy' in a for a in anomalies)
                has_signature = any('Possible' in a for a in anomalies)
                has_appended = any('Appended data' in a for a in anomalies)
                
                if has_high_entropy or has_appended:
                    confidence = "HIGH"
                    has_true_positive = True
                elif has_signature:
                    confidence = "MEDIUM"
                    has_true_positive = True
                else:
                    confidence = "LOW"
                    has_true_positive = False
                
                content_lines = [
                    f"{Fore.RED}{Style.BRIGHT}{warning} WARNING: Anomalies detected{Style.RESET_ALL}",
                    ""
                ]
                for a in anomalies[:5]:
                    content_lines.append(f"  {Fore.YELLOW}▸{Style.RESET_ALL} {a}")
                if len(anomalies) > 5:
                    content_lines.append(f"  {Fore.YELLOW}▸{Style.RESET_ALL} ... and {len(anomalies) - 5} more")
                
                content_lines.append("")
                content_lines.append(f"  {Fore.CYAN}Confidence:{Style.RESET_ALL} {Fore.YELLOW}{confidence}{Style.RESET_ALL}")
                
                self.print_box(f"{warning} STEGANOGRAPHY ALERT", content_lines, Fore.RED, term_width)
            else:
                content_lines = [
                    f"{Fore.GREEN}{Style.BRIGHT}{checkmark} No anomalies detected{Style.RESET_ALL}",
                    "",
                    f"  {Fore.CYAN}Entropy Score:{Style.RESET_ALL} {Fore.GREEN}{entropy:.2f}{Style.RESET_ALL}",
                    f"  {Fore.CYAN}File Type:{Style.RESET_ALL} {Fore.WHITE}{file_info['type']}{Style.RESET_ALL}",
                    f"  {Fore.CYAN}Status:{Style.RESET_ALL} {Fore.GREEN}{checkmark} File appears normal{Style.RESET_ALL}"
                ]
                self.print_box(f"{checkmark} ANALYSIS COMPLETE", content_lines, Fore.GREEN, term_width)

            time.sleep(0.2)

            # Generate reports
            print()
            self.print_centered("📄 Generating reports...", Fore.CYAN, term_width=term_width)
            
            report_data = {
                'report_id': f"STEG-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'file': {
                    'path': file_path,
                    'name': file_name,
                    'size': os.path.getsize(file_path),
                    'type': file_info['type'],
                    'category': file_info['category']
                },
                'analysis': {
                    'entropy': entropy,
                    'anomalies': anomalies,
                    'has_anomalies': len(anomalies) > 0
                },
                'extracted_data': extracted_data
            }
            
            # Generate HTML report
            html_path = self.generate_html_report(report_data)
            pdf_path = self.generate_pdf_report(report_data)
            
            # Display report generation status
            self.display_report_generation(html_path, pdf_path, term_width)
            
            # Display analysis results with extracted data
            self.display_analysis_results(report_data, extracted_data, term_width)
            
            # Extraction prompt if anomalies found
            if has_true_positive and (extracted_data.get('text') or extracted_data.get('strings') or extracted_data.get('appended_data')):
                print()
                content_lines = [
                    f"{Fore.YELLOW}🔍 Hidden data was detected and extracted{Style.RESET_ALL}",
                    "",
                    f"  {Fore.CYAN}Text chunks:{Style.RESET_ALL} {len(extracted_data.get('text', []))}",
                    f"  {Fore.CYAN}Readable strings:{Style.RESET_ALL} {len(extracted_data.get('strings', []))}",
                    f"  {Fore.CYAN}Metadata items:{Style.RESET_ALL} {len(extracted_data.get('metadata', []))}"
                ]
                if extracted_data.get('appended_data'):
                    content_lines.append(f"  {Fore.CYAN}Appended data:{Style.RESET_ALL} {extracted_data['appended_data']['size']} bytes")
                
                self.print_box("🔓 EXTRACTED DATA SUMMARY", content_lines, Fore.CYAN, term_width)
            
            return report_data

        except KeyboardInterrupt:
            self.print_centered("⚠️ Operation cancelled", Fore.YELLOW, term_width=term_width)
            return None
        except Exception as e:
            self.print_centered(f"❌ Error: {str(e)}", Fore.RED, bold=True, term_width=term_width)
            if verbose:
                import traceback
                traceback.print_exc()
            return None

    # ============================================================
    # REPORT GENERATION
    # ============================================================
    
    def generate_html_report(self, report_data):
        """Generate HTML report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        filename = f"steg_report_{report_data['report_id']}.html"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Build extracted data section
        extracted_html = ""
        extracted = report_data.get('extracted_data', {})
        
        if extracted.get('text'):
            extracted_html += '<h3>📝 Embedded Text</h3><div class="extracted-data">'
            for t in extracted['text'][:10]:
                extracted_html += f'<div class="text-item">• {t}</div>'
            if len(extracted['text']) > 10:
                extracted_html += f'<div class="text-item">... and {len(extracted["text"]) - 10} more</div>'
            extracted_html += '</div>'
        
        if extracted.get('strings'):
            extracted_html += '<h3>📊 Readable Strings</h3><div class="extracted-data">'
            for s in extracted['strings'][:10]:
                extracted_html += f'<div class="text-item">• {s}</div>'
            if len(extracted['strings']) > 10:
                extracted_html += f'<div class="text-item">... and {len(extracted["strings"]) - 10} more</div>'
            extracted_html += '</div>'
        
        if extracted.get('metadata'):
            extracted_html += '<h3>📋 Metadata</h3><div class="extracted-data">'
            for m in extracted['metadata'][:10]:
                extracted_html += f'<div class="text-item">• {m}</div>'
            if len(extracted['metadata']) > 10:
                extracted_html += f'<div class="text-item">... and {len(extracted["metadata"]) - 10} more</div>'
            extracted_html += '</div>'
        
        if extracted.get('appended_data'):
            extracted_html += f'''
        <h3>📦 Appended Data</h3>
        <div class="extracted-data">
        Size: {extracted['appended_data']['size']} bytes
        {f'<div class="text-item">Preview: {extracted["appended_data"]["text"][:500]}</div>' if extracted['appended_data'].get('text') else ''}
        </div>'''
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSTerminal Steganography Report - {report_data['report_id']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Courier New', monospace; background: #0a0a0f; color: #00ffaa; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: #111118; border: 1px solid #00ffaa33; border-radius: 10px; padding: 30px; }}
        h1, h2, h3 {{ color: #00ffaa; border-bottom: 1px solid #00ffaa33; padding-bottom: 10px; margin-top: 20px; }}
        .header {{ text-align: center; padding: 20px 0; border-bottom: 2px solid #00ffaa; margin-bottom: 30px; }}
        .header h1 {{ font-size: 28px; color: #00ffaa; text-shadow: 0 0 20px #00ffaa33; border: none; }}
        .header .subtitle {{ color: #8888aa; font-size: 14px; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 15px 0; }}
        .info-card {{ background: #1a1a2e; padding: 15px; border-radius: 8px; border-left: 3px solid #00ffaa; }}
        .info-card .label {{ color: #8888aa; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
        .info-card .value {{ font-size: 18px; color: #00ffaa; margin-top: 5px; word-break: break-all; }}
        .anomaly-list {{ list-style: none; padding: 0; }}
        .anomaly-list li {{ padding: 8px 15px; margin: 5px 0; background: #1a1a2e; border-radius: 5px; border-left: 3px solid #ff0044; }}
        .extracted-data {{ background: #0d0d1a; padding: 15px; border-radius: 8px; margin: 10px 0; max-height: 400px; overflow-y: auto; font-size: 13px; white-space: pre-wrap; word-break: break-all; }}
        .extracted-data .text-item {{ color: #cccccc; padding: 2px 0; border-bottom: 1px solid #00ffaa11; }}
        .extracted-data .chunk-type {{ color: #ffaa44; font-weight: bold; }}
        .recommendations {{ background: #0d0d1a; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 3px solid #00ffaa; }}
        .recommendations .rec-item {{ padding: 5px 0; color: #cccccc; }}
        .recommendations .rec-item .icon {{ margin-right: 10px; }}
        .recommendations .rec-item.high {{ border-left: 3px solid #ff0044; padding-left: 12px; }}
        .recommendations .rec-item.medium {{ border-left: 3px solid #ffaa00; padding-left: 12px; }}
        .recommendations .rec-item.low {{ border-left: 3px solid #44ff88; padding-left: 12px; }}
        .footer {{ text-align: center; padding: 20px 0; margin-top: 30px; border-top: 1px solid #00ffaa33; color: #666688; font-size: 12px; }}
        .severity-high {{ color: #ff0044; }}
        .severity-medium {{ color: #ffaa00; }}
        .severity-low {{ color: #44ff88; }}
        @media (max-width: 600px) {{ .info-grid {{ grid-template-columns: 1fr; }} .container {{ padding: 15px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 DSTerminal Steganography Report</h1>
            <div class="subtitle">Report ID: {report_data['report_id']} | Generated: {timestamp}</div>
        </div>
        
        <h2>📋 File Information</h2>
        <div class="info-grid">
            <div class="info-card"><div class="label">File Name</div><div class="value">{report_data['file']['name']}</div></div>
            <div class="info-card"><div class="label">File Type</div><div class="value">{report_data['file']['type']}</div></div>
            <div class="info-card"><div class="label">File Size</div><div class="value">{report_data['file']['size']} bytes</div></div>
            <div class="info-card"><div class="label">Category</div><div class="value">{report_data['file']['category']}</div></div>
            <div class="info-card"><div class="label">Entropy Score</div><div class="value">{report_data['analysis']['entropy']:.2f}/8.0</div></div>
            <div class="info-card"><div class="label">Anomalies Found</div><div class="value">{'✅' if report_data['analysis']['has_anomalies'] else '❌'}</div></div>
        </div>
        
        <h2>⚠️ Anomalies Detected</h2>'''
        
        if report_data['analysis']['anomalies']:
            html_content += '<ul class="anomaly-list">'
            for a in report_data['analysis']['anomalies']:
                html_content += f'<li>🔴 {a}</li>'
            html_content += '</ul>'
        else:
            html_content += '<p style="color: #44ff88;">✅ No anomalies detected - File appears clean</p>'
        
        html_content += '<h2>📤 Extracted Data</h2>'
        html_content += extracted_html
        
        # Recommendations section
        html_content += '<h2>💡 Recommendations</h2><div class="recommendations">'
        recommendations = self._generate_recommendations(report_data)
        if recommendations:
            for rec in recommendations:
                severity = rec.get('severity', 'low').lower()
                icon = rec.get('icon', '•')
                html_content += f'''
        <div class="rec-item {severity}">
            <span class="icon">{icon}</span>
            <span class="severity-{severity}">[{severity.upper()}]</span>
            {rec['text']}
        </div>'''
        else:
            html_content += '<p style="color: #44ff88;">✅ No recommendations - File appears clean and secure.</p>'
        html_content += '</div>'
        
        html_content += f'''
        <div class="footer">
            <p>Generated by DSTerminal v4.0.0.113 | Report ID: {report_data['report_id']}</p>
            <p>🔒 This report is confidential and intended for authorized personnel only.</p>
        </div>
    </div>
</body>
</html>'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_pdf_report(self, report_data):
        """Generate PDF report with extracted data - FIXED"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            filename = f"steg_report_{report_data['report_id']}.pdf"
            filepath = os.path.join(self.reports_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4, 
                                rightMargin=50, leftMargin=50, 
                                topMargin=50, bottomMargin=50)
            
            styles = getSampleStyleSheet()
            
            recommendations = self._generate_recommendations(report_data)
            
            # Style definitions
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1a237e'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            )
            
            subheading_style = ParagraphStyle(
                'SubHeading',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.HexColor('#283593'),
                spaceAfter=8,
                spaceBefore=10,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                spaceAfter=4,
                fontName='Helvetica'
            )
            
            rec_high_style = ParagraphStyle(
                'RecHigh',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#cc0000'),
                spaceAfter=4,
                fontName='Helvetica-Bold'
            )
            
            rec_medium_style = ParagraphStyle(
                'RecMedium',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#cc8800'),
                spaceAfter=4,
                fontName='Helvetica'
            )
            
            rec_low_style = ParagraphStyle(
                'RecLow',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#006600'),
                spaceAfter=4,
                fontName='Helvetica'
            )
            
            story = []
            
            # Title
            story.append(Paragraph("DSTerminal Steganography Report", title_style))
            story.append(Paragraph(f"Report ID: {report_data['report_id']}", normal_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            story.append(Spacer(1, 0.3*inch))
            
            # File Information Table
            story.append(Paragraph("File Information", heading_style))
            file_data = [
                ["File Name", report_data['file']['name']],
                ["File Type", report_data['file']['type']],
                ["File Size", f"{report_data['file']['size']} bytes"],
                ["Category", report_data['file']['category']],
                ["Entropy Score", f"{report_data['analysis']['entropy']:.2f}/8.0"],
                ["Anomalies Found", "Yes" if report_data['analysis']['has_anomalies'] else "No"]
            ]
            
            file_table = Table(file_data, colWidths=[2*inch, 4*inch])
            file_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (1, 1), colors.HexColor('#f5f5f5')),
                ('BACKGROUND', (0, 2), (1, 2), colors.white),
                ('BACKGROUND', (0, 3), (1, 3), colors.HexColor('#f5f5f5')),
                ('BACKGROUND', (0, 4), (1, 4), colors.white),
                ('BACKGROUND', (0, 5), (1, 5), colors.HexColor('#f5f5f5')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ]))
            story.append(file_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Anomalies
            story.append(Paragraph("Anomalies Detected", heading_style))
            if report_data['analysis']['anomalies']:
                for a in report_data['analysis']['anomalies']:
                    story.append(Paragraph(f"• {a}", normal_style))
            else:
                story.append(Paragraph("✅ No anomalies detected - File appears clean", normal_style))
            
            story.append(Spacer(1, 0.2*inch))
            
            # Extracted Data - REAL DATA
            extracted = report_data.get('extracted_data', {})
            if extracted:
                story.append(Paragraph("Extracted Data", heading_style))
                
                if extracted.get('text'):
                    story.append(Paragraph("Embedded Text:", subheading_style))
                    for t in extracted['text'][:10]:
                        # Escape special characters for ReportLab
                        safe_text = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(f"• {safe_text[:200]}", normal_style))
                    if len(extracted['text']) > 10:
                        story.append(Paragraph(f"... and {len(extracted['text']) - 10} more entries", normal_style))
                    story.append(Spacer(1, 0.1*inch))
                
                if extracted.get('strings'):
                    story.append(Paragraph("Readable Strings:", subheading_style))
                    for s in extracted['strings'][:10]:
                        safe_text = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(f"• {safe_text[:200]}", normal_style))
                    if len(extracted['strings']) > 10:
                        story.append(Paragraph(f"... and {len(extracted['strings']) - 10} more strings", normal_style))
                    story.append(Spacer(1, 0.1*inch))
                
                if extracted.get('metadata'):
                    story.append(Paragraph("Metadata:", subheading_style))
                    for m in extracted['metadata'][:10]:
                        safe_text = m.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(f"• {safe_text[:200]}", normal_style))
                    if len(extracted['metadata']) > 10:
                        story.append(Paragraph(f"... and {len(extracted['metadata']) - 10} more items", normal_style))
                    story.append(Spacer(1, 0.1*inch))
                
                if extracted.get('appended_data'):
                    story.append(Paragraph("Appended Data:", subheading_style))
                    story.append(Paragraph(f"Size: {extracted['appended_data']['size']} bytes", normal_style))
                    if extracted['appended_data'].get('text'):
                        safe_text = extracted['appended_data']['text'][:200].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(f"Preview: {safe_text}", normal_style))
            
            # Recommendations section
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Recommendations", heading_style))
            
            if recommendations:
                for rec in recommendations:
                    severity = rec.get('severity', 'low').upper()
                    icon = rec.get('icon', '•')
                    text = f"{icon} [{severity}] {rec['text']}"
                    # Escape special characters
                    safe_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    
                    if severity == 'HIGH':
                        story.append(Paragraph(safe_text, rec_high_style))
                    elif severity == 'MEDIUM':
                        story.append(Paragraph(safe_text, rec_medium_style))
                    else:
                        story.append(Paragraph(safe_text, rec_low_style))
            else:
                story.append(Paragraph("✅ No recommendations - File appears clean and secure.", normal_style))
            
            # Footer
            story.append(Spacer(1, 0.5*inch))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER
            )
            story.append(Paragraph(
                "Generated by DSTerminal v4.0.0.113 | Report ID: " + report_data['report_id'],
                footer_style
            ))
            story.append(Paragraph(
                "This report is confidential and intended for authorized personnel only.",
                footer_style
            ))
            
            doc.build(story)
            return filepath
            
        except ImportError:
            return None
        except Exception as e:
            print(f"⚠️ PDF generation error: {str(e)}")
            return None
    # ============================================================
    # RECOMMENDATIONS GENERATOR
    # ============================================================
    
    def _generate_recommendations(self, report_data):
        """Generate recommendations based on analysis results"""
        recommendations = []
        anomalies = report_data.get('analysis', {}).get('anomalies', [])
        entropy = report_data.get('analysis', {}).get('entropy', 0.0)
        file_type = report_data.get('file', {}).get('type', 'Unknown')
        extracted = report_data.get('extracted_data', {})
        
        # Check for high entropy
        if entropy > 7.5:
            recommendations.append({
                'severity': 'HIGH',
                'icon': '🚨',
                'text': f'High entropy detected ({entropy:.2f}/8.0). This suggests possible embedded/steganographic data. Perform deep forensic analysis.'
            })
        elif entropy > 6.5:
            recommendations.append({
                'severity': 'MEDIUM',
                'icon': '⚠️',
                'text': f'Elevated entropy detected ({entropy:.2f}/8.0). Consider running additional steganography tools for verification.'
            })
        
        # Check for steganography signatures
        for anomaly in anomalies:
            if 'Steghide' in anomaly:
                recommendations.append({
                    'severity': 'HIGH',
                    'icon': '🔐',
                    'text': 'Steghide tool reference detected. This file may contain hidden data extracted with Steghide. Investigate immediately.'
                })
            elif 'STEGO' in anomaly:
                recommendations.append({
                    'severity': 'MEDIUM',
                    'icon': '🔍',
                    'text': 'Generic steganography marker detected. Run specialized tools for deeper analysis.'
                })
        
        # Check for extracted data
        if extracted.get('text'):
            recommendations.append({
                'severity': 'MEDIUM',
                'icon': '📝',
                'text': f'Embedded text found ({len(extracted["text"])} items). Review content for sensitive or hidden information.'
            })
        
        if extracted.get('appended_data'):
            recommendations.append({
                'severity': 'HIGH',
                'icon': '📦',
                'text': f'Appended data found ({extracted["appended_data"]["size"]} bytes). Extract and analyze the appended content.'
            })
        
        # File type specific recommendations
        if file_type == 'PNG Image':
            recommendations.append({
                'severity': 'LOW',
                'icon': '🔬',
                'text': 'Consider using specialized PNG steganography tools: zsteg, pngcheck, or StegOnline for deeper analysis.'
            })
        elif file_type == 'JPEG Image':
            recommendations.append({
                'severity': 'LOW',
                'icon': '🔬',
                'text': 'Consider using JPEG-specific steganography tools: steghide, outguess, or jsteg for deeper analysis.'
            })
        elif file_type == 'PDF Document':
            recommendations.append({
                'severity': 'LOW',
                'icon': '🔬',
                'text': 'Consider using PDF analysis tools: pdf-parser, peepdf, or Didier Stevens\' tools for deeper analysis.'
            })
        
        # General forensic recommendations
        if anomalies or extracted.get('text') or extracted.get('appended_data'):
            recommendations.append({
                'severity': 'MEDIUM',
                'icon': '🔒',
                'text': 'Preserve the original file as evidence. Create a forensic copy before attempting extraction.'
            })
            recommendations.append({
                'severity': 'MEDIUM',
                'icon': '📊',
                'text': 'Document all findings with timestamps and hash values for chain of custody.'
            })
        else:
            recommendations.append({
                'severity': 'LOW',
                'icon': '✅',
                'text': 'No anomalies detected. File appears clean. No further action required.'
            })
        
        return recommendations[:6]
    
    # ============================================================
    # REPORT MANAGEMENT METHODS
    # ============================================================
    
    def list_reports(self):
        """List all generated reports with details"""
        reports = []
        if os.path.exists(self.reports_dir):
            for f in os.listdir(self.reports_dir):
                if f.startswith('steg_report_') and f.endswith('.html'):
                    filepath = os.path.join(self.reports_dir, f)
                    stat = os.stat(filepath)
                    reports.append({
                        'filename': f,
                        'path': filepath,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
        return sorted(reports, key=lambda x: x['modified'], reverse=True)
    
    def view_report(self, report_path):
        """Open a report in the default browser"""
        if os.path.exists(report_path):
            import webbrowser
            webbrowser.open(f"file://{report_path}")
            return True
        return False
    
    def cleanup_old_reports(self, days=7):
        """Delete reports older than specified days"""
        import time as time_module
        cutoff = time_module.time() - (days * 24 * 60 * 60)
        deleted = 0
        for f in os.listdir(self.reports_dir):
            if f.startswith('steg_report_') and f.endswith('.html'):
                filepath = os.path.join(self.reports_dir, f)
                if os.path.getmtime(filepath) < cutoff:
                    try:
                        os.remove(filepath)
                        deleted += 1
                    except:
                        pass
        return deleted


# ============================================================
# HACKER-THEMED DASHBOARD
# ============================================================

def dashboard(workspace_root=None):
    """
    StegCheck Dashboard - Hacker-themed interactive steganography analysis.
    """
    import shutil
    import time
    import os
    from colorama import Fore, Style, init
    init(autoreset=True)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    analyzer = StegAnalyzer(workspace_root=workspace_root)
    
    def print_hacker_banner(term_width):
        banner_lines = [
            "",
            f"{Fore.GREEN}╔{'═' * 60}╗{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}  {Fore.RED}███████╗████████╗███████╗ ██████╗ ██╗  ██╗███████╗ ██████╗██╗  ██╗{Fore.GREEN}  ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}  {Fore.RED}██╔════╝╚══██╔══╝██╔════╝██╔════╝ ██║  ██║██╔════╝██╔════╝██║ ██╔╝{Fore.GREEN}  ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}  {Fore.RED}███████╗   ██║   █████╗  ██║  ███╗███████║█████╗  ██║     █████╔╝ {Fore.GREEN}  ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}  {Fore.RED}╚════██║   ██║   ██╔══╝  ██║   ██║██╔══██║██╔══╝  ██║     ██╔═██╗ {Fore.GREEN}  ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}  {Fore.RED}███████║   ██║   ███████╗╚██████╔╝██║  ██║███████╗╚██████╗██║  ██╗{Fore.GREEN}  ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}  {Fore.RED}╚══════╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝{Fore.GREEN}  ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}                                                          {Fore.GREEN}║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}     {Fore.CYAN}🛡️  STEGANOGRAPHY ANALYSIS v2.0  {Fore.RED}🔓{Fore.GREEN}             ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}     {Fore.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Fore.GREEN}             ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}     {Fore.YELLOW}Workspace:{Fore.WHITE} {analyzer.workspace_root}{Fore.GREEN}             ║{Style.RESET_ALL}",
            f"{Fore.GREEN}╚{'═' * 60}╝{Style.RESET_ALL}",
            ""
        ]
        for line in banner_lines:
            padding = max(0, (term_width - 62) // 2)
            print(" " * padding + line)
    
    def print_menu_option(num, text, color=Fore.GREEN, term_width=100):
        padding = max(0, (term_width - 50) // 2)
        print(f"{' ' * padding}{Fore.CYAN}┃{Style.RESET_ALL}  {color}[{num}]{Style.RESET_ALL} {text}  {Fore.CYAN}┃{Style.RESET_ALL}")
    
    while True:
        try:
            term_width = shutil.get_terminal_size().columns
            if term_width < 80:
                term_width = 80
            if term_width > 200:
                term_width = 200
        except:
            term_width = 100
        
        print_hacker_banner(term_width)
        
        padding = max(0, (term_width - 50) // 2)
        print(f"{' ' * padding}{Fore.CYAN}┌{'─' * 48}┐{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.YELLOW}⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯  {Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█{Fore.CYAN}  │{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}█{Fore.RESET}  {Fore.GREEN}┌────────────────────────────────────────────┐{Fore.RED}█{Fore.CYAN}  │{Style.RESET_ALL}")
        
        print_menu_option("1", "🔍 Analyze a file for steganography", Fore.CYAN, term_width)
        print_menu_option("2", "📊 View recent reports", Fore.CYAN, term_width)
        print_menu_option("3", "📄 Open last report in browser", Fore.CYAN, term_width)
        print_menu_option("4", "🗑️  Clean up old reports (7+ days)", Fore.CYAN, term_width)
        print_menu_option("5", "❌ Exit to main terminal", Fore.RED, term_width)
        
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}█{Fore.RESET}  {Fore.GREEN}└────────────────────────────────────────────┘{Fore.RED}█{Fore.CYAN}  │{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█{Fore.CYAN}  │{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}└{'─' * 48}┘{Style.RESET_ALL}")
        
        print()
        prompt_padding = max(0, (term_width - 45) // 2)
        print(f"{' ' * prompt_padding}{Fore.GREEN}[{Fore.YELLOW}ROOT@{Fore.CYAN}STEGCHECK{Fore.GREEN}]{Fore.RED} ▶{Style.RESET_ALL} ")
        choice = input(f"{' ' * (prompt_padding + 1)}{Fore.RED}└─$ {Style.RESET_ALL}").strip()
        
        if choice == '1':
            print()
            input_padding = max(0, (term_width - 50) // 2)
            print(f"{' ' * input_padding}{Fore.CYAN}┌─[{Fore.YELLOW}ANALYZE{Fore.CYAN}]─[{Fore.GREEN}Enter file path{Fore.CYAN}]")
            file_path = input(f"{' ' * input_padding}{Fore.CYAN}└─$ {Style.RESET_ALL}").strip()
            
            if not file_path:
                print(f"{' ' * input_padding}{Fore.RED}❌ No path provided.{Style.RESET_ALL}")
                time.sleep(1)
                continue
            
            if not os.path.exists(file_path):
                print(f"{' ' * input_padding}{Fore.RED}❌ File not found: {file_path}{Style.RESET_ALL}")
                time.sleep(1.5)
                continue
            
            results = analyzer.analyze(file_path, verbose=False)
            
            if results:
                print()
                input(f"{' ' * input_padding}{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            else:
                print(f"{' ' * input_padding}{Fore.RED}❌ Analysis failed.{Style.RESET_ALL}")
                time.sleep(1.5)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            
        elif choice == '2':
            reports = analyzer.list_reports()
            
            if not reports:
                print(f"\n{' ' * padding}{Fore.YELLOW}📭 No reports found.{Style.RESET_ALL}")
                input(f"\n{' ' * padding}{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            print(f"\n{' ' * padding}{Fore.CYAN}📊 Recent Reports ({len(reports)} total){Style.RESET_ALL}")
            print(f"{' ' * padding}{Fore.CYAN}─" * 60 + f"{Style.RESET_ALL}")
            print(f"{' ' * padding}{Fore.YELLOW}{'#':<4} {'Filename':<35} {'Size':<10} {'Modified':<20}{Style.RESET_ALL}")
            print(f"{' ' * padding}{Fore.CYAN}─" * 60 + f"{Style.RESET_ALL}")
            
            for i, report in enumerate(reports[:10], 1):
                size_kb = report['size'] / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
                print(f"{' ' * padding}{Fore.WHITE}{i:<4} {report['filename'][:35]:<35} {size_str:<10} {report['modified']:<20}{Style.RESET_ALL}")
            
            if len(reports) > 10:
                print(f"{' ' * padding}{Fore.DIM}... and {len(reports) - 10} more{Style.RESET_ALL}")
            
            print(f"{' ' * padding}{Fore.CYAN}─" * 60 + f"{Style.RESET_ALL}")
            
            report_choice = input(f"\n{' ' * padding}{Fore.CYAN}Enter report number to open (or press Enter to skip): {Style.RESET_ALL}").strip()
            if report_choice.isdigit():
                idx = int(report_choice) - 1
                if 0 <= idx < len(reports):
                    analyzer.view_report(reports[idx]['path'])
                    print(f"{' ' * padding}{Fore.GREEN}✅ Opening report...{Style.RESET_ALL}")
            
            input(f"\n{' ' * padding}{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            os.system('cls' if os.name == 'nt' else 'clear')
            
        elif choice == '3':
            reports = analyzer.list_reports()
            if reports:
                analyzer.view_report(reports[0]['path'])
                print(f"{' ' * padding}{Fore.GREEN}✅ Opening most recent report: {reports[0]['filename']}{Style.RESET_ALL}")
            else:
                print(f"{' ' * padding}{Fore.YELLOW}📭 No reports found.{Style.RESET_ALL}")
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')
            
        elif choice == '4':
            reports = analyzer.list_reports()
            if not reports:
                print(f"{' ' * padding}{Fore.YELLOW}📭 No reports to clean.{Style.RESET_ALL}")
                time.sleep(1)
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            deleted = analyzer.cleanup_old_reports(7)
            if deleted > 0:
                print(f"{' ' * padding}{Fore.GREEN}✅ Deleted {deleted} old reports (older than 7 days).{Style.RESET_ALL}")
            else:
                print(f"{' ' * padding}{Fore.GREEN}✅ No reports older than 7 days.{Style.RESET_ALL}")
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')
            
        elif choice == '5' or choice.lower() == 'exit':
            print(f"\n{' ' * padding}{Fore.GREEN}👋 Returning to main terminal...{Style.RESET_ALL}")
            time.sleep(0.5)
            os.system('cls' if os.name == 'nt' else 'clear')
            break
            
        else:
            print(f"{' ' * padding}{Fore.RED}❌ Invalid option. Please try again.{Style.RESET_ALL}")
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')


# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================

def main():
    """Command-line interface for StegAnalyzer (standalone mode)"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Steganography Analyzer - Detect hidden data in files',
        epilog='Example: python steg_analyzer.py image.png -v'
    )
    parser.add_argument('file', nargs='?', help='File to analyze (optional, will prompt if not provided)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    parser.add_argument('-w', '--workspace', help='Workspace directory')
    
    args = parser.parse_args()
    
    analyzer = StegAnalyzer(workspace_root=args.workspace)
    
    file_path = args.file
    if not file_path:
        print(f"\n{Fore.CYAN}┌─[{Fore.YELLOW}STEGANALYZER{Fore.CYAN}]─[{Fore.GREEN}File Path{Fore.CYAN}]")
        file_path = input(f"{Fore.CYAN}└─$ {Style.RESET_ALL}").strip()
        
        if not file_path:
            print(f"{Fore.RED}❌ No file path provided. Exiting.{Style.RESET_ALL}")
            sys.exit(1)
    
    print(f"\n{Fore.CYAN}🔍 Analyzing: {file_path}{Style.RESET_ALL}\n")
    results = analyzer.analyze(file_path, verbose=args.verbose)
    
    if results:
        report_path = os.path.join(analyzer.reports_dir, f'steg_report_{results["report_id"]}.html')
        print(f"\n{Fore.GREEN}✅ Analysis complete!{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}Report ID:{Style.RESET_ALL} {results['report_id']}")
        print(f"   {Fore.CYAN}Anomalies found:{Style.RESET_ALL} {'Yes' if results['analysis']['has_anomalies'] else 'No'}")
        if results['analysis']['anomalies']:
            print(f"   {Fore.CYAN}Anomalies:{Style.RESET_ALL}")
            for a in results['analysis']['anomalies']:
                print(f"     - {a}")
        print(f"\n   {Fore.CYAN}HTML Report:{Style.RESET_ALL} {report_path}")
    else:
        print(f"\n{Fore.RED}❌ Analysis failed.{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()