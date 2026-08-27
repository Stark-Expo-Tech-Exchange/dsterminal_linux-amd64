#!/usr/bin/env python3
import sys
# -*- coding: utf-8 -*-

"""
DSTerminal® Ransomware Detection & Monitoring Module - Enhanced Interactive Dashboard
Version: 5.0.0
"""

import json
import os
import platform
import shutil
import socket
import sys
import time
import threading
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import asdict, dataclass, field
# ============================================================================
# VERSION DEFINITION
# ============================================================================
VERSION = "5.0.0"
APP_NAME = "DSTerminal Ransomware Defense"
AUTHOR = "Spark Wilson Spink"
# Try to import reportlab
try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from dataclasses import dataclass, field

@dataclass
class Indicator:
    timestamp: str
    category: str
    indicator_type: str
    severity: str
    score: int
    path: str = ""
    process: str = ""
    pid: int = 0
    evidence: str = ""
    recommendation: str = ""
    confidence: str = "LOW"

@dataclass
class FileEvent:
    timestamp: str
    event_type: str
    path: str
    size: int = 0
    extension: str = ""
    suspicious: bool = False
# ============================================================================
# ENHANCED INTERACTIVE DASHBOARD
# ============================================================================

class EnhancedDashboard:
    """
    Fully responsive, auto-resizing interactive terminal dashboard with real-time updates.
    """
    
    def __init__(self, monitor):
        self.monitor = monitor
        self.running = True
        self.selected_option = 0
        self.scan_progress = 0
        self.scanning = False
        self.scan_result = None
        self.last_update = time.time()
        self.update_interval = 0.5  # seconds
        self._initialized = False
        
        # Color scheme with gradient support
        self.colors = {
            'header': '\033[38;5;51m',
            'header2': '\033[38;5;45m',
            'success': '\033[38;5;46m',
            'warning': '\033[38;5;226m',
            'error': '\033[38;5;196m',
            'info': '\033[38;5;39m',
            'dim': '\033[38;5;244m',
            'highlight': '\033[38;5;201m',
            'border': '\033[38;5;33m',
            'border2': '\033[38;5;27m',
            'reset': '\033[0m',
            'bold': '\033[1m',
            'blink': '\033[5m',
        }
        
        # Box characters
        self.box = {
            'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
            'h': '─', 'v': '│', 
            'tl_d': '╔', 'tr_d': '╗',
            'bl_d': '╚', 'br_d': '╝', 
            'h_d': '═', 'v_d': '║',
            'tl_r': '╒', 'tr_r': '╕',
            'bl_r': '╘', 'br_r': '╛',
            'h_r': '═', 'v_r': '│',
        }
        
        # Menu items with icons
        self.menu_items = [
            ("🔍 SYSTEM SCAN", self.menu_scan),
            ("📡 REAL-TIME MONITOR", self.menu_monitor),
            ("⚠️ SHOW INDICATORS", self.menu_indicators),
            ("📊 STATUS DASHBOARD", self.menu_status),
            ("📁 QUARANTINE", self.menu_quarantine),
            ("💾 RESTORE BACKUP", self.menu_restore),
            ("📄 EXPORT REPORT", self.menu_export),
            ("🚪 EXIT", self.menu_exit),
        ]
        
        # Terminal size tracking
        self._last_width = 0
        self._last_height = 0
        self._resize_lock = threading.Lock()
        
        # Start resize monitoring thread
        self._resize_thread = threading.Thread(target=self._monitor_resize, daemon=True)
        self._resize_thread.start()
        
        # Mark as initialized
        self._initialized = True
    
    def _monitor_resize(self):
        """Monitor terminal size changes and trigger redraw"""
        while self.running:
            try:
                cols, rows = self._get_terminal_size()
                if cols != self._last_width or rows != self._last_height:
                    with self._resize_lock:
                        self._last_width = cols
                        self._last_height = rows
                        # Only redraw if we're in the main menu (not in a sub-menu)
                        if not self.scanning and self._initialized:
                            self._render_main_menu()
            except:
                pass
            time.sleep(0.5)

    def _get_terminal_size(self):
        """Get terminal dimensions with caching"""
        try:
            cols, rows = shutil.get_terminal_size()
            # Ensure minimum size
            cols = max(80, cols)
            rows = max(24, rows)
            return cols, rows
        except:
            return 80, 24
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def _center_text(self, text, width, char=' '):
        """Center text within given width"""
        text_len = len(text)
        if text_len >= width:
            return text[:width-3] + '...'
        padding = (width - text_len) // 2
        return char * padding + text + char * (width - text_len - padding)
    
    def _boxed_text(self, text, width=None, height=None, border_color='border',
                    title="", title_color='header', border_style='single', padding=1):
        """Create a boxed text window with responsive sizing"""
        try:
            cols, rows = self._get_terminal_size()
            
            # Calculate responsive dimensions
            if width is None:
                width = min(70, cols - 6)
            if height is None:
                lines = text.count('\n') + 1
                height = lines + padding * 2 + 2
            
            # Ensure minimum dimensions
            width = max(30, min(width, cols - 4))
            height = max(3, min(height, rows - 2))
            
            # Box characters
            if border_style == 'double':
                tl, tr, bl, br, h, v = self.box['tl_d'], self.box['tr_d'], self.box['bl_d'], self.box['br_d'], self.box['h_d'], self.box['v_d']
            elif border_style == 'rounded':
                tl, tr, bl, br, h, v = self.box['tl_r'], self.box['tr_r'], self.box['bl_r'], self.box['br_r'], self.box['h_r'], self.box['v_r']
            else:
                tl, tr, bl, br, h, v = self.box['tl'], self.box['tr'], self.box['bl'], self.box['br'], self.box['h'], self.box['v']
            
            border_color_code = self.colors.get(border_color, self.colors['border'])
            reset = self.colors['reset']
            bold = self.colors['bold']
            
            lines = []
            
            # Top border with title
            if title:
                title_text = f" {bold}{self.colors.get(title_color, self.colors['header'])}{title}{reset}{border_color_code} "
                title_len = len(title_text) - len(border_color_code) - len(reset) - len(bold)
                left_pad = max(1, (width - title_len - 4) // 2)
                right_pad = max(0, width - title_len - left_pad - 4)
                top_line = f"{border_color_code}{tl}{h * left_pad}{title_text}{h * right_pad}{tr}{reset}"
            else:
                top_line = f"{border_color_code}{tl}{h * (width - 2)}{tr}{reset}"
            lines.append(top_line)
            
            # Content
            content_lines = text.split('\n')
            content_height = min(len(content_lines), height - 2)
            
            for i in range(content_height):
                if i < len(content_lines):
                    content = content_lines[i]
                    if len(content) > width - 4:
                        content = content[:width-7] + '...'
                    padded = self._center_text(content, width - 4)
                    lines.append(f"{border_color_code}{v}{reset} {padded} {border_color_code}{v}{reset}")
                else:
                    lines.append(f"{border_color_code}{v}{reset} {' ' * (width - 4)} {border_color_code}{v}{reset}")
            
            # Bottom border
            lines.append(f"{border_color_code}{bl}{h * (width - 2)}{br}{reset}")
            
            return '\n'.join(lines)
        except Exception as e:
            return f"Error creating box: {e}"
    
    def _colored_text(self, text, color='white', bold=False, blink=False):
        """Apply color to text with optional effects"""
        color_code = self.colors.get(color, '')
        bold_code = self.colors['bold'] if bold else ''
        blink_code = self.colors['blink'] if blink else ''
        reset = self.colors['reset']
        return f"{bold_code}{blink_code}{color_code}{text}{reset}"
    
    def _gradient_text(self, text, colors=None):
        """Apply gradient effect to text"""
        if colors is None:
            colors = ['header', 'header2', 'info', 'success']
        result = ""
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            result += self._colored_text(char, color)
        return result
    
    def _progress_bar(self, progress, width=40, color='success'):
        """Create a progress bar with gradient"""
        filled = int(width * progress / 100)
        bar = '█' * filled + '░' * (width - filled)
        if progress < 30:
            bar_color = 'warning'
        elif progress < 70:
            bar_color = 'info'
        else:
            bar_color = 'success'
        return f"[{self._colored_text(bar, bar_color)}] {progress}%"
    
    def _severity_color(self, severity):
        """Get color for severity level"""
        mapping = {
            'CRITICAL': 'error',
            'HIGH': 'warning',
            'MEDIUM': 'warning',
            'LOW': 'info',
            'NORMAL': 'success',
        }
        return mapping.get(severity.upper(), 'white')
    
    def _get_status_icon(self, status):
        """Get icon for status"""
        icons = {
            'running': '🟢',
            'stopped': '🔴',
            'scanning': '🔄',
            'error': '❌',
            'success': '✅',
            'warning': '⚠️',
        }
        return icons.get(status, '●')
    
    def run(self):
        """Main dashboard loop"""
        try:
            # Initial render with error handling
            try:
                self._render_main_menu()
            except Exception as e:
                print(f"Error rendering initial menu: {e}")
                traceback.print_exc()
                input("Press Enter to continue...")
                return
            
            while self.running:
                # Handle input with timeout for responsive updates
                try:
                    if platform.system() == 'Windows':
                        import msvcrt
                        if msvcrt.kbhit():
                            key = msvcrt.getch()
                            if key == b'\xe0':  # Arrow keys
                                key = msvcrt.getch()
                                if key == b'H':  # Up
                                    self.selected_option = (self.selected_option - 1) % len(self.menu_items)
                                    self._render_main_menu()
                                elif key == b'P':  # Down
                                    self.selected_option = (self.selected_option + 1) % len(self.menu_items)
                                    self._render_main_menu()
                            elif key == b'\r':  # Enter
                                if 0 <= self.selected_option < len(self.menu_items):
                                    self.menu_items[self.selected_option][1]()
                            elif key == b'q' or key == b'Q':
                                self.running = False
                                break
                    else:
                        import select
                        import sys
                        if select.select([sys.stdin], [], [], self.update_interval)[0]:
                            key = sys.stdin.read(1)
                            if key == '\x1b':  # Arrow keys
                                sys.stdin.read(1)
                                arrow = sys.stdin.read(1)
                                if arrow == 'A':  # Up
                                    self.selected_option = (self.selected_option - 1) % len(self.menu_items)
                                    self._render_main_menu()
                                elif arrow == 'B':  # Down
                                    self.selected_option = (self.selected_option + 1) % len(self.menu_items)
                                    self._render_main_menu()
                            elif key == '\r':  # Enter
                                if 0 <= self.selected_option < len(self.menu_items):
                                    self.menu_items[self.selected_option][1]()
                            elif key == 'q' or key == 'Q':
                                self.running = False
                                break
                            elif key.isdigit():
                                idx = int(key) - 1
                                if 0 <= idx < len(self.menu_items):
                                    self.selected_option = idx
                                    self.menu_items[idx][1]()
                    
                    # Auto-refresh status if not in a menu
                    if not self.scanning and time.time() - self.last_update > self.update_interval * 4:
                        self._render_main_menu()
                        self.last_update = time.time()
                        
                except Exception as e:
                    # Silently handle input errors
                    pass
                time.sleep(0.05)  # Small delay to prevent CPU spinning
                
        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            print(f"\nDashboard error: {e}")
            traceback.print_exc()
            input("Press Enter to exit...")
        
        self._clear_screen()
        print(f"\n{self._colored_text('👋 Dashboard closed.', 'info')}\n")
    
    def _render_main_menu(self):
        """Render the main menu with responsive layout"""
        try:
            cols, rows = self._get_terminal_size()
            
            # Clear screen
            self._clear_screen()
            
            # Calculate responsive widths
            header_width = min(80, cols - 4)
            status_width = min(70, cols - 4)
            menu_width = min(60, cols - 10)
            
            # Header with gradient
            header_text = self._gradient_text(" DSTERMINAL RANSOMWARE DEFENSE ")
            header = f"""
    {self._colored_text('╔' + '═' * (header_width - 2) + '╗', 'header')}
    {self._colored_text('║', 'header')}{self._center_text(header_text, header_width - 2)}{self._colored_text('║', 'header')}
    {self._colored_text('║', 'header')}{self._center_text(f"Version: 5.0.0 | Session: {self.monitor.session_id[:12]}...", header_width - 2, ' ')}{self._colored_text('║', 'header')}
    {self._colored_text('╚' + '═' * (header_width - 2) + '╝', 'header')}
    """
            print(header)
            
            # Status line with real-time data
            try:
                status = self.monitor.status()
                threat_color = self._severity_color(status['threat_level'])
                status_icon = self._get_status_icon('running' if status['running'] else 'stopped')
                
                # Extract values to avoid nested quote issues
                running = status['running']
                threat_level = status['threat_level']
                risk_score = status['risk_score']
                
                status_line = f"""
    {self._colored_text('┌' + '─' * (status_width - 2) + '┐', 'border')}
    {self._colored_text('│', 'border')}  {status_icon} {self._colored_text('Status:', 'info')} {self._colored_text('ACTIVE' if running else 'STOPPED', 'success' if running else 'error', True)}  │  ⚡ {self._colored_text('Threat:', 'warning')} {self._colored_text(threat_level, threat_color, True)}  │  📊 {self._colored_text(f'Risk: {risk_score}/100', 'info')}  {self._colored_text('│', 'border')}
    {self._colored_text('└' + '─' * (status_width - 2) + '┘', 'border')}
    """
                print(status_line)
            except Exception as e:
                print(f"Error getting status: {e}")
            
            # Menu items with responsive layout
            menu_list = ""
            for i, (label, _) in enumerate(self.menu_items):
                number = f"{i+1}."
                if i == self.selected_option:
                    menu_list += f"  {self._colored_text(f'▶ {number} {label}', 'highlight', True)}\n"
                else:
                    menu_list += f"  {self._colored_text(number, 'dim')} {label}\n"
            
            menu_box = self._boxed_text(
                menu_list.rstrip('\n'), 
                width=menu_width,
                title="📋 MAIN MENU", 
                border_color='border', 
                title_color='header',
                border_style='double'
            )
            print(menu_box)
            
            # Footer with navigation hints
            footer_width = min(70, cols - 4)
            footer = f"""
    {self._colored_text('┌' + '─' * (footer_width - 2) + '┐', 'dim')}
    {self._colored_text('│', 'dim')}  {self._colored_text('⬆/⬇ Navigate  |  ENTER Select  |  Q Exit  |  Number keys: 1-8', 'dim')}  {self._colored_text('│', 'dim')}
    {self._colored_text('└' + '─' * (footer_width - 2) + '┘', 'dim')}
    """
            print(footer)
            
            # Last update time
            update_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n{self._colored_text(f'🔄 Last update: {update_time}', 'dim')}")
            sys.stdout.flush()
        except Exception as e:
            print(f"Error rendering menu: {e}")
            traceback.print_exc()
    
    # ========================================================================
    # MENU FUNCTIONS
    # ========================================================================
    
    def menu_scan(self):
        """System scan menu with progress"""
        try:
            self._clear_screen()
            cols, rows = self._get_terminal_size()
            box_width = min(70, cols - 6)
            
            print(self._boxed_text(
                f"{self._colored_text('🔍 SYSTEM-WIDE RANSOMWARE SCAN', 'header', True)}\n\n"
                "This will scan all user directories for ransomware indicators.\n"
                "The scan is READ-ONLY - no files will be modified.\n",
                width=box_width, title="SYSTEM SCAN", border_color='info', border_style='double'
            ))
            
            print(f"\n{self._colored_text('Press ENTER for full system scan, or enter a specific path:', 'dim')}")
            path_input = input("Path: ").strip()
            target = path_input if path_input else None
            
            self.scanning = True
            self.scan_progress = 0
            self.scan_result = None
            
            def update_progress(percent, message):
                self.scan_progress = percent
                self._render_scan_progress(percent, message)
            
            def run_scan():
                try:
                    result = self.monitor.scan_system(target, deep=True, max_findings=500)
                    self.scan_result = result
                    self.scanning = False
                except Exception as e:
                    self.scan_result = None
                    self.scanning = False
                    self._render_scan_progress(0, f"{self._colored_text(f'ERROR: {e}', 'error')}")
            
            thread = threading.Thread(target=run_scan, daemon=True)
            thread.start()
            
            # Show progress
            while self.scanning:
                time.sleep(0.5)
            
            if self.scan_result:
                self._display_scan_results(self.scan_result)
            
            input(f"\n{self._colored_text('Press ENTER to continue...', 'dim')}")
            self._render_main_menu()
        except Exception as e:
            print(f"Scan error: {e}")
            traceback.print_exc()
            input("Press Enter to continue...")
            self._render_main_menu()
    
    def _render_scan_progress(self, percent, message):
        """Render scan progress with animation"""
        self._clear_screen()
        cols, rows = self._get_terminal_size()
        box_width = min(70, cols - 6)
        
        progress_bar = self._progress_bar(percent, width=40)
        time_str = datetime.now().strftime("%H:%M:%S")
        
        print(self._boxed_text(
            f"{self._colored_text('🔍 SCANNING IN PROGRESS', 'header', True)}\n\n"
            f"{progress_bar}\n\n"
            f"{self._colored_text(f'Status: {message}', 'info')}\n"
            f"{self._colored_text(f'Time: {time_str}', 'dim')}",
            width=box_width, title="SCAN PROGRESS", border_color='info', border_style='double'
        ))
        sys.stdout.flush()
    
    def _display_scan_results(self, result):
        """Display scan results in a formatted box"""
        self._clear_screen()
        cols, rows = self._get_terminal_size()
        box_width = min(80, cols - 6)
        
        threat_color = self._severity_color(result.threat_level)
        threat_icon = self._get_status_icon('success' if result.threat_level == 'NORMAL' else 'warning')
        
        # Summary
        summary = f"""
{self._colored_text('📊 SCAN SUMMARY', 'header', True)}
{'─' * 50}
{self._colored_text('Scan ID:', 'dim')} {result.scan_id}
{self._colored_text('Started:', 'dim')} {result.started_at}
{self._colored_text('Finished:', 'dim')} {result.finished_at}
{self._colored_text('Files Scanned:', 'dim')} {result.files_scanned:,}
{self._colored_text('Directories:', 'dim')} {result.directories_scanned:,}
{self._colored_text('Indicators Found:', 'dim')} {len(result.indicators):,}
{self._colored_text('Risk Score:', 'dim')} {self._colored_text(f'{result.risk_score}/100', threat_color, True)}
{self._colored_text('Threat Level:', 'dim')} {threat_icon} {self._colored_text(result.threat_level, threat_color, True)}
"""
        
        # Indicator breakdown
        if result.indicators:
            indicators = []
            for item in result.indicators[:10]:
                severity = item.get('severity', 'NORMAL')
                color = self._severity_color(severity)
                indicators.append(
                    f"  {self._colored_text('●', color)} {self._colored_text(severity, color)} "
                    f"{item.get('category', '')}/{item.get('indicator_type', '')} "
                    f"{self._colored_text('+' + str(item.get('score', 0)), 'dim')}"
                )
            if len(result.indicators) > 10:
                indicators.append(f"  ... and {len(result.indicators) - 10} more")
            
            summary += f"\n\n{self._colored_text('⚠️ INDICATORS DETECTED', 'warning', True)}\n"
            summary += '\n'.join(indicators)
        else:
            summary += f"\n\n{self._colored_text('✅ NO INDICATORS FOUND', 'success', True)}"
        
        print(self._boxed_text(summary, width=box_width, title="SCAN RESULTS",
                               border_color='info', title_color='header', border_style='double'))
    
    def menu_monitor(self):
        """Real-time monitoring dashboard with live updates"""
        try:
            self._clear_screen()
            cols, rows = self._get_terminal_size()
            
            if not self.monitor.is_running:
                print(self._colored_text("Starting monitoring...", "info"))
                self.monitor.start_monitoring()
                time.sleep(0.5)
            
            # Track last update for live refresh
            last_refresh = time.time()
            refresh_interval = 1.0  # seconds
            
            # Import for non-blocking input
            import sys
            import select
            
            while True:
                # Check for key press (non-blocking)
                if platform.system() == 'Windows':
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch()
                        if key == b'q' or key == b'Q':
                            break
                else:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        if key == 'q' or key == 'Q':
                            break
                
                # Refresh the display
                if time.time() - last_refresh >= refresh_interval:
                    self._clear_screen()
                    status = self.monitor.status()
                    box_width = min(80, cols - 6)
                    
                    # Status header
                    # Extract values first
                    is_running = status['running']
                    threat_level = status['threat_level']
                    risk_score = status['risk_score']
                    threat_color = self._severity_color(threat_level)
                    status_icon = self._get_status_icon('running' if is_running else 'stopped')

                    # Build the header text as a single string
                    header_text = (
                        f"{self._colored_text('📡 REAL-TIME MONITORING', 'header', True)}\n\n"
                        f"{status_icon} {self._colored_text('Status:', 'info')} {self._colored_text('ACTIVE' if is_running else 'STOPPED', 'success' if is_running else 'error', True)}  |  "
                        f"⚡ {self._colored_text('Threat:', 'warning')} {self._colored_text(threat_level, threat_color, True)}  |  "
                        f"📊 {self._colored_text(f'Risk: {risk_score}/100', 'info')}"
                    )
                    # Create the boxed text with the single string
                    header = self._boxed_text(
                        header_text,
                        width=box_width,
                        title="LIVE MONITOR",
                        border_color='header',
                        border_style='double'
                    )
                    print(header)
                    
                    # Stats
                    stats = status['stats']
                    stats_box = self._boxed_text(
                        f"{self._colored_text('📊 ACTIVITY STATISTICS', 'info', True)}\n\n"
                        f"  {self._colored_text('Created:', 'dim')} {stats['files_created']:,}  "
                        f"{self._colored_text('Modified:', 'dim')} {stats['files_modified']:,}  "
                        f"{self._colored_text('Deleted:', 'dim')} {stats['files_deleted']:,}\n"
                        f"  {self._colored_text('Renamed:', 'dim')} {stats['files_renamed']:,}  "
                        f"{self._colored_text('Scanned:', 'dim')} {stats['directories_scanned']:,}  "
                        f"{self._colored_text('Errors:', 'dim')} {stats['errors']:,}",
                        width=box_width, title="STATISTICS", border_color='info', border_style='single'
                    )
                    print(stats_box)
                    
                    # Recent indicators
                    recent = list(self.monitor.indicators)[-8:]
                    if recent:
                        indicator_lines = []
                        for item in recent:
                            color = self._severity_color(item.severity)
                            evidence = item.evidence[:50] + '...' if len(item.evidence) > 50 else item.evidence
                            indicator_lines.append(
                                f"  {self._colored_text('●', color)} {self._colored_text(item.severity, color)} "
                                f"{item.indicator_type}: {evidence}"
                            )
                        indicators_box = self._boxed_text(
                            f"{self._colored_text('⚠️ RECENT INDICATORS', 'warning', True)}\n\n" + '\n'.join(indicator_lines),
                            width=box_width, title="RECENT ALERTS", border_color='warning', border_style='single'
                        )
                        print(indicators_box)
                    else:
                        # Show no indicators message
                        indicators_box = self._boxed_text(
                            f"{self._colored_text('✅ No indicators detected', 'success', True)}",
                            width=box_width, title="RECENT ALERTS", border_color='success', border_style='single'
                        )
                        print(indicators_box)
                    
                    # Footer
                    print(f"\n{self._colored_text('Press Q to stop monitoring', 'dim')}")
                    update_time = datetime.now().strftime("%H:%M:%S")
                    print(f"{self._colored_text(f'⏱️ Last update: {update_time}', 'dim')}")                    
                    sys.stdout.flush()
                    
                    last_refresh = time.time()
                
                time.sleep(0.05)  # Small delay to prevent CPU spinning
                    
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"\n{self._colored_text(f'Monitoring error: {e}', 'error')}")
            traceback.print_exc()
            input(f"\n{self._colored_text('Press ENTER to continue...', 'dim')}")
        
        if self.monitor.is_running:
            self.monitor.stop_monitoring()
        
        self._render_main_menu()

    def menu_indicators(self):
        """Show all indicators in a formatted box"""
        self._clear_screen()
        cols, rows = self._get_terminal_size()
        box_width = min(80, cols - 6)
        
        indicators = list(self.monitor.indicators)
        
        if not indicators:
            print(self._boxed_text(
                f"{self._colored_text('✅ NO INDICATORS DETECTED', 'success', True)}\n\n"
                f"Run a system scan or start monitoring to detect threats.",
                width=box_width, title="INDICATORS", border_color='success', border_style='double'
            ))
        else:
            # Group by severity
            grouped = {}
            for item in indicators:
                severity = item.severity
                if severity not in grouped:
                    grouped[severity] = []
                grouped[severity].append(item)
            
            # Build display
            display = f"{self._colored_text(f'Total Indicators: {len(indicators)}', 'header', True)}\n"
            display += f"{self._colored_text('─' * 50, 'dim')}\n\n"
            
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NORMAL']:
                if severity in grouped:
                    items = grouped[severity]
                    color = self._severity_color(severity)
                    display += f"{self._colored_text(f'● {severity} ({len(items)})', color, True)}\n"
                    
                    for item in items[:5]:
                        display += f"  {self._colored_text('└', 'dim')} {item.indicator_type}: {item.evidence[:60]}\n"
                        if item.path:
                            display += f"    {self._colored_text('→', 'dim')} {Path(item.path).name}\n"
                    
                    if len(items) > 5:
                        display += f"  {self._colored_text(f'... and {len(items) - 5} more', 'dim')}\n"
                    display += "\n"
            
            print(self._boxed_text(display.rstrip('\n'), width=box_width,
                                   title="📋 INDICATORS", border_color='warning',
                                   title_color='header', border_style='double'))
        
        input(f"\n{self._colored_text('Press ENTER to continue...', 'dim')}")
        self._render_main_menu()
    
    def menu_status(self):
        """Display detailed status dashboard"""
        self._clear_screen()
        cols, rows = self._get_terminal_size()
        box_width = min(80, cols - 6)
        
        status = self.monitor.status()
        correlation = self.monitor.get_correlated_risk()
        threat_color = self._severity_color(status['threat_level'])
        
        display = f"""
{self._colored_text('🛡️ SYSTEM STATUS', 'header', True)}
{'─' * 50}

{self._colored_text('Engine:', 'dim')} DSTerminal Ransomware Defense v{VERSION}
{self._colored_text('Session:', 'dim')} {status['session_id']}
{self._colored_text('Host:', 'dim')} {status['hostname']}
{self._colored_text('Platform:', 'dim')} {status['platform']}
{self._colored_text('Running:', 'dim')} {self._colored_text('ACTIVE' if status['running'] else 'STOPPED', 'success' if status['running'] else 'error', True)}
{self._colored_text('Backup Enabled:', 'dim')} {self._colored_text('✅' if status['backup_enabled'] else '❌', 'success' if status['backup_enabled'] else 'error')}
{self._colored_text('Auto Quarantine:', 'dim')} {self._colored_text('⚠️' if status['auto_quarantine'] else '❌', 'warning' if status['auto_quarantine'] else 'dim')}

{self._colored_text('THREAT ASSESSMENT', 'warning', True)}
{'─' * 50}
{self._colored_text('Threat Level:', 'dim')} {self._colored_text(status['threat_level'], threat_color, True)}
{self._colored_text('Risk Score:', 'dim')} {self._colored_text(f'{status["risk_score"]}/100', threat_color, True)}
{self._colored_text('Raw Score:', 'dim')} {status['raw_risk_score']}/100
{self._colored_text('Correlation Bonus:', 'dim')} +{correlation.get('correlation_bonus', 0)}

{self._colored_text('STATISTICS', 'info', True)}
{'─' * 50}
{self._colored_text('Files Scanned:', 'dim')} {status['stats']['files_scanned']:,}
{self._colored_text('Directories:', 'dim')} {status['stats']['directories_scanned']:,}
{self._colored_text('Indicators:', 'dim')} {status['indicators']}
{self._colored_text('Errors:', 'dim')} {status['stats']['errors']:,}

{self._colored_text('BACKUP & QUARANTINE', 'info', True)}
{'─' * 50}
{self._colored_text('Backup Dir:', 'dim')} {status['backup_dir']}
{self._colored_text('Quarantine Dir:', 'dim')} {status['quarantine_dir']}
"""
        
        print(self._boxed_text(display, width=box_width, title="📊 STATUS DASHBOARD",
                               border_color='header', title_color='header', border_style='double'))
        
        input(f"\n{self._colored_text('Press ENTER to continue...', 'dim')}")
        self._render_main_menu()
    
    def menu_quarantine(self):
        """Manage quarantine"""
        self._clear_screen()
        cols, rows = self._get_terminal_size()
        box_width = min(80, cols - 6)
        
        quarantine_dir = self.monitor.quarantine_dir
        
        if not quarantine_dir.exists():
            print(self._boxed_text(
                f"{self._colored_text('📁 Quarantine directory not found', 'warning')}",
                width=box_width, title="QUARANTINE", border_color='warning', border_style='double'
            ))
            input(f"\n{self._colored_text('Press ENTER to continue...', 'dim')}")
            self._render_main_menu()
            return
        
        files = list(quarantine_dir.glob('*'))
        files = [f for f in files if f.is_file() and not f.suffix == '.json']
        
        if not files:
            print(self._boxed_text(
                f"{self._colored_text('📁 No files in quarantine', 'info')}",
                width=box_width, title="QUARANTINE", border_color='info', border_style='double'
            ))
        else:
            display = f"{self._colored_text(f'📁 Quarantined Files ({len(files)})', 'header', True)}\n"
            display += f"{self._colored_text('─' * 50, 'dim')}\n\n"
            
            for i, file in enumerate(files[:15], 1):
                size = file.stat().st_size
                size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
                display += f"  {i}. {self._colored_text(file.name, 'info')} ({size_str})\n"
            
            if len(files) > 15:
                display += f"\n{self._colored_text(f'... and {len(files) - 15} more files', 'dim')}"
            
            print(self._boxed_text(display, width=box_width, title="📁 QUARANTINE",
                                   border_color='warning', title_color='header', border_style='double'))
        
        # Option to quarantine a new file
        print(f"\n{self._colored_text('Enter file path to quarantine (or press ENTER to skip):', 'dim')}")
        path_input = input("Path: ").strip()
        if path_input:
            file_path = Path(path_input)
            if file_path.exists():
                result = self.monitor.quarantine_file(file_path)
                if result:
                    print(f"\n{self._colored_text(f'✅ File quarantined: {result}', 'success')}")
                else:
                    print(f"\n{self._colored_text('❌ Failed to quarantine file', 'error')}")
            else:
                print(f"\n{self._colored_text('❌ File not found', 'error')}")
        
        input(f"\n{self._colored_text('Press ENTER to continue...', 'dim')}")
        self._render_main_menu()
    
    def menu_restore(self):
        """Restore from backup"""
        self._clear_screen()
        cols, rows = self._get_terminal_size()
        box_width = min(80, cols - 6)
        
        backup_dir = self.monitor.backup_dir
        
        if not backup_dir.exists():
            print(self._boxed_text(
                f"{self._colored_text('💾 Backup directory not found', 'warning')}",
                width=box_width, title="RESTORE", border_color='warning', border_style='double'
            ))
            input(f"\n{self._colored_text('Press ENTER to continue...', 'dim')}")
            self._render_main_menu()
            return
        
        files = list(backup_dir.glob('*'))
        files = [f for f in files if f.is_file() and not f.suffix == '.json']
        
        if not files:
            print(self._boxed_text(
                f"{self._colored_text('💾 No backups available', 'info')}",
                width=box_width, title="RESTORE", border_color='info', border_style='double'
            ))
        else:
            display = f"{self._colored_text(f'💾 Available Backups ({len(files)})', 'header', True)}\n"
            display += f"{self._colored_text('─' * 50, 'dim')}\n\n"
            
            for i, file in enumerate(files[:15], 1):
                size = file.stat().st_size
                size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
                meta_file = file.with_suffix(file.suffix + '.json')
                original = ""
                if meta_file.exists():
                    try:
                        meta = json.loads(meta_file.read_text(encoding='utf-8'))
                        original = meta.get('original_path', '')
                        if original:
                            original = f" → {Path(original).name}"
                    except:
                        pass
                display += f"  {i}. {self._colored_text(file.name, 'info')} ({size_str}){original}\n"
            
            if len(files) > 15:
                display += f"\n{self._colored_text(f'... and {len(files) - 15} more files', 'dim')}"
            
            print(self._boxed_text(display, width=box_width, title="💾 RESTORE",
                                   border_color='info', title_color='header', border_style='double'))
        
        # Option to restore
        print(f"\n{self._colored_text('Enter backup filename to restore (or press ENTER to skip):', 'dim')}")
        backup_input = input("Backup: ").strip()
        if backup_input:
            result = self.monitor.restore_backup(backup_input)
            if result:
                print(f"\n{self._colored_text(f'✅ File restored successfully!', 'success')}")
            else:
                print(f"\n{self._colored_text('❌ Failed to restore backup', 'error')}")
        
        input(f"\n{self._colored_text('Press ENTER to continue...', 'dim')}")
        self._render_main_menu()
    
    def menu_export(self):
        """Export report with enhanced HTML/PDF design"""
        self._clear_screen()
        cols, rows = self._get_terminal_size()
        box_width = min(70, cols - 6)
        
        print(self._boxed_text(
            f"{self._colored_text('📄 EXPORT REPORT', 'header', True)}\n\n"
            f"Select report format:\n"
            f"  {self._colored_text('1.', 'dim')} JSON\n"
            f"  {self._colored_text('2.', 'dim')} HTML {self._colored_text('(Enhanced Design)', 'info')}\n"
            f"  {self._colored_text('3.', 'dim')} PDF {self._colored_text('(Enhanced Design)', 'info')}\n"
            f"  {self._colored_text('4.', 'dim')} All Formats\n",
            width=box_width, title="EXPORT", border_color='header', border_style='double'
        ))
        
        choice = input(f"\n{self._colored_text('Select format (1-4): ', 'dim')}").strip()
        formats = {'1': 'json', '2': 'html', '3': 'pdf', '4': 'all'}
        fmt = formats.get(choice, 'html')
        
        try:
            if fmt == 'all':
                for f in ['json', 'html', 'pdf']:
                    result = self.monitor.export_report(f)
                    print(f"{self._colored_text(f'✅ {f.upper()}:', 'success')} {result}")
            else:
                result = self.monitor.export_report(fmt)
                print(f"\n{self._colored_text(f'✅ Report exported:', 'success')} {result}")
        except Exception as e:
            print(f"\n{self._colored_text(f'❌ Export failed: {e}', 'error')}")
        
        input(f"\n{self._colored_text('Press ENTER to continue...', 'dim')}")
        self._render_main_menu()
    
    def menu_exit(self):
        """Exit the dashboard"""
        if self.monitor.is_running:
            self.monitor.stop_monitoring()
        self.running = False


