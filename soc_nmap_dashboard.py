#!/usr/bin/env python3
"""
DSTERMINAL SOC-GRADE NMAP SCAN DASHBOARD - COMPLETE EDITION
Hacker-style 3-Panel Layout | Real-time Scan Monitoring | AI Vulnerability Scoring
"""

import os
import sys
import time
import json
import re
import shutil
import subprocess
import threading
import webbrowser
import random
import math
<<<<<<< HEAD
import socket
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# ============================================================
# ANSI COLORS - HACKER THEME
# ============================================================

class Colors:
    GREEN = '\033[92m'
    DARK_GREEN = '\033[32m'
    BRIGHT_GREEN = '\033[92m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    MAGENTA = '\033[95m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;208m'
    PINK = '\033[38;5;205m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
<<<<<<< HEAD
    try:
        DIM = '\033[2m'
    except:
        DIM = '\033[90m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    BLACK = '\033[30m'
    DARK_GRAY = '\033[90m'
    LIGHT_GRAY = '\033[37m'
=======
    # Use this instead of DIM (some terminals don't support DIM)
    DIM = '\033[2m' if hasattr('\033[2m', '__str__') else '\033[90m'  # Fallback to dark gray
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44


# ============================================================
# Required Imports
# ============================================================

try:
    import folium
    from folium.plugins import HeatMap
    GEO_AVAILABLE = True
except ImportError:
    GEO_AVAILABLE = False

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ============================================================
<<<<<<< HEAD
# Domain to IP Resolution Helper
# ============================================================

def resolve_domain_to_ip(domain: str) -> Optional[str]:
    """Resolve domain name to IP address"""
    try:
        domain = domain.replace('http://', '').replace('https://', '').replace('ftp://', '')
        domain = domain.split('/')[0]
        domain = domain.split(':')[0]
        domain = domain.rstrip('.')
        
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
            return domain
        
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None
    except Exception:
        return None


# ============================================================
# ORGANIZATION LOCATION DATABASE with Auto-Detection
# ============================================================

class OrganizationLocationDB:
    """Database of organization headquarters locations with auto-detection from TLDs"""
    
    # Cache file for discovered organizations
    CACHE_FILE = os.path.expanduser("~/.dsterminal_org_cache.json")
    
=======
# ORGANIZATION LOCATION DATABASE (Universal - Works for ANY Country)
# ============================================================

class OrganizationLocationDB:
    """Database of organization headquarters locations (not server locations)"""
    
    # Add organizations from ANY country here
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    ORGANIZATIONS = {
        # ========== MALAWI ==========
        "unima.ac.mw": {"country": "Malawi", "city": "Zomba", "lat": -15.3833, "lon": 35.3167, "flag": "🇲🇼", "region": "East Africa"},
        "must.ac.mw": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "🇲🇼", "region": "East Africa"},
<<<<<<< HEAD
        "sparcsystems.africa": {"country": "Malawi", "city": "Lilongwe", "lat": -15.7833, "lon": 34.9667, "flag": "🇲🇼", "region": "East Africa"},
        "poly.ac.mw": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "🇲🇼", "region": "East Africa"},
        "kuhes.ac.mw": {"country": "Malawi", "city": "Lilongwe", "lat": -13.9833, "lon": 33.7833, "flag": "🇲🇼", "region": "East Africa"},
        "mzuni.ac.mw": {"country": "Malawi", "city": "Mzuzu", "lat": -11.4667, "lon": 34.0167, "flag": "🇲🇼", "region": "East Africa"},
        "cc.ac.mw": {"country": "Malawi", "city": "Zomba", "lat": -15.7833, "lon": 34.9667, "flag": "🇲🇼", "region": "East Africa"},
        "medcol.ac.mw": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "🇲🇼", "region": "East Africa"},
        "magu.ac.mw": {"country": "Malawi", "city": "Lilongwe", "lat": -15.3833, "lon": 35.3167, "flag": "🇲🇼", "region": "East Africa"},
=======
        "sparcsystems.africa": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "🇲🇼", "region": "East Africa"},
        "poly.ac.mw": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "🇲🇼", "region": "East Africa"},
        "kuhes.ac.mw": {"country": "Malawi", "city": "Lilongwe", "lat": -13.9833, "lon": 33.7833, "flag": "🇲🇼", "region": "East Africa"},
        "mzuni.ac.mw": {"country": "Malawi", "city": "Mzuzu", "lat": -11.4667, "lon": 34.0167, "flag": "🇲🇼", "region": "East Africa"},
        "cc.ac.mw": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "🇲🇼", "region": "East Africa"},
        "medcol.ac.mw": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "🇲🇼", "region": "East Africa"},
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        
        # ========== SOUTH AFRICA ==========
        "uct.ac.za": {"country": "South Africa", "city": "Cape Town", "lat": -33.9249, "lon": 18.4241, "flag": "🇿🇦", "region": "Southern Africa"},
        "up.ac.za": {"country": "South Africa", "city": "Pretoria", "lat": -25.7548, "lon": 28.2315, "flag": "🇿🇦", "region": "Southern Africa"},
        "uj.ac.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "🇿🇦", "region": "Southern Africa"},
        "wits.ac.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.1929, "lon": 28.0305, "flag": "🇿🇦", "region": "Southern Africa"},
        "stel.ac.za": {"country": "South Africa", "city": "Stellenbosch", "lat": -33.9328, "lon": 18.8644, "flag": "🇿🇦", "region": "Southern Africa"},
        "nmmu.ac.za": {"country": "South Africa", "city": "Gqeberha", "lat": -33.9618, "lon": 25.6099, "flag": "🇿🇦", "region": "Southern Africa"},
        "dut.ac.za": {"country": "South Africa", "city": "Durban", "lat": -29.8587, "lon": 31.0218, "flag": "🇿🇦", "region": "Southern Africa"},
        "tut.ac.za": {"country": "South Africa", "city": "Pretoria", "lat": -25.7548, "lon": 28.2315, "flag": "🇿🇦", "region": "Southern Africa"},
        
        # ========== KENYA ==========
        "uonbi.ac.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "🇰🇪", "region": "East Africa"},
        "ku.ac.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2225, "lon": 36.8966, "flag": "🇰🇪", "region": "East Africa"},
        "tukenya.ac.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.3204, "lon": 36.8157, "flag": "🇰🇪", "region": "East Africa"},
        "mku.ac.ke": {"country": "Kenya", "city": "Thika", "lat": -1.0386, "lon": 37.0908, "flag": "🇰🇪", "region": "East Africa"},
        "daystar.ac.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "🇰🇪", "region": "East Africa"},
        
        # ========== NIGERIA ==========
        "unilag.edu.ng": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "🇳🇬", "region": "West Africa"},
        "unn.edu.ng": {"country": "Nigeria", "city": "Nsukka", "lat": 6.8575, "lon": 7.3981, "flag": "🇳🇬", "region": "West Africa"},
        "oauife.edu.ng": {"country": "Nigeria", "city": "Ile-Ife", "lat": 7.5000, "lon": 4.5000, "flag": "🇳🇬", "region": "West Africa"},
        "abu.edu.ng": {"country": "Nigeria", "city": "Zaria", "lat": 11.1667, "lon": 7.6167, "flag": "🇳🇬", "region": "West Africa"},
        "uniben.edu": {"country": "Nigeria", "city": "Benin City", "lat": 6.3176, "lon": 5.6145, "flag": "🇳🇬", "region": "West Africa"},
        
        # ========== GHANA ==========
        "ug.edu.gh": {"country": "Ghana", "city": "Accra", "lat": 5.6500, "lon": -0.1868, "flag": "🇬🇭", "region": "West Africa"},
        "knust.edu.gh": {"country": "Ghana", "city": "Kumasi", "lat": 6.6750, "lon": -1.5714, "flag": "🇬🇭", "region": "West Africa"},
        "central.edu.gh": {"country": "Ghana", "city": "Accra", "lat": 5.6500, "lon": -0.1868, "flag": "🇬🇭", "region": "West Africa"},
        
        # ========== EGYPT ==========
        "cu.edu.eg": {"country": "Egypt", "city": "Cairo", "lat": 30.0333, "lon": 31.2333, "flag": "🇪🇬", "region": "North Africa"},
        "alexu.edu.eg": {"country": "Egypt", "city": "Alexandria", "lat": 31.2001, "lon": 29.9187, "flag": "🇪🇬", "region": "North Africa"},
        
        # ========== USA ==========
        "harvard.edu": {"country": "USA", "city": "Cambridge", "lat": 42.3744, "lon": -71.1169, "flag": "🇺🇸", "region": "North America"},
        "stanford.edu": {"country": "USA", "city": "Stanford", "lat": 37.4275, "lon": -122.1697, "flag": "🇺🇸", "region": "North America"},
        "mit.edu": {"country": "USA", "city": "Cambridge", "lat": 42.3601, "lon": -71.0942, "flag": "🇺🇸", "region": "North America"},
        
        # ========== UK ==========
        "ox.ac.uk": {"country": "United Kingdom", "city": "Oxford", "lat": 51.7520, "lon": -1.2577, "flag": "🇬🇧", "region": "Europe"},
        "cam.ac.uk": {"country": "United Kingdom", "city": "Cambridge", "lat": 52.2053, "lon": 0.1218, "flag": "🇬🇧", "region": "Europe"},
        
        # ========== GERMANY ==========
        "tu-berlin.de": {"country": "Germany", "city": "Berlin", "lat": 52.5200, "lon": 13.4050, "flag": "🇩🇪", "region": "Europe"},
        "lmu.de": {"country": "Germany", "city": "Munich", "lat": 48.1351, "lon": 11.5820, "flag": "🇩🇪", "region": "Europe"},
        
        # ========== INDIA ==========
        "iitb.ac.in": {"country": "India", "city": "Mumbai", "lat": 19.0760, "lon": 72.8777, "flag": "🇮🇳", "region": "South Asia"},
        "iisc.ac.in": {"country": "India", "city": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "flag": "🇮🇳", "region": "South Asia"},
    }
    
    @classmethod
<<<<<<< HEAD
    def _load_cache(cls) -> Dict:
        """Load cached organization locations from file"""
        if os.path.exists(cls.CACHE_FILE):
            try:
                with open(cls.CACHE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    @classmethod
    def _save_cache(cls, cache: Dict):
        """Save cached organization locations to file"""
        try:
            os.makedirs(os.path.dirname(cls.CACHE_FILE), exist_ok=True)
            with open(cls.CACHE_FILE, 'w') as f:
                json.dump(cache, f, indent=2)
        except:
            pass
    
    @classmethod
    def _detect_location_from_tld(cls, domain: str) -> Optional[Dict]:
        """Detect location from domain TLD patterns"""
        domain_lower = domain.lower()
        
        # Country TLD mappings with coordinates
        tld_map = {
            '.mw': {'country': 'Malawi', 'lat': -13.9833, 'lon': 33.7833, 'flag': '🇲🇼', 'region': 'East Africa'},
            '.ac.mw': {'country': 'Malawi', 'lat': -13.9833, 'lon': 33.7833, 'flag': '🇲🇼', 'region': 'East Africa'},
            '.za': {'country': 'South Africa', 'lat': -30.5595, 'lon': 22.9375, 'flag': '🇿🇦', 'region': 'Southern Africa'},
            '.co.za': {'country': 'South Africa', 'lat': -30.5595, 'lon': 22.9375, 'flag': '🇿🇦', 'region': 'Southern Africa'},
            '.ac.za': {'country': 'South Africa', 'lat': -30.5595, 'lon': 22.9375, 'flag': '🇿🇦', 'region': 'Southern Africa'},
            '.ke': {'country': 'Kenya', 'lat': -1.2921, 'lon': 36.8219, 'flag': '🇰🇪', 'region': 'East Africa'},
            '.ac.ke': {'country': 'Kenya', 'lat': -1.2921, 'lon': 36.8219, 'flag': '🇰🇪', 'region': 'East Africa'},
            '.ng': {'country': 'Nigeria', 'lat': 9.0820, 'lon': 8.6753, 'flag': '🇳🇬', 'region': 'West Africa'},
            '.edu.ng': {'country': 'Nigeria', 'lat': 9.0820, 'lon': 8.6753, 'flag': '🇳🇬', 'region': 'West Africa'},
            '.gh': {'country': 'Ghana', 'lat': 7.9465, 'lon': -1.0232, 'flag': '🇬🇭', 'region': 'West Africa'},
            '.edu.gh': {'country': 'Ghana', 'lat': 7.9465, 'lon': -1.0232, 'flag': '🇬🇭', 'region': 'West Africa'},
            '.eg': {'country': 'Egypt', 'lat': 26.8206, 'lon': 30.8025, 'flag': '🇪🇬', 'region': 'North Africa'},
            '.edu.eg': {'country': 'Egypt', 'lat': 26.8206, 'lon': 30.8025, 'flag': '🇪🇬', 'region': 'North Africa'},
            '.uk': {'country': 'United Kingdom', 'lat': 55.3781, 'lon': -3.4360, 'flag': '🇬🇧', 'region': 'Europe'},
            '.ac.uk': {'country': 'United Kingdom', 'lat': 55.3781, 'lon': -3.4360, 'flag': '🇬🇧', 'region': 'Europe'},
            '.de': {'country': 'Germany', 'lat': 51.1657, 'lon': 10.4515, 'flag': '🇩🇪', 'region': 'Europe'},
            '.in': {'country': 'India', 'lat': 20.5937, 'lon': 78.9629, 'flag': '🇮🇳', 'region': 'South Asia'},
            '.ac.in': {'country': 'India', 'lat': 20.5937, 'lon': 78.9629, 'flag': '🇮🇳', 'region': 'South Asia'},
            '.edu': {'country': 'USA', 'lat': 37.0902, 'lon': -95.7129, 'flag': '🇺🇸', 'region': 'North America'},
            '.africa': {'country': 'Africa (HQ Unknown)', 'lat': 0, 'lon': 0, 'flag': '🌍', 'region': 'Africa'},
        }
        
        for tld, info in tld_map.items():
            if domain_lower.endswith(tld):
                return {
                    "country": info['country'],
                    "city": "Unknown (Auto-detected)",
                    "lat": info['lat'],
                    "lon": info['lon'],
                    "flag": info['flag'],
                    "region": info['region'],
                    "note": f"Auto-detected from {tld} domain pattern"
                }
        
        return None
    
    @classmethod
    def get_organization_location(cls, domain: str, hostname: str = "") -> Optional[Dict]:
        """Get organization headquarters location for a domain with auto-detection and caching"""
        domain_lower = domain.lower()
        
        # 1. Check hardcoded ORGANIZATIONS
        if domain_lower in cls.ORGANIZATIONS:
            return cls.ORGANIZATIONS[domain_lower]
        
        # 2. Check cache file
        cache = cls._load_cache()
        if domain_lower in cache:
            return cache[domain_lower]
        
        # 3. Check partial match
=======
    def get_organization_location(cls, domain: str, hostname: str = "") -> Optional[Dict]:
        """Get organization headquarters location for a domain"""
        domain_lower = domain.lower()
        hostname_lower = hostname.lower()
        
        # Check exact domain match
        if domain_lower in cls.ORGANIZATIONS:
            return cls.ORGANIZATIONS[domain_lower]
        
        # Check partial match (e.g., .ac.mw domains)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        for org_domain, location in cls.ORGANIZATIONS.items():
            if org_domain in domain_lower or domain_lower.endswith(org_domain):
                return location
        
<<<<<<< HEAD
        # 4. Auto-detect from TLD
        detected = cls._detect_location_from_tld(domain)
        if detected:
            # Cache it for future use
            cache[domain_lower] = detected
            cls._save_cache(cache)
            return detected
        
        # 5. Check .africa domains
=======
        # Check if it's an .africa domain (could be any African country)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if domain_lower.endswith('.africa') or '.africa' in domain_lower:
            return {
                "country": "Africa (HQ Unknown)",
                "city": "Unknown",
                "lat": 0,
                "lon": 0,
                "flag": "🌍",
                "region": "Africa",
<<<<<<< HEAD
                "note": "Organization headquarters location unknown"
=======
                "note": "Organization headquarters location unknown - showing approximate continent"
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            }
        
        return None
    
    @classmethod
    def add_organization(cls, domain: str, country: str, city: str, lat: float, lon: float, flag: str = "🌐", region: str = "Unknown"):
<<<<<<< HEAD
        """Dynamically add an organization to the database and cache"""
        domain_lower = domain.lower()
        location = {
=======
        """Dynamically add an organization to the database"""
        cls.ORGANIZATIONS[domain.lower()] = {
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            "country": country,
            "city": city,
            "lat": lat,
            "lon": lon,
            "flag": flag,
            "region": region
        }
<<<<<<< HEAD
        # Add to in-memory database
        cls.ORGANIZATIONS[domain_lower] = location
        
        # Save to cache
        cache = cls._load_cache()
        cache[domain_lower] = location
        cls._save_cache(cache)
        
        print(f"[+] Added {domain} to organization database ({country})")


=======
        print(f"[+] Added {domain} to organization database ({country})")


# Initialize organization database at startup

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
# ============================================================
# Data Classes
# ============================================================

@dataclass
class NetworkNode:
    ip: str
    hostname: str = ""
    country: str = ""
    city: str = ""
    lat: float = 0.0
    lon: float = 0.0
    isp: str = ""
    ports: List[Dict] = field(default_factory=list)
    risk_score: float = 0.0
    is_organization_location: bool = False
    server_location: str = ""
<<<<<<< HEAD
    server_country: str = ""
    server_city: str = ""
    server_lat: float = 0.0
    server_lon: float = 0.0
    server_isp: str = ""
    org_country: str = ""
    org_city: str = ""
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44


@dataclass
class ScanHistory:
    timestamp: datetime
    target: str
    duration: float
    open_ports: int
    risk_score: float
    services: List[str]


# ============================================================
# AI Vulnerability Scorer
# ============================================================

class AIVulnerabilityScorer:
    @staticmethod
    def analyze_service(service: str, port: str, version: str = "") -> Dict:
        vuln_db = {
            "ftp": {"cvss_id": "CVE-2024-1234", "score": 7.5, "exploit": "Metasploit/ftp"},
            "ssh": {"cvss_id": "CVE-2024-5678", "score": 5.5, "exploit": "Hydra/SSH"},
            "telnet": {"cvss_id": "CVE-2024-9012", "score": 9.0, "exploit": "TelnetBleed"},
            "http": {"cvss_id": "CVE-2024-3456", "score": 6.5, "exploit": "SQLMap/HTTP"},
            "https": {"cvss_id": "CVE-2024-7890", "score": 5.0, "exploit": "Heartbleed"},
            "smb": {"cvss_id": "CVE-2024-2345", "score": 8.5, "exploit": "EternalBlue"},
            "rdp": {"cvss_id": "CVE-2024-6789", "score": 9.0, "exploit": "BlueKeep"},
            "domain": {"cvss_id": "CVE-2024-1111", "score": 6.0, "exploit": "DNSpoof"},
            "rtsp": {"cvss_id": "CVE-2024-3333", "score": 6.0, "exploit": "RTSP Brute"},
            "dns": {"cvss_id": "CVE-2024-5555", "score": 7.0, "exploit": "DNS Cache Poisoning"},
        }
        
        service_lower = service.lower()
        for vuln_service, data in vuln_db.items():
            if vuln_service in service_lower:
                severity = "CRITICAL" if data["score"] >= 9 else "HIGH" if data["score"] >= 7 else "MEDIUM"
                return {
                    "vulnerable": True,
                    "cvss_id": data["cvss_id"],
                    "cvss_score": data["score"],
                    "severity": severity,
                    "exploit": data["exploit"],
                    "recommendation": f"Patch {service} immediately" if data["score"] >= 7 else f"Update {service}"
                }
        
        return {"vulnerable": False, "cvss_score": 0, "severity": "LOW", "recommendation": "Monitor"}


# ============================================================
<<<<<<< HEAD
# Enhanced GeoIP Lookup with Dual Location
=======
# Enhanced GeoIP Lookup with Organization Location
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
# ============================================================

def get_server_location(ip: str) -> Dict:
    """Get actual server location (where the website is hosted)"""
    try:
<<<<<<< HEAD
        if ip.startswith(("192.168.", "10.", "172.", "127.", "169.254.", "::1")):
            return {"country": "Private Network", "city": "Local", "lat": 0, "lon": 0, "isp": "Private", "location": "Local Network"}
        
        if not re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
            resolved = resolve_domain_to_ip(ip)
            if resolved:
                ip = resolved
            else:
                return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "location": "Unknown"}
        import requests
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        
        if data.get('status') == 'success':
            return {
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
                "lat": data.get("lat", 0),
                "lon": data.get("lon", 0),
                "isp": data.get("isp", "Unknown"),
                "location": f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}",
                "is_organization_location": False
            }
        else:
            return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "location": "Unknown"}
    except requests.exceptions.Timeout:
        return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "location": "Unknown (Timeout)"}
    except Exception:
        return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "location": "Unknown"}


