#!/usr/bin/env python3
"""
DSTerminal Module Lister - Hacker Style Interactive Module Browser
Pure hardcoded list of DSTerminal integrated modules
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Tuple
import re

# Colors for hacker theme
class Colors:
    """ANSI color codes for hacker theme"""
    # Main colors
    GREEN = '\033[92m'
    DARK_GREEN = '\033[32m'
    LIGHT_GREEN = '\033[92m'
    BRIGHT_GREEN = '\033[92m'
    RED = '\033[91m'
    DARK_RED = '\033[31m'
    BRIGHT_RED = '\033[91m'
    CYAN = '\033[96m'
    DARK_CYAN = '\033[36m'
    BRIGHT_CYAN = '\033[96m'
    BLUE = '\033[94m'
    DARK_BLUE = '\033[34m'
    BRIGHT_BLUE = '\033[94m'
    PURPLE = '\033[95m'
    DARK_PURPLE = '\033[35m'
    BRIGHT_PURPLE = '\033[95m'
    YELLOW = '\033[93m'
    DARK_YELLOW = '\033[33m'
    BRIGHT_YELLOW = '\033[93m'
    WHITE = '\033[97m'
    DARK_WHITE = '\033[37m'
    BRIGHT_WHITE = '\033[97m'
    BLACK = '\033[30m'
    
    # Special
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    
    # Backgrounds
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_PURPLE = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'
    
    # Reset
    RESET = '\033[0m'

class ModuleManager:
    """Manages hardcoded DSTerminal modules"""
    
    def __init__(self):
        self.modules = []
        self.load_hardcoded_modules()
    
    def load_hardcoded_modules(self):
        """Load hardcoded list of DSTerminal modules"""
        self.modules = []
        
        # ============================================================
        # CORE MODULES - Essential DSTerminal components
        # ============================================================
        core_modules = [
            {
                'name': 'DSTerminal Core',
                'key': 'core',
                'description': 'Main terminal engine and command processor',
                'category': 'Core',
                'status': 'âœ“',
                'version': '4.0.0.113',
                'dependencies': ['Python 3.11+', 'psutil'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Command Parser',
                'key': 'parser',
                'description': 'Parse and execute terminal commands with argument handling',
                'category': 'Core',
                'status': 'âœ“',
                'version': '2.0.0',
                'dependencies': ['argparse', 'shlex'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Shell Integration',
                'key': 'shell',
                'description': 'Windows PowerShell and CMD integration layer',
                'category': 'Core',
                'status': 'âœ“',
                'version': '1.5.0',
                'dependencies': ['subprocess', 'os'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'File System Manager',
                'key': 'fs',
                'description': 'File and directory operations with advanced features',
                'category': 'Core',
                'status': 'âœ“',
                'version': '2.1.0',
                'dependencies': ['os', 'shutil', 'pathlib'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Network Utilities',
                'key': 'network',
                'description': 'Networking tools, diagnostics, and port scanning',
                'category': 'Core',
                'status': 'âœ“',
                'version': '1.8.0',
                'dependencies': ['socket', 'netifaces', 'requests'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Security Module',
                'key': 'security',
                'description': 'Encryption, hashing, and security features',
                'category': 'Core',
                'status': 'âœ“',
                'version': '2.0.0',
                'dependencies': ['cryptography', 'hashlib', 'secrets'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'UI Renderer',
                'key': 'ui',
                'description': 'Terminal UI rendering engine with animations',
                'category': 'Core',
                'status': 'âœ“',
                'version': '1.9.0',
                'dependencies': ['curses', 'colorama', 'rich'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Plugin Manager',
                'key': 'plugins',
                'description': 'Plugin system for extensions and third-party modules',
                'category': 'Core',
                'status': 'âœ“',
                'version': '1.5.0',
                'dependencies': ['importlib', 'pkgutil'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Logging System',
                'key': 'logs',
                'description': 'Event logging, debugging, and audit trails',
                'category': 'Core',
                'status': 'âœ“',
                'version': '1.4.0',
                'dependencies': ['logging', 'traceback'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Configuration Manager',
                'key': 'config',
                'description': 'Settings management with JSON/YAML support',
                'category': 'Core',
                'status': 'âœ“',
                'version': '1.6.0',
                'dependencies': ['json', 'yaml', 'toml'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Terminal Emulator',
                'key': 'terminal',
                'description': 'VT100/xterm terminal emulation engine',
                'category': 'Core',
                'status': 'âœ“',
                'version': '2.0.0',
                'dependencies': ['pty', 'select', 'termios'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Process Manager',
                'key': 'process',
                'description': 'Process management and monitoring tools',
                'category': 'Core',
                'status': 'âœ“',
                'version': '1.3.0',
                'dependencies': ['psutil', 'subprocess', 'signal'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Task Scheduler',
                'key': 'scheduler',
                'description': 'Automated task scheduling and cron-like functionality',
                'category': 'Core',
                'status': 'âœ“',
                'version': '1.2.0',
                'dependencies': ['schedule', 'apscheduler'],
                'color': Colors.DARK_GREEN
            },
            {
                'name': 'Notification System',
                'key': 'notify',
                'description': 'System notifications and alerts engine',
                'category': 'Core',
                'status': 'âœ“',
                'version': '1.0.0',
                'dependencies': ['plyer', 'win10toast'],
                'color': Colors.DARK_GREEN
            }
        ]
        
        # ============================================================
        # EXTENDED MODULES - Additional functionality
        # ============================================================
        extended_modules = [
            {
                'name': 'Folium Maps',
                'key': 'folium',
                'description': 'Interactive map generation and visualization',
                'category': 'Extended',
                'status': 'âœ“',
                'version': '0.15.0',
                'dependencies': ['folium', 'branca', 'geojson'],
                'color': Colors.DARK_CYAN
            },
            {
                'name': 'Plotly Charts',
                'key': 'plotly',
                'description': 'Advanced data visualization and interactive charts',
                'category': 'Extended',
                'status': 'âœ“',
                'version': '5.18.0',
                'dependencies': ['plotly', 'kaleido', 'pandas'],
                'color': Colors.DARK_CYAN
            },
            {
                'name': 'Branca Color Maps',
                'key': 'branca',
                'description': 'Color map generation and management for visualizations',
                'category': 'Extended',
                'status': 'âœ“',
                'version': '1.0.0',
                'dependencies': ['branca', 'jinja2'],
                'color': Colors.DARK_CYAN
            },
            {
                'name': 'Netifaces',
                'key': 'netifaces',
                'description': 'Network interface detection and management',
                'category': 'Extended',
                'status': 'âœ“',
                'version': '0.11.0',
                'dependencies': ['netifaces'],
                'color': Colors.DARK_CYAN
            },
            {
                'name': 'JSON Schema',
                'key': 'jsonschema',
                'description': 'JSON validation and schema handling',
                'category': 'Extended',
                'status': 'âœ“',
                'version': '4.20.0',
                'dependencies': ['jsonschema', 'referencing'],
                'color': Colors.DARK_CYAN
            },
            {
                'name': 'Web Encodings',
                'key': 'webencodings',
                'description': 'Character encoding detection and conversion',
                'category': 'Extended',
                'status': 'âœ“',
                'version': '0.5.1',
                'dependencies': ['webencodings'],
                'color': Colors.DARK_CYAN
            },
            {
                'name': 'Fast JSON Schema',
                'key': 'fastjsonschema',
                'description': 'High-performance JSON schema validator',
                'category': 'Extended',
                'status': 'âœ“',
                'version': '2.19.0',
                'dependencies': ['fastjsonschema'],
                'color': Colors.DARK_CYAN
            },
            {
                'name': 'Package Management',
                'key': 'pip',
                'description': 'Python package management and installation',
                'category': 'Extended',
                'status': 'âœ“',
                'version': '24.0',
                'dependencies': ['pip', 'setuptools'],
                'color': Colors.DARK_CYAN
            },
            {
                'name': 'Virtual Environment',
                'key': 'venv',
                'description': 'Python virtual environment management',
                'category': 'Extended',
                'status': 'âœ“',
                'version': '1.0.0',
                'dependencies': ['venv', 'virtualenv'],
                'color': Colors.DARK_CYAN
            }
        ]
        
        # ============================================================
        # TOOL MODULES - Utility and helper modules
        # ============================================================
        tool_modules = [
            {
                'name': 'Text Processing',
                'key': 'text',
                'description': 'Advanced text manipulation and processing tools',
                'category': 'Tools',
                'status': 'âœ“',
                'version': '1.2.0',
                'dependencies': ['re', 'string', 'textwrap'],
                'color': Colors.DARK_PURPLE
            },
            {
                'name': 'Data Processing',
                'key': 'data',
                'description': 'Data manipulation, CSV, JSON, XML handling',
                'category': 'Tools',
                'status': 'âœ“',
                'version': '1.1.0',
                'dependencies': ['csv', 'json', 'xml'],
                'color': Colors.DARK_PURPLE
            },
            {
                'name': 'System Monitoring',
                'key': 'sysmon',
                'description': 'System resource monitoring and performance metrics',
                'category': 'Tools',
                'status': 'âœ“',
                'version': '1.0.0',
                'dependencies': ['psutil', 'platform', 'cpuinfo'],
                'color': Colors.DARK_PURPLE
            },
            {
                'name': 'Automation Engine',
                'key': 'auto',
                'description': 'Task automation and scripting engine',
                'category': 'Tools',
                'status': 'âœ“',
                'version': '1.3.0',
                'dependencies': ['schedule', 'apscheduler'],
                'color': Colors.DARK_PURPLE
            },
            {
                'name': 'Report Generator',
                'key': 'reports',
                'description': 'PDF, HTML, and Markdown report generation',
                'category': 'Tools',
                'status': 'âœ“',
                'version': '1.0.0',
                'dependencies': ['reportlab', 'markdown', 'jinja2'],
                'color': Colors.DARK_PURPLE
            },
            {
                'name': 'Clipboard Manager',
                'key': 'clip',
                'description': 'System clipboard operations and history',
                'category': 'Tools',
                'status': 'âœ“',
                'version': '1.0.0',
                'dependencies': ['pyperclip', 'win32clipboard'],
                'color': Colors.DARK_PURPLE
            },
            {
                'name': 'File Converter',
                'key': 'convert',
                'description': 'File format conversion tools',
                'category': 'Tools',
                'status': 'âœ“',
                'version': '1.0.0',
                'dependencies': ['pillow', 'pypdf', 'python-docx'],
                'color': Colors.DARK_PURPLE
            },
            {
                'name': 'Archive Manager',
                'key': 'archive',
                'description': 'Compression and archive management',
                'category': 'Tools',
                'status': 'âœ“',
                'version': '1.0.0',
                'dependencies': ['zipfile', 'tarfile', 'py7zr'],
                'color': Colors.DARK_PURPLE
            }
        ]
        
        # ============================================================
        # COMMUNITY MODULES - Third-party integrations
        # ============================================================
        community_modules = [
            {
                'name': 'Git Integration',
                'key': 'git',
                'description': 'Git version control operations and management',
                'category': 'Community',
                'status': 'â˜…',
                'version': '1.0.0',
                'dependencies': ['gitpython', 'pygit2'],
                'color': Colors.DARK_YELLOW
            },
            {
                'name': 'Docker Manager',
                'key': 'docker',
                'description': 'Docker container management and orchestration',
                'category': 'Community',
                'status': 'â˜…',
                'version': '1.0.0',
                'dependencies': ['docker', 'docker-compose'],
                'color': Colors.DARK_YELLOW
            },
            {
                'name': 'Kubernetes Tools',
                'key': 'k8s',
                'description': 'Kubernetes cluster management and monitoring',
                'category': 'Community',
                'status': 'â˜…',
                'version': '1.0.0',
                'dependencies': ['kubernetes', 'kubectl'],
                'color': Colors.DARK_YELLOW
            },
            {
                'name': 'Database Connector',
                'key': 'db',
                'description': 'Database connections for SQL, MongoDB, Redis',
                'category': 'Community',
                'status': 'â˜…',
                'version': '1.0.0',
                'dependencies': ['sqlalchemy', 'pymongo', 'redis'],
                'color': Colors.DARK_YELLOW
            },
            {
                'name': 'Cloud Integration',
                'key': 'cloud',
                'description': 'AWS, Azure, GCP cloud service integration',
                'category': 'Community',
                'status': 'â˜…',
                'version': '1.0.0',
                'dependencies': ['boto3', 'azure', 'google-cloud'],
                'color': Colors.DARK_YELLOW
            },
            {
                'name': 'DevOps Tools',
                'key': 'devops',
                'description': 'DevOps automation and CI/CD integration',
                'category': 'Community',
                'status': 'â˜…',
                'version': '1.0.0',
                'dependencies': ['jenkins', 'github', 'gitlab'],
                'color': Colors.DARK_YELLOW
            },
            {
                'name': 'Machine Learning',
                'key': 'ml',
                'description': 'Machine learning and AI integration',
                'category': 'Community',
                'status': 'â˜…',
                'version': '1.0.0',
                'dependencies': ['tensorflow', 'pytorch', 'scikit-learn'],
                'color': Colors.DARK_YELLOW
            },
            {
                'name': 'Data Science',
                'key': 'ds',
                'description': 'Data science and analytics tools',
                'category': 'Community',
                'status': 'â˜…',
                'version': '1.0.0',
                'dependencies': ['pandas', 'numpy', 'scipy'],
                'color': Colors.DARK_YELLOW
            }
        ]
        
        # Combine all modules
        all_modules = core_modules + extended_modules + tool_modules + community_modules
        
        # Add all modules to the list
        for module in all_modules:
            self.modules.append(module)
    
    def get_modules_by_category(self, category: str = None):
        """Get modules filtered by category"""
        if category:
            return [m for m in self.modules if m['category'].lower() == category.lower()]
        return self.modules
    
    def search_modules(self, search_term: str):
        """Search modules by name, key, or description"""
        search_term = search_term.lower()
        return [m for m in self.modules if 
                search_term in m['name'].lower() or 
                search_term in m['key'].lower() or 
                search_term in m['description'].lower()]

class HackerUI:
    """Hacker-style UI renderer"""
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def draw_border(width: int = 80, color: str = Colors.DARK_GREEN, 
                    top: str = "â•", bottom: str = "â•", 
                    left: str = "â•‘", right: str = "â•‘",
                    corner_tl: str = "â•”", corner_tr: str = "â•—",
                    corner_bl: str = "â•š", corner_br: str = "â•"):
        """Draw a border with custom characters"""
        print(f"{color}{corner_tl}{top * (width - 2)}{corner_tr}{Colors.RESET}")
        return {"color": color, "left": left, "right": right, 
                "width": width, "top": top, "bottom": bottom,
                "corner_tl": corner_tl, "corner_tr": corner_tr,
                "corner_bl": corner_bl, "corner_br": corner_br}
    
    @staticmethod
    def draw_line(text: str, border, centered: bool = False, 
                  pad_left: int = 2, pad_right: int = 2):
        """Draw a line within the border"""
        width = border["width"]
        left = border["left"]
        right = border["right"]
        color = border["color"]
        
        # Remove ANSI codes for length calculation
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        
        if centered:
            text_len = len(clean_text)
            total_padding = width - text_len - 4
            pad_left = total_padding // 2
            pad_right = total_padding - pad_left
        
        line = f"{color}{left}{Colors.RESET}"
        line += " " * pad_left
        line += text
        line += " " * pad_right
        line += f"{color}{right}{Colors.RESET}"
        print(line)
    
    @staticmethod
    def draw_header(title: str):
        """Draw the main header"""
        border = HackerUI.draw_border(80, Colors.DARK_GREEN)
        
        HackerUI.draw_line("", border)
        title_text = f"{Colors.BOLD}{Colors.DARK_GREEN}â–“â–“â–“â–“â–“ {Colors.BRIGHT_GREEN}{title}{Colors.DARK_GREEN} â–“â–“â–“â–“â–“{Colors.RESET}"
        HackerUI.draw_line(title_text, border, centered=True)
        HackerUI.draw_line("", border)
        subtext = f"{Colors.DIM}DSTerminal Module Database v4.0.0.113{Colors.RESET}"
        HackerUI.draw_line(subtext, border, centered=True)
        HackerUI.draw_line("", border)
        HackerUI.draw_line("", border)
        HackerUI.draw_line(f"{Colors.DARK_GREEN}â”œ{'â”€' * (border['width'] - 4)}â”¤{Colors.RESET}", border)
        HackerUI.draw_line("", border)
        
        stats = f"{Colors.DARK_CYAN}â–º System: Windows 11 {Colors.DIM}|{Colors.RESET} "
        stats += f"{Colors.DARK_GREEN}â–º Python: {sys.version[:5]} {Colors.DIM}|{Colors.RESET} "
        stats += f"{Colors.DARK_YELLOW}â–º Modules: {len(ModuleManager().modules)}{Colors.RESET}"
        HackerUI.draw_line(stats, border)
        HackerUI.draw_line("", border)
        
        return border
    
    @staticmethod
    def draw_footer(border, start_time):
        """Draw the footer"""
        HackerUI.draw_line("", border)
        HackerUI.draw_line(f"{Colors.DARK_GREEN}â”œ{'â”€' * (border['width'] - 4)}â”¤{Colors.RESET}", border)
        HackerUI.draw_line("", border)
        
        footer_text = f"{Colors.DIM}Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        footer_text += f"| Runtime: {(datetime.now() - start_time).total_seconds():.2f}s "
        footer_text += f"| DSTerminal v4.0.0.113{Colors.RESET}"
        HackerUI.draw_line(footer_text, border)
        
        print(f"{Colors.DARK_GREEN}â•š{'â•' * (border['width'] - 2)}â•{Colors.RESET}")

class ModuleDisplay:
    """Display modules in hacker-style format"""
    
    @staticmethod
    def display_modules(modules: List[Dict], filter_type: str = "all"):
        """Display modules with hacker styling"""
        
        filtered = modules
        if filter_type != "all":
            filtered = [m for m in modules if m['category'].lower() == filter_type.lower()]
        
        if not filtered:
            print(f"{Colors.DARK_RED}No modules found for type: {filter_type}{Colors.RESET}")
            return
        
        max_name_len = max([len(m['name']) for m in filtered])
        max_key_len = max([len(m['key']) for m in filtered])
        max_category_len = max([len(m['category']) for m in filtered])
        
        print(f"\n{Colors.BOLD}{Colors.DARK_GREEN}â”Œ{'â”€' * (max_name_len + max_key_len + max_category_len + 30)}â”{Colors.RESET}")
        header = f"{Colors.BOLD}{Colors.DARK_CYAN}â”‚ {Colors.BRIGHT_CYAN}MODULE{Colors.RESET}{Colors.DARK_CYAN} "
        header += f"{' ' * (max_name_len - 6)}{Colors.BRIGHT_CYAN}KEY{Colors.RESET}{Colors.DARK_CYAN} "
        header += f"{' ' * (max_key_len - 3)}{Colors.BRIGHT_CYAN}STATUS{Colors.RESET}{Colors.DARK_CYAN} "
        header += f"{Colors.BRIGHT_CYAN}CATEGORY{Colors.RESET}{Colors.DARK_CYAN} â”‚{Colors.RESET}"
        print(header)
        print(f"{Colors.DARK_GREEN}â”œ{'â”€' * (max_name_len + max_key_len + max_category_len + 30)}â”¤{Colors.RESET}")
        
        for module in filtered:
            name = module['name']
            key = module['key']
            status = module['status']
            category = module['category']
            color = module['color']
            desc = module['description']
            version = module.get('version', 'N/A')
            deps = module.get('dependencies', [])
            
            if status == 'âœ“':
                status_colored = f"{Colors.BRIGHT_GREEN}{status}{Colors.RESET}"
            elif status == 'â˜…':
                status_colored = f"{Colors.BRIGHT_YELLOW}{status}{Colors.RESET}"
            elif status == 'âœ—':
                status_colored = f"{Colors.DARK_RED}{status}{Colors.RESET}"
            else:
                status_colored = f"{Colors.DARK_WHITE}{status}{Colors.RESET}"
            
            # Category colors
            if category == 'Core':
                cat_colored = f"{Colors.DARK_GREEN}{category}{Colors.RESET}"
            elif category == 'Extended':
                cat_colored = f"{Colors.DARK_CYAN}{category}{Colors.RESET}"
            elif category == 'Tools':
                cat_colored = f"{Colors.DARK_PURPLE}{category}{Colors.RESET}"
            else:
                cat_colored = f"{Colors.DARK_YELLOW}{category}{Colors.RESET}"
            
            line = f"{Colors.DARK_GREEN}â”‚ {Colors.RESET}"
            line += f"{color}{name}{Colors.RESET}"
            line += " " * (max_name_len - len(name) + 2)
            line += f"{Colors.DARK_WHITE}{key}{Colors.RESET}"
            line += " " * (max_key_len - len(key) + 2)
            line += f"{status_colored}  "
            line += f"{cat_colored}"
            line += " " * (max_category_len - len(category) + 2)
            line += f"{Colors.DARK_GREEN}â”‚{Colors.RESET}"
            print(line)
            
            # Description
            desc_line = f"{Colors.DARK_GREEN}â”‚ {Colors.RESET}{Colors.DIM}{desc}{Colors.RESET}"
            desc_line += " " * (max_name_len + max_key_len + max_category_len + 30 - len(desc) - 4)
            desc_line += f"{Colors.DARK_GREEN}â”‚{Colors.RESET}"
            print(desc_line)
            
            # Version and dependencies (in dim)
            if deps:
                deps_str = ", ".join(deps)
                info_line = f"{Colors.DARK_GREEN}â”‚ {Colors.RESET}{Colors.DIM}v{version} | Deps: {deps_str}{Colors.RESET}"
                info_line += " " * (max_name_len + max_key_len + max_category_len + 30 - len(f"v{version} | Deps: {deps_str}") - 4)
                info_line += f"{Colors.DARK_GREEN}â”‚{Colors.RESET}"
                print(info_line)
            
            print(f"{Colors.DARK_GREEN}â”œ{'â”€' * (max_name_len + max_key_len + max_category_len + 30)}â”¤{Colors.RESET}")
        
        print(f"{Colors.DARK_GREEN}â””{'â”€' * (max_name_len + max_key_len + max_category_len + 30)}â”˜{Colors.RESET}")
        print(f"\n{Colors.DIM}Total modules: {len(filtered)} | Category: {filter_type}{Colors.RESET}")

def interactive_menu():
    """Interactive menu for module browsing"""
    
    manager = ModuleManager()
    ui = HackerUI()
    
    while True:
        ui.clear_screen()
        start_time = datetime.now()
        
        border = ui.draw_header("DSTERMINAL MODULE DATABASE")
        
        options = [
            ("1", "Show All Modules", Colors.DARK_GREEN),
            ("2", "Show Core Modules", Colors.DARK_GREEN),
            ("3", "Show Extended Modules", Colors.DARK_CYAN),
            ("4", "Show Tool Modules", Colors.DARK_PURPLE),
            ("5", "Show Community Modules", Colors.DARK_YELLOW),
            ("6", "Search Modules", Colors.DARK_BLUE),
            ("7", "Module Details", Colors.DARK_RED),
            ("8", "Export Module List", Colors.DARK_RED),
            ("0", "Exit", Colors.DARK_RED),
        ]
        
        ui.draw_line("", border)
        ui.draw_line(f"{Colors.BOLD}{Colors.DARK_CYAN}â•â•â• MENU OPTIONS â•â•â•{Colors.RESET}", border, centered=True)
        ui.draw_line("", border)
        
        for num, text, color in options:
            option_line = f"{Colors.DARK_GREEN}â–º {Colors.RESET}{color}{num}. {text}{Colors.RESET}"
            ui.draw_line(option_line, border, pad_left=4)
        
        ui.draw_line("", border)
        ui.draw_footer(border, start_time)
        
        choice = input(f"\n{Colors.BRIGHT_GREEN}âžœ {Colors.RESET}{Colors.BOLD}Enter choice: {Colors.RESET}").strip()
        
        if choice == "0":
            print(f"\n{Colors.DARK_GREEN}Exiting DSTerminal Module Database...{Colors.RESET}")
            break
        
        elif choice == "1":
            ui.clear_screen()
            print(f"\n{Colors.BOLD}{Colors.BRIGHT_GREEN}â•â• ALL MODULES â•â•{Colors.RESET}\n")
            ModuleDisplay.display_modules(manager.modules, "all")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "2":
            ui.clear_screen()
            print(f"\n{Colors.BOLD}{Colors.DARK_GREEN}â•â• CORE MODULES â•â•{Colors.RESET}\n")
            ModuleDisplay.display_modules(manager.modules, "core")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "3":
            ui.clear_screen()
            print(f"\n{Colors.BOLD}{Colors.DARK_CYAN}â•â• EXTENDED MODULES â•â•{Colors.RESET}\n")
            ModuleDisplay.display_modules(manager.modules, "extended")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "4":
            ui.clear_screen()
            print(f"\n{Colors.BOLD}{Colors.DARK_PURPLE}â•â• TOOL MODULES â•â•{Colors.RESET}\n")
            ModuleDisplay.display_modules(manager.modules, "tools")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "5":
            ui.clear_screen()
            print(f"\n{Colors.BOLD}{Colors.DARK_YELLOW}â•â• COMMUNITY MODULES â•â•{Colors.RESET}\n")
            ModuleDisplay.display_modules(manager.modules, "community")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "6":
            ui.clear_screen()
            search = input(f"\n{Colors.CYAN}ðŸ” Enter search term: {Colors.RESET}").strip().lower()
            if search:
                results = manager.search_modules(search)
                print(f"\n{Colors.BOLD}{Colors.BRIGHT_GREEN}â•â• SEARCH RESULTS: '{search}' â•â•{Colors.RESET}\n")
                if results:
                    ModuleDisplay.display_modules(results, "all")
                else:
                    print(f"{Colors.DARK_RED}No modules found matching '{search}'{Colors.RESET}")
            else:
                print(f"{Colors.DARK_YELLOW}No search term entered{Colors.RESET}")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "7":
            ui.clear_screen()
            module_name = input(f"\n{Colors.CYAN}ðŸ“¦ Enter module name: {Colors.RESET}").strip()
            if module_name:
                module = next((m for m in manager.modules if 
                             m['name'].lower() == module_name.lower() or 
                             m['key'].lower() == module_name.lower()), None)
                if module:
                    print(f"\n{Colors.BOLD}{Colors.BRIGHT_GREEN}â•â• MODULE DETAILS â•â•{Colors.RESET}")
                    print(f"{Colors.DARK_GREEN}Name:{Colors.RESET} {module['name']}")
                    print(f"{Colors.DARK_GREEN}Key:{Colors.RESET} {module['key']}")
                    print(f"{Colors.DARK_GREEN}Status:{Colors.RESET} {module['status']}")
                    print(f"{Colors.DARK_GREEN}Category:{Colors.RESET} {module['category']}")
                    print(f"{Colors.DARK_GREEN}Version:{Colors.RESET} {module.get('version', 'N/A')}")
                    print(f"{Colors.DARK_GREEN}Description:{Colors.RESET} {module['description']}")
                    if module.get('dependencies'):
                        print(f"{Colors.DARK_GREEN}Dependencies:{Colors.RESET} {', '.join(module['dependencies'])}")
                else:
                    print(f"{Colors.DARK_RED}Module '{module_name}' not found{Colors.RESET}")
            else:
                print(f"{Colors.DARK_YELLOW}No module name entered{Colors.RESET}")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "8":
            filename = f"dst_modules_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("DSTERMINAL MODULE DATABASE - EXPORT\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Python Version: {sys.version}\n")
                    f.write(f"Total Modules: {len(manager.modules)}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    # Group by category
                    categories = {}
                    for module in manager.modules:
                        cat = module['category']
                        if cat not in categories:
                            categories[cat] = []
                        categories[cat].append(module)
                    
                    for category, modules in categories.items():
                        f.write(f"{category.upper()} MODULES:\n")
                        f.write("-" * 40 + "\n")
                        for module in modules:
                            f.write(f"  {module['name']} ({module['key']})\n")
                            f.write(f"    Status: {module['status']}\n")
                            f.write(f"    Version: {module.get('version', 'N/A')}\n")
                            f.write(f"    Description: {module['description']}\n")
                            if module.get('dependencies'):
                                f.write(f"    Dependencies: {', '.join(module['dependencies'])}\n")
                            f.write("\n")
                    
                    f.write("=" * 60 + "\n")
                    f.write("SUMMARY:\n")
                    for category, modules in categories.items():
                        f.write(f"  Total {category} Modules: {len(modules)}\n")
                    f.write(f"  Grand Total: {len(manager.modules)}\n")
                    f.write("=" * 60 + "\n")
                    
                print(f"\n{Colors.BRIGHT_GREEN}âœ… Module list exported to: {filename}{Colors.RESET}")
                print(f"{Colors.DIM}File saved with UTF-8 encoding{Colors.RESET}")
                
            except Exception as e:
                print(f"\n{Colors.DARK_RED}âŒ Export failed: {e}{Colors.RESET}")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        else:
            print(f"\n{Colors.DARK_RED}âŒ Invalid choice. Please try again.{Colors.RESET}")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")

def main():
    """Main entry point"""
    if os.name != 'nt':
        print(f"{Colors.DARK_YELLOW}âš ï¸ DSTerminal is optimized for Windows{Colors.RESET}")
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.DARK_GREEN}Exiting...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.DARK_RED}âŒ An error occurred: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        input(f"\n{Colors.DIM}Press Enter to exit...{Colors.RESET}")

if __name__ == "__main__":
    main()