# ============================================================================
# ENHANCED HTML REPORT GENERATOR
# ============================================================================

class EnhancedReportGenerator:
    """Generate beautifully designed HTML and PDF reports"""
    
    @staticmethod
    def generate_html_report(monitor, target_path: Optional[Path] = None) -> str:
        """Generate a modern, responsive HTML report"""
        import html
        status = monitor.status()
        indicators = list(monitor.indicators)
        
        if target_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_path = monitor.report_dir / f"ransomware_report_{timestamp}.html"
        
        threat_color = {
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107',
            'LOW': '#28a745',
            'NORMAL': '#6c757d'
        }.get(status['threat_level'], '#6c757d')
        
        # Build indicator rows
        indicator_rows = ""
        for item in indicators[-200:]:
            severity = item.severity
            severity_class = severity.lower()
            indicator_rows += f"""
            <tr class="severity-{severity_class}">
                <td>{item.timestamp[:19]}</td>
                <td><span class="badge badge-{severity_class}">{severity}</span></td>
                <td>{item.category}</td>
                <td>{item.indicator_type}</td>
                <td>{item.score}</td>
                <td class="path-cell">{html.escape(str(item.path)[:60])}</td>
                <td>{html.escape(str(item.evidence)[:80])}</td>
            </tr>
            """
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSTerminal Ransomware Report</title>
    <style>
        :root {{
            --primary: #0a1628;
            --secondary: #1a2a4a;
            --accent: #00d4ff;
            --accent2: #7b2ffc;
            --text: #e8e8e8;
            --text-dim: #8899bb;
            --border: #2a3a5a;
            --card-bg: #0d1b2a;
            --shadow: 0 8px 32px rgba(0,0,0,0.4);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            background: var(--primary);
            color: var(--text);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
            overflow: hidden;
            padding: 30px;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            border-left: 4px solid var(--accent);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header .meta {{
            text-align: right;
            font-size: 13px;
            color: var(--text-dim);
        }}
        
        .header .meta span {{
            display: block;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: var(--secondary);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            transition: transform 0.2s, border-color 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
        }}
        
        .card .label {{
            font-size: 12px;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .card .value {{
            font-size: 24px;
            font-weight: 700;
        }}
        
        .card .value.threat-critical {{ color: #dc3545; }}
        .card .value.threat-high {{ color: #fd7e14; }}
        .card .value.threat-medium {{ color: #ffc107; }}
        .card .value.threat-low {{ color: #28a745; }}
        .card .value.threat-normal {{ color: #6c757d; }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: var(--accent);
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        
        thead {{
            background: var(--secondary);
        }}
        
        th {{
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            color: var(--accent);
            border-bottom: 2px solid var(--border);
            position: sticky;
            top: 0;
            background: var(--secondary);
        }}
        
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
        }}
        
        tr:hover {{
            background: rgba(0, 212, 255, 0.05);
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge-critical {{ background: #dc3545; color: white; }}
        .badge-high {{ background: #fd7e14; color: white; }}
        .badge-medium {{ background: #ffc107; color: #1a1a2e; }}
        .badge-low {{ background: #28a745; color: white; }}
        .badge-normal {{ background: #6c757d; color: white; }}
        
        .severity-critical {{ border-left: 4px solid #dc3545; }}
        .severity-high {{ border-left: 4px solid #fd7e14; }}
        .severity-medium {{ border-left: 4px solid #ffc107; }}
        .severity-low {{ border-left: 4px solid #28a745; }}
        .severity-normal {{ border-left: 4px solid #6c757d; }}
        
        .path-cell {{
            font-family: 'Consolas', monospace;
            font-size: 12px;
            color: var(--text-dim);
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-dim);
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .status-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        
        .status-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }}
        
        .status-dot.active {{ background: #28a745; }}
        .status-dot.inactive {{ background: #dc3545; }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 16px; }}
            .header {{ flex-direction: column; text-align: center; }}
            .header .meta {{ text-align: center; }}
            .grid {{ grid-template-columns: repeat(2, 1fr); }}
            th, td {{ padding: 8px 10px; font-size: 12px; }}
            .path-cell {{ max-width: 120px; }}
        }}
        
        @media (max-width: 480px) {{
            .grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <h1>🛡️ DSTerminal Ransomware Defense</h1>
            <div style="margin-top: 8px; color: var(--text-dim); font-size: 14px;">
                <span class="status-indicator">
                    <span class="status-dot {'active' if status['running'] else 'inactive'}"></span>
                    {'ACTIVE' if status['running'] else 'STOPPED'}
                </span>
                · Threat Level: <strong style="color: {threat_color};">{status['threat_level']}</strong>
                · Risk Score: <strong style="color: {threat_color};">{status['risk_score']}/100</strong>
            </div>
        </div>
        <div class="meta">
            <span>Report ID: {status['session_id']}</span>
            <span>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            <span>Host: {status['hostname']}</span>
        </div>
    </div>
    
    <div class="grid">
        <div class="card">
            <div class="label">🔍 Files Scanned</div>
            <div class="value">{status['stats']['files_scanned']:,}</div>
        </div>
        <div class="card">
            <div class="label">⚠️ Indicators</div>
            <div class="value">{len(indicators):,}</div>
        </div>
        <div class="card">
            <div class="label">📊 Risk Score</div>
            <div class="value threat-{status['threat_level'].lower()}">{status['risk_score']}/100</div>
        </div>
        <div class="card">
            <div class="label">🚨 Threat Level</div>
            <div class="value threat-{status['threat_level'].lower()}">{status['threat_level']}</div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">📊 Activity Statistics</div>
        <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
            <div class="card"><div class="label">Created</div><div class="value">{status['stats']['files_created']:,}</div></div>
            <div class="card"><div class="label">Modified</div><div class="value">{status['stats']['files_modified']:,}</div></div>
            <div class="card"><div class="label">Deleted</div><div class="value">{status['stats']['files_deleted']:,}</div></div>
            <div class="card"><div class="label">Renamed</div><div class="value">{status['stats']['files_renamed']:,}</div></div>
            <div class="card"><div class="label">Suspicious Processes</div><div class="value">{status['stats']['suspicious_processes']:,}</div></div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">⚠️ Indicators ({len(indicators)})</div>
        {f'<div class="table-wrapper"><table><thead><tr><th>Time</th><th>Severity</th><th>Category</th><th>Indicator</th><th>Score</th><th>Path</th><th>Evidence</th></tr></thead><tbody>{indicator_rows}</tbody></table></div>' if indicators else '<p style="color: var(--text-dim);">No indicators detected.</p>'}
    </div>
    
    <div class="footer">
        <span>DSTerminal v{VERSION} · Ransomware Detection Engine</span>
        <span>🔒 Defensive-only · READ-ONLY scanning</span>
    </div>
</div>
</body>
</html>'''
        
        target_path.write_text(html_content, encoding='utf-8')
        return str(target_path)
    
    @staticmethod
    def generate_pdf_report(monitor, target_path: Optional[Path] = None) -> str:
        """Generate a beautifully designed PDF report"""
        if not REPORTLAB_AVAILABLE:
            print("PDF export requires reportlab: pip install reportlab")
            return None
        
        if target_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_path = monitor.report_dir / f"ransomware_report_{timestamp}.pdf"
        
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        
        doc = SimpleDocTemplate(
            str(target_path),
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
            title="DSTerminal Ransomware Report",
            author="DSTerminal Defense System",
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#0a1628'),
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_CENTER,
            spaceAfter=12,
        )
        
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a2a4a'),
            spaceAfter=10,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        )
        
        metric_style = ParagraphStyle(
            'Metric',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_CENTER,
        )
        
        value_style = ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#0a1628'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        story = []
        
        # Title
        story.append(Paragraph("DSTerminal Ransomware Defense Report", title_style))
        story.append(Spacer(1, 6))
        
        # Metadata
        status = monitor.status()
        story.append(Paragraph(
            f"Report ID: {status['session_id']} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            subtitle_style
        ))
        story.append(Spacer(1, 16))
        
        # Status header with color
        threat_color = {
            'CRITICAL': colors.HexColor('#dc3545'),
            'HIGH': colors.HexColor('#fd7e14'),
            'MEDIUM': colors.HexColor('#ffc107'),
            'LOW': colors.HexColor('#28a745'),
            'NORMAL': colors.HexColor('#6c757d')
        }.get(status['threat_level'], colors.HexColor('#6c757d'))
        
        header_data = [
            [Paragraph(f"<b>Status:</b> {'ACTIVE' if status['running'] else 'STOPPED'}", styles['Normal'])],
            [Paragraph(f"<b>Threat Level:</b> <font color='{threat_color.hexval()}'>{status['threat_level']}</font>", styles['Normal'])],
            [Paragraph(f"<b>Risk Score:</b> <font color='{threat_color.hexval()}'>{status['risk_score']}/100</font>", styles['Normal'])],
            [Paragraph(f"<b>Host:</b> {status['hostname']}", styles['Normal'])],
        ]
        header_table = Table(header_data, colWidths=[6*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a2a4a')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a2a4a')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Metrics Grid
        metrics_data = [
            [
                Paragraph("Files Scanned", metric_style),
                Paragraph("Indicators", metric_style),
                Paragraph("Risk Score", metric_style),
                Paragraph("Threat Level", metric_style),
            ],
            [
                Paragraph(f"<b>{status['stats']['files_scanned']:,}</b>", value_style),
                Paragraph(f"<b>{len(monitor.indicators):,}</b>", value_style),
                Paragraph(f"<b>{status['risk_score']}/100</b>", value_style),
                Paragraph(f"<b>{status['threat_level']}</b>", value_style),
            ],
        ]
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#0a1628')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Statistics
        story.append(Paragraph("Activity Statistics", section_style))
        stats_data = [
            ['Metric', 'Value'],
            ['Files Created', str(status['stats']['files_created'])],
            ['Files Modified', str(status['stats']['files_modified'])],
            ['Files Deleted', str(status['stats']['files_deleted'])],
            ['Files Renamed', str(status['stats']['files_renamed'])],
            ['Suspicious Processes', str(status['stats']['suspicious_processes'])],
            ['Directories Scanned', str(status['stats']['directories_scanned'])],
            ['Errors', str(status['stats']['errors'])],
        ]
        stats_table = Table(stats_data, colWidths=[2.5*inch, 3.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 16))
        
        # Indicators
        indicators = list(monitor.indicators)
        if indicators:
            story.append(Paragraph(f"Indicators ({len(indicators)})", section_style))
            
            indicator_data = [
                ['Time', 'Severity', 'Category', 'Indicator', 'Score']
            ]
            for item in indicators[-50:]:
                indicator_data.append([
                    item.timestamp[:19],
                    item.severity,
                    item.category,
                    item.indicator_type,
                    str(item.score)
                ])
            
            indicator_table = Table(indicator_data, colWidths=[1.2*inch, 0.8*inch, 1.2*inch, 1.5*inch, 0.6*inch])
            indicator_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2a4a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(indicator_table)
        else:
            story.append(Paragraph("No indicators detected.", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_CENTER,
            spaceBefore=16,
        )
        story.append(Paragraph(f"Generated by DSTerminal v{VERSION} · Ransomware Detection Engine", footer_style))
        story.append(Paragraph(f"Report ID: {status['session_id']} · Defensive-only · READ-ONLY scanning", footer_style))
        
        doc.build(story)
        return str(target_path)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point with dashboard"""
    try:
        # Create a minimal monitor instance
        class MinimalMonitor:
            def __init__(self):
                self.session_id = "RANSOM-TEST"
                self.is_running = False
                self.indicators = []
                self.quarantine_dir = Path.home() / "DSTerminal" / "ransomware" / "quarantine"
                self.backup_dir = Path.home() / "DSTerminal" / "ransomware" / "backups"
                self.report_dir = Path.home() / "DSTerminal" / "ransomware" / "reports"
                self.auto_quarantine = False
                self.backup_enabled = True
                self.raw_risk_score = 0
                self.risk_score = 0
                self.threat_level = "NORMAL"
                self._indicator_counter = 0
                self._event_counter = 0
                self.stats = {
                    'files_created': 0,
                    'files_modified': 0,
                    'files_deleted': 0,
                    'files_renamed': 0,
                    'suspicious_processes': 0,
                    'files_scanned': 0,
                    'directories_scanned': 0,
                    'errors': 0,
                    'alerts_triggered': 0,
                    'total_scans': 0,
                }
                self._generate_fake_indicators()
            
            def _generate_fake_indicators(self):
                """Generate fake indicators for testing the dashboard"""
                import random
                
                # Create some fake indicators
                indicator_types = [
                    ('suspicious_extension', 'HIGH', '.encrypted file detected'),
                    ('ransom_note_filename', 'HIGH', 'README.txt detected'),
                    ('abnormal_file_modification_rate', 'MEDIUM', '150 files modified in 60 seconds'),
                    ('mass_file_deletion', 'HIGH', '80 files deleted in 60 seconds'),
                    ('known_ransomware_name', 'CRITICAL', 'wannacry.exe detected'),
                    ('suspicious_script_activity', 'MEDIUM', 'powershell with suspicious args'),
                    ('recovery_or_security_tampering_command', 'CRITICAL', 'vssadmin delete shadows'),
                    ('suspicious_persistence_entry', 'MEDIUM', 'scheduled task found'),
                ]
                
                categories = ['process', 'filesystem', 'ransom_note', 'behavior', 'recovery', 'persistence']
                
                for i in range(5):
                    ind_type, severity, evidence = random.choice(indicator_types)
                    category = random.choice(categories)
                    indicator = Indicator(
                        timestamp=datetime.now().isoformat(),
                        category=category,
                        indicator_type=ind_type,
                        severity=severity,
                        score=random.randint(5, 35),
                        path=f"C:\\Users\\test\\{random.choice(['file1.txt', 'file2.docx', 'image.png', 'data.xlsx'])}",
                        process=random.choice(['svchost.exe', 'powershell.exe', 'cmd.exe', 'wannacry.exe']),
                        pid=random.randint(1000, 9999),
                        evidence=evidence,
                        recommendation="Investigate immediately",
                        confidence=random.choice(['LOW', 'MEDIUM', 'HIGH'])
                    )
                    self.indicators.append(indicator)
                
                # Add some recent events
                event_types = ['created', 'modified', 'deleted', 'renamed']
                for i in range(20):
                    event = FileEvent(
                        timestamp=datetime.now().isoformat(),
                        event_type=random.choice(event_types),
                        path=f"C:\\Users\\test\\{random.choice(['file1.txt', 'file2.docx', 'image.png', 'data.xlsx'])}",
                        size=random.randint(1024, 1048576),
                        extension=random.choice(['.txt', '.docx', '.png', '.xlsx']),
                        suspicious=random.choice([True, False])
                    )
                    if event.event_type == 'created':
                        self.stats['files_created'] += 1
                    elif event.event_type == 'modified':
                        self.stats['files_modified'] += 1
                    elif event.event_type == 'deleted':
                        self.stats['files_deleted'] += 1
                    elif event.event_type == 'renamed':
                        self.stats['files_renamed'] += 1
                
                # Add some scanned files
                self.stats['files_scanned'] = random.randint(1000, 5000)
                self.stats['directories_scanned'] = random.randint(100, 500)
                self.stats['alerts_triggered'] = random.randint(5, 20)
                self.stats['total_scans'] = random.randint(1, 5)
            
            def status(self):
                return {
                    'running': self.is_running,
                    'threat_level': self.threat_level,
                    'risk_score': self.risk_score,
                    'session_id': self.session_id,
                    'hostname': socket.gethostname(),
                    'platform': platform.platform(),
                    'stats': self.stats,
                    'indicators': len(self.indicators),
                    'backup_enabled': self.backup_enabled,
                    'auto_quarantine': self.auto_quarantine,
                    'backup_dir': str(self.backup_dir),
                    'quarantine_dir': str(self.quarantine_dir),
                    'raw_risk_score': self.raw_risk_score,
                }
            
            def get_correlated_risk(self):
                return {'correlation_bonus': 0}
            
            def start_monitoring(self):
                self.is_running = True
                # Generate some activity while monitoring
                import threading
                def generate_activity():
                    import random
                    while self.is_running:
                        # Randomly add indicators
                        if random.random() < 0.3:
                            indicator_types = [
                                ('suspicious_extension', 'HIGH', '.encrypted file detected'),
                                ('ransom_note_filename', 'HIGH', 'README.txt detected'),
                                ('abnormal_file_modification_rate', 'MEDIUM', '150 files modified in 60 seconds'),
                                ('mass_file_deletion', 'HIGH', '80 files deleted in 60 seconds'),
                            ]
                            ind_type, severity, evidence = random.choice(indicator_types)
                            indicator = Indicator(
                                timestamp=datetime.now().isoformat(),
                                category=random.choice(['process', 'filesystem', 'ransom_note']),
                                indicator_type=ind_type,
                                severity=severity,
                                score=random.randint(5, 35),
                                path=f"C:\\Users\\test\\{random.choice(['file1.txt', 'file2.docx'])}",
                                process=random.choice(['svchost.exe', 'powershell.exe']),
                                pid=random.randint(1000, 9999),
                                evidence=evidence,
                                recommendation="Investigate immediately",
                                confidence=random.choice(['LOW', 'MEDIUM', 'HIGH'])
                            )
                            self.indicators.append(indicator)
                            
                            # Update stats
                            self.stats['alerts_triggered'] += 1
                            self.risk_score = min(100, self.risk_score + random.randint(1, 5))
                        
                        time.sleep(2)
                
                thread = threading.Thread(target=generate_activity, daemon=True)
                thread.start()
                return True
            
            def stop_monitoring(self):
                self.is_running = False
                return True
            
            def scan_system(self, target=None, deep=True, max_findings=500):
                import time
                time.sleep(2)
                from types import SimpleNamespace
                result = SimpleNamespace()
                result.scan_id = "SCAN-001"
                result.started_at = datetime.now().isoformat()
                result.finished_at = datetime.now().isoformat()
                result.files_scanned = self.stats['files_scanned']
                result.directories_scanned = self.stats['directories_scanned']
                result.indicators = [asdict(x) for x in self.indicators[:10]]
                result.risk_score = self.risk_score
                result.threat_level = self.threat_level
                return result
            
            def quarantine_file(self, path):
                return path
            
            def restore_backup(self, backup_name):
                return True
            
            def export_report(self, fmt):
                # Create a fake report path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if fmt == "json":
                    return f"ransomware_report_{timestamp}.json"
                elif fmt == "html":
                    return EnhancedReportGenerator.generate_html_report(self)
                elif fmt == "pdf":
                    return EnhancedReportGenerator.generate_pdf_report(self)
                return f"ransomware_report_{timestamp}.{fmt}"

        # Create monitor and dashboard instances
        print("Initializing monitor...")
        monitor = MinimalMonitor()
        
        print("Initializing dashboard...")
        dashboard = EnhancedDashboard(monitor)
        
        print("Starting dashboard...")
        dashboard.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()