def enhanced_geoip_lookup(domain: str, ip: Optional[str] = None) -> Tuple[Dict, Dict, bool]:
    """
    Enhanced GeoIP that returns BOTH organization location AND server location
    Returns: (org_location, server_location, is_organization_location)
    """
    # If no IP provided, resolve domain
    if not ip or ip == domain:
        resolved_ip = resolve_domain_to_ip(domain)
        if resolved_ip:
            ip = resolved_ip
        else:
            ip = domain
    
    # Get organization headquarters location
    org_location = OrganizationLocationDB.get_organization_location(domain, ip)
    is_org_location = False
    
    if org_location and org_location.get("lat", 0) != 0:
        is_org_location = True
    else:
        org_location = {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "flag": "🌐"}
    
    # Get server location
    server_location = get_server_location(ip)
    
    return org_location, server_location, is_org_location


# ============================================================
# Enhanced GeoMap Visualizer with Dual Location Support
# ============================================================

class EnhancedGeoMapVisualizer:
    """Advanced Geographic Threat Intelligence Map with Dual Location Support"""
    
    def __init__(self):
        self.locations = []
        self.org_locations = []
=======
        if ip.startswith(("192.168.", "10.", "172.", "127.", "169.254.")):
            return {"country": "Private Network", "city": "Local", "lat": 0, "lon": 0, "isp": "Private", "location": "Local Network"}
        
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = response.json()
        return {
            "country": data.get("country", "Unknown"),
            "city": data.get("city", "Unknown"),
            "lat": data.get("lat", 0),
            "lon": data.get("lon", 0),
            "isp": data.get("isp", "Unknown"),
            "location": f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}",
            "is_organization_location": False
        }
    except:
        return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "location": "Unknown"}


def enhanced_geoip_lookup(domain: str, ip: str) -> Tuple[Dict, bool]:
    """
    Enhanced GeoIP that shows ORGANIZATION location, not server location
    Returns (location_dict, is_organization_location)
    """
    # First, check if we have the organization's headquarters location
    org_location = OrganizationLocationDB.get_organization_location(domain, ip)
    
    if org_location and org_location.get("lat", 0) != 0:
        # Get server location for comparison (CDN/cloud info)
        server_loc = get_server_location(ip)
        
        return {
            "country": org_location["country"],
            "city": org_location["city"],
            "lat": org_location["lat"],
            "lon": org_location["lon"],
            "flag": org_location.get("flag", "🌐"),
            "region": org_location.get("region", "Unknown"),
            "is_organization_location": True,
            "server_location": server_loc.get("location", "Unknown"),
            "server_country": server_loc.get("country", "Unknown"),
            "note": f"Showing organization headquarters in {org_location['country']}"
        }, True
    
    # Fallback to server location
    server_loc = get_server_location(ip)
    return server_loc, False


class EnhancedGeoMapVisualizer:
    """Advanced Geographic Threat Intelligence Map with Blinking Markers and Organization Locations"""
    
    def __init__(self):
        self.locations = []
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        
    def add_location(self, lat: float, lon: float, ip: str, risk_score: float, 
                     ports: List[Dict] = None, country: str = "", 
                     is_org_location: bool = False, server_location: str = "",
<<<<<<< HEAD
                     server_country: str = "", server_city: str = "",
                     server_lat: float = 0.0, server_lon: float = 0.0,
                     server_isp: str = "",
                     org_country: str = "", org_city: str = "",
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                     domain: str = ""):
        self.locations.append({
            "lat": lat, "lon": lon, "ip": ip, "risk_score": risk_score,
            "ports": ports or [], "country": country, "timestamp": datetime.now(),
            "is_organization_location": is_org_location,
            "server_location": server_location,
<<<<<<< HEAD
            "server_country": server_country,
            "server_city": server_city,
            "server_lat": server_lat,
            "server_lon": server_lon,
            "server_isp": server_isp,
            "org_country": org_country,
            "org_city": org_city,
            "domain": domain
        })
        
        # Also track organization locations separately for dual display
        if is_org_location and org_country:
            self.org_locations.append({
                "lat": lat, "lon": lon, "domain": domain,
                "org_country": org_country, "org_city": org_city,
                "server_location": server_location,
                "server_country": server_country,
                "server_city": server_city,
                "server_lat": server_lat,
                "server_lon": server_lon,
                "risk_score": risk_score
            })
    
    def generate_threat_map(self) -> str:
        """Generate interactive threat intelligence map with DUAL location display"""
=======
            "domain": domain
        })
    
    def generate_threat_map(self) -> str:
        """Generate interactive threat intelligence map with BLINKING lines and circles"""
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if not GEO_AVAILABLE:
            return '<div style="padding:50px;text-align:center;">🌍 GeoIP module not available</div>'
        
        m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter', control_scale=True)
        
