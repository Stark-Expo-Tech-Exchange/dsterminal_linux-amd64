#!/usr/bin/env python3
"""
Web Security Analyzer - DSTERMINAL Enterprise Edition v3.1.113
Enhanced with Platform-Specific Remediation Configurations
"""

import os
import sys
import re
import json
import time
import socket
import threading
import webbrowser
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin, parse_qs, quote
from io import BytesIO
import queue
import platform 
import random


# Rich imports for advanced UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.syntax import Syntax
    from rich import box
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.align import Align
    from rich.live import Live
    from rich.tree import Tree
    from rich.markdown import Markdown
    from rich.text import Text
    from rich.columns import Columns
    from rich.console import Group
    from rich.padding import Padding
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table as PDFTable, TableStyle, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch, cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ============================================================
# COLOR SUPPORT DETECTION
# ============================================================

def should_use_colors():
    """Determine if we should use ANSI colors"""
    # Check if NO_COLOR environment variable is set
    if os.environ.get('NO_COLOR'):
        return False
    
    # Check if we're in a terminal
    if not sys.stdout.isatty():
        return False
    
    # Check for Windows
    if platform.system() == 'Windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                # Check if ENABLE_VIRTUAL_TERMINAL_PROCESSING is set
                return bool(mode.value & 0x4)
            return False
        except:
            return False
    
    return True

# Set global flag
USE_COLORS = should_use_colors()


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "v3.1.113"
PLATFORM = "DSTERMINAL Cyber Ops Platform"
WATERMARK_TEXT = f"{PLATFORM} {VERSION}"

# XSS Payloads
XSS_PAYLOADS = [
    '<script>alert("XSS")</script>',
    '<script>alert(document.cookie)</script>',
    '<img src=x onerror=alert("XSS")>',
    '<svg/onload=alert("XSS")>',
    '<body onload=alert("XSS")>',
    '"><script>alert("XSS")</script>',
    'javascript:alert("XSS")',
]

# ============================================================
# COLORS CLASS - MUST BE DEFINED BEFORE TypeWriter
# ============================================================

