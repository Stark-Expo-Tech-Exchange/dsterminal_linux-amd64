# -*- coding: utf-8 -*-
import sys
"""

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


# ============================================================
# FIX: Handle OSError 22 on Windows
# ============================================================
if sys.platform == "win32":
    try:
        import subprocess as sp
        sp.run(["chcp", "65001"], capture_output=True, shell=True)
    except:
        pass


    try:
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

Steganography & Forensic Text Analyzer Module
Extracts ALL readable text/data from files for security compliance and forensic research.
Supports: Images, PDFs, Documents, Archives, and more.
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
    LIGHTRED_EX = '\033[91m'
    LIGHTGREEN_EX = '\033[92m'
    LIGHTYELLOW_EX = '\033[93m'
    LIGHTCYAN_EX = '\033[96m'
    LIGHTMAGENTA_EX = '\033[95m'
    
class Styles:
    BRIGHT = '\033[1m'
    DIM = '\033[2m'
    NORMAL = '\033[22m'
    RESET_ALL = '\033[0m'

# ============================================================
# TRY TO IMPORT COLORAMA WITH PROPER ERROR HANDLING
# ============================================================
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = Styles
except Exception as e:
    COLORAMA_AVAILABLE = False
    # Use our defined colors as fallback
    Fore = Colors
    Style = Styles

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
# REST OF THE CLASS
# ============================================================
class StegAnalyzer:
    """
    Steganography & Forensic Text Analyzer
    Extracts ALL readable text/data from files for security compliance.
    """
    
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
    
    def scan_bar(self, label, duration=0.3, width=25, term_width=100):
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
    # COMPREHENSIVE TEXT EXTRACTION - VISIBLE & HIDDEN
    # ============================================================
    
    def extract_all_text_from_file(self, file_path, file_info):
        """
        Extract ALL readable text/data from file - both visible and hidden.
        Returns comprehensive forensic data.
        """
        results = {
            'visible_text': [],      # Readable visible text
            'hidden_text': [],       # Hidden/steganographic text
            'metadata': [],          # File metadata
            'strings': [],           # Extracted strings
            'structure': [],         # File structure info
            'anomalies': [],         # Suspicious findings
            'summary': {}            # Summary statistics
        }
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            file_type = file_info.get('type', 'Unknown')
            
            # ============================================================
            # 1. EXTRACT VISIBLE TEXT (What you can see/read)
            # ============================================================
            
            # For PDFs - extract actual readable text
            if file_type == 'PDF Document':
                visible = self._extract_pdf_visible_text(data)
                results['visible_text'].extend(visible)
                results['summary']['visible_text_count'] = len(visible)
            
            # For Images with text (EXIF, comments, etc.)
            elif file_type in ['PNG Image', 'JPEG Image', 'GIF Image', 'BMP Image', 'WebP Image']:
                visible = self._extract_image_visible_text(data, file_type)
                results['visible_text'].extend(visible)
                results['summary']['visible_text_count'] = len(visible)
            
            # For Text files - all content is visible
            elif file_type == 'Text File':
                try:
                    text = data.decode('utf-8', errors='ignore')
                    lines = [l for l in text.split('\n') if l.strip()]
                    results['visible_text'].extend(lines[:100])
                    results['summary']['visible_text_count'] = len(lines)
                except:
                    pass
            
            # ============================================================
            # 2. EXTRACT HIDDEN TEXT (Steganography, embedded data)
            # ============================================================
            
            # Check PNG chunks for hidden text
            if file_type == 'PNG Image':
                hidden = self._extract_png_hidden_text(data)
                results['hidden_text'].extend(hidden)
                results['summary']['hidden_text_count'] = len(hidden)
            
            # Check for steganography signatures
            steg_signatures = self._check_steg_signatures(data)
            if steg_signatures:
                results['anomalies'].extend(steg_signatures)
                results['summary']['steg_signatures'] = len(steg_signatures)
            
            # Check for appended data
            appended = self._check_appended_data(data, file_type)
            if appended:
                results['hidden_text'].append(appended)
                results['summary']['appended_data'] = appended.get('size', 0)
            
            # ============================================================
            # 3. EXTRACT METADATA (Forensic artifacts)
            # ============================================================
            
            metadata = self._extract_metadata(data, file_type)
            results['metadata'].extend(metadata)
            results['summary']['metadata_count'] = len(metadata)
            
            # ============================================================
            # 4. EXTRACT READABLE STRINGS (Forensic)
            # ============================================================
            
            strings = self._extract_readable_strings(data)
            results['strings'].extend(strings[:50])
            results['summary']['strings_count'] = len(strings)
            
            # ============================================================
            # 5. EXTRACT FILE STRUCTURE (Forensic)
            # ============================================================
            
            structure = self._extract_file_structure(data, file_type)
            results['structure'].extend(structure)
            results['summary']['structure_count'] = len(structure)
            
            # ============================================================
            # 6. CALCULATE ENTROPY (Detect hidden data)
            # ============================================================
            
            entropy = self._calculate_entropy(data)
            results['summary']['entropy'] = entropy
            
            if entropy > 7.5:
                results['anomalies'].append(f"High entropy ({entropy:.2f}/8.0) - possible hidden data")
            elif entropy > 6.5:
                results['anomalies'].append(f"Elevated entropy ({entropy:.2f}/8.0) - potential hidden content")
            
            # ============================================================
            # 7. GENERATE FORENSIC SUMMARY
            # ============================================================
            
            results['summary']['total_text'] = (
                results['summary'].get('visible_text_count', 0) +
                results['summary'].get('hidden_text_count', 0) +
                results['summary'].get('strings_count', 0)
            )
            results['summary']['has_anomalies'] = len(results['anomalies']) > 0
            results['summary']['has_visible_text'] = len(results['visible_text']) > 0
            results['summary']['has_hidden_text'] = len(results['hidden_text']) > 0
            
        except Exception as e:
            results['anomalies'].append(f"Extraction error: {str(e)}")
        
        return results
    
 
    # ============================================================
    # EXTRACTION SUB-FUNCTIONS
    # ============================================================
    
    def _extract_pdf_visible_text(self, data):
        """Extract visible text from PDF"""
        text = []
        try:
            # Extract text between parentheses
            matches = re.findall(rb'\(([^)]*)\)', data)
            for match in matches:
                try:
                    decoded = match.decode('latin-1', errors='ignore')
                    # Clean up - keep only readable text
                    clean = re.sub(r'[^\x20-\x7E\n\r]', '', decoded)
                    if len(clean) > 3 and any(c.isalnum() for c in clean):
                        text.append(clean)
                except:
                    pass
        except:
            pass
        return text[:100]
    
    def _extract_image_visible_text(self, data, file_type):
        """Extract visible text from images (EXIF, comments)"""
        text = []
        try:
            # Extract text chunks from PNG
            if file_type == 'PNG Image':
                pos = 8
                while pos < len(data) - 12:
                    chunk_len = struct.unpack('>I', data[pos:pos+4])[0]
                    chunk_type = data[pos+4:pos+8]
                    chunk_data = data[pos+8:pos+8+chunk_len]
                    
                    if chunk_type in [b'tEXt', b'zTXt', b'iTXt']:
                        try:
                            if chunk_type == b'tEXt':
                                decoded = chunk_data.decode('latin-1', errors='ignore')
                                clean = re.sub(r'[^\x20-\x7E\n\r]', '', decoded)
                                if len(clean) > 3:
                                    text.append(clean)
                            elif chunk_type == b'zTXt':
                                idx = chunk_data.find(b'\x00')
                                if idx > 0:
                                    keyword = chunk_data[:idx].decode('latin-1', errors='ignore')
                                    compressed = chunk_data[idx+2:]
                                    decompressed = zlib.decompress(compressed)
                                    decoded = decompressed.decode('latin-1', errors='ignore')
                                    clean = re.sub(r'[^\x20-\x7E\n\r]', '', decoded)
                                    if len(clean) > 3:
                                        text.append(f"{keyword}: {clean}")
                            elif chunk_type == b'iTXt':
                                parts = chunk_data.split(b'\x00')
                                if len(parts) >= 4:
                                    keyword = parts[0].decode('latin-1', errors='ignore')
                                    decoded = parts[3].decode('utf-8', errors='ignore')
                                    clean = re.sub(r'[^\x20-\x7E\n\r]', '', decoded)
                                    if len(clean) > 3:
                                        text.append(f"{keyword}: {clean}")
                        except:
                            pass
                    
                    pos += 4 + 4 + chunk_len + 4
            
            # Try to extract EXIF data using PIL if available
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                
                img = Image.open(file_path)
                exifdata = img.getexif()
                
                for tag_id, value in exifdata.items():
                    if isinstance(value, str) and len(value) > 3:
                        tag = TAGS.get(tag_id, tag_id)
                        text.append(f"{tag}: {value}")
            except:
                pass
        except:
            pass
        
        return text[:100]
    
    def _extract_png_hidden_text(self, data):
        """Extract hidden text from PNG (steganography)"""
        hidden = []
        try:
            # Check for unusual chunks that might contain hidden data
            pos = 8
            while pos < len(data) - 12:
                chunk_len = struct.unpack('>I', data[pos:pos+4])[0]
                chunk_type = data[pos+4:pos+8]
                chunk_data = data[pos+8:pos+8+chunk_len]
                
                # Check for custom/unknown chunks that might contain hidden data
                chunk_name = chunk_type.decode('ascii', errors='ignore')
                if chunk_type not in [b'IHDR', b'PLTE', b'IDAT', b'IEND', b'tEXt', b'zTXt', b'iTXt', b'sRGB', b'gAMA']:
                    try:
                        # Try to decode as text
                        decoded = chunk_data.decode('latin-1', errors='ignore')
                        clean = re.sub(r'[^\x20-\x7E\n\r]', '', decoded)
                        if len(clean) > 10:
                            hidden.append(f"[{chunk_name}] {clean[:200]}")
                    except:
                        pass
                
                pos += 4 + 4 + chunk_len + 4
            
            # Check for appended data after IEND
            iend_pos = data.rfind(b'IEND')
            if iend_pos > 0 and iend_pos + 8 < len(data):
                appended = data[iend_pos + 8:]
                if len(appended) > 100:
                    try:
                        decoded = appended.decode('latin-1', errors='ignore')
                        clean = re.sub(r'[^\x20-\x7E\n\r]', '', decoded)
                        if len(clean) > 10:
                            hidden.append(f"[Appended] {clean[:500]}")
                    except:
                        pass
        except:
            pass
        
        return hidden[:50]
    
    def _check_steg_signatures(self, data):
        """Check for steganography tool signatures"""
        anomalies = []
        signatures = {
            b'STEGO': 'Generic steganography marker',
            b'Steghide': 'Steghide tool reference',
            b'outguess': 'OutGuess tool reference',
            b'JPHIDE': 'JP Hide and Seek',
            b'JPSEEK': 'JP Seek',
            b'F5': 'F5 steganography algorithm',
            b'OpenStego': 'OpenStego tool reference',
        }
        
        for sig, desc in signatures.items():
            if sig in data:
                anomalies.append(f"Possible {desc}")
        
        return anomalies
    
    def _check_appended_data(self, data, file_type):
        """Check for appended data after file end"""
        result = None
        
        # PNG: check after IEND
        if file_type == 'PNG Image':
            iend_pos = data.rfind(b'IEND')
            if iend_pos > 0 and iend_pos + 8 < len(data):
                appended = data[iend_pos + 8:]
                if len(appended) > 100:
                    try:
                        text = appended.decode('latin-1', errors='ignore')
                        clean = re.sub(r'[^\x20-\x7E\n\r]', '', text)
                        if len(clean) > 10:
                            result = {
                                'size': len(appended),
                                'text': clean[:500],
                                'type': 'Appended data after PNG IEND'
                            }
                    except:
                        result = {
                            'size': len(appended),
                            'text': '[Binary data - cannot display]',
                            'type': 'Appended binary data'
                        }
        
        # JPEG: check after EOF marker
        elif file_type == 'JPEG Image':
            # JPEG ends with FF D9
            if data.endswith(b'\xff\xd9'):
                # Check if there's data after the marker
                pass
        
        return result
    
    def _extract_metadata(self, data, file_type):
        """Extract forensic metadata"""
        metadata = []
        try:
            # Check for common metadata patterns
            patterns = {
                'Created': rb'Created[:\s]+([^\n\r]+)',
                'Modified': rb'Modified[:\s]+([^\n\r]+)',
                'Author': rb'Author[:\s]+([^\n\r]+)',
                'Creator': rb'Creator[:\s]+([^\n\r]+)',
                'Producer': rb'Producer[:\s]+([^\n\r]+)',
                'Title': rb'Title[:\s]+([^\n\r]+)',
                'Subject': rb'Subject[:\s]+([^\n\r]+)',
                'Keywords': rb'Keywords[:\s]+([^\n\r]+)',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, data, re.IGNORECASE)
                if match:
                    try:
                        value = match.group(1).decode('latin-1', errors='ignore')
                        clean = re.sub(r'[^\x20-\x7E]', '', value)
                        if clean:
                            metadata.append(f"{key}: {clean}")
                    except:
                        pass
        except:
            pass
        
        return metadata[:20]
    
    def _extract_readable_strings(self, data):
        """Extract readable strings (forensic)"""
        strings = []
        try:
            pattern = re.compile(b'[\\x20-\\x7E]{4,}')
            matches = pattern.findall(data)
            for m in matches:
                try:
                    s = m.decode('ascii', errors='ignore')
                    # Skip common headers
                    if len(s) > 3 and not s.startswith(('IHDR', 'IDAT', 'IEND', 'sRGB', 'gAMA', 'PLTE')):
                        strings.append(s)
                except:
                    pass
        except:
            pass
        return strings[:50]
    
    def _extract_file_structure(self, data, file_type):
        """Extract file structure information"""
        structure = []
        try:
            if file_type == 'PNG Image':
                pos = 8
                chunk_count = 0
                while pos < len(data) - 12 and chunk_count < 20:
                    chunk_len = struct.unpack('>I', data[pos:pos+4])[0]
                    chunk_type = data[pos+4:pos+8]
                    chunk_name = chunk_type.decode('ascii', errors='ignore')
                    structure.append(f"Chunk {chunk_count+1}: {chunk_name} ({chunk_len} bytes)")
                    pos += 4 + 4 + chunk_len + 4
                    chunk_count += 1
                if chunk_count >= 20:
                    structure.append("... and more chunks")
            
            elif file_type == 'PDF Document':
                # Count objects
                obj_count = len(re.findall(rb'obj\s+\d+\s+\d+', data))
                structure.append(f"PDF Objects: {obj_count}")
                
                # Check for streams
                stream_count = len(re.findall(rb'stream\r\n', data))
                structure.append(f"Streams: {stream_count}")
        except:
            pass
        
        return structure[:20]
    
    def _calculate_entropy(self, data):
        """Calculate Shannon entropy of data"""
        if len(data) == 0:
            return 0.0
        
        byte_counts = Counter(data)
        entropy = 0.0
        for count in byte_counts.values():
            p = count / len(data)
            if p > 0:
                entropy -= p * math.log2(p)
        
        return round(entropy, 2)
    
    # ============================================================
    # DISPLAY FUNCTIONS
    # ============================================================
    
    def display_forensic_results(self, results, file_path, term_width=100):
        """Display comprehensive forensic results"""
        print()
        file_name = os.path.basename(file_path)
        summary = results.get('summary', {})
        
        # Status
        if summary.get('has_anomalies'):
            status = "⚠️ ANOMALIES DETECTED - FORENSIC REVIEW REQUIRED"
            status_color = Fore.RED
            border_color = Fore.RED
        elif summary.get('has_hidden_text'):
            status = "🔍 HIDDEN DATA FOUND - REVIEW RECOMMENDED"
            status_color = Fore.YELLOW
            border_color = Fore.YELLOW
        else:
            status = "✅ FORENSIC ANALYSIS COMPLETE - FILE APPEARS CLEAN"
            status_color = Fore.GREEN
            border_color = Fore.GREEN
        
        content_lines = []
        content_lines.append(f"{status_color}{status}{Style.RESET_ALL}")
        content_lines.append("")
        content_lines.append(f"  {Fore.CYAN}📁 File:{Style.RESET_ALL} {file_name}")
        content_lines.append(f"  {Fore.CYAN}📊 Entropy:{Style.RESET_ALL} {summary.get('entropy', 0.0):.2f}/8.0")
        content_lines.append("")
        
        # Text summary
        content_lines.append(f"  {Fore.CYAN}📝 Text Analysis:{Style.RESET_ALL}")
        content_lines.append(f"    {Fore.WHITE}Visible Text:{Style.RESET_ALL} {summary.get('visible_text_count', 0)} items")
        content_lines.append(f"    {Fore.WHITE}Hidden Text:{Style.RESET_ALL} {summary.get('hidden_text_count', 0)} items")
        content_lines.append(f"    {Fore.WHITE}Strings:{Style.RESET_ALL} {summary.get('strings_count', 0)} items")
        content_lines.append(f"    {Fore.WHITE}Metadata:{Style.RESET_ALL} {summary.get('metadata_count', 0)} items")
        content_lines.append("")
        
        # Anomalies
        anomalies = results.get('anomalies', [])
        if anomalies:
            content_lines.append(f"  {Fore.RED}⚠️ Anomalies Found:{Style.RESET_ALL} {len(anomalies)}")
            for a in anomalies[:5]:
                content_lines.append(f"    {Fore.YELLOW}▸{Style.RESET_ALL} {a}")
            if len(anomalies) > 5:
                content_lines.append(f"    {Fore.YELLOW}▸{Style.RESET_ALL} ... and {len(anomalies) - 5} more")
            content_lines.append("")
        
        # Visible Text Sample
        visible = results.get('visible_text', [])
        if visible:
            content_lines.append(f"  {Fore.GREEN}📖 Visible Text Sample:{Style.RESET_ALL}")
            for t in visible[:3]:
                clean = t[:80] + "..." if len(t) > 80 else t
                content_lines.append(f"    {Fore.WHITE}• {clean}{Style.RESET_ALL}")
            if len(visible) > 3:
                content_lines.append(f"    {Fore.DIM}... and {len(visible) - 3} more visible items{Style.RESET_ALL}")
            content_lines.append("")
        
        # Hidden Text Sample
        hidden = results.get('hidden_text', [])
        if hidden:
            content_lines.append(f"  {Fore.YELLOW}🔒 Hidden Text Sample:{Style.RESET_ALL}")
            for t in hidden[:3]:
                clean = t[:80] + "..." if len(t) > 80 else t
                content_lines.append(f"    {Fore.WHITE}• {clean}{Style.RESET_ALL}")
            if len(hidden) > 3:
                content_lines.append(f"    {Fore.DIM}... and {len(hidden) - 3} more hidden items{Style.RESET_ALL}")
            content_lines.append("")
        
        # Metadata
        metadata = results.get('metadata', [])
        if metadata:
            content_lines.append(f"  {Fore.CYAN}📋 Forensic Metadata:{Style.RESET_ALL}")
            for m in metadata[:3]:
                content_lines.append(f"    {Fore.WHITE}• {m}{Style.RESET_ALL}")
            if len(metadata) > 3:
                content_lines.append(f"    {Fore.DIM}... and {len(metadata) - 3} more metadata items{Style.RESET_ALL}")
            content_lines.append("")
        
        # Structure
        structure = results.get('structure', [])
        if structure:
            content_lines.append(f"  {Fore.CYAN}📂 File Structure:{Style.RESET_ALL}")
            for s in structure[:3]:
                content_lines.append(f"    {Fore.WHITE}• {s}{Style.RESET_ALL}")
            if len(structure) > 3:
                content_lines.append(f"    {Fore.DIM}... and {len(structure) - 3} more structure items{Style.RESET_ALL}")
        
        self.print_box("🔬 FORENSIC ANALYSIS RESULTS", content_lines, border_color, term_width)
    
    # ============================================================
    # MAIN ANALYSIS METHOD
    # ============================================================
    
    def analyze(self, file_path, verbose=False):
        """Perform comprehensive forensic analysis on a file"""
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
            self.print_box("🔬 FORENSIC TEXT ANALYSIS", content_lines, Fore.CYAN, term_width)
            print()
            
            # Loading animation
            self.print_centered(f"{loading_emoji} Loading file...", Fore.CYAN, term_width=term_width)
            time.sleep(0.2)

            self.print_centered(f"{microscope_emoji} Analyzing for visible & hidden data...", Fore.CYAN, term_width=term_width)
            time.sleep(0.1)
            print()

            # Animated scan stages
            scan_stages = [
                ("Visible Text Extraction", folder_emoji),
                ("Hidden Data Detection", search_emoji),
                ("Metadata Extraction", chart_emoji),
                ("Forensic Analysis", microscope_emoji)
            ]
            
            for stage, icon in scan_stages:
                self.scan_bar(f"{icon} {stage}", duration=0.3, width=25, term_width=term_width)
                time.sleep(0.05)

            # Extract ALL data
            file_info = self.detect_file_type(file_path)
            results = self.extract_all_text_from_file(file_path, file_info)
            
            # Display forensic results
            self.display_forensic_results(results, file_path, term_width)
            
            # Generate report data
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
                    'entropy': results.get('summary', {}).get('entropy', 0.0),
                    'anomalies': results.get('anomalies', []),
                    'has_anomalies': len(results.get('anomalies', [])) > 0,
                    'has_hidden_data': len(results.get('hidden_text', [])) > 0,
                    'has_visible_text': len(results.get('visible_text', [])) > 0
                },
                'extracted_data': results
            }
            
            # Generate reports
            print()
            self.print_centered("📄 Generating forensic reports...", Fore.CYAN, term_width=term_width)
            
            html_path = self.generate_html_report(report_data)
            pdf_path = self.generate_pdf_report(report_data)
            
            # Display report status
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
            
            self.print_box("📄 FORENSIC REPORTS", content_lines, Fore.CYAN, term_width)
            
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
    
    # ============================================================
    # REPORT GENERATION
    # ============================================================
    
    def generate_html_report(self, report_data):
        """Generate HTML forensic report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        filename = f"forensic_report_{report_data['report_id']}.html"
        filepath = os.path.join(self.reports_dir, filename)
        
        extracted = report_data.get('extracted_data', {})
        
        # Build sections
        visible_html = ""
        for t in extracted.get('visible_text', [])[:20]:
            visible_html += f'<div class="text-item">• {t}</div>'
        if len(extracted.get('visible_text', [])) > 20:
            visible_html += f'<div class="text-item">... and {len(extracted["visible_text"]) - 20} more</div>'
        
        hidden_html = ""
        for t in extracted.get('hidden_text', [])[:20]:
            hidden_html += f'<div class="text-item hidden">• {t}</div>'
        if len(extracted.get('hidden_text', [])) > 20:
            hidden_html += f'<div class="text-item">... and {len(extracted["hidden_text"]) - 20} more</div>'
        
        metadata_html = ""
        for m in extracted.get('metadata', [])[:20]:
            metadata_html += f'<div class="text-item">• {m}</div>'
        if len(extracted.get('metadata', [])) > 20:
            metadata_html += f'<div class="text-item">... and {len(extracted["metadata"]) - 20} more</div>'
        
        strings_html = ""
        for s in extracted.get('strings', [])[:20]:
            strings_html += f'<div class="text-item">• {s}</div>'
        if len(extracted.get('strings', [])) > 20:
            strings_html += f'<div class="text-item">... and {len(extracted["strings"]) - 20} more</div>'
        
        anomalies_html = ""
        for a in extracted.get('anomalies', []):
            anomalies_html += f'<li>🔴 {a}</li>'
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSTerminal Forensic Report - {report_data['report_id']}</title>
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
        .extracted-data {{ background: #0d0d1a; padding: 15px; border-radius: 8px; margin: 10px 0; max-height: 400px; overflow-y: auto; font-size: 13px; }}
        .text-item {{ color: #cccccc; padding: 2px 0; border-bottom: 1px solid #00ffaa11; }}
        .text-item.hidden {{ color: #ffaa44; border-left: 3px solid #ffaa44; padding-left: 10px; }}
        .anomaly-list {{ list-style: none; padding: 0; }}
        .anomaly-list li {{ padding: 8px 15px; margin: 5px 0; background: #1a1a2e; border-radius: 5px; border-left: 3px solid #ff0044; }}
        .footer {{ text-align: center; padding: 20px 0; margin-top: 30px; border-top: 1px solid #00ffaa33; color: #666688; font-size: 12px; }}
        .badge {{ display: inline-block; padding: 2px 10px; border-radius: 3px; font-size: 11px; font-weight: bold; }}
        .badge-danger {{ background: #ff0044; color: white; }}
        .badge-warning {{ background: #ffaa00; color: #0a0a0f; }}
        .badge-success {{ background: #00ff44; color: #0a0a0f; }}
        @media (max-width: 600px) {{ .info-grid {{ grid-template-columns: 1fr; }} .container {{ padding: 15px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 DSTerminal StegCheck Forensic Analysis</h1>
            <div class="subtitle">Report ID: {report_data['report_id']} | Generated: {timestamp}</div>
        </div>
        
        <h2>📋 File Information</h2>
        <div class="info-grid">
            <div class="info-card"><div class="label">File Name</div><div class="value">{report_data['file']['name']}</div></div>
            <div class="info-card"><div class="label">File Type</div><div class="value">{report_data['file']['type']}</div></div>
            <div class="info-card"><div class="label">File Size</div><div class="value">{report_data['file']['size']} bytes</div></div>
            <div class="info-card"><div class="label">Category</div><div class="value">{report_data['file']['category']}</div></div>
            <div class="info-card"><div class="label">Entropy Score</div><div class="value">{report_data['analysis']['entropy']:.2f}/8.0</div></div>
            <div class="info-card">
                <div class="label">Status</div>
                <div class="value">{'<span class="badge badge-danger">⚠️ ANOMALIES</span>' if report_data['analysis']['has_anomalies'] else '<span class="badge badge-success">✅ CLEAN</span>'}</div>
            </div>
        </div>
        
        <h2>📊 Text Analysis Summary</h2>
        <div class="info-grid">
            <div class="info-card"><div class="label">Visible Text</div><div class="value">{len(extracted.get('visible_text', []))} items</div></div>
            <div class="info-card"><div class="label">Hidden Text</div><div class="value">{len(extracted.get('hidden_text', []))} items</div></div>
            <div class="info-card"><div class="label">Strings</div><div class="value">{len(extracted.get('strings', []))} items</div></div>
            <div class="info-card"><div class="label">Metadata</div><div class="value">{len(extracted.get('metadata', []))} items</div></div>
        </div>
        
        <h2>⚠️ Anomalies Detected</h2>
        {'' if extracted.get('anomalies') else '<p style="color: #44ff88;">✅ No anomalies detected - File appears clean</p>'}
        <ul class="anomaly-list">
        {anomalies_html}
        </ul>
        
        <h2>📖 Visible Text (Readable Content)</h2>
        <div class="extracted-data">
        {visible_html if visible_html else '<p style="color: #666;">No visible text found</p>'}
        </div>
        
        <h2>🔒 Hidden Text (Steganographic/Embedded)</h2>
        <div class="extracted-data">
        {hidden_html if hidden_html else '<p style="color: #666;">No hidden text found</p>'}
        </div>
        
        <h2>📋 Forensic Metadata</h2>
        <div class="extracted-data">
        {metadata_html if metadata_html else '<p style="color: #666;">No metadata found</p>'}
        </div>
        
        <h2>📊 Extracted Strings</h2>
        <div class="extracted-data">
        {strings_html if strings_html else '<p style="color: #666;">No strings extracted</p>'}
        </div>
        
        <div class="footer">
            <p>Generated by DSTerminal v4.0.0.113 | Report ID: {report_data['report_id']}</p>
            <p>🔒 This forensic report is confidential and intended for authorized personnel only.</p>
        </div>
    </div>
</body>
</html>'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_pdf_report(self, report_data):
        """Generate PDF forensic report"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            filename = f"forensic_report_{report_data['report_id']}.pdf"
            filepath = os.path.join(self.reports_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4, 
                                   rightMargin=50, leftMargin=50, 
                                   topMargin=50, bottomMargin=50)
            
            styles = getSampleStyleSheet()
            extracted = report_data.get('extracted_data', {})
            
            # Style definitions
            title_style = ParagraphStyle(
                'CustomTitle', parent=styles['Heading1'], fontSize=20,
                textColor=colors.HexColor('#1a237e'), alignment=TA_CENTER, spaceAfter=20,
                fontName='Helvetica-Bold'
            )
            heading_style = ParagraphStyle(
                'CustomHeading', parent=styles['Heading2'], fontSize=14,
                textColor=colors.HexColor('#1a237e'), spaceAfter=10, spaceBefore=15,
                fontName='Helvetica-Bold'
            )
            subheading_style = ParagraphStyle(
                'SubHeading', parent=styles['Heading3'], fontSize=12,
                textColor=colors.HexColor('#283593'), spaceAfter=8, spaceBefore=10,
                fontName='Helvetica-Bold'
            )
            normal_style = ParagraphStyle(
                'CustomNormal', parent=styles['Normal'], fontSize=10,
                textColor=colors.black, spaceAfter=4, fontName='Helvetica'
            )
            
            story = []
            
            # Title
            story.append(Paragraph("DSTerminal Forensic Text Analysis Report", title_style))
            story.append(Paragraph(f"Report ID: {report_data['report_id']}", normal_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            story.append(Spacer(1, 0.3*inch))
            
            # File Information
            story.append(Paragraph("File Information", heading_style))
            file_data = [
                ["File Name", report_data['file']['name']],
                ["File Type", report_data['file']['type']],
                ["File Size", f"{report_data['file']['size']} bytes"],
                ["Entropy Score", f"{report_data['analysis']['entropy']:.2f}/8.0"],
                ["Anomalies", "Yes" if report_data['analysis']['has_anomalies'] else "No"],
                ["Hidden Data", "Yes" if report_data['analysis']['has_hidden_data'] else "No"]
            ]
            
            file_table = Table(file_data, colWidths=[2*inch, 4*inch])
            file_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
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
            if extracted.get('anomalies'):
                for a in extracted['anomalies']:
                    story.append(Paragraph(f"• {a}", normal_style))
            else:
                story.append(Paragraph("✅ No anomalies detected", normal_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Visible Text
            story.append(Paragraph("Visible Text (Readable Content)", heading_style))
            if extracted.get('visible_text'):
                for t in extracted['visible_text'][:10]:
                    safe_text = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(f"• {safe_text[:200]}", normal_style))
                if len(extracted['visible_text']) > 10:
                    story.append(Paragraph(f"... and {len(extracted['visible_text']) - 10} more items", normal_style))
            else:
                story.append(Paragraph("No visible text found", normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Hidden Text
            story.append(Paragraph("Hidden Text (Steganographic/Embedded)", heading_style))
            if extracted.get('hidden_text'):
                for t in extracted['hidden_text'][:10]:
                    safe_text = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(f"• {safe_text[:200]}", normal_style))
                if len(extracted['hidden_text']) > 10:
                    story.append(Paragraph(f"... and {len(extracted['hidden_text']) - 10} more items", normal_style))
            else:
                story.append(Paragraph("No hidden text found", normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Metadata
            story.append(Paragraph("Forensic Metadata", heading_style))
            if extracted.get('metadata'):
                for m in extracted['metadata'][:10]:
                    safe_text = m.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(f"• {safe_text[:200]}", normal_style))
                if len(extracted['metadata']) > 10:
                    story.append(Paragraph(f"... and {len(extracted['metadata']) - 10} more items", normal_style))
            else:
                story.append(Paragraph("No metadata found", normal_style))
            
            # Footer
            story.append(Spacer(1, 0.5*inch))
            footer_style = ParagraphStyle(
                'Footer', parent=styles['Normal'], fontSize=8,
                textColor=colors.HexColor('#666666'), alignment=TA_CENTER
            )
            story.append(Paragraph(
                f"Generated by DSTerminal v4.0.0.113 | Report ID: {report_data['report_id']}",
                footer_style
            ))
            story.append(Paragraph(
                "This forensic report is confidential and intended for authorized personnel only.",
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
    # REPORT MANAGEMENT
    # ============================================================
    
    def list_reports(self):
        reports = []
        if os.path.exists(self.reports_dir):
            for f in os.listdir(self.reports_dir):
                if f.startswith('forensic_report_') and f.endswith('.html'):
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
        if os.path.exists(report_path):
            import webbrowser
            webbrowser.open(f"file://{report_path}")
            return True
        return False
    
    def cleanup_old_reports(self, days=7):
        import time as time_module
        cutoff = time_module.time() - (days * 24 * 60 * 60)
        deleted = 0
        for f in os.listdir(self.reports_dir):
            if f.startswith('forensic_report_') and f.endswith('.html'):
                filepath = os.path.join(self.reports_dir, f)
                if os.path.getmtime(filepath) < cutoff:
                    try:
                        os.remove(filepath)
                        deleted += 1
                    except:
                        pass
        return deleted


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(workspace_root=None):
    """Forensic Analysis Dashboard"""
    import shutil, time, os
    init(autoreset=True)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    analyzer = StegAnalyzer(workspace_root=workspace_root)
    
    def print_banner(term_width):
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
            f"{Fore.GREEN}║{Style.RESET_ALL}     {Fore.CYAN}🔬 FORENSIC INFORMATION ANALYSIS v2.0.987  {Fore.RED}🔓{Fore.GREEN}             ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}     {Fore.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Fore.GREEN}             ║{Style.RESET_ALL}",
            f"{Fore.GREEN}║{Style.RESET_ALL}     {Fore.YELLOW}Sandbox=Workspace:{Fore.WHITE} {analyzer.workspace_root}{Fore.GREEN}             ║{Style.RESET_ALL}",
            f"{Fore.GREEN}╚{'═' * 60}╝{Style.RESET_ALL}",
            ""
        ]
        for line in banner_lines:
            padding = max(0, (term_width - 62) // 2)
            print(" " * padding + line)
    
    while True:
        try:
            term_width = shutil.get_terminal_size().columns
            if term_width < 80:
                term_width = 80
            if term_width > 200:
                term_width = 200
        except:
            term_width = 100
        
        print_banner(term_width)
        
        padding = max(0, (term_width - 50) // 2)
        print(f"{' ' * padding}{Fore.CYAN}┌{'─' * 48}┐{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.YELLOW}⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯  {Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█{Fore.CYAN}  │{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}█{Fore.RESET}  {Fore.GREEN}┌────────────────────────────────────────────┐{Fore.RED}█{Fore.CYAN}  │{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}┃{Style.RESET_ALL}  {Fore.GREEN}[1]{Style.RESET_ALL} 🔍 Analyze file (Visible + Hidden Text){Fore.CYAN}  ┃{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}┃{Style.RESET_ALL}  {Fore.GREEN}[2]{Style.RESET_ALL} 📊 View forensic reports{Fore.CYAN}                  ┃{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}┃{Style.RESET_ALL}  {Fore.GREEN}[3]{Style.RESET_ALL} 📄 Open last report{Fore.CYAN}                      ┃{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}┃{Style.RESET_ALL}  {Fore.GREEN}[4]{Style.RESET_ALL} 🗑️  Clean up old reports{Fore.CYAN}                 ┃{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}┃{Style.RESET_ALL}  {Fore.GREEN}[5]{Style.RESET_ALL} ❌ Exit to main terminal{Fore.CYAN}                 ┃{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}█{Fore.RESET}  {Fore.GREEN}└────────────────────────────────────────────┘{Fore.RED}█{Fore.CYAN}  │{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█{Fore.CYAN}  │{Style.RESET_ALL}")
        print(f"{' ' * padding}{Fore.CYAN}└{'─' * 48}┘{Style.RESET_ALL}")
        
        print()
        prompt_padding = max(0, (term_width - 45) // 2)
        print(f"{' ' * prompt_padding}{Fore.GREEN}[{Fore.YELLOW}DFFENEX@{Fore.CYAN}FORENSIC{Fore.GREEN}]{Fore.RED} ▶{Style.RESET_ALL} ")
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
            
            print(f"\n{' ' * padding}{Fore.CYAN}📊 Forensic Reports ({len(reports)} total){Style.RESET_ALL}")
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
            print(f"{' ' * padding}{Fore.RED}❌ Invalid option.{Style.RESET_ALL}")
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Standalone mode"""
    import argparse
    parser = argparse.ArgumentParser(
        description='Forensic Text Analyzer - Extract visible & hidden data from files',
        epilog='Example: python steg_analyzer.py document.pdf -v'
    )
    parser.add_argument('file', nargs='?', help='File to analyze')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    parser.add_argument('-w', '--workspace', help='Workspace directory')
    args = parser.parse_args()
    
    analyzer = StegAnalyzer(workspace_root=args.workspace)
    
    file_path = args.file
    if not file_path:
        print(f"\n{Fore.CYAN}┌─[{Fore.YELLOW}FORENSIC{Fore.CYAN}]─[{Fore.GREEN}File Path{Fore.CYAN}]")
        file_path = input(f"{Fore.CYAN}└─$ {Style.RESET_ALL}").strip()
        if not file_path:
            print(f"{Fore.RED}❌ No file path provided. Exiting.{Style.RESET_ALL}")
            sys.exit(1)
    
    print(f"\n{Fore.CYAN}🔬 Analyzing: {file_path}{Style.RESET_ALL}\n")
    results = analyzer.analyze(file_path, verbose=args.verbose)
    
    if results:
        report_path = os.path.join(analyzer.reports_dir, f'forensic_report_{results["report_id"]}.html')
        print(f"\n{Fore.GREEN}✅ Analysis complete!{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}Report ID:{Style.RESET_ALL} {results['report_id']}")
        print(f"   {Fore.CYAN}Anomalies found:{Style.RESET_ALL} {'Yes' if results['analysis']['has_anomalies'] else 'No'}")
        print(f"   {Fore.CYAN}Hidden data:{Style.RESET_ALL} {'Yes' if results['analysis']['has_hidden_data'] else 'No'}")
        print(f"\n   {Fore.CYAN}HTML Report:{Style.RESET_ALL} {report_path}")
    else:
        print(f"\n{Fore.RED}❌ Analysis failed.{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()