<<<<<<< HEAD
        blink_css = """
        <style>
=======
        # CSS for blinking animations - LINES AND CIRCLES
        blink_css = """
        <style>
            /* Blinking animations for circles */
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            @keyframes blink-red { 
                0%, 100% { opacity: 1; filter: drop-shadow(0 0 5px #ff0000); transform: scale(1); } 
                50% { opacity: 0.3; filter: drop-shadow(0 0 20px #ff0000); transform: scale(1.2); } 
            }
            @keyframes blink-orange { 
                0%, 100% { opacity: 1; filter: drop-shadow(0 0 5px #ff6600); transform: scale(1); } 
                50% { opacity: 0.4; filter: drop-shadow(0 0 15px #ff6600); transform: scale(1.15); } 
            }
            @keyframes blink-yellow { 
                0%, 100% { opacity: 1; filter: drop-shadow(0 0 5px #ffcc00); transform: scale(1); } 
                50% { opacity: 0.5; filter: drop-shadow(0 0 10px #ffcc00); transform: scale(1.1); } 
            }
            @keyframes blink-green { 
                0%, 100% { opacity: 1; filter: drop-shadow(0 0 5px #00ff00); transform: scale(1); } 
                50% { opacity: 0.6; filter: drop-shadow(0 0 8px #00ff00); transform: scale(1.05); } 
            }
<<<<<<< HEAD
=======
            
            /* Blinking animations for lines */
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            @keyframes blink-line-red {
                0%, 100% { stroke: #ff0000; stroke-width: 2; stroke-dasharray: 5, 5; opacity: 1; }
                50% { stroke: #ff6666; stroke-width: 4; stroke-dasharray: 10, 5; opacity: 0.7; }
            }
            @keyframes blink-line-orange {
                0%, 100% { stroke: #ff6600; stroke-width: 2; stroke-dasharray: 5, 5; opacity: 1; }
                50% { stroke: #ffaa66; stroke-width: 3; stroke-dasharray: 8, 5; opacity: 0.7; }
            }
            @keyframes blink-line-yellow {
                0%, 100% { stroke: #ffcc00; stroke-width: 2; stroke-dasharray: 5, 5; opacity: 1; }
                50% { stroke: #ffeeaa; stroke-width: 3; stroke-dasharray: 6, 5; opacity: 0.7; }
            }
            @keyframes blink-line-green {
                0%, 100% { stroke: #00ff00; stroke-width: 1.5; stroke-dasharray: 4, 4; opacity: 1; }
                50% { stroke: #88ff88; stroke-width: 2.5; stroke-dasharray: 6, 4; opacity: 0.7; }
            }
<<<<<<< HEAD
=======
            
            /* Circle blinking classes */
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            .blink-critical { animation: blink-red 0.6s ease-in-out infinite; }
            .blink-high { animation: blink-orange 0.8s ease-in-out infinite; }
            .blink-medium { animation: blink-yellow 1s ease-in-out infinite; }
            .blink-low { animation: blink-green 1.2s ease-in-out infinite; }
<<<<<<< HEAD
=======
            
            /* Line blinking classes */
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            .line-critical { animation: blink-line-red 0.6s ease-in-out infinite; }
            .line-high { animation: blink-line-orange 0.8s ease-in-out infinite; }
            .line-medium { animation: blink-line-yellow 1s ease-in-out infinite; }
            .line-low { animation: blink-line-green 1.2s ease-in-out infinite; }
<<<<<<< HEAD
=======
            
            /* Pulse ring effect */
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            @keyframes pulse-ring {
                0% { transform: scale(0.8); opacity: 0.8; }
                100% { transform: scale(2); opacity: 0; }
            }
<<<<<<< HEAD
            .pulse-ring { animation: pulse-ring 1.5s ease-out infinite; }
=======
            .pulse-ring {
                animation: pulse-ring 1.5s ease-out infinite;
            }
            
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            .live-badge { 
                position: fixed; top: 10px; right: 10px; background: #00ff00; color: #000; 
                padding: 5px 10px; border-radius: 5px; font-family: monospace; font-size: 10px; 
                z-index: 1000; animation: blink-green 1s infinite; font-weight: bold;
            }
<<<<<<< HEAD
=======
            
            .org-marker {
                border: 3px solid #ffaa00;
                box-shadow: 0 0 10px rgba(255,170,0,0.5);
            }
            
            /* Animated connection line */
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            .animated-line {
                stroke-dasharray: 10;
                animation: dash 1s linear infinite;
            }
            @keyframes dash {
                to { stroke-dashoffset: -20; }
            }
<<<<<<< HEAD
            .dual-location-badge {
                background: rgba(0,0,0,0.8);
                color: #ffaa00;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 8px;
                margin-left: 5px;
                border: 1px solid #ffaa00;
            }
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        </style>
        """
        m.get_root().header.add_child(folium.Element(blink_css))
        m.get_root().html.add_child(folium.Element('<div class="live-badge">🔴 LIVE MONITORING ACTIVE 🔴</div>'))
        
        # Heatmap
        heat_data = [[loc["lat"], loc["lon"], loc["risk_score"] / 10] for loc in self.locations if loc["lat"] != 0]
        if heat_data:
            HeatMap(heat_data, radius=25, blur=15, max_zoom=6,
                gradient={0.2: 'blue', 0.5: 'lime', 0.8: 'orange', 1: 'red'}).add_to(m)
        
<<<<<<< HEAD
        valid_locations = [loc for loc in self.locations if loc["lat"] != 0]
        
        # Draw connection lines
=======
        # Create list of locations with valid coordinates for connection lines
        valid_locations = [loc for loc in self.locations if loc["lat"] != 0]
        
        # Draw BLINKING connection lines between locations
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if len(valid_locations) >= 2:
            for i in range(len(valid_locations) - 1):
                loc1 = valid_locations[i]
                loc2 = valid_locations[i + 1]
<<<<<<< HEAD
                avg_risk = (loc1["risk_score"] + loc2["risk_score"]) / 2
                if avg_risk >= 7:
                    line_class = "line-critical"
                    color = "#ff0000"
                elif avg_risk >= 4:
                    line_class = "line-high"
                    color = "#ff6600"
                elif avg_risk >= 2:
                    line_class = "line-medium"
                    color = "#ffcc00"
                else:
                    line_class = "line-low"
                    color = "#00ff00"
                
                folium.PolyLine(
                    locations=[[loc1["lat"], loc1["lon"]], [loc2["lat"], loc2["lon"]]],
                    color=color,
=======
                
                # Determine line color based on risk
                avg_risk = (loc1["risk_score"] + loc2["risk_score"]) / 2
                if avg_risk >= 7:
                    line_class = "line-critical"
                elif avg_risk >= 4:
                    line_class = "line-high"
                elif avg_risk >= 2:
                    line_class = "line-medium"
                else:
                    line_class = "line-low"
                
                # Draw blinking polyline
                folium.PolyLine(
                    locations=[[loc1["lat"], loc1["lon"]], [loc2["lat"], loc2["lon"]]],
                    color="#ff0000" if avg_risk >= 7 else "#ff6600" if avg_risk >= 4 else "#ffcc00" if avg_risk >= 2 else "#00ff00",
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                    weight=3,
                    opacity=0.8,
                    dash_array='5, 5',
                    className=line_class,
                    popup=f"Connection: {loc1['ip']} → {loc2['ip']}<br>Risk: {avg_risk:.1f}"
                ).add_to(m)
<<<<<<< HEAD
        
        # Add BLINKING markers for ALL locations
=======
                
                # Add animated directional arrow (small circle along the line)
                mid_lat = (loc1["lat"] + loc2["lat"]) / 2
                mid_lon = (loc1["lon"] + loc2["lon"]) / 2
                
                folium.CircleMarker(
                    location=[mid_lat, mid_lon],
                    radius=4,
                    color="#00ffff",
                    fill=True,
                    fill_color="#00ffff",
                    fill_opacity=0.8,
                    className="animated-line",
                    popup="Data Flow Direction"
                ).add_to(m)
        
        # Add BLINKING markers
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        for loc in self.locations:
            if loc["lat"] == 0:
                continue
            
            risk = loc["risk_score"]
            if risk >= 7:
                color = "#ff0000"
                blink_class = "blink-critical"
                radius = 16
<<<<<<< HEAD
                pulse_radius = 200000
=======
                icon = "💀"
                pulse_radius = 200000  # Large pulse for critical
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            elif risk >= 4:
                color = "#ff6600"
                blink_class = "blink-high"
                radius = 13
<<<<<<< HEAD
=======
                icon = "⚠️"
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                pulse_radius = 150000
            elif risk >= 2:
                color = "#ffcc00"
                blink_class = "blink-medium"
                radius = 10
<<<<<<< HEAD
=======
                icon = "●"
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                pulse_radius = 100000
            else:
                color = "#00ff00"
                blink_class = "blink-low"
                radius = 7
<<<<<<< HEAD
                pulse_radius = 50000
            
            # Build popup HTML with DUAL location info
            if loc.get("is_organization_location", False):
                # Show HQ location with server info
                popup_html = f"""
                <div style="font-family: monospace; background: #0a0a0a; color: #00ff00; padding: 12px; border-radius: 8px; min-width: 350px;">
                    <b style="color: #00ffff;">🏢 {loc.get('domain', loc['ip'])}</b><br>
                     
                    <b>📍 ORGANIZATION HEADQUARTERS:</b><br>
                    <span style="color: #ffcc00;">  🏛️ {loc.get('org_country', loc['country'])} - {loc.get('org_city', loc.get('city', 'Unknown'))}</span><br>
                    
                    <b>🖥️ SERVER/HOSTING LOCATION:</b><br>
                    <span style="color: #ff6600;">  🌍 {loc.get('server_country', 'Unknown')} - {loc.get('server_city', 'Unknown')}</span><br>
                    <span style="color: #888; font-size: 10px;">  Provider: {loc.get('server_isp', 'Unknown')}</span><br>
=======
                icon = "✓"
                pulse_radius = 50000
            
            # Build popup HTML
            if loc.get("is_organization_location", False):
                popup_html = f"""
                <div style="font-family: monospace; background: #0a0a0a; color: #00ff00; padding: 12px; border-radius: 8px; min-width: 320px;">
                    <b style="color: #00ffff;">🏢 {loc.get('domain', loc['ip'])}</b><br>
                    <hr style="border-color: #333; margin: 5px 0;">
                    
                    <b>📍 ORGANIZATION HEADQUARTERS:</b><br>
                    <span style="color: #ffcc00;">  {loc.get('flag', '🌐')} {loc['country']} - {loc.get('city', 'Unknown')}</span><br>
                    
                    <b>🖥️ SERVER/CLOUD LOCATION:</b><br>
                    <span style="color: #ff6600;">  🌍 {loc.get('server_location', 'Unknown')}</span><br>
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                    
                    <b>⚠️ Risk Score:</b> <span style="color: {color}; font-weight: bold;">{risk}/10</span><br>
                    <b>🔓 Open Ports:</b> {len(loc.get('ports', []))}<br>
                    <b>🔧 Services:</b> {', '.join([p.get('service', 'unknown') for p in loc.get('ports', [])[:3]])}<br>
                    
<<<<<<< HEAD
                    <span style="color: #888; font-size: 10px;">📌 Showing HQ location with server location overlay</span>
                    <br><span style="color: #ff6600; font-size: 10px;">🔘 Blinking circle indicates live monitoring</span>
                </div>
                """
                # Star for organization headquarters
=======
                    <hr style="border-color: #333; margin: 5px 0;">
                    <span style="color: #888; font-size: 10px;">ℹ️ Organization uses CDN/Cloud hosting - showing HQ location</span>
                    <br><span style="color: #ff6600; font-size: 10px;">🔘 Blinking circle indicates live monitoring</span>
                </div>
                """
                # Add star marker for organization headquarters
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                folium.Marker(
                    location=[loc["lat"], loc["lon"]],
                    icon=folium.Icon(color="orange", icon="star", prefix="fa"),
                    popup=folium.Popup(popup_html, max_width=400)
                ).add_to(m)
<<<<<<< HEAD
                
                # Also add a small circle marker at the HQ location
                folium.CircleMarker(
                    location=[loc["lat"], loc["lon"]],
                    radius=radius,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.6,
                    weight=2,
                    className=blink_class,
                    popup=folium.Popup(popup_html, max_width=400)
                ).add_to(m)
                
                # Add server location as a separate marker if different from HQ
                if (loc.get("server_country") and loc["server_country"] != loc.get("org_country", "") and 
                    loc.get("server_lat") and loc.get("server_lon") and
                    loc["server_lat"] != 0 and loc["server_lon"] != 0):
                    server_html = f"""
                    <div style="font-family: monospace; background: #0a0a0a; color: #00ff00; padding: 10px; border-radius: 8px; min-width: 250px;">
                        <b style="color: #ff6600;">🌐 {loc.get('domain', loc['ip'])} - SERVER</b><br>
                        <hr style="border-color: #333; margin: 5px 0;">
                        <b>📍 Location:</b> {loc.get('server_country', 'Unknown')} - {loc.get('server_city', 'Unknown')}<br>
                        <b>🖥️ Hosting Provider:</b> {loc.get('server_isp', 'Unknown')}<br>
                        <span style="color: #888; font-size: 10px;">📌 Server location (CDN/Cloud hosting)</span>
                    </div>
                    """
                    folium.CircleMarker(
                        location=[loc["server_lat"], loc["server_lon"]],
                        radius=6,
                        color="#ff6600",
                        fill=True,
                        fill_color="#ff6600",
                        fill_opacity=0.7,
                        weight=2,
                        popup=folium.Popup(server_html, max_width=300)
                    ).add_to(m)
                    
                    # Connection line between HQ and Server
                    folium.PolyLine(
                        locations=[[loc["lat"], loc["lon"]], [loc["server_lat"], loc["server_lon"]]],
                        color="#ffaa00",
                        weight=1.5,
                        opacity=0.5,
                        dash_array='5, 10',
                        popup=f"🏢 HQ → 🖥️ Server: {loc.get('domain', '')}"
                    ).add_to(m)
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            else:
                popup_html = f"""
                <div style="font-family: monospace; background: #0a0a0a; color: #00ff00; padding: 12px; border-radius: 8px; min-width: 280px;">
                    <b style="color: #00ffff;">🎯 {loc.get('domain', loc['ip'])}</b><br>
                    <hr style="border-color: #333; margin: 5px 0;">
                    
                    <b>🖥️ SERVER LOCATION:</b><br>
<<<<<<< HEAD
                    <span style="color: #ffcc00;">  🌍 {loc.get('country', 'Unknown')} - {loc.get('city', 'Unknown')}</span><br>
                    <span style="color: #888; font-size: 10px;">  Provider: {loc.get('server_isp', 'Unknown')}</span><br>
=======
                    <span style="color: #ffcc00;">  {loc.get('flag', '🌐')} {loc['country']} - {loc.get('city', 'Unknown')}</span><br>
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                    
                    <b>⚠️ Risk Score:</b> <span style="color: {color}; font-weight: bold;">{risk}/10</span><br>
                    <b>🔓 Open Ports:</b> {len(loc.get('ports', []))}<br>
                    <b>🔧 Services:</b> {', '.join([p.get('service', 'unknown') for p in loc.get('ports', [])[:3]])}<br>
                    
                    <hr style="border-color: #333; margin: 5px 0;">
                    <span style="color: #888; font-size: 10px;">ℹ️ Server location detected via GeoIP</span>
                    <br><span style="color: #ff6600; font-size: 10px;">🔘 Blinking circle indicates live monitoring</span>
                </div>
                """
                
<<<<<<< HEAD
=======
                # Add BLINKING circle marker
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                folium.CircleMarker(
                    location=[loc["lat"], loc["lon"]],
                    radius=radius,
                    popup=folium.Popup(popup_html, max_width=350),
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.8,
                    weight=3,
                    className=blink_class
                ).add_to(m)
            
<<<<<<< HEAD
=======
            # Add PULSE RING effect for critical/high risk
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            if risk >= 4:
                folium.Circle(
                    location=[loc["lat"], loc["lon"]],
                    radius=pulse_radius,
                    color=color,
                    fill=True,
                    fill_opacity=0.05,
                    weight=2,
                    className="pulse-ring",
                    popup=f"⚠️ Active Threat Zone - Risk Level: {risk}/10"
                ).add_to(m)
        
<<<<<<< HEAD
        # Network mesh lines
=======
        # Add BLINKING connection lines between all location pairs (network mesh)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if len(valid_locations) >= 2:
            for i in range(len(valid_locations)):
                for j in range(i + 1, len(valid_locations)):
                    loc1 = valid_locations[i]
                    loc2 = valid_locations[j]
<<<<<<< HEAD
=======
                    
                    # Calculate distance-based risk
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                    dist_risk = (loc1["risk_score"] + loc2["risk_score"]) / 2
                    
                    if dist_risk >= 7:
                        line_color = "#ff0000"
                        line_class = "line-critical"
                        weight = 3
                    elif dist_risk >= 4:
                        line_color = "#ff6600"
                        line_class = "line-high"
                        weight = 2.5
                    elif dist_risk >= 2:
                        line_color = "#ffcc00"
                        line_class = "line-medium"
                        weight = 2
                    else:
                        line_color = "#00ff00"
                        line_class = "line-low"
                        weight = 1.5
                    
                    folium.PolyLine(
                        locations=[[loc1["lat"], loc1["lon"]], [loc2["lat"], loc2["lon"]]],
                        color=line_color,
                        weight=weight,
                        opacity=0.7,
                        dash_array='8, 6',
                        className=line_class,
                        popup=f"Network Link<br>{loc1['ip']} ↔ {loc2['ip']}<br>Risk: {dist_risk:.1f}"
                    ).add_to(m)
        
<<<<<<< HEAD
        # Legend with dual location indicator
=======
        # Legend with blinking indicators
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        legend_html = '''
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000; background: rgba(0,0,0,0.85); padding: 12px; border-radius: 8px; border: 1px solid #00ff00; font-family: monospace; font-size: 10px;">
            <b style="color: #00ff00;">🗺️ THREAT LEGEND</b><br>
            <span style="color:#ff0000; animation: blink-red 0.6s infinite;">🔴</span> Critical (Risk 7-10)<br>
            <span style="color:#ff6600; animation: blink-orange 0.8s infinite;">🟠</span> High (Risk 5-6)<br>
            <span style="color:#ffcc00; animation: blink-yellow 1s infinite;">🟡</span> Medium (Risk 3-4)<br>
            <span style="color:#00ff00; animation: blink-green 1.2s infinite;">🟢</span> Low (Risk 0-2)<br>
            <span style="color:#ffaa00;">⭐</span> Organization Headquarters<br>
<<<<<<< HEAD
            <span style="color:#ff6600;">●</span> Server/Cloud Location<br>
            <span style="color:#ffaa00;">━━━</span> <span style="animation: blink-green 1s infinite;">HQ → Server Connection</span><br>
            <span style="color:#00ffff;">━━━</span> <span style="animation: blink-green 1s infinite;">Network Link</span><br>
            <span style="color:#ff00ff;">◉</span> <span style="animation: blink-red 1s infinite;">Pulse Ring = Active Threat Zone</span>
            <br><span style="color:#ffaa00; font-size:9px;">🏢 Dual Location: HQ + Server</span>
=======
            <span style="color:#00ffff;">━━━</span> <span style="animation: blink-green 1s infinite;">Blinking Connection</span><br>
            <span style="color:#ff00ff;">◉</span> <span style="animation: blink-red 1s infinite;">Pulse Ring = Active Threat Zone</span>
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m._repr_html_()
<<<<<<< HEAD


# ============================================================
# Interactive SOC Dashboard
# ============================================================

=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
class InteractiveSOCDashboard:
    def __init__(self):
        self.workspace = os.path.expanduser("~/dsterminal_workspace")
        self.scans_dir = os.path.join(self.workspace, "scans")
        os.makedirs(self.scans_dir, exist_ok=True)
        
        self.network_nodes: Dict[str, NetworkNode] = {}
        self.discovered_ports = []
        self.services_found = []
        self.scan_duration = 0
        self.current_target = ""
        self.scan_active = False
        self.ai_scorer = AIVulnerabilityScorer()
        self.geo_map = EnhancedGeoMapVisualizer()
        self.scan_history: List[ScanHistory] = []
<<<<<<< HEAD
        self.scan_output = []  # Store scan output lines for persistence
        self.host_details = {}  # Store host details

        self.history_file = os.path.join(self.scans_dir, "scan_history.json")
        self._load_history()
        
=======
        

        # Load history from file
        self.history_file = os.path.join(self.scans_dir, "scan_history.json")
        self._load_history()
        
        # Terminal display settings
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        self.spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.terminal_width = self._get_terminal_width()

    def _get_terminal_width(self):
<<<<<<< HEAD
=======
        """Get terminal width safely"""
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        try:
            return shutil.get_terminal_size((100, 24)).columns
        except:
            return 100
<<<<<<< HEAD
            
    def _load_history(self):
=======
    def _load_history(self):
        """Load scan history from file"""
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        hist = ScanHistory(
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            target=item['target'],
                            duration=item['duration'],
                            open_ports=item['open_ports'],
                            risk_score=item['risk_score'],
                            services=item['services']
                        )
                        self.scan_history.append(hist)
            except:
                pass
    
    def _save_history(self):
<<<<<<< HEAD
=======
        """Save scan history to file"""
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        try:
            data = []
            for hist in self.scan_history:
                data.append({
                    'timestamp': hist.timestamp.isoformat(),
                    'target': hist.target,
                    'duration': hist.duration,
                    'open_ports': hist.open_ports,
                    'risk_score': hist.risk_score,
                    'services': hist.services
                })
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
        
    def generate_pdf_report(self, target: str = None) -> str:
<<<<<<< HEAD
=======
        """Generate professional PDF report of scan results"""
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from reportlab.pdfgen import canvas
            import datetime
            
<<<<<<< HEAD
=======
            # Create PDF filename
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            if not target:
                target = self.current_target if self.current_target else "scan"
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"soc_report_{target.replace('.', '_')}_{timestamp}.pdf"
            pdf_path = os.path.join(self.scans_dir, pdf_filename)
            
<<<<<<< HEAD
=======
            # Create the PDF document
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=72)
            
<<<<<<< HEAD
=======
            # Styles
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#00ff00'),
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#00ffff'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            risk_high_style = ParagraphStyle(
                'RiskHigh',
                parent=styles['Normal'],
                textColor=colors.HexColor('#ff0000'),
                fontSize=10
            )
            
            risk_medium_style = ParagraphStyle(
                'RiskMedium',
                parent=styles['Normal'],
                textColor=colors.HexColor('#ffcc00'),
                fontSize=10
            )
            
            risk_low_style = ParagraphStyle(
                'RiskLow',
                parent=styles['Normal'],
                textColor=colors.HexColor('#00ff00'),
                fontSize=10
            )
            
<<<<<<< HEAD
            story = []
            
            story.append(Paragraph("DSTERMINAL SOC Security Assessment Report", title_style))
            story.append(Spacer(1, 12))
            
=======
            # Build story (content)
            story = []
            
            # Title
            story.append(Paragraph("DSTERMINAL SOC Security Assessment Report", title_style))
            story.append(Spacer(1, 12))
            
            # Report metadata
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            story.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"Target: {target}", styles['Normal']))
            story.append(Paragraph(f"Scan Duration: {self.scan_duration} seconds", styles['Normal']))
            story.append(Spacer(1, 20))
            
<<<<<<< HEAD
=======
            # Executive Summary
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            story.append(Paragraph("Executive Summary", heading_style))
            
            total_risk = sum(p.get("risk_score", 0) for p in self.discovered_ports)
            avg_risk = total_risk / max(1, len(self.discovered_ports))
            
            if avg_risk >= 7:
                risk_level = "CRITICAL"
                risk_color = colors.HexColor('#ff0000')
            elif avg_risk >= 4:
                risk_level = "WARNING"
                risk_color = colors.HexColor('#ffcc00')
            else:
                risk_level = "LOW"
                risk_color = colors.HexColor('#00ff00')
            
            summary_text = f"""
            <b>Risk Assessment Score: {avg_risk:.1f}/10 - {risk_level}</b><br/>
            <br/>
            This report summarizes the security assessment performed on {target}. 
            The scan identified {len(self.network_nodes)} host(s) with {len(self.discovered_ports)} open ports 
            and {len(self.services_found)} active services.<br/>
            <br/>
            <b>Key Findings:</b><br/>
            • Total Open Ports: {len(self.discovered_ports)}<br/>
            • Total Services: {len(self.services_found)}<br/>
            • Average Risk Score: {avg_risk:.1f}/10<br/>
            • Scan Duration: {self.scan_duration} seconds
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
<<<<<<< HEAD
            story.append(Paragraph("Discovered Services & Vulnerabilities", heading_style))
            
            if self.services_found:
                table_data = [['Port', 'Service', 'Version', 'Risk Score', 'Exploit', 'CVE ID']]
                
                for service in self.services_found[:20]:
=======
            # Discovered Services Table
            story.append(Paragraph("Discovered Services & Vulnerabilities", heading_style))
            
            if self.services_found:
                # Table data
                table_data = [['Port', 'Service', 'Version', 'Risk Score', 'Exploit', 'CVE ID']]
                
                for service in self.services_found[:20]:  # Limit to 20 for PDF
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                    risk_score = service.get("risk_score", 0)
                    risk_str = f"{risk_score:.1f}"
                    
                    table_data.append([
                        f"{service['port']}/{service['protocol']}",
                        service['service'][:20],
                        service.get('version', 'N/A')[:15],
                        risk_str,
                        service.get('exploit', 'N/A')[:15],
                        service.get('cvss_id', 'N/A')
                    ])
                
<<<<<<< HEAD
=======
                # Create table
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                table = Table(table_data, colWidths=[60, 80, 70, 50, 80, 70])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00ffff')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                story.append(table)
            else:
                story.append(Paragraph("No services discovered during the scan.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
<<<<<<< HEAD
=======
            # Critical Findings (High Risk)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            high_risk = [s for s in self.services_found if s.get("risk_score", 0) >= 7]
            if high_risk:
                story.append(Paragraph("Critical Findings (High Risk)", heading_style))
                for service in high_risk[:10]:
                    finding_text = f"""
                    <b>• {service['port']}/{service['protocol']} - {service['service']}</b><br/>
                    Risk Score: {service['risk_score']}/10 | CVE: {service.get('cvss_id', 'N/A')}<br/>
                    Exploit: {service.get('exploit', 'N/A')}<br/>
                    Recommendation: {service.get('recommendation', 'Patch immediately')}
                    """
                    story.append(Paragraph(finding_text, risk_high_style))
                    story.append(Spacer(1, 10))
            
<<<<<<< HEAD
=======
            # Medium Risk Findings
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            medium_risk = [s for s in self.services_found if 4 <= s.get("risk_score", 0) < 7]
            if medium_risk:
                story.append(Paragraph("Medium Risk Findings", heading_style))
                for service in medium_risk[:10]:
                    finding_text = f"""
                    <b>• {service['port']}/{service['protocol']} - {service['service']}</b><br/>
                    Risk Score: {service['risk_score']}/10 | CVE: {service.get('cvss_id', 'N/A')}
                    """
                    story.append(Paragraph(finding_text, risk_medium_style))
                    story.append(Spacer(1, 10))
            
            story.append(PageBreak())
            
<<<<<<< HEAD
=======
            # Network Topology
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            story.append(Paragraph("Network Topology Analysis", heading_style))
            
            if self.network_nodes:
                topo_data = [['Host', 'Open Ports', 'Risk Score', 'Location Type']]
                for ip, node in self.network_nodes.items():
<<<<<<< HEAD
                    location_type = "🏢 HQ + Server" if node.is_organization_location else "🖥️ Server"
=======
                    location_type = "🏢 HQ" if node.is_organization_location else "🖥️ Server"
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                    topo_data.append([
                        ip[:15],
                        str(len(node.ports)),
                        f"{node.risk_score:.1f}",
                        location_type
                    ])
                
<<<<<<< HEAD
                topo_table = Table(topo_data, colWidths=[100, 70, 70, 100])
=======
                topo_table = Table(topo_data, colWidths=[100, 70, 70, 80])
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                topo_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00ffff')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                story.append(topo_table)
            else:
                story.append(Paragraph("No network topology data available.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
<<<<<<< HEAD
=======
            # Recommendations
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            story.append(Paragraph("Security Recommendations", heading_style))
            
            recommendations = []
            for service in self.services_found:
                if service.get("risk_score", 0) >= 7:
                    recommendations.append(f"• CRITICAL: Patch {service['service']} on port {service['port']} immediately")
                elif service.get("risk_score", 0) >= 4:
                    recommendations.append(f"• MEDIUM: Update {service['service']} on port {service['port']}")
            
            if recommendations:
                for rec in recommendations[:10]:
                    story.append(Paragraph(rec, styles['Normal']))
                    story.append(Spacer(1, 5))
            else:
                story.append(Paragraph("No critical recommendations at this time. Continue regular security monitoring.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
<<<<<<< HEAD
            story.append(Paragraph("This report was automatically generated by DSTERMINAL Cyber-Ops Platform", styles['Normal']))
            story.append(Paragraph("For questions or support, contact your security team.", styles['Normal']))
            
=======
            # Footer note
            story.append(Paragraph("This report was automatically generated by DSTERMINAL Cyber-Ops Platform", styles['Normal']))
            story.append(Paragraph("For questions or support, contact your security team.", styles['Normal']))
            
            # Build PDF
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            doc.build(story)
            
            print(f"{Colors.GREEN}[+] PDF Report generated: {pdf_path}{Colors.RESET}")
            return pdf_path
            
        except ImportError:
            print(f"{Colors.RED}[!] ReportLab not installed. Install with: pip install reportlab{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.RED}[!] PDF generation failed: {e}{Colors.RESET}")
            return None
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def center(self, text: str) -> str:
        return text.center(self.terminal_width)
    
    def draw_header(self):
        header = f"""
{Colors.RED}{Colors.BOLD}
{self.center("╔" + "═" * 76 + "╗")}
{self.center("║" + " " * 76 + "║")}
{self.center("║" + " " * 10 + "██████╗ ███████╗████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗" + " " * 10 + "║")}
{self.center("║" + " " * 10 + "██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║" + " " * 10 + "║")}
{self.center("║" + " " * 10 + "██║  ██║███████╗   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║" + " " * 10 + "║")}
{self.center("║" + " " * 10 + "██║  ██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║" + " " * 10 + "║")}
{self.center("║" + " " * 10 + "██████╔╝███████╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗" + " " * 10 + "║")}
{self.center("║" + " " * 10 + "╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝" + " " * 10 + "║")}
{self.center("║" + " " * 76 + "║")}
{self.center("║" + " " * 20 + Colors.YELLOW + "⚡ SOC-GRADE NETWORK INTELLIGENCE ⚡" + Colors.RED + " " * 20 + "║")}
{self.center("║" + " " * 25 + Colors.DIM + "Real-time Scanning | AI Scoring | Threat Intelligence | DNS Reconnaissance" + Colors.RED + " " * 25 + "║")}
<<<<<<< HEAD
{self.center("║" + " " * 25 + Colors.CYAN + "🏢 HQ + Server Dual Location Tracking" + Colors.RED + " " * 25 + "║")}
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
{self.center("║" + " " * 76 + "║")}
{self.center("╚" + "═" * 76 + "╝")}
{Colors.RESET}
"""
        print(header)
    
    def draw_centered_dashboard(self):
<<<<<<< HEAD
=======
        """
        Ultra-centered SOC dashboard with:
        LEFT PANEL  | CENTER PANEL | RIGHT PANEL
        """
        # Get actual terminal width safely
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        try:
            terminal_width = shutil.get_terminal_size((80, 24)).columns
        except:
            terminal_width = 80
        
<<<<<<< HEAD
        if terminal_width < 120:
            panel_width = 38
            spacing = 5
=======
        # Adjust panel widths based on terminal size
        if terminal_width < 120:
            panel_width = 38
            spacing = 5

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        elif terminal_width < 150:
            panel_width = 38
            spacing = 5
        else:
<<<<<<< HEAD
            panel_width = 38
            spacing = 18
=======
            panel_width = 35
            spacing = 45
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        
        total_width = (panel_width * 3) + (spacing * 2)
        left_padding = max(0, (terminal_width - total_width) // 2)
        pad = " " * left_padding

<<<<<<< HEAD
=======
        # =========================================================
        # LEFT PANEL
        # =========================================================

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        left_panel = [
            f"{Colors.CYAN}┌{'─' * panel_width}┐{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} {Colors.BOLD}{Colors.GREEN}🎯 SCAN CONTROL CENTER{Colors.RESET}{' ' * 8}{Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}├{'─' * panel_width}┤{Colors.RESET}",
<<<<<<< HEAD
=======

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            f"{Colors.CYAN}│{Colors.RESET} {Colors.YELLOW}[1]{Colors.RESET} Quick Scan{' ' * 18}{Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} {Colors.YELLOW}[2]{Colors.RESET} Standard Scan{' ' * 15}{Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} {Colors.YELLOW}[3]{Colors.RESET} Full Aggressive{' ' * 13}{Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} {Colors.YELLOW}[4]{Colors.RESET} DNS Recon{' ' * 20}{Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} {Colors.YELLOW}[5]{Colors.RESET} UDP Scan{' ' * 20}{Colors.CYAN}│{Colors.RESET}",
<<<<<<< HEAD
            f"{Colors.CYAN}├{'─' * panel_width}┤{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} Target : {Colors.GREEN}{self.current_target[:18]:<18}{Colors.RESET} {Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} Status : {Colors.RED if self.scan_active else Colors.YELLOW}{'● ACTIVE' if self.scan_active else '○ IDLE'}{Colors.RESET}{' ' * 17}{Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}└{'─' * panel_width}┘{Colors.RESET}",
        ]

=======

            f"{Colors.CYAN}├{'─' * panel_width}┤{Colors.RESET}",

            f"{Colors.CYAN}│{Colors.RESET} Target : {Colors.GREEN}{self.current_target[:18]:<18}{Colors.RESET} {Colors.CYAN}│{Colors.RESET}",
            f"{Colors.CYAN}│{Colors.RESET} Status : {Colors.RED if self.scan_active else Colors.YELLOW}{'● ACTIVE' if self.scan_active else '○ IDLE'}{Colors.RESET}{' ' * 17}{Colors.CYAN}│{Colors.RESET}",

            f"{Colors.CYAN}└{'─' * panel_width}┘{Colors.RESET}",
        ]

        # =========================================================
        # CENTER PANEL
        # =========================================================

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        total_risk = sum(p.get("risk_score", 0) for p in self.discovered_ports)
        avg_risk = total_risk / max(1, len(self.discovered_ports))

        risk_bar_size = 22
        filled = int((avg_risk / 10) * risk_bar_size)
        risk_bar = "█" * filled + "░" * (risk_bar_size - filled)

        if avg_risk >= 7:
            risk_color = Colors.RED
            threat = "CRITICAL"
        elif avg_risk >= 4:
            risk_color = Colors.YELLOW
            threat = "WARNING"
        else:
            risk_color = Colors.GREEN
            threat = "LOW"

        center_panel = [
            f"{Colors.MAGENTA}┌{'─' * panel_width}┐{Colors.RESET}",
            f"{Colors.MAGENTA}│{Colors.RESET} {Colors.BOLD}{Colors.CYAN}🛡 SOC LIVE STATUS{Colors.RESET}{' ' * 13}{Colors.MAGENTA}│{Colors.RESET}",
            f"{Colors.MAGENTA}├{'─' * panel_width}┤{Colors.RESET}",
<<<<<<< HEAD
=======

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            f"{Colors.MAGENTA}│{Colors.RESET} Hosts Found : {Colors.GREEN}{len(self.network_nodes):<10}{Colors.RESET}{' ' * 9}{Colors.MAGENTA}│{Colors.RESET}",
            f"{Colors.MAGENTA}│{Colors.RESET} Open Ports : {Colors.GREEN}{len(self.discovered_ports):<10}{Colors.RESET}{' ' * 9}{Colors.MAGENTA}│{Colors.RESET}",
            f"{Colors.MAGENTA}│{Colors.RESET} Services    : {Colors.GREEN}{len(self.services_found):<10}{Colors.RESET}{' ' * 9}{Colors.MAGENTA}│{Colors.RESET}",
            f"{Colors.MAGENTA}│{Colors.RESET} Duration    : {Colors.GREEN}{self.scan_duration}s{' ' * 16}{Colors.RESET}{Colors.MAGENTA}│{Colors.RESET}",
<<<<<<< HEAD
            f"{Colors.MAGENTA}├{'─' * panel_width}┤{Colors.RESET}",
            f"{Colors.MAGENTA}│{Colors.RESET} Threat Level:{' ' * 18}{Colors.MAGENTA}│{Colors.RESET}",
            f"{Colors.MAGENTA}│{Colors.RESET} {risk_color}{risk_bar}{Colors.RESET} {avg_risk:.1f}/10 {Colors.MAGENTA}│{Colors.RESET}",
            f"{Colors.MAGENTA}│{Colors.RESET} Status : {risk_color}{threat}{Colors.RESET}{' ' * (21 - len(threat))}{Colors.MAGENTA}│{Colors.RESET}",
            f"{Colors.MAGENTA}└{'─' * panel_width}┘{Colors.RESET}",
        ]

=======

            f"{Colors.MAGENTA}├{'─' * panel_width}┤{Colors.RESET}",

            f"{Colors.MAGENTA}│{Colors.RESET} Threat Level:{' ' * 18}{Colors.MAGENTA}│{Colors.RESET}",
            f"{Colors.MAGENTA}│{Colors.RESET} {risk_color}{risk_bar}{Colors.RESET} {avg_risk:.1f}/10 {Colors.MAGENTA}│{Colors.RESET}",
            f"{Colors.MAGENTA}│{Colors.RESET} Status : {risk_color}{threat}{Colors.RESET}{' ' * (21 - len(threat))}{Colors.MAGENTA}│{Colors.RESET}",

            f"{Colors.MAGENTA}└{'─' * panel_width}┘{Colors.RESET}",
        ]

        # =========================================================
        # RIGHT PANEL
        # =========================================================

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        right_panel = [
            f"{Colors.BLUE}┌{'─' * panel_width}┐{Colors.RESET}",
            f"{Colors.BLUE}│{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🔍 LIVE DISCOVERIES{Colors.RESET}{' ' * 11}{Colors.BLUE}│{Colors.RESET}",
            f"{Colors.BLUE}├{'─' * panel_width}┤{Colors.RESET}",
        ]

        recent = self.discovered_ports[-6:]

        if recent:
            for p in recent:
                port = f"{p['port']}/{p['protocol']}"
                service = p["service"][:14]
<<<<<<< HEAD
                score = p.get("risk_score", 0)
=======

                score = p.get("risk_score", 0)

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                if score >= 7:
                    color = Colors.RED
                    icon = "⚠"
                elif score >= 4:
                    color = Colors.YELLOW
                    icon = "●"
                else:
                    color = Colors.GREEN
                    icon = "✓"
<<<<<<< HEAD
                line = f"{icon} {port:<10} {service:<14}"
=======

                line = f"{icon} {port:<10} {service:<14}"

>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
                right_panel.append(
                    f"{Colors.BLUE}│{Colors.RESET} {color}{line:<32}{Colors.RESET}{Colors.BLUE}│{Colors.RESET}"
                )
        else:
            for _ in range(6):
                right_panel.append(
                    f"{Colors.BLUE}│{Colors.RESET} {Colors.DIM}Waiting for scan results...{Colors.RESET}{' ' * 4}{Colors.BLUE}│{Colors.RESET}"
                )

        right_panel.extend([
            f"{Colors.BLUE}├{'─' * panel_width}┤{Colors.RESET}",
            f"{Colors.BLUE}│{Colors.RESET} Updated : {Colors.GREEN}{datetime.now().strftime('%H:%M:%S')}{Colors.RESET}{' ' * 12}{Colors.BLUE}│{Colors.RESET}",
            f"{Colors.BLUE}└{'─' * panel_width}┘{Colors.RESET}",
        ])

<<<<<<< HEAD
        max_lines = max(len(left_panel), len(center_panel), len(right_panel))

        for i in range(max_lines):
            left = left_panel[i] if i < len(left_panel) else " " * (panel_width + 2)
            center = center_panel[i] if i < len(center_panel) else " " * (panel_width + 2)
            right = right_panel[i] if i < len(right_panel) else " " * (panel_width + 2)
            print(pad + left + (" " * spacing) + center + (" " * spacing) + right)
=======
        # =========================================================
        # RENDER DASHBOARD
        # =========================================================

        max_lines = max(
            len(left_panel),
            len(center_panel),
            len(right_panel)
        )

        for i in range(max_lines):

            left = left_panel[i] if i < len(left_panel) else " " * (panel_width + 2)
            center = center_panel[i] if i < len(center_panel) else " " * (panel_width + 2)
            right = right_panel[i] if i < len(right_panel) else " " * (panel_width + 2)

            print(
                pad +
                left +
                (" " * spacing) +
                center +
                (" " * spacing) +
                right
            )
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    
    def draw_results_table(self):
        if not self.services_found:
            print(f"\n{self.center(Colors.YELLOW + '─' * 70 + Colors.RESET)}")
            print(self.center(Colors.YELLOW + ' ' * 28 + '⚠ NO RESULTS YET ⚠' + Colors.RESET))
            print(self.center(Colors.YELLOW + '─' * 70 + Colors.RESET))
            return
        
        print(f"\n{self.center(Colors.CYAN + Colors.BOLD + '─' * 90 + Colors.RESET)}")
        print(self.center(Colors.CYAN + Colors.BOLD + '│' + ' ' * 38 + '🔓 DISCOVERED SERVICES 🔓' + ' ' * 38 + '│' + Colors.RESET))
        print(self.center(Colors.CYAN + Colors.BOLD + '─' * 90 + Colors.RESET))
        
        header = f"{Colors.CYAN}│ {Colors.GREEN}PORT{Colors.RESET} │ {Colors.GREEN}SERVICE{Colors.RESET} │ {Colors.GREEN}VERSION{Colors.RESET} │ {Colors.GREEN}RISK{Colors.RESET} │ {Colors.GREEN}EXPLOIT{Colors.RESET} │{Colors.CYAN}"
        print(self.center(header))
        print(self.center(Colors.CYAN + '─' * 90 + Colors.RESET))
        
        for service in self.services_found[:8]:
            risk_score = service.get("risk_score", 0)
            if risk_score >= 7:
                risk_text = f"{Colors.RED}⚠ HIGH ⚠{Colors.RESET}"
            elif risk_score >= 4:
                risk_text = f"{Colors.YELLOW}● MED ●{Colors.RESET}"
            else:
                risk_text = f"{Colors.GREEN}○ LOW ○{Colors.RESET}"
            
            exploit_info = service.get("exploit", "N/A")[:10]
            line = f"{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}{service['port']}/{service['protocol']:<4}{Colors.RESET} │ {Colors.CYAN}{service['service'][:10]:<10}{Colors.RESET} │ {Colors.DIM}{service.get('version', 'N/A')[:8]:<8}{Colors.RESET} │ {risk_text:<10} │ {Colors.PURPLE}{exploit_info:<10}{Colors.RESET} │{Colors.CYAN}"
            print(self.center(line))
        
        print(self.center(Colors.CYAN + '─' * 90 + Colors.RESET))
    
    def draw_footer(self):
        footer = f"""
{Colors.DIM}{self.center('═' * 90)}{Colors.RESET}
{self.center(Colors.DIM + ' Commands: ' + Colors.GREEN + '[S]' + Colors.DIM + ' Scan  ' + Colors.YELLOW + '[Q]' + Colors.DIM + ' Quick  ' + Colors.RED + '[F]' + Colors.DIM + ' Full  ' + Colors.CYAN + '[D]' + Colors.DIM + ' DNS Recon  ' + Colors.MAGENTA + '[H]' + Colors.DIM + ' Help  ' + Colors.WHITE + '[X]' + Colors.DIM + ' Exit')}{Colors.RESET}
{Colors.DIM}{self.center('═' * 90)}{Colors.RESET}
"""
        print(footer)
    
<<<<<<< HEAD
    def enhanced_geoip_lookup(self, hostname: str, ip: str = None) -> Tuple[Dict, Dict, bool]:
        """Enhanced GeoIP lookup with organization location override and dual location support"""
        if not ip or ip == hostname:
            resolved_ip = resolve_domain_to_ip(hostname)
            if resolved_ip:
                ip = resolved_ip
            else:
                ip = hostname
        
        # Get organization headquarters location
        org_location = OrganizationLocationDB.get_organization_location(hostname, ip)
        is_org_location = False
        
        if org_location and org_location.get("lat", 0) != 0:
            is_org_location = True
        else:
            org_location = {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "flag": "🌐"}
        
        # Get server location
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
            server_data = response.json()
            if server_data.get('status') == 'success':
                server_location = {
                    "country": server_data.get("country", "Unknown"),
                    "city": server_data.get("city", "Unknown"),
                    "lat": server_data.get("lat", 0),
                    "lon": server_data.get("lon", 0),
                    "isp": server_data.get("isp", "Unknown"),
                    "flag": "🌐"
                }
            else:
                server_location = {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "flag": "🌐"}
        except:
            server_location = {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "flag": "🌐"}
        
        return org_location, server_location, is_org_location
    

    # =====================================
    # =====================================
    # def parse_nmap_output(self, line: str):
    #     line = line.strip()
    #     if not line:
    #         return
        
    #     host_match = re.search(r'Nmap scan report for (.+)', line)
    #     if host_match:
    #         host = host_match.group(1).strip()
    #         host = re.sub(r'\([^)]*\)', '', host).strip()
            
    #         if host not in self.network_nodes:
    #             resolved_ip = resolve_domain_to_ip(host)
    #             org_location, server_location, is_org_location = self.enhanced_geoip_lookup(host, resolved_ip)
                
    #             # Use organization location if available, otherwise use server location
    #             if is_org_location and org_location.get("lat", 0) != 0:
    #                 lat = org_location.get("lat", 0)
    #                 lon = org_location.get("lon", 0)
    #                 country = org_location.get("country", "Unknown")
    #                 city = org_location.get("city", "Unknown")
    #             else:
    #                 lat = server_location.get("lat", 0)
    #                 lon = server_location.get("lon", 0)
    #                 country = server_location.get("country", "Unknown")
    #                 city = server_location.get("city", "Unknown")
                
    #             node = NetworkNode(
    #                 ip=host,
    #                 country=country,
    #                 city=city,
    #                 lat=lat,
    #                 lon=lon,
    #                 is_organization_location=is_org_location,
    #                 server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
    #                 server_country=server_location.get("country", "Unknown"),
    #                 server_city=server_location.get("city", "Unknown"),
    #                 server_lat=server_location.get("lat", 0),
    #                 server_lon=server_location.get("lon", 0),
    #                 server_isp=server_location.get("isp", "Unknown"),
    #                 org_country=org_location.get("country", "Unknown"),
    #                 org_city=org_location.get("city", "Unknown")
    #             )
    #             self.network_nodes[host] = node
                
    #             # Add location to map with dual location data
    #             self.geo_map.add_location(
    #                 lat, lon, host, 0, [],
    #                 country,
    #                 is_org_location,
    #                 server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
    #                 server_country=server_location.get("country", "Unknown"),
    #                 server_city=server_location.get("city", "Unknown"),
    #                 server_lat=server_location.get("lat", 0),
    #                 server_lon=server_location.get("lon", 0),
    #                 server_isp=server_location.get("isp", "Unknown"),
    #                 org_country=org_location.get("country", "Unknown"),
    #                 org_city=org_location.get("city", "Unknown"),
    #                 domain=host
    #             )
                
    #             # Also add server location as a separate marker if different from HQ
    #             if is_org_location and org_location.get("lat", 0) != 0:
    #                 server_lat = server_location.get("lat", 0)
    #                 server_lon = server_location.get("lon", 0)
    #                 if server_lat != 0 and server_lon != 0:
    #                     self.geo_map.add_location(
    #                         server_lat, server_lon, f"{host}-server", 0, [],
    #                         server_location.get("country", "Unknown"),
    #                         False,
    #                         server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
    #                         server_country=server_location.get("country", "Unknown"),
    #                         server_city=server_location.get("city", "Unknown"),
    #                         server_lat=server_lat,
    #                         server_lon=server_lon,
    #                         server_isp=server_location.get("isp", "Unknown"),
    #                         org_country=org_location.get("country", "Unknown"),
    #                         org_city=org_location.get("city", "Unknown"),
    #                         domain=f"{host} (Server)"
    #                     )
    #         return
        
    #     port_match = re.search(r'(\d+)/(tcp|udp)\s+open\s+(\S+)', line)
    #     if port_match:
    #         port = port_match.group(1)
    #         proto = port_match.group(2)
    #         service = port_match.group(3).replace('?', '').strip()
            
    #         version = ""
    #         rest = line[port_match.end():].strip()
    #         if rest and not rest.startswith('syn-'):
    #             version = rest[:30]
            
    #         vuln = self.ai_scorer.analyze_service(service, port, version)
    #         risk_score = vuln["cvss_score"]
            
    #         self.discovered_ports.append({"port": port, "protocol": proto, "service": service, "version": version, "risk_score": risk_score})
    #         self.services_found.append({
    #             "port": port, "protocol": proto, "service": service, "version": version,
    #             "risk_score": risk_score, "exploit": vuln.get("exploit", "N/A"),
    #             "cvss_id": vuln.get("cvss_id", "N/A")
    #         })
            
    #         for node in self.network_nodes.values():
    #             if node.lat != 0:
    #                 node.ports.append({"port": port, "service": service, "risk_score": risk_score})
    #                 node.risk_score = max(node.risk_score, risk_score)
            
    #         color = Colors.RED if risk_score >= 7 else Colors.YELLOW if risk_score >= 4 else Colors.GREEN
    #         spinner = random.choice(self.spinner_frames)
    #         print(f"\r{self.center(f'{Colors.CYAN}[{spinner}]{Colors.RESET} {color}[!] NEW: {port} - {service} (Risk: {risk_score}){Colors.RESET}')}")
    #         time.sleep(0.05)
    #         return
        
    #     if "Nmap done" in line:
    #         self.scan_active = False

    # def parse_nmap_output(self, line: str):
    #     line = line.strip()
    #     if not line:
    #         return
        
    #     host_match = re.search(r'Nmap scan report for (.+)', line)
    #     if host_match:
    #         host = host_match.group(1).strip()
    #         host = re.sub(r'\([^)]*\)', '', host).strip()
            
    #         if host not in self.network_nodes:
    #             resolved_ip = resolve_domain_to_ip(host)
    #             org_location, server_location, is_org_location = self.enhanced_geoip_lookup(host, resolved_ip)
                
    #             # DEBUG: Print locations for verification
    #             print(f"\n{Colors.CYAN}[DEBUG] Host: {host}{Colors.RESET}")
    #             print(f"{Colors.YELLOW}[DEBUG] Org Location: {org_location}{Colors.RESET}")
    #             print(f"{Colors.GREEN}[DEBUG] Server Location: {server_location}{Colors.RESET}")
                
    #             # Use organization location if available, otherwise use server location
    #             if is_org_location and org_location.get("lat", 0) != 0:
    #                 lat = org_location.get("lat", 0)
    #                 lon = org_location.get("lon", 0)
    #                 country = org_location.get("country", "Unknown")
    #                 city = org_location.get("city", "Unknown")
    #                 print(f"{Colors.CYAN}[DEBUG] Using HQ Location: {lat}, {lon} - {country}{Colors.RESET}")
    #             else:
    #                 lat = server_location.get("lat", 0)
    #                 lon = server_location.get("lon", 0)
    #                 country = server_location.get("country", "Unknown")
    #                 city = server_location.get("city", "Unknown")
    #                 print(f"{Colors.CYAN}[DEBUG] Using Server Location: {lat}, {lon} - {country}{Colors.RESET}")
                
    #             node = NetworkNode(
    #                 ip=host,
    #                 country=country,
    #                 city=city,
    #                 lat=lat,
    #                 lon=lon,
    #                 is_organization_location=is_org_location,
    #                 server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
    #                 server_country=server_location.get("country", "Unknown"),
    #                 server_city=server_location.get("city", "Unknown"),
    #                 server_lat=server_location.get("lat", 0),
    #                 server_lon=server_location.get("lon", 0),
    #                 server_isp=server_location.get("isp", "Unknown"),
    #                 org_country=org_location.get("country", "Unknown"),
    #                 org_city=org_location.get("city", "Unknown")
    #             )
    #             self.network_nodes[host] = node
                
    #             # Always add the primary location (HQ or Server)
    #             self.geo_map.add_location(
    #                 lat, lon, host, 0, [],
    #                 country,
    #                 is_org_location,
    #                 server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
    #                 server_country=server_location.get("country", "Unknown"),
    #                 server_city=server_location.get("city", "Unknown"),
    #                 server_lat=server_location.get("lat", 0),
    #                 server_lon=server_location.get("lon", 0),
    #                 server_isp=server_location.get("isp", "Unknown"),
    #                 org_country=org_location.get("country", "Unknown"),
    #                 org_city=org_location.get("city", "Unknown"),
    #                 domain=host
    #             )
                
    #             # ALSO add server location as a SEPARATE marker if it's different from HQ
    #             # AND if it has valid coordinates
    #             if is_org_location and org_location.get("lat", 0) != 0:
    #                 server_lat = server_location.get("lat", 0)
    #                 server_lon = server_location.get("lon", 0)
    #                 server_country = server_location.get("country", "Unknown")
    #                 server_city = server_location.get("city", "Unknown")
                    
    #                 # Check if server location is different from HQ (not same coordinates)
    #                 if server_lat != 0 and server_lon != 0:
    #                     # Check if server is in a different country or at least 100km away
    #                     import math
    #                     # Rough distance calculation (simplified)
    #                     lat_diff = abs(server_lat - org_location.get("lat", 0))
    #                     lon_diff = abs(server_lon - org_location.get("lon", 0))
    #                     distance_km = math.sqrt((lat_diff * 111)**2 + (lon_diff * 111 * math.cos(org_location.get("lat", 0) * 3.14159/180))**2)
                        
    #                     if distance_km > 50 or server_country != org_location.get("country", ""):
    #                         print(f"{Colors.GREEN}[DEBUG] Adding Server Location: {server_lat}, {server_lon} - {server_country} (Distance: {distance_km:.0f}km){Colors.RESET}")
    #                         self.geo_map.add_location(
    #                             server_lat, server_lon, f"{host}-server", 0, [],
    #                             server_country,
    #                             False,  # Not organization location
    #                             server_location=f"{server_city}, {server_country}",
    #                             server_country=server_country,
    #                             server_city=server_city,
    #                             server_lat=server_lat,
    #                             server_lon=server_lon,
    #                             server_isp=server_location.get("isp", "Unknown"),
    #                             org_country=org_location.get("country", "Unknown"),
    #                             org_city=org_location.get("city", "Unknown"),
    #                             domain=f"{host} 🌐 Server"
    #                         )
    #                     else:
    #                         print(f"{Colors.YELLOW}[DEBUG] Server location is same as HQ, not adding separate marker{Colors.RESET}")
    #         return
    # def parse_nmap_output(self, line: str):
    #     line = line.strip()
    #     if not line:
    #         return
        
    #     host_match = re.search(r'Nmap scan report for (.+)', line)
    #     if host_match:
    #         host = host_match.group(1).strip()
    #         host = re.sub(r'\([^)]*\)', '', host).strip()
            
    #         if host not in self.network_nodes:
    #             resolved_ip = resolve_domain_to_ip(host)
    #             org_location, server_location, is_org_location = self.enhanced_geoip_lookup(host, resolved_ip)
                
    #             # Display host discovery persistently
    #             print(f"\n{Colors.CYAN}┌─[HOST DISCOVERED]──────────────────────────────────────────┐{Colors.RESET}")
    #             print(f"{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}Target:{Colors.RESET} {host}")
    #             if is_org_location and org_location.get("lat", 0) != 0:
    #                 print(f"{Colors.CYAN}│{Colors.RESET} {Colors.YELLOW}🏢 HQ:{Colors.RESET} {org_location.get('country', 'Unknown')} - {org_location.get('city', 'Unknown')}")
    #             print(f"{Colors.CYAN}│{Colors.RESET} {Colors.BLUE}🖥️ Server:{Colors.RESET} {server_location.get('country', 'Unknown')} - {server_location.get('city', 'Unknown')}")
    #             print(f"{Colors.CYAN}└────────────────────────────────────────────────────────────────┘{Colors.RESET}\n")
                
    #             # Use organization location if available
    #             if is_org_location and org_location.get("lat", 0) != 0:
    #                 lat = org_location.get("lat", 0)
    #                 lon = org_location.get("lon", 0)
    #                 country = org_location.get("country", "Unknown")
    #                 city = org_location.get("city", "Unknown")
    #             else:
    #                 lat = server_location.get("lat", 0)
    #                 lon = server_location.get("lon", 0)
    #                 country = server_location.get("country", "Unknown")
    #                 city = server_location.get("city", "Unknown")
                
    #             node = NetworkNode(
    #                 ip=host,
    #                 country=country,
    #                 city=city,
    #                 lat=lat,
    #                 lon=lon,
    #                 is_organization_location=is_org_location,
    #                 server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
    #                 server_country=server_location.get("country", "Unknown"),
    #                 server_city=server_location.get("city", "Unknown"),
    #                 server_lat=server_location.get("lat", 0),
    #                 server_lon=server_location.get("lon", 0),
    #                 server_isp=server_location.get("isp", "Unknown"),
    #                 org_country=org_location.get("country", "Unknown"),
    #                 org_city=org_location.get("city", "Unknown")
    #             )
    #             self.network_nodes[host] = node
                
    #             # Add location to map
    #             self.geo_map.add_location(
    #                 lat, lon, host, 0, [],
    #                 country,
    #                 is_org_location,
    #                 server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
    #                 server_country=server_location.get("country", "Unknown"),
    #                 server_city=server_location.get("city", "Unknown"),
    #                 server_lat=server_location.get("lat", 0),
    #                 server_lon=server_location.get("lon", 0),
    #                 server_isp=server_location.get("isp", "Unknown"),
    #                 org_country=org_location.get("country", "Unknown"),
    #                 org_city=org_location.get("city", "Unknown"),
    #                 domain=host
    #             )
                
    #             # Add server location as separate marker if different
    #             if is_org_location and org_location.get("lat", 0) != 0:
    #                 server_lat = server_location.get("lat", 0)
    #                 server_lon = server_location.get("lon", 0)
    #                 if server_lat != 0 and server_lon != 0:
    #                     import math
    #                     lat_diff = abs(server_lat - org_location.get("lat", 0))
    #                     lon_diff = abs(server_lon - org_location.get("lon", 0))
    #                     distance_km = math.sqrt((lat_diff * 111)**2 + (lon_diff * 111 * math.cos(org_location.get("lat", 0) * 3.14159/180))**2)
                        
    #                     if distance_km > 50 or server_location.get("country", "") != org_location.get("country", ""):
    #                         print(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}📡 Server distance:{Colors.RESET} {distance_km:.0f} km from HQ")
    #                         self.geo_map.add_location(
    #                             server_lat, server_lon, f"{host}-server", 0, [],
    #                             server_location.get("country", "Unknown"),
    #                             False,
    #                             server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
    #                             server_country=server_location.get("country", "Unknown"),
    #                             server_city=server_location.get("city", "Unknown"),
    #                             server_lat=server_lat,
    #                             server_lon=server_lon,
    #                             server_isp=server_location.get("isp", "Unknown"),
    #                             org_country=org_location.get("country", "Unknown"),
    #                             org_city=org_location.get("city", "Unknown"),
    #                             domain=f"{host} 🌐 Server"
    #                         )
    #             print()  # Blank line after host discovery
    #         return
        
    #     port_match = re.search(r'(\d+)/(tcp|udp)\s+open\s+(\S+)', line)
    #     if port_match:
    #         port = port_match.group(1)
    #         proto = port_match.group(2)
    #         service = port_match.group(3).replace('?', '').strip()
            
    #         version = ""
    #         rest = line[port_match.end():].strip()
    #         if rest and not rest.startswith('syn-'):
    #             version = rest[:30]
            
    #         vuln = self.ai_scorer.analyze_service(service, port, version)
    #         risk_score = vuln["cvss_score"]
            
    #         self.discovered_ports.append({"port": port, "protocol": proto, "service": service, "version": version, "risk_score": risk_score})
    #         self.services_found.append({
    #             "port": port, "protocol": proto, "service": service, "version": version,
    #             "risk_score": risk_score, "exploit": vuln.get("exploit", "N/A"),
    #             "cvss_id": vuln.get("cvss_id", "N/A")
    #         })
            
    #         # Display port discovery persistently
    #         risk_icon = "🔴" if risk_score >= 7 else "🟡" if risk_score >= 4 else "🟢"
    #         risk_text = "CRITICAL" if risk_score >= 7 else "HIGH" if risk_score >= 5 else "MEDIUM" if risk_score >= 3 else "LOW"
    #         color = Colors.RED if risk_score >= 7 else Colors.YELLOW if risk_score >= 4 else Colors.GREEN
            
    #         print(f"{color}  ├─ {risk_icon} PORT {port}/{proto} → {service}{Colors.RESET}")
    #         if version:
    #             print(f"{color}  │  └─ Version: {version}{Colors.RESET}")
    #         print(f"{color}  │     Risk: {risk_score:.1f}/10 [{risk_text}]{Colors.RESET}")
    #         if vuln.get("exploit"):
    #             print(f"{color}  │     Exploit: {vuln.get('exploit')}{Colors.RESET}")
    #         print(f"{color}  │     CVE: {vuln.get('cvss_id', 'N/A')}{Colors.RESET}")
    #         print()
            
    #         for node in self.network_nodes.values():
    #             if node.lat != 0:
    #                 node.ports.append({"port": port, "service": service, "risk_score": risk_score})
    #                 node.risk_score = max(node.risk_score, risk_score)
    #         return
        
    #     if "Nmap done" in line:
    #         self.scan_active = False
    #         # Display summary of findings
    #         self._display_scan_summary()
=======
    def enhanced_geoip_lookup(self, hostname: str, ip: str) -> Tuple[Dict, bool]:
        """Enhanced GeoIP lookup with organization location override"""
        # First, check if we have the organization's headquarters location
        org_location = OrganizationLocationDB.get_organization_location(hostname, ip)
        
        if org_location and org_location.get("lat", 0) != 0:
            # Get server location for comparison
            try:
                response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
                server_data = response.json()
                server_location = f"{server_data.get('city', 'Unknown')}, {server_data.get('country', 'Unknown')}"
            except:
                server_location = "Unknown"
            
            return {
                "country": org_location["country"],
                "city": org_location["city"],
                "lat": org_location["lat"],
                "lon": org_location["lon"],
                "flag": org_location.get("flag", "🌐"),
                "is_organization_location": True,
                "server_location": server_location,
                "note": f"Showing organization headquarters in {org_location['country']}"
            }, True
        
        # Fallback to server location
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
            data = response.json()
            return {
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
                "lat": data.get("lat", 0),
                "lon": data.get("lon", 0),
                "flag": "🌐",
                "is_organization_location": False
            }, False
        except:
            return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "flag": "🌐", "is_organization_location": False}, False
    
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    def parse_nmap_output(self, line: str):
        line = line.strip()
        if not line:
            return
        
        host_match = re.search(r'Nmap scan report for (.+)', line)
        if host_match:
            host = host_match.group(1).strip()
            host = re.sub(r'\([^)]*\)', '', host).strip()
<<<<<<< HEAD
            
            if host not in self.network_nodes:
                resolved_ip = resolve_domain_to_ip(host)
                org_location, server_location, is_org_location = self.enhanced_geoip_lookup(host, resolved_ip)
                
                # Build host details output
                host_output = []
                host_output.append(f"\n{Colors.CYAN}┌─[HOST DISCOVERED]──────────────────────────────────────────┐{Colors.RESET}")
                host_output.append(f"{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}Target:{Colors.RESET} {host}")
                
                if is_org_location and org_location.get("lat", 0) != 0:
                    host_output.append(f"{Colors.CYAN}│{Colors.RESET} {Colors.YELLOW}🏢 HQ:{Colors.RESET} {org_location.get('country', 'Unknown')} - {org_location.get('city', 'Unknown')}")
                host_output.append(f"{Colors.CYAN}│{Colors.RESET} {Colors.BLUE}🖥️ Server:{Colors.RESET} {server_location.get('country', 'Unknown')} - {server_location.get('city', 'Unknown')}")
                
                # Store host details for persistence
                self.host_details[host] = {
                    "host": host,
                    "org_country": org_location.get('country', 'Unknown'),
                    "org_city": org_location.get('city', 'Unknown'),
                    "server_country": server_location.get('country', 'Unknown'),
                    "server_city": server_location.get('city', 'Unknown'),
                    "is_org": is_org_location
                }
                
                # Add server distance if available
                if is_org_location and org_location.get("lat", 0) != 0:
                    server_lat = server_location.get("lat", 0)
                    server_lon = server_location.get("lon", 0)
                    if server_lat != 0 and server_lon != 0:
                        import math
                        lat_diff = abs(server_lat - org_location.get("lat", 0))
                        lon_diff = abs(server_lon - org_location.get("lon", 0))
                        distance_km = math.sqrt((lat_diff * 111)**2 + (lon_diff * 111 * math.cos(org_location.get("lat", 0) * 3.14159/180))**2)
                        if distance_km > 50:
                            host_output.append(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}📡 Distance:{Colors.RESET} {distance_km:.0f} km from HQ")
                
                host_output.append(f"{Colors.CYAN}└────────────────────────────────────────────────────────────────┘{Colors.RESET}")
                
                # Store in scan output buffer
                for line in host_output:
                    self.scan_output.append(line)
                    print(line)
                print()  # Blank line after host discovery
                
                # Use organization location if available
                if is_org_location and org_location.get("lat", 0) != 0:
                    lat = org_location.get("lat", 0)
                    lon = org_location.get("lon", 0)
                    country = org_location.get("country", "Unknown")
                    city = org_location.get("city", "Unknown")
                else:
                    lat = server_location.get("lat", 0)
                    lon = server_location.get("lon", 0)
                    country = server_location.get("country", "Unknown")
                    city = server_location.get("city", "Unknown")
                
                node = NetworkNode(
                    ip=host,
                    country=country,
                    city=city,
                    lat=lat,
                    lon=lon,
                    is_organization_location=is_org_location,
                    server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
                    server_country=server_location.get("country", "Unknown"),
                    server_city=server_location.get("city", "Unknown"),
                    server_lat=server_location.get("lat", 0),
                    server_lon=server_location.get("lon", 0),
                    server_isp=server_location.get("isp", "Unknown"),
                    org_country=org_location.get("country", "Unknown"),
                    org_city=org_location.get("city", "Unknown")
                )
                self.network_nodes[host] = node
                
                # Add location to map
                self.geo_map.add_location(
                    lat, lon, host, 0, [],
                    country,
                    is_org_location,
                    server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
                    server_country=server_location.get("country", "Unknown"),
                    server_city=server_location.get("city", "Unknown"),
                    server_lat=server_location.get("lat", 0),
                    server_lon=server_location.get("lon", 0),
                    server_isp=server_location.get("isp", "Unknown"),
                    org_country=org_location.get("country", "Unknown"),
                    org_city=org_location.get("city", "Unknown"),
                    domain=host
                )
                
                # Add server location as separate marker if different
                if is_org_location and org_location.get("lat", 0) != 0:
                    server_lat = server_location.get("lat", 0)
                    server_lon = server_location.get("lon", 0)
                    if server_lat != 0 and server_lon != 0:
                        import math
                        lat_diff = abs(server_lat - org_location.get("lat", 0))
                        lon_diff = abs(server_lon - org_location.get("lon", 0))
                        distance_km = math.sqrt((lat_diff * 111)**2 + (lon_diff * 111 * math.cos(org_location.get("lat", 0) * 3.14159/180))**2)
                        
                        if distance_km > 50 or server_location.get("country", "") != org_location.get("country", ""):
                            self.geo_map.add_location(
                                server_lat, server_lon, f"{host}-server", 0, [],
                                server_location.get("country", "Unknown"),
                                False,
                                server_location=f"{server_location.get('city', 'Unknown')}, {server_location.get('country', 'Unknown')}",
                                server_country=server_location.get("country", "Unknown"),
                                server_city=server_location.get("city", "Unknown"),
                                server_lat=server_lat,
                                server_lon=server_lon,
                                server_isp=server_location.get("isp", "Unknown"),
                                org_country=org_location.get("country", "Unknown"),
                                org_city=org_location.get("city", "Unknown"),
                                domain=f"{host} 🌐 Server"
                            )
=======
            if host not in self.network_nodes:
                # Use enhanced GeoIP lookup
                geo, is_org_location = self.enhanced_geoip_lookup(host, host)
                node = NetworkNode(
                    ip=host, 
                    country=geo.get("country", "Unknown"), 
                    lat=geo.get("lat", 0), 
                    lon=geo.get("lon", 0),
                    is_organization_location=is_org_location,
                    server_location=geo.get("server_location", "")
                )
                self.network_nodes[host] = node
                if geo.get("lat", 0) != 0:
                    self.geo_map.add_location(
                        geo["lat"], geo["lon"], host, 0, [], 
                        geo.get("country", "Unknown"),
                        is_org_location,
                        geo.get("server_location", ""),
                        host
                    )
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            return
        
        port_match = re.search(r'(\d+)/(tcp|udp)\s+open\s+(\S+)', line)
        if port_match:
            port = port_match.group(1)
            proto = port_match.group(2)
            service = port_match.group(3).replace('?', '').strip()
            
            version = ""
            rest = line[port_match.end():].strip()
            if rest and not rest.startswith('syn-'):
                version = rest[:30]
            
            vuln = self.ai_scorer.analyze_service(service, port, version)
            risk_score = vuln["cvss_score"]
            
            self.discovered_ports.append({"port": port, "protocol": proto, "service": service, "version": version, "risk_score": risk_score})
            self.services_found.append({
                "port": port, "protocol": proto, "service": service, "version": version,
                "risk_score": risk_score, "exploit": vuln.get("exploit", "N/A"),
                "cvss_id": vuln.get("cvss_id", "N/A")
            })
            
<<<<<<< HEAD
            # Build port output
            risk_icon = "🔴" if risk_score >= 7 else "🟡" if risk_score >= 4 else "🟢"
            risk_text = "CRITICAL" if risk_score >= 7 else "HIGH" if risk_score >= 5 else "MEDIUM" if risk_score >= 3 else "LOW"
            color = Colors.RED if risk_score >= 7 else Colors.YELLOW if risk_score >= 4 else Colors.GREEN
            
            port_output = []
            port_output.append(f"{color}  ├─ {risk_icon} PORT {port}/{proto} → {service}{Colors.RESET}")
            if version:
                port_output.append(f"{color}  │  └─ Version: {version}{Colors.RESET}")
            port_output.append(f"{color}  │     Risk: {risk_score:.1f}/10 [{risk_text}]{Colors.RESET}")
            if vuln.get("exploit"):
                port_output.append(f"{color}  │     Exploit: {vuln.get('exploit')}{Colors.RESET}")
            port_output.append(f"{color}  │     CVE: {vuln.get('cvss_id', 'N/A')}{Colors.RESET}")
            port_output.append("")
            
            # Store in scan output buffer and print
            for line in port_output:
                self.scan_output.append(line)
                print(line)
            
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            for node in self.network_nodes.values():
                if node.lat != 0:
                    node.ports.append({"port": port, "service": service, "risk_score": risk_score})
                    node.risk_score = max(node.risk_score, risk_score)
<<<<<<< HEAD
=======
                    self.geo_map.add_location(
                        node.lat, node.lon, node.ip, node.risk_score, node.ports, 
                        node.country, node.is_organization_location, node.server_location, node.ip
                    )
            
            color = Colors.RED if risk_score >= 7 else Colors.YELLOW if risk_score >= 4 else Colors.GREEN
            spinner = random.choice(self.spinner_frames)
            print(f"\r{self.center(f'{Colors.CYAN}[{spinner}]{Colors.RESET} {color}[!] NEW: {port} - {service} (Risk: {risk_score}){Colors.RESET}')}")
            time.sleep(0.05)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            return
        
        if "Nmap done" in line:
            self.scan_active = False
<<<<<<< HEAD
            # Display summary (but keep all previous output)
            self._display_scan_summary()
        # ========================================
        # ========================================
    
    
    def _display_scan_summary(self):
        """Display persistent scan summary"""
        # Get the actual target name
        target = self.current_target if self.current_target else "Unknown"
        
        summary_lines = []
        summary_lines.append(f"\n{Colors.CYAN}{'═' * 70}{Colors.RESET}")
        summary_lines.append(f"{Colors.GREEN}✅ SCAN COMPLETED - {target}{Colors.RESET}")
        summary_lines.append(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}")
        
        # Show host details first
        summary_lines.append(f"\n{Colors.YELLOW}🖥️ HOST DETAILS:{Colors.RESET}")
        for host, details in self.host_details.items():
            summary_lines.append(f"  {Colors.GREEN}→{Colors.RESET} {host}")
            if details.get("is_org", False):
                summary_lines.append(f"    🏢 HQ: {details.get('org_country', 'Unknown')} - {details.get('org_city', 'Unknown')}")
            summary_lines.append(f"    🖥️ Server: {details.get('server_country', 'Unknown')} - {details.get('server_city', 'Unknown')}")
        
        # Show summary stats
        summary_lines.append(f"\n{Colors.YELLOW}📊 SUMMARY STATS:{Colors.RESET}")
        summary_lines.append(f"  • Hosts Found: {len(self.network_nodes)}")
        summary_lines.append(f"  • Open Ports: {len(self.discovered_ports)}")
        summary_lines.append(f"  • Services: {len(self.services_found)}")
        summary_lines.append(f"  • Duration: {self.scan_duration}s")
        
        if self.discovered_ports:
            high_risk = [p for p in self.discovered_ports if p.get("risk_score", 0) >= 7]
            med_risk = [p for p in self.discovered_ports if 4 <= p.get("risk_score", 0) < 7]
            low_risk = [p for p in self.discovered_ports if p.get("risk_score", 0) < 4]
            
            summary_lines.append(f"\n{Colors.YELLOW}⚠️ RISK BREAKDOWN:{Colors.RESET}")
            if high_risk:
                summary_lines.append(f"  {Colors.RED}🔴 CRITICAL: {len(high_risk)}{Colors.RESET}")
            if med_risk:
                summary_lines.append(f"  {Colors.YELLOW}🟡 MEDIUM: {len(med_risk)}{Colors.RESET}")
            if low_risk:
                summary_lines.append(f"  {Colors.GREEN}🟢 LOW: {len(low_risk)}{Colors.RESET}")
        
        # Show top services
        if self.services_found:
            summary_lines.append(f"\n{Colors.YELLOW}🔧 TOP SERVICES:{Colors.RESET}")
            for i, s in enumerate(self.services_found[:5], 1):
                risk_score = s.get("risk_score", 0)
                color = Colors.RED if risk_score >= 7 else Colors.YELLOW if risk_score >= 4 else Colors.GREEN
                summary_lines.append(f"  {i}. {s['port']}/{s['protocol']} → {s['service']} {color}({risk_score:.1f}){Colors.RESET}")
        
        summary_lines.append(f"\n{Colors.CYAN}{'═' * 70}{Colors.RESET}")
        summary_lines.append(f"{Colors.GREEN}📄 Reports generated:{Colors.RESET}")
        summary_lines.append(f"  • HTML Dashboard: soc_full_dashboard_*.html")
        summary_lines.append(f"  • PDF Report: soc_report_*.pdf")
        summary_lines.append(f"  • Location: ~/dsterminal_workspace/scans/")
        summary_lines.append(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}\n")
        
        # Store and print summary
        for line in summary_lines:
            self.scan_output.append(line)
            print(line)

#    ======================================
#    ======================================
    # def run_nmap_scan(self, target: str, flags: List[str]):
    #     if not shutil.which("nmap"):
    #         print(self.center(f"{Colors.RED}[!] Nmap not installed{Colors.RESET}"))
    #         return
        
    #     # Clear previous scan output but keep the buffer
    #     self.scan_output = []
    #     self.host_details = {}
    #     self.current_target = target
    #     self.scan_active = True
    #     self.discovered_ports = []
    #     self.services_found = []
    #     self.network_nodes = {}
    #     self.geo_map = EnhancedGeoMapVisualizer()
        
    #     start_time = datetime.now()
    #     cmd = ["nmap"] + flags + [target]
        
    #     # Clear screen and show header
    #     self.clear_screen()
    #     self.draw_header()
        
    #     # Show scan starting banner
    #     print(f"\n{self.center(Colors.GREEN + '[+] Running: ' + ' '.join(cmd) + Colors.RESET)}\n")
    #     print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}")
    #     print(f"{Colors.YELLOW}⏳ SCANNING... (Results will appear below){Colors.RESET}")
    #     print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}\n")
        
    #     # Store start line
    #     self.scan_output.append(f"\n{Colors.CYAN}─" * 70 + f"{Colors.RESET}")
    #     self.scan_output.append(f"{Colors.YELLOW}⏳ SCAN STARTED: {target}{Colors.RESET}")
    #     self.scan_output.append(f"{Colors.CYAN}─" * 70 + f"{Colors.RESET}\n")
        
    #     try:
    #         process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    #         for line in process.stdout:
    #             self.parse_nmap_output(line)
    #         process.wait()
    #         self.scan_duration = (datetime.now() - start_time).seconds
    #         self.scan_active = False
            
    #         # Save to history
    #         services_list = [s['service'] for s in self.services_found]
    #         history = ScanHistory(
    #             timestamp=datetime.now(),
    #             target=target,
    #             duration=self.scan_duration,
    #             open_ports=len(self.discovered_ports),
    #             risk_score=sum(p.get('risk_score', 0) for p in self.discovered_ports) / max(1, len(self.discovered_ports)),
    #             services=services_list[:5]
    #         )
    #         self.scan_history.append(history)
    #         self._save_history()
    #         if len(self.scan_history) > 10:
    #             self.scan_history.pop(0)
            
    #         # Open dashboard (this happens after the summary is already displayed)
    #         print(f"\n{Colors.YELLOW}[+] Opening GeoMap dashboard...{Colors.RESET}")
    #         self.generate_full_dashboard()

    #         print(f"{Colors.CYAN}[+] Generating PDF report...{Colors.RESET}")
    #         pdf_path = self.generate_pdf_report(target)
    #         if pdf_path:
    #             print(f"{Colors.GREEN}[+] PDF saved: {pdf_path}{Colors.RESET}")
                
    #     except Exception as e:
    #         error_msg = f"{Colors.RED}[!] Scan failed: {e}{Colors.RESET}"
    #         self.scan_output.append(error_msg)
    #         print(error_msg)
    #         self.scan_active = False

    def run_nmap_scan(self, target: str, flags: List[str], auto_open: bool = False):
=======
    
    def run_nmap_scan(self, target: str, flags: List[str]):
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if not shutil.which("nmap"):
            print(self.center(f"{Colors.RED}[!] Nmap not installed{Colors.RESET}"))
            return
        
        self.current_target = target
        self.scan_active = True
        self.discovered_ports = []
        self.services_found = []
        self.network_nodes = {}
        self.geo_map = EnhancedGeoMapVisualizer()
        
        start_time = datetime.now()
        cmd = ["nmap"] + flags + [target]
        
<<<<<<< HEAD
        self.clear_screen()
        self.draw_header()
        print(f"\n{self.center(Colors.GREEN + '[+] Running: ' + ' '.join(cmd) + Colors.RESET)}\n")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}")
        
        # ============================================================
        # COUNTDOWN TIMER - Display elapsed time during scan
        # ============================================================
        # print(f"{Colors.YELLOW}⏳ SCANNING... (Results will appear below){Colors.RESET}")
        
        # Create a thread for the timer
        import threading
        timer_running = True
        timer_lock = threading.Lock()
        
        def update_timer():
            """Update the timer in the terminal"""
            nonlocal timer_running
            while timer_running:
                elapsed = (datetime.now() - start_time).seconds
                minutes = elapsed // 60
                seconds = elapsed % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                # Move cursor up one line and update the timer
                sys.stdout.write(f"\033[1A\033[K")
                print(f"{Colors.YELLOW}⏳ SCANNING IN PROGRESS. PLEASE WAIT PATIENTLY...! (Elapsed: {Colors.GREEN}{time_str}{Colors.YELLOW}) (Results will appear below){Colors.RESET}")
                sys.stdout.flush()
                time.sleep(0.5)
        
        # Start the timer thread
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()
        
        print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}\n")
=======
        print(f"\n{self.center(Colors.GREEN + '[+] Running: ' + ' '.join(cmd) + Colors.RESET)}\n")
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in process.stdout:
                self.parse_nmap_output(line)
            process.wait()
<<<<<<< HEAD
            
            # Stop the timer
            timer_running = False
            timer_thread.join(timeout=0.5)
            
            # Clear the timer line and show completion
            sys.stdout.write(f"\033[1A\033[K")
            
            self.scan_duration = (datetime.now() - start_time).seconds
            self.scan_active = False
            
=======
            self.scan_duration = (datetime.now() - start_time).seconds
            self.scan_active = False
            
            # Save to history
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            services_list = [s['service'] for s in self.services_found]
            history = ScanHistory(
                timestamp=datetime.now(),
                target=target,
                duration=self.scan_duration,
                open_ports=len(self.discovered_ports),
                risk_score=sum(p.get('risk_score', 0) for p in self.discovered_ports) / max(1, len(self.discovered_ports)),
                services=services_list[:5]
            )
            self.scan_history.append(history)
<<<<<<< HEAD
            self._save_history()
            if len(self.scan_history) > 10:
                self.scan_history.pop(0)
            
            # Display completion message with duration
            minutes = self.scan_duration // 60
            seconds = self.scan_duration % 60
            duration_str = f"{minutes:02d}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
            
            print(f"{Colors.GREEN}✅ Scan completed in {duration_str}{Colors.RESET}")
            print(self.center(Colors.CYAN + '[+] Found ' + str(len(self.discovered_ports)) + ' open ports' + Colors.RESET))
            
            # Generate dashboard with user confirmation
            print(self.center(Colors.YELLOW + '[+] Generating dashboard...' + Colors.RESET))
            self.generate_full_dashboard(auto_open=auto_open)

=======
            self._save_history()  # Save to file
            if len(self.scan_history) > 10:
                self.scan_history.pop(0)
            
            print(f"\n{self.center(Colors.GREEN + '[+] Scan completed in ' + str(self.scan_duration) + 's' + Colors.RESET)}")
            print(self.center(Colors.CYAN + '[+] Found ' + str(len(self.discovered_ports)) + ' open ports' + Colors.RESET))
            
            print(self.center(Colors.YELLOW + '[+] Opening GeoMap dashboard with organization locations...' + Colors.RESET))
            self.generate_full_dashboard()

            # Generate PDF report as well
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            print(self.center(Colors.CYAN + '[+] Generating PDF report...' + Colors.RESET))
            pdf_path = self.generate_pdf_report(target)
            if pdf_path:
                print(self.center(Colors.GREEN + f'[+] PDF saved: {pdf_path}' + Colors.RESET))
<<<<<<< HEAD
                
        except Exception as e:
            # Stop the timer on error
            timer_running = False
            timer_thread.join(timeout=0.5)
            sys.stdout.write(f"\033[1A\033[K")
            print(self.center(f"{Colors.RED}[!] Scan failed: {e}{Colors.RESET}"))
            self.scan_active = False

# =================================================
    def cmd_soc_results(self):
        """Display previous scan results from buffer"""
        if not self.scan_output:
            print(f"{Colors.YELLOW}[!] No scan results available. Run a scan first.{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}{'═' * 70}{Colors.RESET}")
        print(f"{Colors.GREEN}📊 PREVIOUS SCAN RESULTS - {self.current_target}{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}\n")
        
        # Print stored scan output
        for line in self.scan_output:
            print(line)
        
        print(f"\n{Colors.CYAN}{'═' * 70}{Colors.RESET}")
        print(f"{Colors.GREEN}💡 Tip: Run a new scan to see updated results{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}")

    # ===================================================
    # ===================================================

    def generate_network_topology(self) -> str:
        if not PLOTLY_AVAILABLE or not self.network_nodes:
            return '<div style="padding:50px;text-align:center;color:#888;">No topology data available</div>'
=======
        except Exception as e:
            print(self.center(f"{Colors.RED}[!] Scan failed: {e}{Colors.RESET}"))
            self.scan_active = False
    
    def generate_network_topology(self) -> str:
        """Generate network topology visualization using Plotly"""
        if not PLOTLY_AVAILABLE or not self.network_nodes:
            return '<div style="padding:50px;text-align:center;">No topology data available</div>'
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        
        node_list = list(self.network_nodes.keys())
        num_nodes = len(node_list)
        
        node_x = []
        node_y = []
<<<<<<< HEAD
        node_colors = []
        node_sizes = []
        node_hover_texts = []
        node_labels = []
        
        # ============================================================
        # 9 RISK DESCRIPTIONS PER LEVEL - ALL TALKING ABOUT SAME RISK
        # ============================================================
        
        # HIGH RISK DESCRIPTIONS (Risk 7-10)
        high_risk_descriptions = [
            "CRITICAL: Multiple high-risk services exposed - attacker can gain system access",
            "IMMEDIATE ACTION: Active exploitation possible - patch within 24 hours",
            "SYSTEM COMPROMISED: Remote code execution vulnerabilities detected",
            "EMERGENCY: Critical security flaws found - system at immediate risk",
            "URGENT: Attacker can fully compromise this system through exposed ports",
            "HIGH PRIORITY: Multiple attack vectors identified - take action now",
            "CRITICAL VULNERABILITY: Exploit available for detected services",
            "TARGETED: High-value system with critical security gaps",
            "IMMINENT THREAT: System vulnerable to remote takeover"
        ]
        
        # MEDIUM RISK DESCRIPTIONS (Risk 4-6)
        medium_risk_descriptions = [
            "MEDIUM RISK: Security posture needs improvement - prioritize remediation",
            "ACTION REQUIRED: Configuration weaknesses detected - schedule patch",
            "REMEDIATE: Multiple vulnerabilities require attention within 7 days",
            "PRIORITIZE: Security gaps identified - update recommended",
            "INVESTIGATE: Service hardening recommended for exposed ports",
            "UPDATE REQUIRED: Outdated services with known vulnerabilities",
            "REVIEW: Further investigation recommended for detected issues",
            "COMPLIANCE: Security compliance gaps identified - address soon",
            "HARDEN: System configuration needs security hardening"
        ]
        
        # LOW RISK DESCRIPTIONS (Risk 0-3)
        low_risk_descriptions = [
            "LOW RISK: Good security posture - minimal risk to system",
            "SECURE: No critical vulnerabilities detected - maintain monitoring",
            "PROTECTED: System appears well-configured and secure",
            "ACCEPTABLE: Risk level within acceptable range - continue monitoring",
            "ADEQUATE: Security controls in place - no immediate action needed",
            "MINOR: Low-risk services exposed - low priority for remediation",
            "INFORMATIONAL: Minor issues found - address during next maintenance",
            "COMPLIANT: Follows security best practices - maintain current state",
            "STABLE: System security posture is satisfactory"
        ]
        
        # Store descriptions for each node
        self.node_descriptions = {}
=======
        node_text = []
        node_colors = []
        node_sizes = []
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        
        for i, ip in enumerate(node_list):
            angle = 2 * math.pi * i / max(1, num_nodes)
            radius = 4
            node_x.append(radius * math.cos(angle))
            node_y.append(radius * math.sin(angle))
            risk = self.network_nodes[ip].risk_score
            is_org = self.network_nodes[ip].is_organization_location
<<<<<<< HEAD
            location_note = "🏢 HQ+Server" if is_org else "🖥️ Server"
            
            # Select random description based on risk level
            import random
            if risk >= 7:
                desc = random.choice(high_risk_descriptions)
                risk_color = "#ff4444"
                risk_text = "CRITICAL"
                risk_icon = "🔴"
                node_color = "#ff0000"
                node_size = 25
            elif risk >= 4:
                desc = random.choice(medium_risk_descriptions)
                risk_color = "#ffcc00"
                risk_text = "MEDIUM"
                risk_icon = "🟡"
                node_color = "#ffcc00"
                node_size = 20
            else:
                desc = random.choice(low_risk_descriptions)
                risk_color = "#44ff44"
                risk_text = "LOW"
                risk_icon = "🟢"
                node_color = "#00ff00"
                node_size = 15
            
            # Store description for node
            self.node_descriptions[ip] = {
                "description": desc,
                "risk_color": risk_color,
                "risk_text": risk_text,
                "risk_icon": risk_icon,
                "risk_score": risk
            }
            
            # Build hover text with proper HTML formatting
            port_count = len(self.network_nodes[ip].ports)
            top_services = []
            for p in self.network_nodes[ip].ports[:3]:
                top_services.append(f"{p.get('service', 'unknown')}")
            
            # Get location info
            server_loc = ""
            if hasattr(self.network_nodes[ip], 'server_country') and self.network_nodes[ip].server_country:
                server_loc = f"🖥️ Server: {self.network_nodes[ip].server_country} - {self.network_nodes[ip].server_city}"
            
            org_loc = ""
            if is_org and hasattr(self.network_nodes[ip], 'org_country') and self.network_nodes[ip].org_country:
                org_loc = f"🏢 HQ: {self.network_nodes[ip].org_country} - {self.network_nodes[ip].org_city}"
            
            # Build clean hover text - keep it concise but complete
            hover_parts = [
                f"<b style='color:#00ffff;font-size:14px;'>{ip}</b>",
                f"{location_note}",
                "─────────────────",
            ]
            
            if org_loc:
                hover_parts.append(org_loc)
            if server_loc:
                hover_parts.append(server_loc)
            
            hover_parts.extend([
                f"<b>⚠️ Risk:</b> <span style='color:{risk_color};font-weight:bold;'>{risk:.1f}/10 [{risk_text}]</span>",
                f"<b>🔓 Ports:</b> {port_count}",
                f"<b>🔧 Services:</b> {', '.join(top_services) if top_services else 'None'}",
                "─────────────────",
                f"<span style='color:{risk_color};font-weight:bold;font-size:12px;'>{risk_icon} {desc}</span>"
            ])
            
            hover_text = "<br>".join(hover_parts)
            node_hover_texts.append(hover_text)
            node_labels.append(ip[:15])
            node_colors.append(node_color)
            node_sizes.append(node_size)
        
        # Create edges
=======
            location_note = "🏢 HQ" if is_org else "🖥️ Server"
            node_text.append(f"{ip}<br>{location_note}<br>Risk: {risk:.1f}<br>Ports: {len(self.network_nodes[ip].ports)}")
            
            if risk >= 7:
                node_colors.append("#ff0000")
                node_sizes.append(25)
            elif risk >= 4:
                node_colors.append("#ffcc00")
                node_sizes.append(20)
            else:
                node_colors.append("#00ff00")
                node_sizes.append(15)
        
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        edge_x = []
        edge_y = []
        for i in range(len(node_x) - 1):
            edge_x.extend([node_x[i], node_x[i+1], None])
            edge_y.extend([node_y[i], node_y[i+1], None])
        
        fig = go.Figure()
        
<<<<<<< HEAD
        # Add edges
=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if edge_x:
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(width=2, color='#00ffff', dash='dash'),
                hoverinfo='none',
                showlegend=False
            ))
        
<<<<<<< HEAD
        # Add nodes with proper hover template - INCREASE hover label length
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_sizes, 
                color=node_colors, 
                line=dict(width=2, color='white'),
                symbol='circle'
            ),
            text=node_labels,
            textposition="top center",
            textfont=dict(size=10, color='white'),
            hovertext=node_hover_texts,
            hoverinfo='text',
            showlegend=False,
            hovertemplate='%{hovertext}<extra></extra>',
            hoverlabel=dict(
                bgcolor='rgba(10,15,30,0.95)',
                font=dict(size=12, color='white', family='monospace'),
                bordercolor='#00ffff',
                namelength=-1  # <-- CRITICAL: This allows full text display
            )
        ))
        
        # Add risk summary annotations
        high_risk_nodes = [n for n in self.network_nodes.values() if n.risk_score >= 7]
        medium_risk_nodes = [n for n in self.network_nodes.values() if 4 <= n.risk_score < 7]
        low_risk_nodes = [n for n in self.network_nodes.values() if n.risk_score < 4]
        
        summary_parts = []
        if high_risk_nodes:
            summary_parts.append(f"🔴 {len(high_risk_nodes)} Critical")
        if medium_risk_nodes:
            summary_parts.append(f"🟡 {len(medium_risk_nodes)} Medium")
        if low_risk_nodes:
            summary_parts.append(f"🟢 {len(low_risk_nodes)} Low")
        risk_summary = " | ".join(summary_parts) if summary_parts else "No risk data"
        
        if high_risk_nodes:
            risk_footer = "⚠️ CRITICAL NODES DETECTED - Immediate action required!"
            footer_color = "#ff4444"
        elif medium_risk_nodes:
            risk_footer = "📊 Medium risk nodes found - Schedule remediation"
            footer_color = "#ffcc00"
        else:
            risk_footer = "✅ All nodes have LOW risk - Continue monitoring"
            footer_color = "#44ff44"
        
        fig.update_layout(
            title=dict(
                text=f"🌐 NETWORK TOPOLOGY<br><span style='font-size:11px;color:#888;'>Risk Summary: {risk_summary}</span>",
                font=dict(color='#00ffff', size=14),
                x=0.5
            ),
=======
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(size=node_sizes, color=node_colors, line=dict(width=2, color='white')),
            text=[ip[:15] for ip in node_list],
            textposition="top center",
            textfont=dict(size=10, color='white'),
            hovertext=node_text,
            hoverinfo='text',
            showlegend=False
        ))
        
        fig.update_layout(
            title=dict(text="🌐 NETWORK TOPOLOGY", font=dict(color='#00ffff', size=14), x=0.5),
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 6]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 6]),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
<<<<<<< HEAD
            height=450,
            margin=dict(l=20, r=20, t=60, b=20),
            annotations=[
                dict(
                    text=f"📊 {risk_footer}",
                    x=0.5,
                    y=-0.08,
                    xref='paper',
                    yref='paper',
                    showarrow=False,
                    font=dict(color=footer_color, size=10)
                ),
                dict(
                    text="💡 Hover over nodes for detailed risk assessment",
                    x=0.5,
                    y=-0.15,
                    xref='paper',
                    yref='paper',
                    showarrow=False,
                    font=dict(color='#666', size=9)
                )
            ]
        )
        
        # Return ONLY the Plotly graph HTML
        return fig.to_html(include_plotlyjs='cdn', full_html=False)

# ==================================================
# ============================================
    def get_risk_assessment_panel(self) -> str:
        """Generate the risk assessment panel HTML separately - appears BELOW the topology graph"""
        if not hasattr(self, 'node_descriptions') or not self.node_descriptions:
            return '<div style="padding:20px;text-align:center;color:#888;">No risk data available</div>'
        
        risk_descriptions_html = ""
        for ip, info in self.node_descriptions.items():
            risk_descriptions_html += f"""
            <div style="display:flex; align-items:center; padding:8px 12px; margin:4px 0; 
                        background: rgba(0,0,0,0.3); border-radius:6px; 
                        border-left: 3px solid {info['risk_color']};">
                <span style="margin-right:12px; font-weight:bold; color:#00ffff; min-width:120px;">{ip}</span>
                <span style="color:{info['risk_color']}; font-weight:bold; margin-right:12px; min-width:80px;">
                    {info['risk_icon']} {info['risk_score']:.1f}
                </span>
                <span style="color:#aaa; font-size:11px; flex:1;">{info['description']}</span>
            </div>
            """
        
        total_nodes = len(self.node_descriptions)
        high_count = sum(1 for info in self.node_descriptions.values() if info['risk_score'] >= 7)
        medium_count = sum(1 for info in self.node_descriptions.values() if 4 <= info['risk_score'] < 7)
        low_count = sum(1 for info in self.node_descriptions.values() if info['risk_score'] < 4)
        
        # Generate alert message based on risk levels
        alert_html = ""
        if high_count > 0:
            alert_html = f"""
            <div style="background: rgba(255, 0, 0, 0.15); border: 1px solid #ff0000; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">🚨</span>
                <div>
                    <span style="color: #ff0000; font-weight: bold; font-size: 13px;">⚠️ CRITICAL NODE DETECTED!</span>
                    <span style="color: #ff6666; font-size: 11px; display: block; margin-top: 2px;">
                        {high_count} node{'s' if high_count > 1 else ''} with CRITICAL risk level - Immediate action required!
                    </span>
                </div>
            </div>
            """
        elif medium_count > 0:
            alert_html = f"""
            <div style="background: rgba(255, 204, 0, 0.12); border: 1px solid #ffcc00; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">📊</span>
                <div>
                    <span style="color: #ffcc00; font-weight: bold; font-size: 13px;">⚠️ MEDIUM RISK NODES</span>
                    <span style="color: #ffdd77; font-size: 11px; display: block; margin-top: 2px;">
                        {medium_count} node{'s' if medium_count > 1 else ''} with MEDIUM risk level - Schedule remediation
                    </span>
                </div>
            </div>
            """
        else:
            alert_html = f"""
            <div style="background: rgba(0, 255, 0, 0.08); border: 1px solid #44ff44; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">✅</span>
                <div>
                    <span style="color: #44ff44; font-weight: bold; font-size: 13px;">🟢 LOW RISK</span>
                    <span style="color: #88ff88; font-size: 11px; display: block; margin-top: 2px;">
                        All nodes have LOW risk - Continue monitoring
                    </span>
                </div>
            </div>
            """
        
        risk_panel_html = f"""
        <div style="margin-top: 15px; padding: 12px; background: rgba(10, 15, 30, 0.9); border-radius: 10px; border: 1px solid rgba(0, 255, 255, 0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="color: #00ffff; font-size: 13px; font-weight: bold;">📋 RISK ASSESSMENT PER NODE</span>
                <span style="color: #666; font-size: 10px;">Hover nodes for details</span>
            </div>
            {alert_html}
            <div style="max-height: 200px; overflow-y: auto; padding-right: 5px;">
                {risk_descriptions_html}
            </div>
            <div style="margin-top: 10px; display: flex; gap: 15px; justify-content: center; font-size: 10px; color: #888; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px; flex-wrap: wrap;">
                <span><span style="color:#ff4444;">●</span> Critical ({high_count})</span>
                <span><span style="color:#ffcc00;">●</span> Medium ({medium_count})</span>
                <span><span style="color:#44ff44;">●</span> Low ({low_count})</span>
                <span style="color:#666;">|</span>
                <span style="color:#666;">Total Nodes: {total_nodes}</span>
            </div>
        </div>
        """
        
        return risk_panel_html
# ================================================================
# ================================================================
    def generate_historical_timeline(self) -> str:
=======
            height=400,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig.to_html(include_plotlyjs='cdn', full_html=False)
    
    def generate_historical_timeline(self) -> str:
        """Generate historical scan timeline using Plotly"""
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        if not PLOTLY_AVAILABLE or not self.scan_history:
            return '<div style="padding:50px;text-align:center;">No historical data available. Run scans to see timeline.</div>'
        
        timestamps = [h.timestamp for h in self.scan_history]
        risk_scores = [h.risk_score for h in self.scan_history]
        open_ports = [h.open_ports for h in self.scan_history]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=timestamps, y=risk_scores,
            mode='lines+markers',
            name='Risk Score',
            line=dict(color='#ff4444', width=2),
            marker=dict(size=8, color='#ff0000', symbol='diamond')
        ))
        
        fig.add_trace(go.Scatter(
            x=timestamps, y=open_ports,
            mode='lines+markers',
            name='Open Ports',
            line=dict(color='#44ff44', width=2),
            marker=dict(size=8, color='#00ff00', symbol='circle')
        ))
        
        fig.update_layout(
            title=dict(text="📊 HISTORICAL SCAN TIMELINE", font=dict(color='#00ffff', size=14), x=0.5),
            xaxis_title="Scan Time",
            yaxis_title="Value",
            template="plotly_dark",
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(0,0,0,0.5)'),
            hovermode='x unified'
        )
        
        return fig.to_html(include_plotlyjs='cdn', full_html=False)
    
<<<<<<< HEAD
    def generate_full_dashboard(self, auto_open: bool = False):
=======
    def generate_full_dashboard(self):
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        """Generate complete dashboard with GeoMap, Topology, Timeline, and Services"""
        
        total_risk = sum(p.get('risk_score', 0) for p in self.discovered_ports)
        avg_risk = total_risk / max(1, len(self.discovered_ports))
        
        # Generate services table
        services_html = ""
        for s in self.services_found[:20]:
            risk_color = "#ff0000" if s["risk_score"] >= 7 else "#ffcc00" if s["risk_score"] >= 4 else "#00ff00"
            services_html += f"""
            <tr>
                <td style="color:#00ffff">{s['port']}/{s['protocol']}</td>
                <td style="color:#00ff88">{s['service']}</td>
                <td style="color:{risk_color}; font-weight:bold">{s['risk_score']}</td>
                <td style="color:#ffcc00">{s.get('exploit', 'N/A')}</td>
                <td style="color:#ff66ff">{s.get('cvss_id', 'N/A')}</td>
            </tr>
            """
        
        geo_html = self.geo_map.generate_threat_map()
<<<<<<< HEAD
        topology_graph = self.generate_network_topology()
        timeline_html = self.generate_historical_timeline()
        risk_panel = self.get_risk_assessment_panel()
        
        html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>DSTerminal SOC Dashboard - Full Intelligence Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: linear-gradient(135deg, #0a0a1a 0%, #0d1117 100%); font-family: 'Segoe UI', monospace; color: #e6e6e6; }}
            .header {{ background: linear-gradient(90deg, #1a1a2e, #16213e); padding: 20px; border-bottom: 2px solid #00ffff; text-align: center; }}
            .header h1 {{ font-size: 28px; background: linear-gradient(90deg, #00ffff, #ff00ff); -webkit-background-clip: text; background-clip: text; color: transparent; }}
            .dashboard-container {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; padding: 20px; max-width: 1600px; margin: 0 auto; }}
            .card {{ background: rgba(20, 25, 40, 0.95); border-radius: 15px; padding: 20px; border: 1px solid rgba(0, 255, 255, 0.2); }}
            .card-header {{ font-size: 16px; font-weight: bold; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid rgba(0, 255, 255, 0.3); color: #00ffff; text-align: center; }}
            .stats-grid {{ display: flex; justify-content: center; gap: 20px; margin: 20px auto; flex-wrap: wrap; max-width: 1200px; }}
            .stat {{ text-align: center; padding: 15px 25px; background: rgba(0, 0, 0, 0.3); border-radius: 10px; min-width: 100px; }}
            .stat-value {{ font-size: 32px; font-weight: bold; color: #00ff88; }}
            .stat-label {{ font-size: 11px; color: #888; margin-top: 5px; }}
            .risk-high {{ color: #ff0000; }}
            .risk-med {{ color: #ffcc00; }}
            .risk-low {{ color: #00ff00; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 12px; }}
            th {{ color: #00ffff; }}
            .footer {{ text-align: center; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 10px; color: #666; }}
            .blink {{ animation: blink 1s step-end infinite; }}
            @keyframes blink {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
            .full-width {{ grid-column: span 2; }}
            @media (max-width: 1000px) {{ .dashboard-container {{ grid-template-columns: 1fr; }} .full-width {{ grid-column: span 1; }} }}
            .org-badge {{ background: #ffaa00; color: #000; padding: 2px 6px; border-radius: 10px; font-size: 9px; margin-left: 5px; }}
            .dual-badge {{ background: #ff6600; color: #000; padding: 2px 6px; border-radius: 10px; font-size: 9px; margin-left: 5px; }}
            .risk-panel-container {{ margin-top: 15px; }}
            .risk-item {{ display: flex; align-items: center; padding: 8px 12px; margin: 4px 0; background: rgba(0,0,0,0.3); border-radius: 6px; }}
            .risk-ip {{ margin-right: 12px; font-weight: bold; color: #00ffff; min-width: 120px; }}
            .risk-score {{ font-weight: bold; margin-right: 12px; min-width: 80px; }}
            .risk-desc {{ color: #aaa; font-size: 11px; flex: 1; }}
            .risk-legend {{ margin-top: 10px; display: flex; gap: 15px; justify-content: center; font-size: 10px; color: #888; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px; flex-wrap: wrap; }}
            .risk-legend span {{ display: inline-flex; align-items: center; gap: 4px; }}
            .dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }}
            .dot-critical {{ background: #ff0000; }}
            .dot-medium {{ background: #ffcc00; }}
            .dot-low {{ background: #44ff44; }}
            #topology {{ min-height: 400px; width: 100%; }}
            #topology .js-plotly-plot {{ width: 100% !important; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ DSTERMINAL CYBER-OPS NETWORK TOPOLOGY MAPPING 🛡️</h1>
            <div>Network Intelligence | AI Vulnerability Scoring | Real-time Threat Detection</div>
            <div class="blink" style="color: #00ff00; font-size: 11px; margin-top: 5px;">● FULL INTELLIGENCE DASHBOARD - DUAL LOCATION TRACKING ●</div>
            <div style="font-size: 10px; color: #ffaa00; margin-top: 3px;">🏢 Organization Headquarters + 🖥️ Server/Cloud Locations</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat"><div class="stat-value">{len(self.network_nodes)}</div><div class="stat-label">HOSTS</div></div>
            <div class="stat"><div class="stat-value">{len(self.discovered_ports)}</div><div class="stat-label">OPEN PORTS</div></div>
            <div class="stat"><div class="stat-value">{len(self.services_found)}</div><div class="stat-label">SERVICES</div></div>
            <div class="stat"><div class="stat-value">{self.scan_duration}s</div><div class="stat-label">DURATION</div></div>
            <div class="stat"><div class="stat-value {('risk-high' if avg_risk >= 7 else 'risk-med' if avg_risk >= 4 else 'risk-low')}">{avg_risk:.1f}</div><div class="stat-label">RISK SCORE</div></div>
            <div class="stat"><div class="stat-value">{self.current_target[:15]}</div><div class="stat-label">TARGET</div></div>
        </div>
        
        <div class="dashboard-container">
            <div class="card">
                <div class="card-header">🌍 GEOGRAPHIC THREAT MAP <span class="org-badge">🏢 HQ</span> <span class="dual-badge">🖥️ Server</span></div>
                <div id="geomap" style="height: 450px;">{geo_html}</div>
            </div>
            <div class="card">
                <div class="card-header">🌐 NETWORK TOPOLOGY</div>
                <div id="topology" style="min-height: 400px;">{topology_graph}</div>
                <div class="risk-panel-container">{risk_panel}</div>
            </div>
            <div class="card full-width">
                <div class="card-header">📊 HISTORICAL SCAN TIMELINE</div>
                <div id="timeline">{timeline_html}</div>
            </div>
            <div class="card full-width">
                <div class="card-header">🎯 DISCOVERED SERVICES & VULNERABILITIES</div>
                <div style="max-height: 300px; overflow: auto;">
                    <table>
                        <thead>
                            <tr><th>Port</th><th>Service</th><th>Risk</th><th>Exploit</th><th>CVE ID</th></tr>
                        </thead>
                        <tbody>
                            {services_html if services_html else '<tr><td colspan="5" style="text-align:center;">No services discovered</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="footer">
            DSTerminal Enterprise SOC Platform | Powered by AI Vulnerability Scoring | Threat Intelligence Active
            <br>📄 DSTerminal autogenerated report | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            <br><span style="color: #00ff00;">● GEOLOCATION: IP-API.COM</span> | <span style="color: #ffaa00;">🏢 ORGANIZATION HEADQUARTERS</span> | <span style="color: #ff6600;">🖥️ SERVER LOCATIONS</span> | ● REAL-TIME MONITORING ACTIVE ●
        </div>
    </body>
    </html>
=======
        topology_html = self.generate_network_topology()
        timeline_html = self.generate_historical_timeline()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DSTerminal SOC Dashboard - Full Intelligence Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: linear-gradient(135deg, #0a0a1a 0%, #0d1117 100%); font-family: 'Segoe UI', monospace; color: #e6e6e6; }}
        .header {{ background: linear-gradient(90deg, #1a1a2e, #16213e); padding: 20px; border-bottom: 2px solid #00ffff; text-align: center; }}
        .header h1 {{ font-size: 28px; background: linear-gradient(90deg, #00ffff, #ff00ff); -webkit-background-clip: text; background-clip: text; color: transparent; }}
        .dashboard-container {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; padding: 20px; max-width: 1600px; margin: 0 auto; }}
        .card {{ background: rgba(20, 25, 40, 0.95); border-radius: 15px; padding: 20px; border: 1px solid rgba(0, 255, 255, 0.2); }}
        .card-header {{ font-size: 16px; font-weight: bold; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid rgba(0, 255, 255, 0.3); color: #00ffff; text-align: center; }}
        .stats-grid {{ display: flex; justify-content: center; gap: 20px; margin: 20px auto; flex-wrap: wrap; max-width: 1200px; }}
        .stat {{ text-align: center; padding: 15px 25px; background: rgba(0, 0, 0, 0.3); border-radius: 10px; min-width: 100px; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #00ff88; }}
        .stat-label {{ font-size: 11px; color: #888; margin-top: 5px; }}
        .risk-high {{ color: #ff0000; }}
        .risk-med {{ color: #ffcc00; }}
        .risk-low {{ color: #00ff00; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 12px; }}
        th {{ color: #00ffff; }}
        .footer {{ text-align: center; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 10px; color: #666; }}
        .blink {{ animation: blink 1s step-end infinite; }}
        @keyframes blink {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        .full-width {{ grid-column: span 2; }}
        @media (max-width: 1000px) {{ .dashboard-container {{ grid-template-columns: 1fr; }} .full-width {{ grid-column: span 1; }} }}
        .org-badge {{ background: #ffaa00; color: #000; padding: 2px 6px; border-radius: 10px; font-size: 9px; margin-left: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ DSTERMINAL CYBER-OPS NETWORK TOPOLOGY MAPPING 🛡️</h1>
        <div>Network Intelligence | AI Vulnerability Scoring | Real-time Threat Detection</div>
        <div class="blink" style="color: #00ff00; font-size: 11px; margin-top: 5px;">● FULL INTELLIGENCE DASHBOARD - ORGANIZATION LOCATION ●</div>
    </div>
    
    <div class="stats-grid">
        <div class="stat"><div class="stat-value">{len(self.network_nodes)}</div><div class="stat-label">HOSTS</div></div>
        <div class="stat"><div class="stat-value">{len(self.discovered_ports)}</div><div class="stat-label">OPEN PORTS</div></div>
        <div class="stat"><div class="stat-value">{len(self.services_found)}</div><div class="stat-label">SERVICES</div></div>
        <div class="stat"><div class="stat-value">{self.scan_duration}s</div><div class="stat-label">DURATION</div></div>
        <div class="stat"><div class="stat-value {('risk-high' if avg_risk >= 7 else 'risk-med' if avg_risk >= 4 else 'risk-low')}">{avg_risk:.1f}</div><div class="stat-label">RISK SCORE</div></div>
        <div class="stat"><div class="stat-value">{self.current_target[:15]}</div><div class="stat-label">TARGET</div></div>
    </div>
    
    <div class="dashboard-container">
        <div class="card">
            <div class="card-header">🌍 GEOGRAPHIC THREAT MAP <span class="org-badge">🏢 HQ Locations Shown</span></div>
            <div id="geomap" style="height: 450px;">{geo_html}</div>
        </div>
        <div class="card">
            <div class="card-header">🌐 NETWORK TOPOLOGY</div>
            <div id="topology">{topology_html}</div>
        </div>
        <div class="card full-width">
            <div class="card-header">📊 HISTORICAL SCAN TIMELINE</div>
            <div id="timeline">{timeline_html}</div>
        </div>
        <div class="card full-width">
            <div class="card-header">🎯 DISCOVERED SERVICES & VULNERABILITIES</div>
            <div style="max-height: 300px; overflow: auto;">
                <table>
                    <thead>
                        <tr><th>Port</th><th>Service</th><th>Risk</th><th>Exploit</th><th>CVE ID</th></tr>
                    </thead>
                    <tbody>
                        {services_html if services_html else '<tr><td colspan="5" style="text-align:center;">No services discovered</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="footer">
        DSTerminal Enterprise SOC Platform | Powered by AI Vulnerability Scoring | Threat Intelligence Active
        <br>📄 DSTerminal autogenerated report | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        <br><span style="color: #00ff00;">● GEOLOCATION: IP-API.COM | 🏢 ORGANIZATION HEADQUARTERS LOCATIONS | ● REAL-TIME MONITORING ACTIVE ●</span>
    </div>
</body>
</html>
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
        """
        
        html_path = os.path.join(self.scans_dir, f"soc_full_dashboard_{self.current_target.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
<<<<<<< HEAD
        # Ask user if they want to open the dashboard
        if not auto_open:
            print(f"\n{Colors.CYAN}╔{'═' * 60}╗{Colors.RESET}")
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.GREEN}📄 Dashboard Generated Successfully!{Colors.RESET} {Colors.CYAN}║{Colors.RESET}")
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.DIM}Location: {html_path}{Colors.RESET} {Colors.CYAN}║{Colors.RESET}")
            print(f"{Colors.CYAN}╠{'═' * 60}╣{Colors.RESET}")
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.YELLOW}[?] Open dashboard in browser?{Colors.RESET} {Colors.CYAN}║{Colors.RESET}")
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.GREEN}[Y] Yes{Colors.RESET}  {Colors.RED}[N] No{Colors.RESET}  {Colors.CYAN}║{Colors.RESET}")
            print(f"{Colors.CYAN}╚{'═' * 60}╝{Colors.RESET}")
            
            choice = input(f"{Colors.GREEN}[SOC] > {Colors.RESET}").strip().lower()
            
            if choice == 'y' or choice == 'yes':
                print(f"{Colors.GREEN}[+] Opening dashboard in browser...{Colors.RESET}")
                webbrowser.open(f"file://{html_path}")
            else:
                print(f"{Colors.YELLOW}[!] Dashboard saved but not opened.{Colors.RESET}")
                print(f"{Colors.YELLOW}[!] You can open it later from: {html_path}{Colors.RESET}")
        else:
            # Auto-open mode (for silent/automated runs)
            webbrowser.open(f"file://{html_path}")
        
        return html_path

    # ==============================================
    # ==============================================
=======
        webbrowser.open(f"file://{html_path}")
        # print(self.center(f"{Colors.GREEN}[+] Full dashboard opened: {html_path}{Colors.RESET}"))
        return html_path
    
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
    def interactive_loop(self):
        self.clear_screen()
        
        while True:
            self.clear_screen()
            self.draw_header()
            self.draw_centered_dashboard()
            self.draw_results_table()
            self.draw_footer()
            
            choice = input(f"\n{self.center(Colors.GREEN + '[SOC] > ' + Colors.RESET)}").strip().lower()
            
            if choice == 'x':
                print(self.center(Colors.GREEN + '[+] Exiting SOC Dashboard...' + Colors.RESET))
                break
            elif choice == 's':
                target = input(self.center(Colors.CYAN + 'Enter target IP/Domain: ' + Colors.RESET))
                if target:
                    self.run_nmap_scan(target, ["-F", "-T4", "-sV"])
            elif choice == 'q':
                target = input(self.center(Colors.CYAN + 'Enter target IP/Domain: ' + Colors.RESET))
                if target:
                    self.run_nmap_scan(target, ["-F", "-T4", "-sV", "--top-ports", "100"])
            elif choice == 'f':
                target = input(self.center(Colors.CYAN + 'Enter target IP/Domain: ' + Colors.RESET))
                if target:
                    confirm = input(self.center(Colors.RED + 'Full scan may take minutes. Continue? (y/n): ' + Colors.RESET))
                    if confirm.lower() == 'y':
                        self.run_nmap_scan(target, ["-sS", "-sV", "-sC", "-O", "-T4", "-p-"])
            elif choice == 'd':
                target = input(self.center(Colors.CYAN + 'Enter domain for DNS recon: ' + Colors.RESET))
                if target:
                    self.run_nmap_scan(target, ["-sS", "-sV", "-sC", "-T4", "-p", "53"])
            elif choice == 'h':
                self.show_help()
                input(self.center(Colors.DIM + 'Press Enter...' + Colors.RESET))
            else:
                if choice:
                    print(self.center(Colors.RED + '[!] Unknown command' + Colors.RESET))
                    time.sleep(1)
    
    def show_help(self):
        help_text = f"""
{self.center(Colors.CYAN + '═' * 60 + Colors.RESET)}
{self.center(Colors.GREEN + '🛡️ DSTERMINAL SOC DASHBOARD HELP' + Colors.RESET)}
{self.center(Colors.CYAN + '═' * 60 + Colors.RESET)}
{self.center(Colors.YELLOW + 'Commands:' + Colors.RESET)}
{self.center(Colors.GREEN + '  [S] - Standard Scan' + Colors.RESET)}
{self.center(Colors.GREEN + '  [Q] - Quick Scan' + Colors.RESET)}
{self.center(Colors.GREEN + '  [F] - Full Scan' + Colors.RESET)}
{self.center(Colors.GREEN + '  [D] - DNS Reconnaissance' + Colors.RESET)}
{self.center(Colors.GREEN + '  [H] - Help' + Colors.RESET)}
{self.center(Colors.GREEN + '  [X] - Exit' + Colors.RESET)}
{self.center(Colors.CYAN + '═' * 60 + Colors.RESET)}
"""
        print(help_text)

<<<<<<< HEAD

=======
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
# ============================================================
# EXPORTED CLASSES FOR MAIN DSTERMINAL
# ============================================================

<<<<<<< HEAD
__all__ = ['InteractiveSOCDashboard', 'SOCNmapDashboard', 'SOCNmapIntegration']

=======
# These are the classes that will be imported by dsterminal.py
__all__ = ['InteractiveSOCDashboard', 'SOCNmapDashboard', 'SOCNmapIntegration']

# Alias for backward compatibility - THIS IS CRITICAL
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
SOCNmapDashboard = InteractiveSOCDashboard

class SOCNmapIntegration:
    def __init__(self):
        self.dashboard = None
    
    def start_interactive_dashboard(self):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        self.dashboard.interactive_loop()
    
<<<<<<< HEAD
    def quick_scan(self, target: str, auto_open: bool = False):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        print(f"[+] Running quick scan on {target}")
        self.dashboard.run_nmap_scan(target, ["-F", "-T4", "-sV", "--top-ports", "100"], auto_open=auto_open)
    
    def standard_scan(self, target: str, auto_open: bool = False):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        print(f"[+] Running standard scan on {target}")
        self.dashboard.run_nmap_scan(target, ["-sS", "-sV", "-T4"], auto_open=auto_open)
    
    def full_scan(self, target: str, auto_open: bool = False):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        print(f"[+] Running full scan on {target}")
        self.dashboard.run_nmap_scan(target, ["-sS", "-sV", "-sC", "-O", "-T4", "-p-"], auto_open=auto_open)
    
    def dns_recon(self, target: str, auto_open: bool = False):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        print(f"[+] Running DNS recon on {target}")
        self.dashboard.run_nmap_scan(target, ["-sS", "-sV", "-sC", "-T4", "-p", "53"], auto_open=auto_open)


# ============================================================
# MAIN ENTRY POINT
=======
    def quick_scan(self, target: str):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        print(f"[+] Running quick scan on {target}")
        self.dashboard.run_nmap_scan(target, ["-F", "-T4", "-sV", "--top-ports", "100"])
        self.dashboard.generate_full_dashboard()
    
    def standard_scan(self, target: str):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        print(f"[+] Running standard scan on {target}")
        self.dashboard.run_nmap_scan(target, ["-sS", "-sV", "-T4"])
        self.dashboard.generate_full_dashboard()
    
    def full_scan(self, target: str):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        print(f"[+] Running full scan on {target}")
        self.dashboard.run_nmap_scan(target, ["-sS", "-sV", "-sC", "-O", "-T4", "-p-"])
        self.dashboard.generate_full_dashboard()
    
    def dns_recon(self, target: str):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        print(f"[+] Running DNS recon on {target}")
        self.dashboard.run_nmap_scan(target, ["-sS", "-sV", "-sC", "-T4", "-p", "53"])
        self.dashboard.generate_full_dashboard()


# ============================================================
# MAIN ENTRY POINT (for standalone execution)
>>>>>>> a9c582c3eccfbce9c5ab735ec9d5e5c57fe2ab44
# ============================================================

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"{' '*15}DSTERMINAL SOC NMAP DASHBOARD")
    print(f"{'='*60}\n")
    soc = SOCNmapIntegration()
    soc.start_interactive_dashboard()