class Colors:
    """ANSI color codes for terminal output with Windows support"""
    
    # Foreground colors
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BLACK = '\033[90m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    DIM = '\033[2m'
    BLINK = '\033[5m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    @staticmethod
    def init_colors():
        """Initialize color support for Windows"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass
    
    @staticmethod
    def strip(text):
        """Strip ANSI color codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# Initialize colors on Windows
Colors.init_colors()


# ============================================================
# TYPEWRITER CLASS - DEFINED AFTER Colors
# ============================================================

class TypeWriter:
    """Human-like typing simulation with pen writing effects"""
    
    def __init__(self, speed='fast'):
        self.speed_presets = {
            'slow': (30, 60),
            'medium': (15, 35),
            'fast': (5, 15),
            'instant': (0, 0)
        }
        self.set_speed(speed)
        self.punctuation_delay = 1.5
        self.typing_enabled = True
        self._stop_typing = False
        self.current_color = Colors.GREEN
        self.use_colors = USE_COLORS
        
    def set_speed(self, speed):
        if speed in self.speed_presets:
            self.min_delay, self.max_delay = self.speed_presets[speed]
        else:
            self.min_delay, self.max_delay = self.speed_presets['fast']
    
    def type_text(self, text, color=Colors.GREEN, newline=True, pause_between_chars=True, 
                  pen_effect=True, line_by_line=False):
        """Type text with human-like pen writing simulation"""
        
        if not self.typing_enabled:
            print(f"{text}", end='\n' if newline else '')
            return
        
        # Split text into lines if line_by_line mode
        if line_by_line:
            lines = text.split('\n')
            for line in lines:
                self._type_line(line, color, pause_between_chars, pen_effect)
                if newline:
                    print()
                time.sleep(random.uniform(0.1, 0.3))
            return
        
        self._type_line(text, color, pause_between_chars, pen_effect)
        if newline:
            print()
    
    def _type_line(self, text, color, pause_between_chars, pen_effect):
        """Type a single line with pen effects"""
        
        pause_chars = ['.', ',', '!', '?', ';', ':', '...', '—', '–']
        
        for i, char in enumerate(text):
            if self._stop_typing:
                break
            
            if char == '\n':
                print()
                continue
            else:
                # Use self.use_colors instead of global USE_COLORS
                if self.use_colors and color and pen_effect and (i == 0 or text[i-1] == ' '):
                    sys.stdout.write(f"{Colors.BOLD}{color}{char}{Colors.END}")
                elif self.use_colors and color:
                    sys.stdout.write(f"{color}{char}{Colors.END}")
                else:
                    sys.stdout.write(char)
                sys.stdout.flush()
            
            if self.min_delay == 0 and self.max_delay == 0:
                delay = 0
            else:
                # Base delay with some randomness
                delay = random.uniform(self.min_delay, self.max_delay) / 1000.0
                
                # Pen effect: slightly longer after punctuation
                if char in pause_chars and pause_between_chars:
                    delay *= self.punctuation_delay
                
                # Random hesitation (like thinking)
                if random.random() < 0.03:
                    delay += random.uniform(50, 200) / 1000.0
                
                # Faster typing after spaces (like natural rhythm)
                if char == ' ':
                    delay *= 0.7
                
                # Slower on numbers/symbols (like thinking)
                if char.isdigit() or char in ['@', '#', '$', '%', '^', '&', '*']:
                    delay *= 1.3
            
            time.sleep(delay)
    
    def type_line(self, text, color=Colors.GREEN, pen_effect=True):
        """Type a single line with newline"""
        self.type_text(text, color, newline=True, pen_effect=pen_effect)
    
    def type_block(self, lines, color=Colors.GREEN, delay_between_lines=0.3, pen_effect=True):
        """Type multiple lines with delays between them"""
        for line in lines:
            self.type_text(line, color, newline=True, pen_effect=pen_effect)
            if delay_between_lines > 0:
                time.sleep(delay_between_lines)
    
    def type_banner(self, lines, color=Colors.CYAN, delay_between=0.1):
        """Type banner with faster typing speed"""
        original_speed = self.min_delay, self.max_delay
        self.min_delay, self.max_delay = 2, 5  # Fast for banners
        
        for line in lines:
            self.type_text(line, color, newline=True, pen_effect=False)
            time.sleep(delay_between)
        
        self.min_delay, self.max_delay = original_speed
    
    def type_animated(self, text, color=Colors.GREEN, duration=0.5):
        """Type with animated cursor effect"""
        if not self.typing_enabled:
            print(f"{text}")
            return
        
        cursor_chars = ['|', '/', '-', '\\']
        cursor_idx = 0
        
        display_text = text if USE_COLORS else strip_ansi(text)
        
        for i in range(len(display_text) + 1):
            if self._stop_typing:
                break
            
            sys.stdout.write('\r')
            if USE_COLORS and color:
                sys.stdout.write(f"{color}{display_text[:i]}{Colors.DIM}{cursor_chars[cursor_idx % len(cursor_chars)]}{Colors.END}")
            else:
                sys.stdout.write(f"{display_text[:i]}{cursor_chars[cursor_idx % len(cursor_chars)]}")
            sys.stdout.flush()
            
            cursor_idx += 1
            time.sleep(duration / (len(display_text) + 1))
        
        sys.stdout.write('\r')
        if USE_COLORS and color:
            sys.stdout.write(f"{color}{display_text}{Colors.END}")
        else:
            sys.stdout.write(display_text)
        sys.stdout.flush()
        print()
    
    def stop_typing(self):
        self._stop_typing = True
    
    def reset(self):
        self._stop_typing = False

class PlatformRemediationGenerator:
    """Generate platform-specific remediation configurations"""
    
    @staticmethod
    def get_platform_configs(server_info: Dict, technologies: List[str]) -> Dict:
        """Get remediation configs based on detected platform"""
        
        platform = {
            'webserver': 'apache',
            'os': 'linux',
            'language': 'php',
            'framework': 'none',
            'cloud_provider': 'none'
        }
        
        # Detect web server
        server = server_info.get('server', '').lower()
        if 'nginx' in server:
            platform['webserver'] = 'nginx'
        elif 'apache' in server:
            platform['webserver'] = 'apache'
        elif 'iis' in server:
            platform['webserver'] = 'iis'
        elif 'cloudflare' in server:
            platform['webserver'] = 'cloudflare'
            platform['cloud_provider'] = 'cloudflare'
        
        # Detect OS
        if 'centos' in server or 'rhel' in server:
            platform['os'] = 'centos'
        elif 'ubuntu' in server or 'debian' in server:
            platform['os'] = 'ubuntu'
        elif 'windows' in server:
            platform['os'] = 'windows'
        elif 'alpine' in server:
            platform['os'] = 'alpine'
        
        # Detect language
        powered_by = server_info.get('powered_by', '').lower()
        if 'php' in powered_by:
            platform['language'] = 'php'
        elif 'python' in powered_by or 'django' in str(technologies):
            platform['language'] = 'python'
        elif 'ruby' in powered_by or 'rails' in str(technologies):
            platform['language'] = 'ruby'
        elif 'node' in powered_by or 'express' in str(technologies):
            platform['language'] = 'node'
        elif 'asp.net' in powered_by or 'iis' in server:
            platform['language'] = 'aspnet'
        
        # Detect framework
        frameworks = ['WordPress', 'Laravel', 'Django', 'Rails', 'React', 'Vue.js', 'Angular', 'Bootstrap', 'AdminLTE']
        for tech in technologies:
            if tech in frameworks:
                platform['framework'] = tech.lower()
                break
            elif 'wordpress' in tech.lower():
                platform['framework'] = 'wordpress'
            elif 'laravel' in tech.lower():
                platform['framework'] = 'laravel'
            elif 'django' in tech.lower():
                platform['framework'] = 'django'
            elif 'rails' in tech.lower():
                platform['framework'] = 'rails'
        
        # Detect cloud
        if 'cloudflare' in server or 'cloudflare' in str(technologies):
            platform['cloud_provider'] = 'cloudflare'
        elif 'aws' in server or 'amazon' in server:
            platform['cloud_provider'] = 'aws'
        elif 'azure' in server:
            platform['cloud_provider'] = 'azure'
        elif 'gcp' in server or 'google' in server:
            platform['cloud_provider'] = 'gcp'
        elif 'netlify' in server:
            platform['cloud_provider'] = 'netlify'
        elif 'github' in server or 'pages' in server:
            platform['cloud_provider'] = 'github'
        
        return {
            'platform': platform,
            'configs': PlatformRemediationGenerator._get_configs(platform)
        }
    
    @staticmethod
    def _get_configs(platform: Dict) -> Dict:
        """Get remediation configs for detected platform"""
        
        configs = {}
        webserver = platform['webserver']
        os_type = platform['os']
        language = platform['language']
        framework = platform['framework']
        
        # Security headers configurations based on webserver
        if webserver == 'apache':
            configs['security_headers'] = {
                'title': 'Apache Security Headers (.htaccess)',
                'code': '''# Add to .htaccess or httpd.conf
<IfModule mod_headers.c>
    # Clickjacking Protection
    Header always set X-Frame-Options "DENY"
    
    # XSS Protection
    Header always set X-XSS-Protection "1; mode=block"
    
    # MIME Sniffing Protection
    Header always set X-Content-Type-Options "nosniff"
    
    # HSTS - Force HTTPS (only if you have SSL)
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    
    # Content Security Policy (CSP)
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; img-src 'self' data:; font-src 'self' data:; connect-src 'self'"
    
    # Referrer Policy
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    
    # Permissions Policy
    Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"
</IfModule>

# Hide server signature
ServerSignature Off
ServerTokens Prod

# Disable directory listing
Options -Indexes

# Protect sensitive files
<FilesMatch "^(config|database|wp-config|\.env|\.htaccess|\.htpasswd|php\.ini)">
    Order allow,deny
    Deny from all
</FilesMatch>''',
                'commands': [
                    '# Enable mod_headers',
                    f'sudo a2enmod headers  # Debian/Ubuntu',
                    f'sudo yum install mod_headers -y  # CentOS/RHEL',
                    '# Restart Apache',
                    f'sudo systemctl restart apache2  # Debian/Ubuntu',
                    f'sudo systemctl restart httpd    # CentOS/RHEL',
                    '# Verify headers',
                    'curl -I https://yourdomain.com | grep -E "X-Frame-Options|X-XSS-Protection|Strict-Transport-Security"'
                ]
            }
        elif webserver == 'nginx':
            configs['security_headers'] = {
                'title': 'Nginx Security Headers (nginx.conf)',
                'code': '''# Add to server block in nginx.conf
server {
    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; img-src 'self' data:; font-src 'self' data:; connect-src 'self'" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # Hide Nginx version
    server_tokens off;
    
    # Disable directory listing
    autoindex off;
    
    # Protect sensitive files
    location ~ ^/(config|database|wp-config|\.env|\.htaccess|\.htpasswd|php\.ini) {
        deny all;
        return 403;
    }
}''',
                'commands': [
                    '# Test Nginx configuration',
                    'sudo nginx -t',
                    '# Reload Nginx',
                    'sudo systemctl reload nginx',
                    '# Verify headers',
                    'curl -I https://yourdomain.com | grep -E "X-Frame-Options|X-XSS-Protection|Strict-Transport-Security"'
                ]
            }
        elif webserver == 'iis':
            configs['security_headers'] = {
                'title': 'IIS Security Headers (web.config)',
                'code': '''<!-- Add to web.config -->
<configuration>
    <system.webServer>
        <httpProtocol>
            <customHeaders>
                <add name="X-Frame-Options" value="DENY" />
                <add name="X-XSS-Protection" value="1; mode=block" />
                <add name="X-Content-Type-Options" value="nosniff" />
                <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains; preload" />
                <add name="Referrer-Policy" value="strict-origin-when-cross-origin" />
                <add name="Permissions-Policy" value="geolocation=(), microphone=(), camera=()" />
            </customHeaders>
        </httpProtocol>
        <security>
            <requestFiltering>
                <hiddenSegments>
                    <add segment="config" />
                    <add segment=".git" />
                </hiddenSegments>
            </requestFiltering>
        </security>
    </system.webServer>
</configuration>''',
                'commands': [
                    '# Open IIS Manager',
                    'iisreset',
                    '# Verify headers',
                    'curl -I https://yourdomain.com | grep -E "X-Frame-Options|X-XSS-Protection"'
                ]
            }
        elif webserver == 'cloudflare':
            configs['security_headers'] = {
                'title': 'Cloudflare Security Headers (Cloudflare Dashboard)',
                'code': '''# Cloudflare Dashboard Configuration:
1. Go to Cloudflare Dashboard → SSL/TLS → Edge Certificates
2. Enable "Always Use HTTPS"
3. Enable "HTTP Strict Transport Security (HSTS)"
   - max-age: 31536000
   - Include subdomains: Yes
   - Preload: Yes
4. Go to Security → Settings
   - Security Level: High
   - Challenge Passage: 30 minutes
   - Browser Integrity Check: On
5. Go to Rules → Page Rules (for custom headers)
   - Create rule for: *yourdomain.com/*
   - Add: 
     - X-Frame-Options: DENY
     - X-XSS-Protection: 1; mode=block
     - X-Content-Type-Options: nosniff''',
                'commands': [
                    '# Verify Cloudflare headers',
                    'curl -I https://yourdomain.com | grep -E "cf-|X-Frame-Options"'
                ]
            }
        
        # Language-specific configurations
        if language == 'php':
            configs['language_config'] = {
                'title': 'PHP Security Configuration (php.ini)',
                'code': '''; Add to php.ini
; Hide PHP version
expose_php = Off

; Disable dangerous functions
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source

; Secure session cookies
session.cookie_secure = On
session.cookie_httponly = On
session.cookie_samesite = Strict
session.use_only_cookies = On

; Error handling (production)
display_errors = Off
display_startup_errors = Off
log_errors = On
error_log = /var/log/php_errors.log

; File uploads
upload_max_filesize = 10M
post_max_size = 10M

; Timezone
date.timezone = UTC''',
                'commands': [
                    '# Find php.ini location',
                    'php -i | grep "Loaded Configuration File"',
                    '# Edit php.ini',
                    f'sudo nano /etc/php/*/apache2/php.ini  # Debian/Ubuntu',
                    f'sudo nano /etc/php.ini  # CentOS/RHEL',
                    '# Restart web server',
                    f'sudo systemctl restart apache2  # Debian/Ubuntu',
                    f'sudo systemctl restart httpd    # CentOS/RHEL',
                    '# Verify PHP configuration',
                    'php -i | grep -E "expose_php|disable_functions"'
                ]
            }
        elif language == 'python':
            configs['language_config'] = {
                'title': 'Python/Django Security Configuration',
                'code': '''# Django settings.py
# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF Protection
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Security Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... other middleware
]''',
                'commands': [
                    '# Apply Django security settings',
                    'python manage.py check --deploy',
                    '# Verify security headers',
                    'curl -I https://yourdomain.com | grep -E "X-Frame-Options|X-XSS-Protection"'
                ]
            }
        elif language == 'node':
            configs['language_config'] = {
                'title': 'Node.js/Express Security Configuration',
                'code': '''// Install helmet package
// npm install helmet

// In your Express app
const helmet = require('helmet');
const express = require('express');
const app = express();

// Use Helmet middleware (sets many security headers)
app.use(helmet());

// Custom CSP with helmet
app.use(helmet.contentSecurityPolicy({
    directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com"],
        styleSrc: ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com"],
        imgSrc: ["'self'", "data:"],
        fontSrc: ["'self'", "data:"],
        connectSrc: ["'self'"]
    }
}));

// Rate limiting
const rateLimit = require('express-rate-limit');
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);''',
                'commands': [
                    '# Install security packages',
                    'npm install helmet express-rate-limit',
                    '# Verify headers',
                    'curl -I https://yourdomain.com | grep -E "X-Frame-Options|X-XSS-Protection"'
                ]
            }
        elif language == 'ruby':
            configs['language_config'] = {
                'title': 'Ruby on Rails Security Configuration',
                'code': '''# config/application.rb
module YourApp
  class Application < Rails::Application
    # Security Headers
    config.action_dispatch.default_headers = {
      'X-Frame-Options' => 'DENY',
      'X-XSS-Protection' => '1; mode=block',
      'X-Content-Type-Options' => 'nosniff',
      'Referrer-Policy' => 'strict-origin-when-cross-origin'
    }
    
    # Force SSL
    config.force_ssl = true
    
    # Session Security
    config.session_store :cookie_store, {
      key: '_your_app_session',
      secure: true,
      httponly: true,
      same_site: :strict
    }
  end
end

# Or use the secure_headers gem
# gem 'secure_headers'
# In config/initializers/secure_headers.rb
SecureHeaders::Configuration.default do |config|
  config.hsts = "max-age=31536000; includeSubDomains; preload"
  config.x_frame_options = "DENY"
  config.x_content_type_options = "nosniff"
  config.x_xss_protection = "1; mode=block"
  config.csp = {
    default_src: %w('self'),
    script_src: %w('self' 'unsafe-inline' https://cdnjs.cloudflare.com),
    style_src: %w('self' 'unsafe-inline' https://cdnjs.cloudflare.com),
    img_src: %w('self' data:),
    font_src: %w('self' data:),
    connect_src: %w('self')
  }
end''',
                'commands': [
                    '# Add secure_headers gem',
                    'gem install secure_headers',
                    '# Restart Rails server',
                    'rails server',
                    '# Verify headers',
                    'curl -I https://yourdomain.com | grep -E "X-Frame-Options|X-XSS-Protection"'
                ]
            }
        
        # Framework-specific configurations
        if framework == 'wordpress':
            configs['framework_config'] = {
                'title': 'WordPress Security Configuration',
                'code': '''# In wp-config.php
# Security Keys
define('AUTH_KEY',         'put your unique phrase here');
define('SECURE_AUTH_KEY',  'put your unique phrase here');
define('LOGGED_IN_KEY',    'put your unique phrase here');
define('NONCE_KEY',        'put your unique phrase here');
define('AUTH_SALT',        'put your unique phrase here');
define('SECURE_AUTH_SALT', 'put your unique phrase here');
define('LOGGED_IN_SALT',   'put your unique phrase here');
define('NONCE_SALT',       'put your unique phrase here');

# Disable file editing
define('DISALLOW_FILE_EDIT', true);

# Disable plugin/theme installation
define('DISALLOW_FILE_MODS', true);

# Force SSL
define('FORCE_SSL_ADMIN', true);

# Disable XML-RPC
add_filter('xmlrpc_enabled', '__return_false');

# In .htaccess
# Block access to sensitive files
<Files wp-config.php>
    Order allow,deny
    Deny from all
</Files>

<Files .htaccess>
    Order allow,deny
    Deny from all
</Files>''',
                'commands': [
                    '# Generate security keys',
                    'curl -s https://api.wordpress.org/secret-key/1.1/salt/',
                    '# Update WordPress',
                    'wp core update',
                    '# Update plugins',
                    'wp plugin update --all',
                    '# Verify security',
                    'wp core verify-checksums'
                ]
            }
        elif framework == 'laravel':
            configs['framework_config'] = {
                'title': 'Laravel Security Configuration',
                'code': '''# In .env
# Force HTTPS
APP_ENV=production
APP_DEBUG=false
APP_URL=https://yourdomain.com

# Session Security
SESSION_DRIVER=database
SESSION_LIFETIME=120
SESSION_SECURE=true
SESSION_HTTP_ONLY=true
SESSION_SAME_SITE=strict

# Cookie Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTP_ONLY=true
SESSION_COOKIE_SAMESITE=strict

# In config/session.php
'secure' => env('SESSION_SECURE', true),
'http_only' => true,
'same_site' => 'strict',

# In app/Http/Kernel.php
protected $middleware = [
    \\App\\Http\\Middleware\\TrustHosts::class,
    \\App\\Http\\Middleware\\TrustProxies::class,
    \\Fruitcake\\Cors\\HandleCors::class,
    \\App\\Http\\Middleware\\PreventRequestsDuringMaintenance::class,
    \\Illuminate\\Foundation\\Http\\Middleware\\ValidatePostSize::class,
    \\App\\Http\\Middleware\\TrimStrings::class,
    \\Illuminate\\Foundation\\Http\\Middleware\\ConvertEmptyStringsToNull::class,
];''',
                'commands': [
                    '# Generate new application key',
                    'php artisan key:generate',
                    '# Clear cache',
                    'php artisan config:cache',
                    'php artisan route:cache',
                    'php artisan view:cache',
                    '# Verify security headers',
                    'curl -I https://yourdomain.com | grep -E "X-Frame-Options|X-XSS-Protection"'
                ]
            }
        elif framework == 'django':
            configs['framework_config'] = {
                'title': 'Django Security Configuration',
                'code': '''# In settings.py
# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF Protection
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_SAMESITE = 'Strict'

# Security Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... other middleware
]

# Allowed Hosts
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']''',
                'commands': [
                    '# Run security check',
                    'python manage.py check --deploy',
                    '# Verify headers',
                    'curl -I https://yourdomain.com | grep -E "X-Frame-Options|X-XSS-Protection"'
                ]
            }
        
        # OS-specific commands
        if os_type == 'ubuntu':
            configs['os_commands'] = {
                'title': 'Ubuntu/Debian System Commands',
                'code': '''# Update system
sudo apt update && sudo apt upgrade -y

# Install security packages
sudo apt install fail2ban ufw -y

# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Configure Fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Install monitoring
sudo apt install htop iotop -y''',
                'commands': [
                    '# Check security updates',
                    'sudo apt list --upgradable | grep security',
                    '# Check firewall status',
                    'sudo ufw status',
                    '# Check fail2ban status',
                    'sudo fail2ban-client status'
                ]
            }
        elif os_type == 'centos':
            configs['os_commands'] = {
                'title': 'CentOS/RHEL System Commands',
                'code': '''# Update system
sudo yum update -y

# Install security packages
sudo yum install epel-release -y
sudo yum install fail2ban firewalld -y

# Configure Firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Configure Fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Install monitoring
sudo yum install htop iotop -y''',
                'commands': [
                    '# Check security updates',
                    'sudo yum list updates | grep security',
                    '# Check firewall status',
                    'sudo firewall-cmd --list-all',
                    '# Check fail2ban status',
                    'sudo fail2ban-client status'
                ]
            }
        
        # Cloud-specific configurations
        if platform['cloud_provider'] == 'cloudflare':
            configs['cloud_config'] = {
                'title': 'Cloudflare WAF Configuration',
                'code': '''# Cloudflare Security Settings
1. SSL/TLS Settings:
   - SSL/TLS Encryption: Full (strict)
   - Always Use HTTPS: On
   - HSTS: On (max-age=31536000)
   - Minimum TLS Version: TLS 1.2

2. Security Settings:
   - Security Level: High
   - Challenge Passage: 30 minutes
   - Browser Integrity Check: On
   - Email Address Obfuscation: On
   - Server Side Excludes: On

3. Firewall Rules:
   Rule 1: Block all countries not needed
   Rule 2: Block known threats
   Rule 3: Rate limiting for login pages

4. Rate Limiting:
   - Rule: /login
   - Requests: 10 per 1 minute
   - Response: 429 Too Many Requests''',
                'commands': [
                    '# Verify Cloudflare configuration',
                    'curl -I https://yourdomain.com | grep -E "cf-|cloudflare"',
                    '# Check HSTS preload status',
                    'curl -I https://yourdomain.com | grep "Strict-Transport-Security"'
                ]
            }
        
        return configs


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class SecurityFinding:
    category: str
    severity: str
    title: str
    description: str
    recommendation: str
    evidence: Optional[str] = None
    cve: Optional[str] = None
    payload: Optional[str] = None
    remediation_configs: Dict[str, Any] = field(default_factory=dict)
    affected_versions: Optional[str] = None
    fix_priority: str = "MEDIUM"

@dataclass
class WebSecurityReport:
    url: str
    timestamp: str
    headers: Dict[str, str] = field(default_factory=dict)
    server_info: Dict[str, str] = field(default_factory=dict)
    technologies: List[str] = field(default_factory=list)
    findings: List[SecurityFinding] = field(default_factory=list)
    security_headers: Dict[str, str] = field(default_factory=dict)
    cookies: List[Dict] = field(default_factory=list)
    forms: List[Dict] = field(default_factory=list)
    exposed_files: List[str] = field(default_factory=list)
    xss_vulnerable: List[Dict] = field(default_factory=list)
    csrf_vulnerable: List[Dict] = field(default_factory=list)
    session_vulnerabilities: List[Dict] = field(default_factory=list)
    php_vulnerabilities: List[Dict] = field(default_factory=list)
    apache_vulnerabilities: List[Dict] = field(default_factory=list)
    risk_score: int = 0
    summary: str = ""
    platform_remediation: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# WEB SECURITY ANALYZER
# ============================================================

class WebSecurityAnalyzer:
    """Web security analyzer with platform-specific remediation"""
    
    def __init__(self, timeout: int = 10, typing_speed: str = 'fast'):
        self.timeout = timeout
        self.typer = TypeWriter(typing_speed)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'DSTERMINAL-Security-Analyzer/{VERSION}',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
        })
        
        self.sensitive_paths = [
            '/phpinfo.php', '/info.php', '/.htaccess', '/.htpasswd',
            '/robots.txt', '/config.php', '/.env', '/.git', '/backup.zip',
            '/dump.sql', '/admin', '/wp-admin', '/server-status',
            '/server-info', '/phpmyadmin', '/xmlrpc.php', '/wp-config.php'
        ]
        
        self.php_vulnerabilities = {
            '7.3.33': [
                ('CVE-2020-7070', 'Memory corruption vulnerability can lead to DoS', 'HIGH'),
                ('CVE-2020-7060', 'NULL pointer dereference in fileinfo extension', 'MEDIUM'),
                ('CVE-2020-7063', 'File read via path traversal in fileinfo', 'HIGH'),
                ('CVE-2019-11047', 'Buffer overflow in phar extension', 'HIGH'),
                ('CVE-2020-7064', 'Information disclosure in EXIF extension', 'MEDIUM'),
                ('CVE-2020-7065', 'Use-after-free in ODBC extension', 'HIGH'),
                ('CVE-2019-11045', 'Stack-based buffer overflow in imagick', 'HIGH'),
                ('CVE-2019-11046', 'Heap buffer overflow in JSON extension', 'HIGH'),
            ],
            '7.4.0': [
                ('CVE-2022-31625', 'Use-after-free in php_register_internal_extensions', 'HIGH'),
                ('CVE-2022-31626', 'FPM vulnerability allowing RCE', 'CRITICAL'),
                ('CVE-2021-21708', 'PHAR deserialization vulnerability', 'HIGH'),
            ],
            '8.0.0': [
                ('CVE-2021-21705', 'Use-after-free in filter_var()', 'HIGH'),
                ('CVE-2021-21704', 'Denial of service in PHP-FPM', 'MEDIUM'),
                ('CVE-2021-21707', 'Heap buffer overflow in php_mb_convert_encoding', 'HIGH'),
            ],
            '8.1.0': [
                ('CVE-2022-31627', 'Heap buffer overflow in ext/standard/url.c', 'HIGH'),
                ('CVE-2022-31628', 'Use-after-free in ext/standard/url.c', 'HIGH'),
                ('CVE-2022-31629', 'Denial of service in ext/spl/spl_array.c', 'MEDIUM'),
            ]
        }
        
        self.apache_vulnerabilities = {
            '2.4.37': [
                ('CVE-2018-17199', 'DoS via mod_session', 'MEDIUM'),
                ('CVE-2018-1303', 'Privilege escalation in mod_cache_socache', 'HIGH'),
                ('CVE-2018-1283', 'DoS in mod_mime', 'MEDIUM'),
                ('CVE-2018-11763', 'DoS in mod_http2', 'MEDIUM'),
                ('CVE-2018-1333', 'Information disclosure via mod_negotiation', 'MEDIUM'),
                ('CVE-2018-1301', 'Server-Side Request Forgery in mod_rewrite', 'HIGH'),
            ],
            '2.4.50': [
                ('CVE-2021-42013', 'Path traversal and RCE (critical)', 'CRITICAL'),
                ('CVE-2021-41773', 'Path traversal (critical)', 'CRITICAL'),
                ('CVE-2021-40438', 'Server-Side Request Forgery', 'HIGH'),
            ],
            '2.4.51': [
                ('CVE-2021-42013', 'Path traversal and RCE (critical)', 'CRITICAL'),
                ('CVE-2021-41773', 'Path traversal (critical)', 'CRITICAL'),
            ]
        }

    def analyze(self, url: str) -> WebSecurityReport:
        """Perform comprehensive analysis with platform-specific remediation"""
        report = WebSecurityReport(
            url=url,
            timestamp=datetime.now().isoformat()
        )
        
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            
            # Headers
            report.headers = dict(response.headers)
            report.server_info = {
                'server': response.headers.get('Server', 'Unknown'),
                'powered_by': response.headers.get('X-Powered-By', 'Unknown'),
                'status_code': response.status_code,
                'content_type': response.headers.get('Content-Type', 'Unknown'),
            }
            
            # Technologies
            self._detect_technologies(response.text, response.headers, report)
            
            # Generate platform-specific remediation
            report.platform_remediation = PlatformRemediationGenerator.get_platform_configs(
                report.server_info,
                report.technologies
            )
            
            # Security headers with remediation
            self._check_security_headers(response.headers, report)
            
            # Cookies with remediation
            self._analyze_cookies(response, report)
            
            # Forms with remediation
            self._analyze_forms(response.text, url, report)
            
            # Sensitive paths with remediation
            self._scan_sensitive_paths(url, report)
            
            # PHP vulnerabilities
            self._check_php_vulnerabilities(report)
            
            # Apache vulnerabilities
            self._check_apache_vulnerabilities(report)
            
            # Generate summary with remediation
            self._generate_summary(report)
            
        except Exception as e:
            report.findings.append(SecurityFinding(
                category='Error',
                severity='INFO',
                title='Analysis Error',
                description=str(e),
                recommendation='Check URL and try again',
                remediation_configs={}
            ))
        
        return report
    
    def _check_security_headers(self, headers: Dict, report: WebSecurityReport):
        """Check security headers and add remediation configurations"""
        header_configs = {
            'X-Frame-Options': {
                'description': 'Prevents clickjacking attacks by controlling if your site can be embedded in frames.',
                'recommendation': 'Add X-Frame-Options: DENY or X-Frame-Options: SAMEORIGIN'
            },
            'X-XSS-Protection': {
                'description': 'Enables browser built-in XSS protection.',
                'recommendation': 'Add X-XSS-Protection: 1; mode=block'
            },
            'X-Content-Type-Options': {
                'description': 'Prevents MIME type sniffing which can lead to XSS attacks.',
                'recommendation': 'Add X-Content-Type-Options: nosniff'
            },
            'Strict-Transport-Security': {
                'description': 'Forces HTTPS connections and prevents SSL stripping attacks.',
                'recommendation': 'Add Strict-Transport-Security: max-age=31536000; includeSubDomains; preload'
            },
            'Content-Security-Policy': {
                'description': 'Helps prevent XSS attacks by controlling what resources can be loaded.',
                'recommendation': 'Implement a Content-Security-Policy header'
            },
            'Referrer-Policy': {
                'description': 'Controls what referrer information is sent with requests.',
                'recommendation': 'Add Referrer-Policy: strict-origin-when-cross-origin'
            },
            'Permissions-Policy': {
                'description': 'Controls which browser features can be used.',
                'recommendation': 'Add Permissions-Policy: geolocation=(), microphone=(), camera=()'
            }
        }
        
        for header, config in header_configs.items():
            value = headers.get(header, 'Not Set')
            report.security_headers[header] = value
            
            if value == 'Not Set':
                # Get platform-specific remediation
                platform_config = report.platform_remediation.get('configs', {})
                security_config = platform_config.get('security_headers', {})
                
                finding = SecurityFinding(
                    category='Security Headers',
                    severity='MEDIUM',
                    title=f'Missing {header}',
                    description=f'{header} is missing. {config["description"]}',
                    recommendation=config['recommendation'],
                    remediation_configs={'security_headers': security_config},
                    fix_priority='HIGH' if header in ['X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options'] else 'MEDIUM'
                )
                report.findings.append(finding)
            elif header == 'X-Powered-By' and 'PHP' in value:
                # PHP version exposed
                version_match = re.search(r'PHP/([\d.]+)', value)
                if version_match:
                    platform_config = report.platform_remediation.get('configs', {})
                    language_config = platform_config.get('language_config', {})
                    
                    finding = SecurityFinding(
                        category='Information Disclosure',
                        severity='HIGH',
                        title=f'PHP Version Exposed: {version_match.group(1)}',
                        description=f'PHP version {version_match.group(1)} is exposed in X-Powered-By header.',
                        recommendation='Disable expose_php in php.ini and remove X-Powered-By header',
                        evidence=value,
                        remediation_configs={'language_config': language_config},
                        fix_priority='HIGH'
                    )
                    report.findings.append(finding)
    
    def _detect_technologies(self, html: str, headers: Dict, report: WebSecurityReport):
        """Detect technologies"""
        techs = []
        
        powered_by = headers.get('X-Powered-By', '')
        if 'PHP' in powered_by:
            techs.append(powered_by)
            # Check PHP version
            version_match = re.search(r'PHP/([\d.]+)', powered_by)
            if version_match:
                report.server_info['php_version'] = version_match.group(1)
                # Check if PHP is outdated
                major_version = int(version_match.group(1).split('.')[0])
                if major_version < 8:
                    platform_config = report.platform_remediation.get('configs', {})
                    language_config = platform_config.get('language_config', {})
                    
                    finding = SecurityFinding(
                        category='Vulnerability Assessment',
                        severity='HIGH',
                        title=f'Outdated PHP Version: {version_match.group(1)}',
                        description=f'PHP {version_match.group(1)} is outdated. PHP 7.x reached end-of-life.',
                        recommendation='Upgrade to PHP 8.1 or newer',
                        evidence=version_match.group(1),
                        remediation_configs={'language_config': language_config},
                        fix_priority='CRITICAL'
                    )
                    report.findings.append(finding)
        
        server = headers.get('Server', '')
        if 'Apache' in server:
            techs.append(server)
            # Check Apache version
            version_match = re.search(r'Apache/([\d.]+)', server)
            if version_match:
                report.server_info['apache_version'] = version_match.group(1)
                # Check if Apache is outdated
                major_version = int(version_match.group(1).split('.')[1])
                if major_version < 4:
                    platform_config = report.platform_remediation.get('configs', {})
                    security_config = platform_config.get('security_headers', {})
                    
                    finding = SecurityFinding(
                        category='Vulnerability Assessment',
                        severity='HIGH',
                        title=f'Outdated Apache Version: {version_match.group(1)}',
                        description=f'Apache {version_match.group(1)} is outdated.',
                        recommendation='Upgrade to latest Apache 2.4.x version',
                        evidence=version_match.group(1),
                        remediation_configs={'security_headers': security_config},
                        fix_priority='HIGH'
                    )
                    report.findings.append(finding)
        
        frameworks = {
            'WordPress': ['wp-content', 'wp-includes', 'wp-json'],
            'Laravel': ['laravel', 'csrf_token'],
            'Django': ['django', 'csrfmiddlewaretoken'],
            'Bootstrap': ['bootstrap.min.css', 'data-toggle'],
            'jQuery': ['jquery.min.js', '$('],
            'AdminLTE': ['AdminLTE.min.css', 'AdminLTE'],
            'React': ['react.min.js', '_reactRootContainer'],
            'Vue.js': ['vue.min.js', 'v-bind'],
        }
        
        for framework, patterns in frameworks.items():
            for pattern in patterns:
                if pattern in html:
                    techs.append(framework)
                    break
        
        if 'cf-turnstile' in html or 'challenges.cloudflare.com' in html:
            techs.append('Cloudflare Turnstile')
        
        if 'google-analytics' in html:
            techs.append('Google Analytics')
        
        report.technologies = techs
    
    def _analyze_cookies(self, response, report: WebSecurityReport):
        """Analyze cookies with remediation"""
        set_cookie_header = response.headers.get('Set-Cookie', '')
        
        for name, value in response.cookies.get_dict().items():
            cookie = {
                'name': name, 
                'value': value[:20] + '...' if len(value) > 20 else value,
                'secure': 'Secure' in set_cookie_header,
                'httponly': 'HttpOnly' in set_cookie_header,
                'samesite': 'SameSite' in set_cookie_header
            }
            
            # Check for insecure session cookies
            if 'PHPSESSID' in name or 'session' in name.lower():
                if 'Secure' not in set_cookie_header:
                    platform_config = report.platform_remediation.get('configs', {})
                    language_config = platform_config.get('language_config', {})
                    
                    finding = SecurityFinding(
                        category='Cookies',
                        severity='HIGH',
                        title=f'Insecure Session Cookie: {name}',
                        description='Session cookie missing Secure flag - can be intercepted over HTTP',
                        recommendation='Set Secure flag on session cookies',
                        evidence=f'Cookie: {name}, Value: {value[:10]}...',
                        remediation_configs={'language_config': language_config},
                        fix_priority='HIGH'
                    )
                    report.findings.append(finding)
                
                if 'HttpOnly' not in set_cookie_header:
                    platform_config = report.platform_remediation.get('configs', {})
                    language_config = platform_config.get('language_config', {})
                    
                    finding = SecurityFinding(
                        category='Cookies',
                        severity='MEDIUM',
                        title=f'Cookie Accessible by JavaScript: {name}',
                        description='Cookie missing HttpOnly flag - XSS risk',
                        recommendation='Set HttpOnly flag on cookies',
                        evidence=f'Cookie: {name}',
                        remediation_configs={'language_config': language_config},
                        fix_priority='MEDIUM'
                    )
                    report.findings.append(finding)
            
            report.cookies.append(cookie)
    
    def _analyze_forms(self, html: str, url: str, report: WebSecurityReport):
        """Analyze forms with remediation"""
        soup = BeautifulSoup(html, 'html.parser')
        
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'has_csrf': False,
                'has_password': False,
                'findings': []
            }
            
            for inp in form.find_all('input'):
                if inp.get('type') == 'password':
                    form_data['has_password'] = True
                if 'csrf' in inp.get('name', '').lower() or 'token' in inp.get('name', '').lower():
                    form_data['has_csrf'] = True
            
            if form_data['method'] == 'POST' and not form_data['has_csrf']:
                # Get framework-specific CSRF config
                framework = report.platform_remediation.get('platform', {}).get('framework', 'none')
                platform_config = report.platform_remediation.get('configs', {})
                framework_config = platform_config.get('framework_config', {})
                
                finding = SecurityFinding(
                    category='Forms',
                    severity='HIGH',
                    title='Missing CSRF Protection',
                    description='POST form lacks CSRF token - vulnerable to CSRF attacks',
                    recommendation='Implement CSRF tokens for all state-changing requests',
                    evidence=f'Form action: {form_data["action"]}',
                    remediation_configs={'framework_config': framework_config},
                    fix_priority='HIGH'
                )
                report.findings.append(finding)
                form_data['findings'].append('Missing CSRF token')
            
            if form_data['has_password'] and not url.startswith('https'):
                platform_config = report.platform_remediation.get('configs', {})
                security_config = platform_config.get('security_headers', {})
                
                finding = SecurityFinding(
                    category='Forms',
                    severity='CRITICAL',
                    title='Login Form Over HTTP',
                    description='Password form submitted over HTTP - credentials exposed in plain text',
                    recommendation='Use HTTPS for all login forms and enforce HSTS',
                    evidence=f'Form action: {form_data["action"]}',
                    remediation_configs={'security_headers': security_config},
                    fix_priority='CRITICAL'
                )
                report.findings.append(finding)
                form_data['findings'].append('Login over HTTP')
            
            report.forms.append(form_data)
    
    def _scan_sensitive_paths(self, url: str, report: WebSecurityReport):
        """Scan for sensitive paths with remediation"""
        for path in self.sensitive_paths:
            try:
                test_url = urljoin(url, path)
                response = self.session.get(test_url, timeout=self.timeout, verify=False, allow_redirects=False)
                if response.status_code == 200:
                    report.exposed_files.append(test_url)
                    
                    # Determine severity
                    severity = 'CRITICAL'
                    if any(p in path for p in ['config', '.env', 'wp-config', '.htpasswd']):
                        severity = 'CRITICAL'
                    elif any(p in path for p in ['.git', '.svn', 'backup', 'dump']):
                        severity = 'HIGH'
                    elif any(p in path for p in ['phpinfo', 'info.php', 'server-status']):
                        severity = 'MEDIUM'
                    else:
                        severity = 'LOW'
                    
                    # Get platform-specific remediation
                    platform_config = report.platform_remediation.get('configs', {})
                    security_config = platform_config.get('security_headers', {})
                    
                    if severity == 'CRITICAL' or severity == 'HIGH':
                        finding = SecurityFinding(
                            category='Exposed Files',
                            severity=severity,
                            title=f'Exposed File: {path}',
                            description=f'{path} is accessible and may contain sensitive information.',
                            recommendation='Remove sensitive files from web root or restrict access',
                            evidence=test_url,
                            remediation_configs={'security_headers': security_config},
                            fix_priority='CRITICAL' if severity == 'CRITICAL' else 'HIGH'
                        )
                        report.findings.append(finding)
            except:
                pass
    
    def _check_php_vulnerabilities(self, report: WebSecurityReport):
        """Check PHP vulnerabilities"""
        php_version = report.server_info.get('php_version', '')
        if php_version:
            for version, vulns in self.php_vulnerabilities.items():
                if php_version.startswith(version[:3]):
                    platform_config = report.platform_remediation.get('configs', {})
                    language_config = platform_config.get('language_config', {})
                    
                    for cve, desc, severity in vulns:
                        finding = SecurityFinding(
                            category='PHP Security',
                            severity=severity,
                            title=f'PHP {php_version} Vulnerability: {cve}',
                            description=f'{cve}: {desc}',
                            recommendation=f'Update PHP from {php_version} to latest version (8.2+)',
                            cve=cve,
                            evidence=php_version,
                            remediation_configs={'language_config': language_config},
                            fix_priority='CRITICAL' if severity == 'CRITICAL' else 'HIGH'
                        )
                        report.findings.append(finding)
                    break
    
    def _check_apache_vulnerabilities(self, report: WebSecurityReport):
        """Check Apache vulnerabilities"""
        apache_version = report.server_info.get('apache_version', '')
        if apache_version:
            for version, vulns in self.apache_vulnerabilities.items():
                if apache_version.startswith(version):
                    platform_config = report.platform_remediation.get('configs', {})
                    security_config = platform_config.get('security_headers', {})
                    
                    for cve, desc, severity in vulns:
                        finding = SecurityFinding(
                            category='Apache Security',
                            severity=severity,
                            title=f'Apache {apache_version} Vulnerability: {cve}',
                            description=f'{cve}: {desc}',
                            recommendation=f'Update Apache from {apache_version} to latest version',
                            cve=cve,
                            evidence=apache_version,
                            remediation_configs={'security_headers': security_config},
                            fix_priority='CRITICAL' if severity == 'CRITICAL' else 'HIGH'
                        )
                        report.findings.append(finding)
                    break
    
    def _generate_summary(self, report: WebSecurityReport):
        """Generate summary with platform remediation"""
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        for finding in report.findings:
            severity_counts[finding.severity] += 1
        
        report.risk_score = min(
            severity_counts['CRITICAL'] * 25 +
            severity_counts['HIGH'] * 15 +
            severity_counts['MEDIUM'] * 8 +
            severity_counts['LOW'] * 3,
            100
        )
        
        priority_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in report.findings:
            priority = getattr(finding, 'fix_priority', 'MEDIUM')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        platform = report.platform_remediation.get('platform', {})
        platform_info = f"""
Platform Information:
  - Web Server: {platform.get('webserver', 'Unknown')}
  - OS: {platform.get('os', 'Unknown')}
  - Language: {platform.get('language', 'Unknown')}
  - Framework: {platform.get('framework', 'None detected')}
  - Cloud Provider: {platform.get('cloud_provider', 'None detected')}
"""
        
        report.summary = f"""
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY ANALYSIS SUMMARY                 │
├─────────────────────────────────────────────────────────────┤
│ Target: {report.url}                                        │
│ Risk Score: {report.risk_score}/100                         │
│                                                             │
│ Findings by Severity:                                       │
│  • CRITICAL: {severity_counts['CRITICAL']}                  │
│  • HIGH: {severity_counts['HIGH']}                          │
│  • MEDIUM: {severity_counts['MEDIUM']}                      │
│  • LOW: {severity_counts['LOW']}                            │
│  • INFO: {severity_counts['INFO']}                          │
│                                                             │
│ Fix Priority:                                               │
│  • CRITICAL (Fix Now): {priority_counts['CRITICAL']}        │
│  • HIGH (Fix ASAP): {priority_counts['HIGH']}               │
│  • MEDIUM (Plan Next): {priority_counts['MEDIUM']}          │
│  • LOW (Consider Later): {priority_counts['LOW']}           │
│                                                             │
│ {platform_info}                                             │
│ Technologies: {', '.join(report.technologies) if report.technologies else 'None'} │
│ Exposed Files: {len(report.exposed_files)}                  │
│ Security Headers Present: {sum(1 for v in report.security_headers.values() if v != 'Not Set')}/{len(report.security_headers)} │
│ Forms Analyzed: {len(report.forms)}                         │
└─────────────────────────────────────────────────────────────┘
"""
    
    def cmd_scan_xss(self, url: str) -> List[Dict]:
        """Scan for XSS"""
        results = []
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for form in soup.find_all('form'):
                action = form.get('action', '')
                method = form.get('method', 'GET').upper()
                fields = {inp.get('name'): inp.get('value', '') for inp in form.find_all('input') if inp.get('name')}
                
                for field in fields.keys():
                    for payload in XSS_PAYLOADS[:3]:
                        test_data = fields.copy()
                        test_data[field] = payload
                        
                        if method == 'POST':
                            test_url = urljoin(url, action)
                            test_response = self.session.post(test_url, data=test_data, timeout=self.timeout, verify=False)
                        else:
                            test_url = urljoin(url, action) + '?' + '&'.join([f'{k}={quote(str(v))}' for k, v in test_data.items()])
                            test_response = self.session.get(test_url, timeout=self.timeout, verify=False)
                        
                        if payload in test_response.text:
                            results.append({
                                'field': field,
                                'payload': payload,
                                'vulnerable': True
                            })
                            break
        except:
            pass
        return results
    
    def cmd_scan_csrf(self, url: str) -> List[Dict]:
        """Scan for CSRF"""
        results = []
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for form in soup.find_all('form'):
                if form.get('method', 'GET').upper() != 'POST':
                    continue
                
                has_csrf = any(
                    'csrf' in inp.get('name', '').lower() 
                    for inp in form.find_all('input')
                )
                
                results.append({
                    'form_action': form.get('action', ''),
                    'has_csrf': has_csrf,
                    'vulnerable': not has_csrf
                })
        except:
            pass
        return results
    
    def cmd_scan_session(self, url: str) -> List[Dict]:
        """Scan session vulnerabilities"""
        results = []
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            for name, value in response.cookies.get_dict().items():
                finding = {'cookie': name, 'vulnerabilities': []}
                set_cookie = response.headers.get('Set-Cookie', '')
                
                if 'Secure' not in set_cookie:
                    finding['vulnerabilities'].append('Missing Secure flag')
                if 'HttpOnly' not in set_cookie:
                    finding['vulnerabilities'].append('Missing HttpOnly flag')
                
                if finding['vulnerabilities']:
                    results.append(finding)
        except:
            pass
        return results
    
    def cmd_scan_php(self, url: str) -> List[Dict]:
        """Scan PHP vulnerabilities"""
        results = []
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            powered_by = response.headers.get('X-Powered-By', '')
            match = re.search(r'PHP/([\d.]+)', powered_by)
            if match:
                results.append({
                    'type': 'PHP Version',
                    'version': match.group(1),
                    'severity': 'INFO'
                })
        except:
            pass
        return results
    
    def cmd_scan_apache(self, url: str) -> List[Dict]:
        """Scan Apache vulnerabilities"""
        results = []
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            server = response.headers.get('Server', '')
            match = re.search(r'Apache/([\d.]+)', server)
            if match:
                results.append({
                    'type': 'Apache Version',
                    'version': match.group(1),
                    'severity': 'INFO'
                })
        except:
            pass
        return results
    
    def cmd_scan_headers(self, url: str) -> Dict:
        """Scan headers"""
        result = {'url': url, 'headers': {}, 'security_headers': {}}
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            result['headers'] = dict(response.headers)
            for header in ['X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options', 'Strict-Transport-Security']:
                result['security_headers'][header] = response.headers.get(header, 'Not Set')
        except:
            pass
        return result
    
    def cmd_scan_technologies(self, url: str) -> List[str]:
        """Scan technologies"""
        techs = []
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            html = response.text
            headers = response.headers
            
            if 'X-Powered-By' in headers:
                techs.append(f"Powered by: {headers['X-Powered-By']}")
            if 'Server' in headers:
                techs.append(f"Server: {headers['Server']}")
            
            frameworks = {
                'WordPress': ['wp-content', 'wp-includes'],
                'Laravel': ['laravel', 'csrf_token'],
                'Django': ['django', 'csrfmiddlewaretoken'],
                'Bootstrap': ['bootstrap.min.css', 'data-toggle'],
                'AdminLTE': ['AdminLTE.min.css', 'AdminLTE'],
            }
            for framework, patterns in frameworks.items():
                for pattern in patterns:
                    if pattern in html:
                        techs.append(framework)
                        break
        except:
            pass
        return techs

    def print_report_with_pen(self, report: WebSecurityReport, verbose: bool = True):
        """Print the security report with human-like pen typing effects"""
        
        # Banner with fast typing
        banner_lines = [
            "╔═══════════════════════════════════════════════════════════════════╗",
            "║  🔐 WEB SECURITY ANALYSIS REPORT                                  ║",
            "║  Generated by DSTERMINAL Security Suite v3.1.113                  ║",
            "╚═══════════════════════════════════════════════════════════════════╝"
        ]
        self.typer.type_banner(banner_lines, color=Colors.CYAN)
        print()
        
        # Header info with medium speed
        self.typer.type_text(f"Target: {report.url}", color=Colors.YELLOW, pen_effect=True)
        self.typer.type_text(f"Timestamp: {report.timestamp}", color=Colors.DIM, pen_effect=True)
        self.typer.type_text(f"Risk Score: {report.risk_score}/100", 
                            color=Colors.RED if report.risk_score > 70 else Colors.YELLOW if report.risk_score > 40 else Colors.GREEN,
                            pen_effect=True)
        print()
        
        # Platform Information
        platform = report.platform_remediation.get('platform', {})
        self.typer.type_text("┌─ PLATFORM DETECTED ──────────────────────────────────", color=Colors.CYAN)
        self.typer.type_text(f"│ Web Server: {platform.get('webserver', 'Unknown')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ OS: {platform.get('os', 'Unknown')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ Language: {platform.get('language', 'Unknown')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ Framework: {platform.get('framework', 'None detected')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ Cloud Provider: {platform.get('cloud_provider', 'None detected')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text("└─────────────────────────────────────────────────────────", color=Colors.CYAN)
        print()
        
        # Technologies
        if report.technologies:
            self.typer.type_text("┌─ TECHNOLOGIES DETECTED ──────────────────────────", color=Colors.MAGENTA)
            for tech in report.technologies:
                self.typer.type_text(f"│ • {tech}", color=Colors.CYAN, pen_effect=True)
            self.typer.type_text("└─────────────────────────────────────────────────────────", color=Colors.MAGENTA)
            print()
        
        # Findings Summary
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        for finding in report.findings:
            severity_counts[finding.severity] += 1
        
        self.typer.type_text("┌─ FINDINGS SUMMARY ──────────────────────────────────", color=Colors.YELLOW)
        self.typer.type_text(f"│ CRITICAL: {severity_counts['CRITICAL']}", color=Colors.RED, pen_effect=True)
        self.typer.type_text(f"│ HIGH: {severity_counts['HIGH']}", color=Colors.RED, pen_effect=True)
        self.typer.type_text(f"│ MEDIUM: {severity_counts['MEDIUM']}", color=Colors.YELLOW, pen_effect=True)
        self.typer.type_text(f"│ LOW: {severity_counts['LOW']}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ INFO: {severity_counts['INFO']}", color=Colors.CYAN, pen_effect=True)
        self.typer.type_text("└─────────────────────────────────────────────────────────", color=Colors.YELLOW)
        print()
        
        # Detailed Findings (only show first 5 if verbose)
        if verbose:
            self.typer.type_text("┌─ DETAILED FINDINGS ──────────────────────────────", color=Colors.CYAN)
            
            # Sort findings by severity
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
            sorted_findings = sorted(report.findings, key=lambda x: severity_order.get(x.severity, 5))
            
            for i, finding in enumerate(sorted_findings[:5]):  # Show top 5
                severity_color = Colors.RED if finding.severity in ['CRITICAL', 'HIGH'] else Colors.YELLOW if finding.severity == 'MEDIUM' else Colors.GREEN
                
                self.typer.type_text(f"│ ◉ {finding.severity} {finding.title}", color=severity_color, pen_effect=True)
                
                # Type description slowly
                if hasattr(finding, 'description'):
                    self.typer.type_text(f"│    {finding.description[:80]}...", color=Colors.DIM, pen_effect=True)
                
                # Show fix priority
                priority = getattr(finding, 'fix_priority', 'MEDIUM')
                priority_color = Colors.RED if priority == 'CRITICAL' else Colors.YELLOW if priority == 'HIGH' else Colors.GREEN
                self.typer.type_text(f"│    Priority: {priority}", color=priority_color, pen_effect=True)
                
                if hasattr(finding, 'recommendation'):
                    self.typer.type_text(f"│    Fix: {finding.recommendation[:60]}...", color=Colors.GREEN, pen_effect=True)
                
                # Show if platform remediation available
                if finding.remediation_configs:
                    self.typer.type_text(f"│    ✓ Platform-specific remediation available", color=Colors.CYAN, pen_effect=True)
                
                if i < len(sorted_findings[:5]) - 1:
                    self.typer.type_text("│", color=Colors.DIM)
                    time.sleep(0.15)
            
            if len(sorted_findings) > 5:
                self.typer.type_text(f"│ ... and {len(sorted_findings) - 5} more findings", color=Colors.DIM, pen_effect=True)
            
            self.typer.type_text("└─────────────────────────────────────────────────────────", color=Colors.CYAN)
            print()
        
        # Security Headers
        headers_present = sum(1 for v in report.security_headers.values() if v != 'Not Set')
        total_headers = len(report.security_headers)
        self.typer.type_text(f"Security Headers: {headers_present}/{total_headers} present", 
                            color=Colors.GREEN if headers_present == total_headers else Colors.YELLOW,
                            pen_effect=True)
        
        # Exposed Files
        if report.exposed_files:
            self.typer.type_text(f"⚠️  Exposed Files: {len(report.exposed_files)}", 
                                color=Colors.RED, pen_effect=True)
            for file in report.exposed_files[:3]:
                self.typer.type_text(f"   • {file}", color=Colors.DIM, pen_effect=True)
            if len(report.exposed_files) > 3:
                self.typer.type_text(f"   ... and {len(report.exposed_files) - 3} more", color=Colors.DIM, pen_effect=True)
        
        # Wait for user
        self.typer.type_text("\n" + "─" * 50, color=Colors.DIM)
        self.typer.type_text("Press Enter to continue...", color=Colors.YELLOW, pen_effect=True)
        

# ============================================================
# ENHANCED PDF REPORT GENERATOR WITH PLATFORM REMEDIATION
# ============================================================

class PDFReportGenerator:
    """Generate PDF reports with platform-specific remediation configurations"""
    
    def __init__(self):
        self.export_dir = os.path.expanduser("~/DSTerminal_Workspace/reports")
        os.makedirs(self.export_dir, exist_ok=True)
    
    def generate_report(self, report: WebSecurityReport, filename: str = None) -> Optional[str]:
        """Generate PDF report with platform-specific remediation"""
        if not REPORTLAB_AVAILABLE:
            print("[red]❌ ReportLab not installed. Install: pip install reportlab[/red]")
            return None
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.export_dir, f"security_report_{timestamp}.pdf")
            
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
                title=f"Security Analysis Report - {report.url}"
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0066cc'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                spaceAfter=10
            )
            
            heading_style = ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#004d99'),
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            )
            
            subheading_style = ParagraphStyle(
                'SubHeading',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=colors.HexColor('#0066cc'),
                spaceAfter=8,
                spaceBefore=10,
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
                fontSize=8,
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
            
            # Watermark
            def add_watermark(canvas_obj, doc_obj):
                canvas_obj.saveState()
                canvas_obj.setFillColor(colors.HexColor('#cccccc'))
                canvas_obj.setFont('Helvetica-Bold', 50)
                canvas_obj.rotate(45)
                canvas_obj.drawString(150, 100, WATERMARK_TEXT)
                canvas_obj.setFillColor(colors.HexColor('#dddddd'))
                canvas_obj.setFont('Helvetica', 25)
                canvas_obj.rotate(-30)
                canvas_obj.drawString(400, -50, WATERMARK_TEXT)
                canvas_obj.restoreState()
            
            # ================================================================
            # 1. EXECUTIVE SUMMARY
            # ================================================================
            story.append(Paragraph("Web Security Analysis Report", title_style))
            story.append(Paragraph(f"Target: {report.url}", subtitle_style))
            story.append(Paragraph(f"Generated: {report.timestamp}", subtitle_style))
            story.append(Spacer(1, 12))
            
            # Risk Score
            risk_color = colors.HexColor('#00ff00')
            if report.risk_score >= 70:
                risk_color = colors.HexColor('#ff0000')
            elif report.risk_score >= 40:
                risk_color = colors.HexColor('#ff8800')
            
            risk_style = ParagraphStyle(
                'Risk',
                parent=styles['Normal'],
                fontSize=16,
                textColor=risk_color,
                alignment=TA_CENTER,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(f"Risk Score: {report.risk_score}/100", risk_style))
            story.append(Spacer(1, 10))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))
            summary_lines = report.summary.split('\n')
            for line in summary_lines:
                if line.strip():
                    story.append(Paragraph(line.strip(), body_style))
            story.append(Spacer(1, 10))
            
            # ================================================================
            # 2. SERVER INFORMATION
            # ================================================================
            story.append(PageBreak())
            story.append(Paragraph("Server Information", heading_style))
            
            server_info_data = [
                ["Server", report.server_info.get('server', 'Unknown')],
                ["Powered By", report.server_info.get('powered_by', 'Unknown')],
                ["Status Code", str(report.server_info.get('status_code', 'Unknown'))],
                ["Content Type", report.server_info.get('content_type', 'Unknown')],
            ]
            
            if 'php_version' in report.server_info:
                server_info_data.append(["PHP Version", report.server_info['php_version']])
            if 'apache_version' in report.server_info:
                server_info_data.append(["Apache Version", report.server_info['apache_version']])
            
            server_table = PDFTable(server_info_data, colWidths=[2*inch, 4*inch])
            server_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(server_table)
            story.append(Spacer(1, 10))
            
            # ================================================================
            # 3. TECHNOLOGIES DETECTED
            # ================================================================
            if report.technologies:
                story.append(Paragraph("Technologies Detected", heading_style))
                tech_text = ", ".join(report.technologies)
                story.append(Paragraph(tech_text, body_style))
                story.append(Spacer(1, 10))
            
            # ================================================================
            # 4. SECURITY HEADERS
            # ================================================================
            if report.security_headers:
                story.append(Paragraph("Security Headers", heading_style))
                header_data = [["Header", "Value", "Status"]]
                for header, value in report.security_headers.items():
                    status = "✅ Set" if value != 'Not Set' else "❌ Missing"
                    header_data.append([header, value[:40], status])
                
                if len(header_data) > 1:
                    header_table = PDFTable(header_data, colWidths=[2*inch, 3*inch, 1.5*inch])
                    header_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('TOPPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ]))
                    story.append(header_table)
                    story.append(Spacer(1, 10))
            
            # ================================================================
            # 5. PLATFORM-SPECIFIC REMEDIATION CONFIGURATIONS
            # ================================================================
            story.append(PageBreak())
            story.append(Paragraph("Platform-Specific Remediation Configurations", heading_style))
            
            platform = report.platform_remediation.get('platform', {})
            configs = report.platform_remediation.get('configs', {})
            
            # Platform Information
            story.append(Paragraph("Detected Platform", subheading_style))
            platform_info = [
                f"Web Server: {platform.get('webserver', 'Unknown')}",
                f"Operating System: {platform.get('os', 'Unknown')}",
                f"Language: {platform.get('language', 'Unknown')}",
                f"Framework: {platform.get('framework', 'None detected')}",
                f"Cloud Provider: {platform.get('cloud_provider', 'None detected')}",
            ]
            for info in platform_info:
                story.append(Paragraph(f"• {info}", body_style))
            story.append(Spacer(1, 10))
            
            # Security Headers Configuration
            if 'security_headers' in configs:
                story.append(Paragraph("Security Headers Configuration", subheading_style))
                sec_config = configs['security_headers']
                story.append(Paragraph(f"<b>{sec_config.get('title', 'Configuration')}</b>", body_style))
                
                # Code
                if sec_config.get('code'):
                    code_lines = sec_config['code'].split('\n')
                    story.append(Paragraph("<i>Configuration Code:</i>", body_style))
                    for line in code_lines:
                        if line.strip():
                            story.append(Paragraph(f"  {line}", code_style))
                
                # Commands
                if sec_config.get('commands'):
                    story.append(Paragraph("<i>Commands to Apply:</i>", body_style))
                    for cmd in sec_config.get('commands', []):
                        if cmd.strip():
                            story.append(Paragraph(f"  $ {cmd}", code_style))
                story.append(Spacer(1, 8))
            
            # Language Configuration
            if 'language_config' in configs:
                story.append(Paragraph("Language-Specific Configuration", subheading_style))
                lang_config = configs['language_config']
                story.append(Paragraph(f"<b>{lang_config.get('title', 'Configuration')}</b>", body_style))
                
                if lang_config.get('code'):
                    code_lines = lang_config['code'].split('\n')
                    story.append(Paragraph("<i>Configuration Code:</i>", body_style))
                    for line in code_lines:
                        if line.strip():
                            story.append(Paragraph(f"  {line}", code_style))
                
                if lang_config.get('commands'):
                    story.append(Paragraph("<i>Commands to Apply:</i>", body_style))
                    for cmd in lang_config.get('commands', []):
                        if cmd.strip():
                            story.append(Paragraph(f"  $ {cmd}", code_style))
                story.append(Spacer(1, 8))
            
            # Framework Configuration
            if 'framework_config' in configs:
                story.append(Paragraph("Framework-Specific Configuration", subheading_style))
                fw_config = configs['framework_config']
                story.append(Paragraph(f"<b>{fw_config.get('title', 'Configuration')}</b>", body_style))
                
                if fw_config.get('code'):
                    code_lines = fw_config['code'].split('\n')
                    story.append(Paragraph("<i>Configuration Code:</i>", body_style))
                    for line in code_lines:
                        if line.strip():
                            story.append(Paragraph(f"  {line}", code_style))
                
                if fw_config.get('commands'):
                    story.append(Paragraph("<i>Commands to Apply:</i>", body_style))
                    for cmd in fw_config.get('commands', []):
                        if cmd.strip():
                            story.append(Paragraph(f"  $ {cmd}", code_style))
                story.append(Spacer(1, 8))
            
            # OS Commands
            if 'os_commands' in configs:
                story.append(Paragraph("System Commands", subheading_style))
                os_config = configs['os_commands']
                story.append(Paragraph(f"<b>{os_config.get('title', 'Commands')}</b>", body_style))
                
                if os_config.get('code'):
                    code_lines = os_config['code'].split('\n')
                    story.append(Paragraph("<i>Commands:</i>", body_style))
                    for line in code_lines:
                        if line.strip():
                            story.append(Paragraph(f"  {line}", code_style))
                story.append(Spacer(1, 8))
            
            # Cloud Configuration
            if 'cloud_config' in configs:
                story.append(Paragraph("Cloud Provider Configuration", subheading_style))
                cloud_config = configs['cloud_config']
                story.append(Paragraph(f"<b>{cloud_config.get('title', 'Configuration')}</b>", body_style))
                
                if cloud_config.get('code'):
                    code_lines = cloud_config['code'].split('\n')
                    story.append(Paragraph("<i>Configuration Steps:</i>", body_style))
                    for line in code_lines:
                        if line.strip():
                            story.append(Paragraph(f"  {line}", code_style))
                
                if cloud_config.get('commands'):
                    story.append(Paragraph("<i>Verification Commands:</i>", body_style))
                    for cmd in cloud_config.get('commands', []):
                        if cmd.strip():
                            story.append(Paragraph(f"  $ {cmd}", code_style))
                story.append(Spacer(1, 8))
            
            # ================================================================
            # 6. SECURITY FINDINGS WITH REMEDIATION
            # ================================================================
            if report.findings:
                story.append(PageBreak())
                story.append(Paragraph("Security Findings & Remediation", heading_style))
                
                for i, finding in enumerate(report.findings, 1):
                    # Severity color
                    severity_color = colors.HexColor('#ff8800')
                    if finding.severity == 'CRITICAL':
                        severity_color = colors.HexColor('#ff0000')
                    elif finding.severity == 'HIGH':
                        severity_color = colors.HexColor('#ff4444')
                    elif finding.severity == 'MEDIUM':
                        severity_color = colors.HexColor('#ff8800')
                    elif finding.severity == 'LOW':
                        severity_color = colors.HexColor('#00aa00')
                    else:
                        severity_color = colors.HexColor('#888888')
                    
                    # Finding header
                    story.append(Paragraph(f"Finding #{i}: {finding.title}", subheading_style))
                    story.append(Paragraph(f"<b>Severity:</b> {finding.severity}", body_style))
                    story.append(Paragraph(f"<b>Category:</b> {finding.category}", body_style))
                    story.append(Paragraph(f"<b>Description:</b> {finding.description}", body_style))
                    story.append(Paragraph(f"<b>Recommendation:</b> {finding.recommendation}", body_style))
                    if finding.cve:
                        story.append(Paragraph(f"<b>CVE:</b> {finding.cve}", body_style))
                    if finding.evidence:
                        story.append(Paragraph(f"<b>Evidence:</b> {finding.evidence}", body_style))
                    if hasattr(finding, 'fix_priority'):
                        story.append(Paragraph(f"<b>Fix Priority:</b> {finding.fix_priority}", body_style))
                    
                    # Remediation Configurations
                    if finding.remediation_configs:
                        story.append(Paragraph("<b>Platform-Specific Remediation:</b>", body_style))
                        story.append(Spacer(1, 4))
                        
                        for config_type, config_data in finding.remediation_configs.items():
                            if config_data:
                                story.append(Paragraph(f"<b>{config_data.get('title', config_type)}:</b>", body_style))
                                
                                if config_data.get('code'):
                                    code_lines = config_data['code'].split('\n')
                                    for line in code_lines[:20]:
                                        if line.strip():
                                            story.append(Paragraph(f"  {line}", code_style))
                                    if len(code_lines) > 20:
                                        story.append(Paragraph("  ... (see full config above)", code_style))
                                
                                if config_data.get('commands'):
                                    story.append(Paragraph("<i>Commands:</i>", body_style))
                                    for cmd in config_data.get('commands', [])[:5]:
                                        if cmd.strip():
                                            story.append(Paragraph(f"  $ {cmd}", code_style))
                                
                                story.append(Spacer(1, 4))
                    
                    story.append(Spacer(1, 8))
            
            # ================================================================
            # FOOTER
            # ================================================================
            story.append(Spacer(1, 30))
            story.append(Paragraph("─" * 80, footer_style))
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"© 2024 {PLATFORM} | All Rights Reserved", footer_style))
            story.append(Paragraph("This report is for AUTHORIZED SECURITY TESTING & EDUCATIONAL PURPOSES only. Use it responsibly.", footer_style))
            story.append(Paragraph(f"Generated by DSTERMINAL Security Analyzer {VERSION}", footer_style))
            
            doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
            print(f"[green]✅ PDF Report generated: {filename}[/green]")
            return filename
            
        except Exception as e:
            print(f"[red]❌ PDF generation failed: {str(e)}[/red]")
            return None


# ============================================================
# MAIN DASHBOARD
# ============================================================

class SecurityDashboard:
    """Interactive dashboard with hacker-style layout"""
    
    def __init__(self):
        self.console = Console()
        self.analyzer = WebSecurityAnalyzer()
        self.current_report = None
        self.scan_history = []
        self.is_running = False
        self._start_time = datetime.now()
        self.pdf_generator = PDFReportGenerator()
        self.target_url = None
        
        # Create a typer instance for dashboard typing effects
        self.typer = TypeWriter('fast')
        
        # Color scheme
        self.colors = {
            'primary': 'bright_green',
            'secondary': 'green', 
            'accent': 'bright_red',
            'warning': 'yellow',
            'danger': 'red',
            'info': 'cyan',
            'dim': 'dim',
            'success': 'green',
        }
    def print_scan_start(self):
        """Print scan start with pen typing effect - Minimal version"""
        
        # Make sure we have a typer
        if not hasattr(self, 'typer'):
            self.typer = TypeWriter('fast')
        
        
        # Main scan announcement with pen effect
        self.typer.type_text("🚀 Starting Full Security Scan", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"Target: {self.target_url}", color=Colors.CYAN, pen_effect=True)
        print()   
        
    def run(self):
        """Run the interactive dashboard"""
        self._clear_screen()
        self._show_centered_banner()
        
        while True:
            try:
                self._show_main_layout()
                choice = Prompt.ask(
                    f"\n[{self.colors['primary']}]┌─[/{self.colors['primary']}]"
                    f"[{self.colors['info']}] Select Option [/{self.colors['info']}]"
                    f"[{self.colors['primary']}]─►[/{self.colors['primary']}]",
                    choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "h", "q"],
                    default="h"
                )
                
                if choice == "q":
                    self._exit_dashboard()
                    break
                elif choice == "h":
                    self._show_help()
                elif choice == "1":
                    self._full_scan()
                elif choice == "2":
                    self._scan_headers()
                elif choice == "3":
                    self._scan_technologies()
                elif choice == "4":
                    self._scan_xss()
                elif choice == "5":
                    self._scan_csrf()
                elif choice == "6":
                    self._scan_session()
                elif choice == "7":
                    self._scan_php()
                elif choice == "8":
                    self._scan_apache()
                elif choice == "9":
                    self._export_report()
                else:
                    self._show_help()
                    
            except KeyboardInterrupt:
                self._exit_dashboard()
                break
            except Exception as e:
                self._show_error(str(e))
    
    def _clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _get_centered_banner(self) -> Panel:
        """Generate centered hacker-style banner"""
        banner_text = """
    [bold green]██████╗ ███████╗████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗[/bold green]
    [bold green]██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║[/bold green]
    [bold green]██║  ██║███████╗   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║[/bold green]
    [bold green]██║  ██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║╚═╝[/bold green]
    [bold green]██████╔╝███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║██╗[/bold green]
    [bold green]╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝[/bold green]

    [bold cyan]       DSTERMINAL Cyber Ops Platform v3.1.113[/bold cyan]
    [dim]═══════════════════════════════════════════════════════════════[/dim]
    [bold yellow]🌐🔒[/bold yellow] Web System Application Security Analysis Module
    [bold yellow]📄[/bold yellow] Platform-Specific Remediation Configurations
    [bold red]💀[/bold red] For Educational & Authorized Security Testing Only
    """
        return Panel(
            banner_text,
            title="[bold cyan]DSTERMINAL SECURITY SUITE[/bold cyan]",
            border_style="cyan",
            box=box.HEAVY,
            padding=(1, 2),
            width=80
        )
        
    def _show_centered_banner(self):
        """Display the centered hacker-style banner"""
        self.console.print(Align.center(self._get_centered_banner()))
        
        status = "═" * 78
        self.console.print(f"\n[dim]{status}[/dim]")
        self.console.print(
            Align.center(
                f"[green]►[/green] [dim]System:[/dim] [cyan]ACTIVE[/cyan] "
                f"[green]│[/green] [dim]Mode:[/dim] [yellow]SECURITY ANALYSIS[/yellow] "
                f"[green]│[/green] [dim]Version:[/dim] [cyan]{VERSION}[/cyan]"
            )
        )
        self.console.print(f"[dim]{status}[/dim]\n")
    
    def _show_main_layout(self):
        """Show the main centered layout"""
        self._clear_screen()
        self._show_centered_banner()
        
        left_panel = Panel(
            self._get_left_panel_content(),
            title="[bold green]░ SYSTEM INFO ░[/bold green]",
            border_style="green",
            box=box.HEAVY,
            width=35
        )
        
        center_panel = Panel(
            self._get_center_panel_content(),
            title="[bold cyan]░ MAIN MENU ░[/bold cyan]",
            border_style="cyan",
            box=box.HEAVY,
            width=45
        )
        
        right_panel = Panel(
            self._get_right_panel_content(),
            title="[bold yellow]░ STATUS ░[/bold yellow]",
            border_style="yellow",
            box=box.HEAVY,
            width=35
        )
        
        layout = Layout()
        layout.split_row(
            Layout(Padding(left_panel, (0, 0)), ratio=1),
            Layout(Padding(center_panel, (0, 2)), ratio=2),
            Layout(Padding(right_panel, (0, 0)), ratio=1)
        )
        
        self.console.print(layout)
        self._show_status_bar()
    
    def _get_left_panel_content(self) -> str:
        """Left panel content"""
        content = f"""
[{self.colors['info']}]┌─ SESSION ─────────────────[/{self.colors['info']}]
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Time:[/dim] {datetime.now().strftime('%H:%M:%S')}
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Date:[/dim] {datetime.now().strftime('%Y-%m-%d')}
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Scans:[/dim] {len(self.scan_history)}
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Status:[/dim] {'🟢 Active' if not self.is_running else '🔄 Scanning'}
[{self.colors['info']}]└──────────────────────────────────[/{self.colors['info']}]

[{self.colors['accent']}]┌─ PLATFORM ──────────────────[/{self.colors['accent']}]
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Name:[/dim] {PLATFORM}
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Version:[/dim] {VERSION}
[{self.colors['accent']}]│[/{self.colors['accent']}] [dim]Mode:[/dim] [green]AUTHORIZED/EDUCATIONAL[/green]
[{self.colors['accent']}]└──────────────────────────────────[/{self.colors['accent']}]

[{self.colors['warning']}]┌─ SECURITY TIPS ──────────────[/{self.colors['warning']}]
[{self.colors['warning']}]│[/{self.colors['warning']}] • [dim]Always get permission[/dim]
[{self.colors['warning']}]│[/{self.colors['warning']}] • [dim]Test responsibly[/dim]
[{self.colors['warning']}]│[/{self.colors['warning']}] • [dim]Document findings[/dim]
[{self.colors['warning']}]└──────────────────────────────────[/{self.colors['warning']}]
"""
        return content
    
    def _get_center_panel_content(self) -> str:
        """Center panel with menu options"""
        content = f"""
[{self.colors['primary']}]╔══════════════════════════════════════════╗[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]               [{self.colors['info']}]📋 MAIN MENU[/{self.colors['info']}]                 [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║──────────────────────────────────────────║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]1.[/{self.colors['accent']}] [{self.colors['primary']}]🚀[/{self.colors['primary']}] Full Security Scan          [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]2.[/{self.colors['accent']}] [{self.colors['info']}]📋[/{self.colors['info']}] Scan Headers                [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]3.[/{self.colors['accent']}] [{self.colors['warning']}]🔧[/{self.colors['warning']}] Scan Technologies           [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]4.[/{self.colors['accent']}] [{self.colors['danger']}]💉[/{self.colors['danger']}] Scan XSS                    [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]5.[/{self.colors['accent']}] [{self.colors['warning']}]🔐[/{self.colors['warning']}] Scan CSRF                   [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]6.[/{self.colors['accent']}] [{self.colors['info']}]🍪[/{self.colors['info']}] Scan Session/Cookies        [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]7.[/{self.colors['accent']}] [{self.colors['accent']}]🐘[/{self.colors['accent']}] Scan PHP                    [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]8.[/{self.colors['accent']}] [{self.colors['accent']}]🌐[/{self.colors['accent']}] Scan Apache                 [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]9.[/{self.colors['accent']}] [{self.colors['warning']}]📄[/{self.colors['warning']}] Export Report with Remediation[{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║──────────────────────────────────────────║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]h.[/{self.colors['accent']}] [{self.colors['info']}]❓[/{self.colors['info']}] Help                        [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['accent']}]q.[/{self.colors['accent']}] [{self.colors['danger']}]🚪[/{self.colors['danger']}] Exit                        [{self.colors['primary']}]║[/{self.colors['primary']}]
[{self.colors['primary']}]╚══════════════════════════════════════════╝[/{self.colors['primary']}]
"""
        return content
    
    def _get_right_panel_content(self) -> str:
        """Right panel with status info"""
        if self.current_report:
            risk_color = "green"
            if self.current_report.risk_score >= 70:
                risk_color = "red"
            elif self.current_report.risk_score >= 40:
                risk_color = "yellow"
            
            content = f"""
[{self.colors['info']}]┌─ LAST SCAN ──────────────────[/{self.colors['info']}]
[{self.colors['info']}]│[/{self.colors['info']}] [dim]Target:[/dim] {self.current_report.url[:25]}...
[{self.colors['info']}]│[/{self.colors['info']}] [dim]Risk:[/dim] [{risk_color}]{self.current_report.risk_score}/100[/{risk_color}]
[{self.colors['info']}]│[/{self.colors['info']}] [dim]Findings:[/dim] {len(self.current_report.findings)}
[{self.colors['info']}]│[/{self.colors['info']}] [dim]Files:[/dim] {len(self.current_report.exposed_files)}
[{self.colors['info']}]└──────────────────────────────────[/{self.colors['info']}]
"""
            if self.current_report.findings:
                critical = sum(1 for f in self.current_report.findings if f.severity == 'CRITICAL')
                high = sum(1 for f in self.current_report.findings if f.severity == 'HIGH')
                content += f"""
[{self.colors['danger']}]┌─ FINDINGS ────────────────────[/{self.colors['danger']}]
[{self.colors['danger']}]│[/{self.colors['danger']}] [dim]Critical:[/dim] [red]{critical}[/red]
[{self.colors['danger']}]│[/{self.colors['danger']}] [dim]High:[/dim] [yellow]{high}[/yellow]
[{self.colors['danger']}]└──────────────────────────────────[/{self.colors['danger']}]
"""
        else:
            content = f"""
[{self.colors['dim']}]┌─ STATUS ──────────────────────[/{self.colors['dim']}]
[{self.colors['dim']}]│[/{self.colors['dim']}] [dim]No scans performed yet[/dim]
[{self.colors['dim']}]│[/{self.colors['dim']}] [dim]Run option 1 to start[/dim]
[{self.colors['dim']}]└──────────────────────────────────[/{self.colors['dim']}]
"""
        
        content += f"""
[{self.colors['primary']}]┌─ STATISTICS ─────────────────[/{self.colors['primary']}]
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]History:[/dim] {len(self.scan_history)}
[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]Uptime:[/dim] {self._get_uptime()}
[{self.colors['primary']}]└──────────────────────────────────[/{self.colors['primary']}]
"""
        return content
    
    def _get_uptime(self) -> str:
        """Get session uptime"""
        elapsed = datetime.now() - self._start_time
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}:{elapsed.seconds % 60:02d}"
    
    def _show_status_bar(self):
        """Show the bottom status bar"""
        status = "═" * 80
        self.console.print(f"\n[dim]{status}[/dim]")
        self.console.print(
            Align.center(
                f"[green]▶[/green] [dim]Ready[/dim] [green]│[/green] "
                f"[dim]Press[/dim] [yellow]h[/yellow] [dim]for help[/dim] [green]│[/green] "
                f"[dim]Press[/dim] [yellow]q[/yellow] [dim]to quit[/dim] [green]│[/green] "
                f"[dim]Version[/dim] [cyan]{VERSION}[/cyan]"
            )
        )
        self.console.print(f"[dim]{status}[/dim]")
    
    def _show_error(self, message: str):
        """Show error message"""
        self.console.print(f"\n[{self.colors['danger']}]╔══════════════════════════════════════════╗[/{self.colors['danger']}]")
        self.console.print(f"[{self.colors['danger']}]║[/{self.colors['danger']}]  [red]✖ ERROR OCCURRED[/red]                    [{self.colors['danger']}]║[/{self.colors['danger']}]")
        self.console.print(f"[{self.colors['danger']}]║──────────────────────────────────────────║[/{self.colors['danger']}]")
        self.console.print(f"[{self.colors['danger']}]║[/{self.colors['danger']}]  {message[:50]}{'...' if len(message) > 50 else ''} [{self.colors['danger']}]║[/{self.colors['danger']}]")
        self.console.print(f"[{self.colors['danger']}]╚══════════════════════════════════════════╝[/{self.colors['danger']}]")
        input("\n[dim]Press Enter to continue...[/dim]")
    
    def _show_success(self, message: str):
        """Show success message"""
        self.console.print(f"\n[{self.colors['primary']}]╔══════════════════════════════════════════╗[/{self.colors['primary']}]")
        self.console.print(f"[{self.colors['primary']}]║[/{self.colors['primary']}]  [green]✔ SUCCESS[/green]                         [{self.colors['primary']}]║[/{self.colors['primary']}]")
        self.console.print(f"[{self.colors['primary']}]║──────────────────────────────────────────║[/{self.colors['primary']}]")
        self.console.print(f"[{self.colors['primary']}]║[/{self.colors['primary']}]  {message[:50]}{'...' if len(message) > 50 else ''} [{self.colors['primary']}]║[/{self.colors['primary']}]")
        self.console.print(f"[{self.colors['primary']}]╚══════════════════════════════════════════╝[/{self.colors['primary']}]")
    
    def _show_help(self):
        """Show help"""
        self._clear_screen()
        self._show_centered_banner()
        
        help_content = f"""
[{self.colors['info']}]╔══════════════════════════════════════════════════════════════╗[/{self.colors['info']}]
[{self.colors['info']}]║[/{self.colors['info']}]  [{self.colors['primary']}]██████╗  ███████╗██╗  ██╗██████╗  [/{self.colors['primary']}]            [{self.colors['info']}]║[/{self.colors['info']}]
[{self.colors['info']}]║[/{self.colors['info']}]  [{self.colors['primary']}]██╔══██╗██╔════╝██║  ██║██╔══██╗ [/{self.colors['primary']}]            [{self.colors['info']}]║[/{self.colors['info']}]
[{self.colors['info']}]║[/{self.colors['info']}]  [{self.colors['primary']}]██████╔╝█████╗  ███████║██████╔╝ [/{self.colors['primary']}]            [{self.colors['info']}]║[/{self.colors['info']}]
[{self.colors['info']}]║[/{self.colors['info']}]  [{self.colors['primary']}]██╔══██╗██╔══╝  ██╔══██║██╔═══╝  [/{self.colors['primary']}]            [{self.colors['info']}]║[/{self.colors['info']}]
[{self.colors['info']}]║[/{self.colors['info']}]  [{self.colors['primary']}]██████╔╝███████╗██║  ██║██║      [/{self.colors['primary']}]            [{self.colors['info']}]║[/{self.colors['info']}]
[{self.colors['info']}]║[/{self.colors['info']}]  [{self.colors['primary']}]╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝      [/{self.colors['primary']}]            [{self.colors['info']}]║[/{self.colors['info']}]
[{self.colors['info']}]╚══════════════════════════════════════════════════════════════╝[/{self.colors['info']}]

[{self.colors['primary']}]┌─ COMMAND REFERENCE ─────────────────────────────────────────[/{self.colors['primary']}]
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]1.[/{self.colors['accent']}] Full Security Scan     - Comprehensive analysis with platform remediation
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]2.[/{self.colors['accent']}] Scan Headers          - HTTP security headers
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]3.[/{self.colors['accent']}] Scan Technologies    - Frameworks & CMS detection
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]4.[/{self.colors['accent']}] Scan XSS              - Cross-Site Scripting testing
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]5.[/{self.colors['accent']}] Scan CSRF             - Cross-Site Request Forgery
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]6.[/{self.colors['accent']}] Scan Session         - Cookie & session security
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]7.[/{self.colors['accent']}] Scan PHP             - PHP vulnerabilities
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]8.[/{self.colors['accent']}] Scan Apache          - Apache vulnerabilities
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]9.[/{self.colors['accent']}] Export Report        - PDF with platform-specific remediation
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]h.[/{self.colors['accent']}] Help               - This help screen
[{self.colors['primary']}]│[/{self.colors['primary']}]  [{self.colors['accent']}]q.[/{self.colors['accent']}] Exit               - Quit dashboard
[{self.colors['primary']}]└─────────────────────────────────────────────────────────────[/{self.colors['primary']}]

[{self.colors['info']}]┌─ PLATFORM-SPECIFIC REMEDIATION ─────────────────────────────[/{self.colors['info']}]
[{self.colors['info']}]│[/{self.colors['info']}]  [dim]Each finding includes remediation based on detected platform:[/dim]
[{self.colors['info']}]│[/{self.colors['info']}]  • [cyan]Web Server[/cyan] - ...
[{self.colors['info']}]│[/{self.colors['info']}]  • [cyan]Language[/cyan] - ...
[{self.colors['info']}]│[/{self.colors['info']}]  • [cyan]Framework[/cyan] - ...
[{self.colors['info']}]│[/{self.colors['info']}]  • [cyan]OS[/cyan] - ...
[{self.colors['info']}]│[/{self.colors['info']}]  • [cyan]Cloud[/cyan] - ...
[{self.colors['info']}]└─────────────────────────────────────────────────────────────[/{self.colors['info']}]

[{self.colors['warning']}]┌─ SECURITY NOTICE ──────────────────────────────────────────[/{self.colors['warning']}]
[{self.colors['warning']}]│[/{self.colors['warning']}]  ⚠️ This tool is for EDUCATIONAL PURPOSES only
[{self.colors['warning']}]│[/{self.colors['warning']}]  ⚠️ Only test systems you own or have permission to test
[{self.colors['warning']}]│[/{self.colors['warning']}]  ⚠️ Unauthorized testing is illegal and unethical
[{self.colors['warning']}]└─────────────────────────────────────────────────────────────[/{self.colors['warning']}]
"""
        self.console.print(help_content)
        input(f"\n[{self.colors}]Press Enter to return to menu...[/{self.colors}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _full_scan(self):
        """Perform full security scan"""
        self._clear_screen()
        self._show_centered_banner()
        
        # Make sure we have a typer
        if not hasattr(self, 'typer'):
            self.typer = TypeWriter('fast')
        
        url = Prompt.ask(
            f"[{self.colors['primary']}]┌─ Target URL ──►[/{self.colors['primary']}]",
            default="https://example.com"
        )
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        if not Confirm.ask(
            f"[{self.colors['warning']}]⚠️ Do you have permission to test {url}?[/{self.colors['warning']}]",
            default=False
        ):
            self._show_error("Scan aborted - permission required")
            return
        
        self.is_running = True
        self.target_url = url
        
        # Show scan start (only once)        
        try:
            with Progress(
                SpinnerColumn(spinner_name="dots12", style="green"),
                TextColumn("[bold green]{task.description}[/bold green]"),
                BarColumn(bar_width=50, style="green", complete_style="bright_green"),
                TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
                TimeElapsedColumn(),
                console=self.console,
            ) as progress:
                
                task = progress.add_task("[cyan]Scanning target...", total=100)
                
                # Run the scan (analyze will NOT call print_scan_start anymore)
                report = self.analyzer.analyze(url)
                
                # Add specialized scans
                progress.update(task, description="[yellow]Checking XSS...", advance=20)
                report.xss_vulnerable = self.analyzer.cmd_scan_xss(url)
                
                progress.update(task, description="[yellow]Checking CSRF...", advance=20)
                report.csrf_vulnerable = self.analyzer.cmd_scan_csrf(url)
                
                progress.update(task, description="[yellow]Checking Session...", advance=20)
                report.session_vulnerabilities = self.analyzer.cmd_scan_session(url)
                
                progress.update(task, description="[yellow]Checking PHP...", advance=20)
                report.php_vulnerabilities = self.analyzer.cmd_scan_php(url)
                
                progress.update(task, description="[yellow]Checking Apache...", advance=20)
                report.apache_vulnerabilities = self.analyzer.cmd_scan_apache(url)
                
                progress.update(task, description="[green]✓ Scan complete!", completed=100)
            
            self.current_report = report
            self.scan_history.append(report)
            self.is_running = False
            
            # Display report with pen typing
            self._display_report(report)
            
        except Exception as e:
            self.is_running = False
            self._show_error(f"Scan failed: {str(e)}")
            
    def _scan_headers(self):
        """Scan headers only"""
        self._clear_screen()
        self._show_centered_banner()
        
        url = Prompt.ask(
            f"[{self.colors['primary']}]┌─ Target URL ──►[/{self.colors['primary']}]",
            default="https://example.com"
        )
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.console.print(f"[{self.colors['primary']}]📋 Scanning Headers[/{self.colors['primary']}]")
        self.console.print(f"[dim]Target: {url}[/dim]")
        
        try:
            result = self.analyzer.cmd_scan_headers(url)
            
            self.console.print(f"\n[{self.colors['primary']}]┌─ HEADERS ──────────────────────────────────────[/{self.colors['primary']}]")
            for key, value in result.get('headers', {}).items():
                self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [cyan]{key}:[/cyan] {value}")
            self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
            
            self.console.print(f"\n[{self.colors['warning']}]┌─ SECURITY HEADERS ─────────────────────────────[/{self.colors['warning']}]")
            for key, value in result.get('security_headers', {}).items():
                status = "✅" if value != 'Not Set' else "❌"
                color = "green" if value != 'Not Set' else "red"
                self.console.print(f"[{self.colors['warning']}]│[/{self.colors['warning']}] [{color}]{status}[/{color}] [cyan]{key}:[/cyan] {value}")
            self.console.print(f"[{self.colors['warning']}]└─────────────────────────────────────────────────[/{self.colors['warning']}]")
            
            self._show_success("Headers scan completed")
            
        except Exception as e:
            self._show_error(str(e))
        
        input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _scan_technologies(self):
        """Scan technologies"""
        self._clear_screen()
        self._show_centered_banner()
        
        url = Prompt.ask(
            f"[{self.colors['primary']}]┌─ Target URL ──►[/{self.colors['primary']}]",
            default="https://example.com"
        )
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.console.print(f"[{self.colors['primary']}]🔧 Detecting Technologies[/{self.colors['primary']}]")
        self.console.print(f"[dim]Target: {url}[/dim]")
        
        try:
            techs = self.analyzer.cmd_scan_technologies(url)
            
            self.console.print(f"\n[{self.colors['primary']}]┌─ TECHNOLOGIES DETECTED ────────────────────────[/{self.colors['primary']}]")
            for tech in techs:
                self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] • [cyan]{tech}[/cyan]")
            if not techs:
                self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]No technologies detected[/dim]")
            self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
            
            self._show_success(f"Found {len(techs)} technologies")
            
        except Exception as e:
            self._show_error(str(e))
        
        input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _scan_xss(self):
        """Scan for XSS"""
        self._clear_screen()
        self._show_centered_banner()
        
        url = Prompt.ask(
            f"[{self.colors['primary']}]┌─ Target URL ──►[/{self.colors['primary']}]",
            default="https://example.com"
        )
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.console.print(f"[{self.colors['primary']}]💉 Scanning for XSS[/{self.colors['primary']}]")
        self.console.print(f"[dim]Target: {url}[/dim]")
        
        try:
            results = self.analyzer.cmd_scan_xss(url)
            
            if results:
                self.console.print(f"\n[{self.colors['danger']}]┌─ XSS VULNERABILITIES ──────────────────────────[/{self.colors['danger']}]")
                for r in results:
                    if r.get('vulnerable'):
                        self.console.print(f"[{self.colors['danger']}]│[/{self.colors['danger']}] [red]✖[/red] {r.get('field', 'Unknown')}")
                        self.console.print(f"[{self.colors['danger']}]│[/{self.colors['danger']}]    [dim]Payload:[/dim] [yellow]{r.get('payload', 'N/A')}[/yellow]")
                self.console.print(f"[{self.colors['danger']}]└─────────────────────────────────────────────────[/{self.colors['danger']}]")
            else:
                self.console.print(f"\n[{self.colors['primary']}]┌─ XSS RESULTS ──────────────────────────────────[/{self.colors['primary']}]")
                self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [green]✅ No XSS vulnerabilities found[/green]")
                self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
            
            self._show_success("XSS scan completed")
            
        except Exception as e:
            self._show_error(str(e))
        
        input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _scan_csrf(self):
        """Scan for CSRF"""
        self._clear_screen()
        self._show_centered_banner()
        
        url = Prompt.ask(
            f"[{self.colors['primary']}]┌─ Target URL ──►[/{self.colors['primary']}]",
            default="https://example.com"
        )
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.console.print(f"[{self.colors['primary']}]🔐 Scanning for CSRF[/{self.colors['primary']}]")
        self.console.print(f"[dim]Target: {url}[/dim]")
        
        try:
            results = self.analyzer.cmd_scan_csrf(url)
            
            if results:
                self.console.print(f"\n[{self.colors['warning']}]┌─ CSRF TEST RESULTS ────────────────────────────[/{self.colors['warning']}]")
                for r in results:
                    status = "❌ VULNERABLE" if r.get('vulnerable') else "✅ SECURE"
                    color = "red" if r.get('vulnerable') else "green"
                    self.console.print(f"[{self.colors['warning']}]│[/{self.colors['warning']}] [{color}]{status}[/{color}] {r.get('form_action', 'Unknown')[:40]}")
                self.console.print(f"[{self.colors['warning']}]└─────────────────────────────────────────────────[/{self.colors['warning']}]")
            else:
                self.console.print(f"\n[{self.colors['primary']}]┌─ CSRF RESULTS ──────────────────────────────────[/{self.colors['primary']}]")
                self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [green]✅ No CSRF vulnerabilities found[/green]")
                self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
            
            self._show_success("CSRF scan completed")
            
        except Exception as e:
            self._show_error(str(e))
        
        input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _scan_session(self):
        """Scan session vulnerabilities"""
        self._clear_screen()
        self._show_centered_banner()
        
        url = Prompt.ask(
            f"[{self.colors['primary']}]┌─ Target URL ──►[/{self.colors['primary']}]",
            default="https://example.com"
        )
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.console.print(f"[{self.colors['primary']}]🍪 Scanning Session Security[/{self.colors['primary']}]")
        self.console.print(f"[dim]Target: {url}[/dim]")
        
        try:
            results = self.analyzer.cmd_scan_session(url)
            
            if results:
                self.console.print(f"\n[{self.colors['warning']}]┌─ SESSION VULNERABILITIES ──────────────────────[/{self.colors['warning']}]")
                for r in results:
                    self.console.print(f"[{self.colors['warning']}]│[/{self.colors['warning']}] [red]✖[/red] Cookie: [cyan]{r.get('cookie', 'Unknown')}[/cyan]")
                    for vuln in r.get('vulnerabilities', []):
                        self.console.print(f"[{self.colors['warning']}]│[/{self.colors['warning']}]    [dim]-[/dim] {vuln}")
                self.console.print(f"[{self.colors['warning']}]└─────────────────────────────────────────────────[/{self.colors['warning']}]")
            else:
                self.console.print(f"\n[{self.colors['primary']}]┌─ SESSION RESULTS ──────────────────────────────[/{self.colors['primary']}]")
                self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [green]✅ No session vulnerabilities found[/green]")
                self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
            
            self._show_success("Session scan completed")
            
        except Exception as e:
            self._show_error(str(e))
        
        input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _scan_php(self):
        """Scan PHP vulnerabilities"""
        self._clear_screen()
        self._show_centered_banner()
        
        url = Prompt.ask(
            f"[{self.colors['primary']}]┌─ Target URL ──►[/{self.colors['primary']}]",
            default="https://example.com"
        )
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        
        self.console.print(f"[{self.colors['primary']}]🐘 Scanning PHP Security[/{self.colors['primary']}]")
        self.console.print(f"[dim]Target: {url}[/dim]")
    
        
        try:
            results = self.analyzer.cmd_scan_php(url)
            
            if results:
                self.console.print(f"\n[{self.colors['primary']}]┌─ PHP INFORMATION ──────────────────────────────[/{self.colors['primary']}]")
                for r in results:
                    self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [cyan]{r.get('type', 'Unknown')}:[/cyan] {r.get('version', 'N/A')}")
                self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
            else:
                self.console.print(f"\n[{self.colors['primary']}]┌─ PHP RESULTS ───────────────────────────────────[/{self.colors['primary']}]")
                self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]No PHP information detected[/dim]")
                self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
            
            self._show_success("PHP scan completed")
            
        except Exception as e:
            self._show_error(str(e))
        
        input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _scan_apache(self):
        """Scan Apache vulnerabilities"""
        self._clear_screen()
        self._show_centered_banner()
        
        url = Prompt.ask(
            f"[{self.colors['primary']}]┌─ Target URL ──►[/{self.colors['primary']}]",
            default="https://example.com"
        )
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        
        self.console.print(f"[{self.colors['primary']}]🌐 Scanning Apache Security[/{self.colors['primary']}]")
        self.console.print(f"[dim]Target: {url}[/dim]")
    
        
        try:
            results = self.analyzer.cmd_scan_apache(url)
            
            if results:
                self.console.print(f"\n[{self.colors['primary']}]┌─ APACHE INFORMATION ───────────────────────────[/{self.colors['primary']}]")
                for r in results:
                    self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [cyan]{r.get('type', 'Unknown')}:[/cyan] {r.get('version', 'N/A')}")
                self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
            else:
                self.console.print(f"\n[{self.colors['primary']}]┌─ APACHE RESULTS ───────────────────────────────[/{self.colors['primary']}]")
                self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [dim]No Apache information detected[/dim]")
                self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
            
            self._show_success("Apache scan completed")
            
        except Exception as e:
            self._show_error(str(e))
        
        input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _export_report(self):
        """Export report with platform-specific remediation"""
        if not self.current_report:
            self._show_error("No report available. Run a scan first.")
            return
        
        self._clear_screen()
        self._show_centered_banner()
        
        
        self.console.print(f"[{self.colors['primary']}]📄 Export Report with Platform-Specific Remediation[/{self.colors['primary']}]")
        self.console.print(f"[dim]Target: {self.current_report.url}[/dim]")
        self.console.print(f"[dim]Risk Score: {self.current_report.risk_score}/100[/dim]")
        self.console.print(f"[dim]Findings: {len(self.current_report.findings)}[/dim]")
        
        # Show detected platform
        platform = self.current_report.platform_remediation.get('platform', {})
        self.console.print(f"[dim]Detected Platform: {platform.get('webserver', 'Unknown')} + {platform.get('language', 'Unknown')}[/dim]")
        
    
        
        choice = Prompt.ask(
            f"[{self.colors['primary']}]┌─ Export Format ──►[/{self.colors['primary']}]",
            choices=["pdf", "json", "html", "all", "c"],
            default="pdf"
        )
        
        if choice == "c":
            return
        
        formats = ["pdf", "json", "html"] if choice == "all" else [choice]
        
        for fmt in formats:
            self.console.print(f"\n[{self.colors['info']}]Generating {fmt.upper()} report with platform-specific remediation...[/{self.colors['info']}]")
            
            if fmt == "pdf":
                self._export_pdf()
            elif fmt == "json":
                self._export_json()
            elif fmt == "html":
                self._export_html()
        
        self._show_success("Report export completed")
        input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _export_pdf(self):
        """Export to PDF with platform-specific remediation"""
        try:
            pdf_path = self.pdf_generator.generate_report(self.current_report)
            if pdf_path:
                self.console.print(f"[green]✅ PDF saved: {pdf_path}[/green]")
                try:
                    os.startfile(pdf_path) if os.name == 'nt' else webbrowser.open(f"file://{pdf_path}")
                except:
                    pass
        except Exception as e:
            self.console.print(f"[red]❌ PDF export failed: {e}[/red]")
    
    def _export_json(self):
        """Export to JSON with platform-specific remediation"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.expanduser(f"~/DSTerminal_Workspace/reports/report_{timestamp}.json")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            data = {
                'url': self.current_report.url,
                'timestamp': self.current_report.timestamp,
                'risk_score': self.current_report.risk_score,
                'summary': self.current_report.summary,
                'platform_remediation': self.current_report.platform_remediation,
                'findings': [
                    {
                        'severity': f.severity,
                        'category': f.category,
                        'title': f.title,
                        'description': f.description,
                        'recommendation': f.recommendation,
                        'cve': f.cve,
                        'evidence': f.evidence,
                        'fix_priority': getattr(f, 'fix_priority', 'MEDIUM'),
                        'remediation_configs': f.remediation_configs
                    }
                    for f in self.current_report.findings
                ],
                'technologies': self.current_report.technologies,
                'exposed_files': self.current_report.exposed_files,
                'security_headers': self.current_report.security_headers,
                'server_info': self.current_report.server_info
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]✅ JSON saved: {filename}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ JSON export failed: {e}[/red]")
    
    def escape_html(self, text):
        """Escape HTML special characters"""
        if not text:
            return ""
        return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')
            .encode('ascii', 'xmlcharrefreplace')
            .decode('ascii'))
    
    def _export_html(self):
        """Export to HTML with platform-specific remediation"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.expanduser(f"~/DSTerminal_Workspace/reports/report_{timestamp}.html")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Use self.escape_html instead of the undefined escape_html function
            def escape_html(text):
                if not text:
                    return ""
                return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#39;')
                    .encode('ascii', 'xmlcharrefreplace')
                    .decode('ascii'))
            
            # Generate platform info HTML
            platform = self.current_report.platform_remediation.get('platform', {})
            platform_html = f'''
            <div class="platform-info">
                <h3>Detected Platform</h3>
                <table>
                    <tr><td><strong>Web Server:</strong></td><td>{escape_html(platform.get('webserver', 'Unknown'))}</td></tr>
                    <tr><td><strong>Operating System:</strong></td><td>{escape_html(platform.get('os', 'Unknown'))}</td></tr>
                    <tr><td><strong>Language:</strong></td><td>{escape_html(platform.get('language', 'Unknown'))}</td></tr>
                    <tr><td><strong>Framework:</strong></td><td>{escape_html(platform.get('framework', 'None detected'))}</td></tr>
                    <tr><td><strong>Cloud Provider:</strong></td><td>{escape_html(platform.get('cloud_provider', 'None detected'))}</td></tr>
                </table>
            </div>
            '''
            
            # Generate findings HTML with platform-specific remediation
            findings_html = ''
            for f in self.current_report.findings:
                remediation_html = ''
                if f.remediation_configs:
                    remediation_html = '<div class="remediation"><h4>🔧 Platform-Specific Remediation</h4>'
                    for config_type, config_data in f.remediation_configs.items():
                        if config_data:
                            remediation_html += f'<h5>{escape_html(config_data.get("title", config_type))}</h5>'
                            if config_data.get('code'):
                                remediation_html += f'<div class="remediation-code">{escape_html(config_data["code"])}</div>'
                            if config_data.get('commands'):
                                remediation_html += '<div class="commands">'
                                for cmd in config_data.get('commands', []):
                                    if cmd.strip():
                                        remediation_html += f'$ {escape_html(cmd)}\n'
                                remediation_html += '</div>'
                    remediation_html += '</div>'
                
                findings_html += f'''
                <div class="finding severity-{f.severity.lower()}">
                    <h3>{escape_html(f.severity)}: {escape_html(f.title)}</h3>
                    <p><strong>Category:</strong> {escape_html(f.category)}</p>
                    <p><strong>Description:</strong> {escape_html(f.description)}</p>
                    <p><strong>Recommendation:</strong> {escape_html(f.recommendation)}</p>
                    {f'<p><strong>CVE:</strong> {escape_html(f.cve)}</p>' if f.cve else ''}
                    {f'<p><strong>Evidence:</strong> <code>{escape_html(f.evidence)}</code></p>' if f.evidence else ''}
                    <p><strong>Fix Priority:</strong> {getattr(f, 'fix_priority', 'MEDIUM')}</p>
                    {remediation_html}
                </div>
                '''
            
            html = f'''<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Security Report - {escape_html(self.current_report.url)}</title>
        <style>
            body {{ font-family: 'Courier New', monospace; background: #0a0e0a; color: #00ff41; margin: 40px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ background: #0d120d; border: 2px solid #00ff41; padding: 20px; border-radius: 10px; }}
            .finding {{ background: #0d120d; border: 1px solid #00ff41; padding: 15px; margin: 15px 0; border-radius: 5px; }}
            .severity-critical {{ border-color: #ff0044; }}
            .severity-high {{ border-color: #ff6b35; }}
            .severity-medium {{ border-color: #ffcc00; }}
            .severity-low {{ border-color: #00cc33; }}
            .summary {{ background: #0d120d; border: 1px solid #00ff41; padding: 20px; border-radius: 5px; white-space: pre-wrap; }}
            .remediation {{ background: #1a1a2e; border: 1px solid #00ff8844; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .remediation-code {{ background: #0a0a0a; padding: 10px; border: 1px solid #446644; border-radius: 3px; font-family: 'Courier New', monospace; color: #00ff88; white-space: pre-wrap; }}
            .commands {{ background: #0a0a0a; padding: 10px; border: 1px solid #444466; border-radius: 3px; font-family: 'Courier New', monospace; color: #88ccff; white-space: pre-wrap; }}
            .platform-info {{ background: #0d120d; border: 1px solid #00ff8844; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 10px; border: 1px solid #00ff41; text-align: left; }}
            th {{ background: #0d120d; color: #00ff41; }}
            .watermark {{ color: #1a3a1a; text-align: center; margin-top: 50px; font-size: 12px; }}
            h3 {{ color: #ffcc00; }}
            h4 {{ color: #00ff88; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Web Security Analysis Report</h1>
                <p>URL: {escape_html(self.current_report.url)}</p>
                <p>Date: {escape_html(self.current_report.timestamp)}</p>
                <p>Risk Score: {self.current_report.risk_score}/100</p>
                <p>Generated by: {PLATFORM} {VERSION}</p>
            </div>
            <div class="summary">
                <h2>Executive Summary</h2>
                <pre>{escape_html(self.current_report.summary)}</pre>
            </div>
            <h2>Server Information</h2>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                {''.join(f'<tr><td>{escape_html(k)}</td><td>{escape_html(v)}</td></tr>' for k, v in self.current_report.server_info.items())}
            </table>
            <h2>Technologies Detected</h2>
            <p>{', '.join(escape_html(t) for t in self.current_report.technologies) if self.current_report.technologies else 'None'}</p>
            {platform_html}
            <h2>Security Headers</h2>
            <table>
                <tr><th>Header</th><th>Value</th><th>Status</th></tr>
                {''.join(f'<tr><td>{escape_html(h)}</td><td>{escape_html(v)}</td><td>{v != "Not Set" and "✅ Set" or "❌ Missing"}</td></tr>' for h, v in self.current_report.security_headers.items())}
            </table>
            <h2>Security Findings with Platform-Specific Remediation ({len(self.current_report.findings)})</h2>
            {findings_html}
            <h2>Exposed Files ({len(self.current_report.exposed_files)})</h2>
            <ul>
                {''.join(f'<li>{escape_html(f)}</li>' for f in self.current_report.exposed_files[:20])}
                {f'<li>... and {len(self.current_report.exposed_files) - 20} more</li>' if len(self.current_report.exposed_files) > 20 else ''}
            </ul>
            <div class="watermark">
                ═══════════════════════════════════════════════════════════════<br>
                {PLATFORM} {VERSION} │ DSTERMINAL Security Analyzer<br>
                ⚠️ This analysis is for AUTHORIZED/EDUCATIONAL purposes only.<br>
                ═══════════════════════════════════════════════════════════════
            </div>
        </div>
    </body>
    </html>'''
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            
            self.console.print(f"[green]✅ HTML saved: {filename}[/green]")
            
            try:
                webbrowser.open(f"file://{filename}")
            except:
                pass
                
        except Exception as e:
            self.console.print(f"[red]❌ HTML export failed: {e}[/red]")
            
    def _generate_remediation_html(self, configs: Dict) -> str:
        """Generate HTML for remediation configurations"""
        if not configs:
            return ""
        
        html = '<div class="remediation"><h4>🔧 Platform-Specific Remediation</h4>'
        
        def escape_html(text):
            if not text:
                return ""
            return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;')
                .encode('ascii', 'xmlcharrefreplace')
                .decode('ascii'))
        
        for config_type, config_data in configs.items():
            if config_data:
                html += f'<h5>{escape_html(config_data.get("title", config_type))}</h5>'
                
                if config_data.get('code'):
                    html += '<div class="remediation-code">'
                    html += escape_html(config_data['code'])
                    html += '</div>'
                
                if config_data.get('commands'):
                    html += '<div class="commands">'
                    for cmd in config_data.get('commands', []):
                        if cmd.strip():
                            html += f'$ {escape_html(cmd)}\n'
                    html += '</div>'
        
        html += '</div>'
        return html
    
    def _show_history(self):
        """Show scan history"""
        self._clear_screen()
        self._show_centered_banner()
        
        if not self.scan_history:
            self.console.print(f"\n[{self.colors['dim']}]No scan history available[/{self.colors['dim']}]")
            input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
            return
        
        
        self.console.print(f"[{self.colors['primary']}]📊 Scan History[/{self.colors['primary']}]")
    
        
        for i, report in enumerate(self.scan_history[-10:], 1):
            risk_color = "green"
            if report.risk_score >= 70:
                risk_color = "red"
            elif report.risk_score >= 40:
                risk_color = "yellow"
            
            self.console.print(f"\n[{self.colors['primary']}]┌─ SCAN #{i} ──────────────────────────────────────[/{self.colors['primary']}]")
            self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [cyan]Target:[/cyan] {report.url}")
            self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [cyan]Time:[/cyan] {report.timestamp}")
            self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [cyan]Risk:[/cyan] [{risk_color}]{report.risk_score}/100[/{risk_color}]")
            self.console.print(f"[{self.colors['primary']}]│[/{self.colors['primary']}] [cyan]Findings:[/cyan] {len(report.findings)}")
            self.console.print(f"[{self.colors['primary']}]└─────────────────────────────────────────────────[/{self.colors['primary']}]")
        
        input(f"\n[{self.colors['dim']}]Press Enter to continue...[/{self.colors['dim']}]")
        self._clear_screen()
        self._show_centered_banner()
    
    def _display_report(self, report: WebSecurityReport):
        """Display the security report with pen typing effects"""
        
        # Make sure we have a typer
        if not hasattr(self, 'typer'):
            self.typer = TypeWriter('fast')
        
        # Header with typing effect
        self.typer.type_text("📊 SECURITY ANALYSIS REPORT", color=Colors.CYAN, pen_effect=True)
        print()
        
        # Risk Score
        risk_color = Colors.GREEN
        risk_text = "LOW RISK"
        if report.risk_score >= 70:
            risk_color = Colors.RED
            risk_text = "CRITICAL RISK"
        elif report.risk_score >= 40:
            risk_color = Colors.YELLOW
            risk_text = "MEDIUM RISK"
        
        self.typer.type_text("┌─ RISK ASSESSMENT ──────────────────────────────", color=Colors.CYAN, pen_effect=False)
        self.typer.type_text(f"│ Score: {report.risk_score}/100", color=risk_color, pen_effect=True)
        self.typer.type_text(f"│ Level: {risk_text}", color=risk_color, pen_effect=True)
        self.typer.type_text("└─────────────────────────────────────────────────", color=Colors.CYAN, pen_effect=False)
        print()
        
        # Platform Info
        platform = report.platform_remediation.get('platform', {})
        self.typer.type_text("┌─ DETECTED PLATFORM ─────────────────────────────", color=Colors.MAGENTA, pen_effect=False)
        self.typer.type_text(f"│ Web Server: {platform.get('webserver', 'Unknown')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ OS: {platform.get('os', 'Unknown')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ Language: {platform.get('language', 'Unknown')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ Framework: {platform.get('framework', 'None detected')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ Cloud: {platform.get('cloud_provider', 'None detected')}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text("└─────────────────────────────────────────────────", color=Colors.MAGENTA, pen_effect=False)
        print()
        
        # Fix Priority
        priority_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in report.findings:
            priority = getattr(finding, 'fix_priority', 'MEDIUM')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        self.typer.type_text("┌─ FIX PRIORITY ──────────────────────────────────", color=Colors.YELLOW, pen_effect=False)
        self.typer.type_text(f"│ CRITICAL (Fix Now): {priority_counts['CRITICAL']}", color=Colors.RED, pen_effect=True)
        self.typer.type_text(f"│ HIGH (Fix ASAP): {priority_counts['HIGH']}", color=Colors.RED, pen_effect=True)
        self.typer.type_text(f"│ MEDIUM (Plan Next): {priority_counts['MEDIUM']}", color=Colors.YELLOW, pen_effect=True)
        self.typer.type_text(f"│ LOW (Consider): {priority_counts['LOW']}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text("└─────────────────────────────────────────────────", color=Colors.YELLOW, pen_effect=False)
        print()
        
        # Findings Summary
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        for finding in report.findings:
            severity_counts[finding.severity] += 1
        
        self.typer.type_text("┌─ FINDINGS SUMMARY ─────────────────────────────", color=Colors.YELLOW, pen_effect=False)
        self.typer.type_text(f"│ CRITICAL: {severity_counts['CRITICAL']}", color=Colors.RED, pen_effect=True)
        self.typer.type_text(f"│ HIGH: {severity_counts['HIGH']}", color=Colors.RED, pen_effect=True)
        self.typer.type_text(f"│ MEDIUM: {severity_counts['MEDIUM']}", color=Colors.YELLOW, pen_effect=True)
        self.typer.type_text(f"│ LOW: {severity_counts['LOW']}", color=Colors.GREEN, pen_effect=True)
        self.typer.type_text(f"│ INFO: {severity_counts['INFO']}", color=Colors.CYAN, pen_effect=True)
        self.typer.type_text("└─────────────────────────────────────────────────", color=Colors.YELLOW, pen_effect=False)
        print()
        
        # Detailed Findings - Show top 10
        if report.findings:
            self.typer.type_text("┌─ DETAILED FINDINGS WITH PLATFORM REMEDIATION ──", color=Colors.CYAN, pen_effect=False)
            
            # Sort findings by severity
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
            sorted_findings = sorted(report.findings, key=lambda x: severity_order.get(x.severity, 5))
            
            for i, finding in enumerate(sorted_findings[:10]):
                severity_color = Colors.RED if finding.severity in ['CRITICAL', 'HIGH'] else Colors.YELLOW if finding.severity == 'MEDIUM' else Colors.GREEN
                priority = getattr(finding, 'fix_priority', 'MEDIUM')
                priority_color = Colors.RED if priority == 'CRITICAL' else Colors.YELLOW if priority == 'HIGH' else Colors.GREEN
                
                self.typer.type_text(f"│ ◉ {finding.severity} {finding.title[:50]}", color=severity_color, pen_effect=True)
                self.typer.type_text(f"│    Priority: {priority}", color=priority_color, pen_effect=True)
                
                if hasattr(finding, 'recommendation'):
                    rec = finding.recommendation[:60]
                    self.typer.type_text(f"│    Fix: {rec}{'...' if len(finding.recommendation) > 60 else ''}", 
                                        color=Colors.GREEN, pen_effect=True)
                
                if finding.remediation_configs:
                    self.typer.type_text(f"│    ✓ Platform-specific remediation available", 
                                        color=Colors.CYAN, pen_effect=True)
                
                if i < len(sorted_findings[:10]) - 1:
                    self.typer.type_text("│", color=Colors.DIM, pen_effect=False)
                    time.sleep(0.05)
            
            if len(sorted_findings) > 10:
                self.typer.type_text(f"│ ... and {len(sorted_findings) - 10} more findings", 
                                    color=Colors.DIM, pen_effect=True)
            
            self.typer.type_text("└─────────────────────────────────────────────────", color=Colors.CYAN, pen_effect=False)
            print()
        
        # Technologies
        if report.technologies:
            self.typer.type_text("┌─ TECHNOLOGIES DETECTED ────────────────────────", color=Colors.MAGENTA, pen_effect=False)
            for tech in report.technologies:
                self.typer.type_text(f"│ • {tech}", color=Colors.CYAN, pen_effect=True)
            self.typer.type_text("└─────────────────────────────────────────────────", color=Colors.MAGENTA, pen_effect=False)
            print()
            
    def _exit_dashboard(self):
        """Exit the dashboard"""
        self._clear_screen()
        self.console.print(Align.center(f"""
[{self.colors['primary']}]╔══════════════════════════════════════════════════════════╗
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['info']}]██████╗  ███████╗██╗  ██╗███████╗██╗████████╗[/{self.colors['primary']}]  [{self.colors['primary']}]║
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['info']}]██╔══██╗██╔════╝██║  ██║██╔════╝██║╚══██╔══╝[/{self.colors['primary']}]  [{self.colors['primary']}]║
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['info']}]██████╔╝█████╗  ███████║█████╗  ██║   ██║   [/{self.colors['primary']}]  [{self.colors['primary']}]║
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['info']}]██╔══██╗██╔══╝  ██╔══██║██╔══╝  ██║   ██║   [/{self.colors['primary']}]  [{self.colors['primary']}]║
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['info']}]██████╔╝███████╗██║  ██║███████╗██║   ██║   [/{self.colors['primary']}]  [{self.colors['primary']}]║
[{self.colors['primary']}]║[/{self.colors['primary']}]  [{self.colors['info']}]╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝   [/{self.colors['primary']}]  [{self.colors['primary']}]║
[{self.colors['primary']}]╚══════════════════════════════════════════════════════════╝[/{self.colors['primary']}]

[{self.colors['primary']}]👋 Thank you for using DSTERMINAL Security Analyzer[/{self.colors['primary']}]
[{self.colors['dim']}] {PLATFORM} {VERSION}[/{self.colors['dim']}]
[{self.colors['dim']}]🔒 Always test responsibly and ethically.[/{self.colors['dim']}]
"""))
        time.sleep(1.5)
        sys.exit(0)


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    """Main entry point for Web Security Analyzer with pen typing effects"""
    
    # Check for required dependencies
    if not REQUESTS_AVAILABLE:
        print("[red]❌ requests not installed. Run: pip install requests[/red]")
        sys.exit(1)
    
    if not BS4_AVAILABLE:
        print("[red]❌ beautifulsoup4 not installed. Run: pip install beautifulsoup4[/red]")
        sys.exit(1)
    
    # Clear screen and show banner
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Initialize typer for the main interface
    typer = TypeWriter('fast')
    
    # Show legal warning with typing effect
    typer.type_text("═" * 80, color=Colors.DIM)
    typer.type_text("⚠️  LEGAL WARNING AND DISCLAIMER ⚠️ : ", color=Colors.RED, pen_effect=True)
    typer.type_text("═" * 80, color=Colors.DIM)
    typer.type_text("This Module is for EDUCATIONAL PURPOSES and AUTHORIZED SECURITY TESTING only.", color=Colors.YELLOW, pen_effect=True)
    typer.type_text("Do not use on systems you do not own or do not have explicit permission to test.", color=Colors.YELLOW, pen_effect=True)
    typer.type_text("═" * 80, color=Colors.DIM)
    typer.type_text("\n", newline=True)
    
    # Show banner with fast typing
    banner_lines = [
        "╔═══════════════════════════════════════════════════════════════════╗",
        "║  🔐 DSTERMINAL Systems & Web Security Analyzer v3.1.113          ║",
        "║  📄 Platform-Specific Remediation Configurations                 ║",
        "║  💀 For Educational & Authorized Security Testing Only           ║",
        "╚═══════════════════════════════════════════════════════════════════╝"
    ]
    typer.type_banner(banner_lines, color=Colors.CYAN)
    typer.type_text("\n", newline=True)
    
    # Show system info
    typer.type_text(f"System: {platform.system()} {platform.release()}", color=Colors.DIM)
    typer.type_text(f"Version: {VERSION}", color=Colors.DIM)
    typer.type_text("\n", newline=True)
    
    # Ask if user wants to continue
    typer.type_text("Press Enter to continue: ", color=Colors.YELLOW, newline=False)
    choice = input().strip().lower()
    if choice == 'q':
        typer.type_text("\nExiting...", color=Colors.RED)
        sys.exit(0)
    
    # Initialize and run the dashboard
    try:
        dashboard = SecurityDashboard()
        dashboard.run()
    except KeyboardInterrupt:
        typer.type_text("\n\n⚠️  Interrupted by user", color=Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        typer.type_text(f"\n❌ Fatal error: {e}", color=Colors.RED)
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()