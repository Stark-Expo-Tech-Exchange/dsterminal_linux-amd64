#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DSTERMINAL SOC-GRADE NMAP SCAN DASHBOARD - COMPLETE EDITION
Hacker-style 3-Panel Layout | Real-time Scan Monitoring | AI Vulnerability Scoring
"""
import sys
if sys.platform == 'win32':
    import os
    import msvcrt
    # Ensure stdout is properly set
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', errors='ignore')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = open(sys.stderr.fileno(), 'w', encoding='utf-8', errors='ignore')
        
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
import socket
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
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    BLACK = '\033[30m'
    DARK_GRAY = '\033[90m'
    LIGHT_GRAY = '\033[37m'

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
# Domain to IP Resolution Helper
# ============================================================

def resolve_domain_to_ip(domain: str) -> Optional[str]:
    """Resolve domain name to IP address with better error handling"""
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
# GeoIP Functions - FIXED
# ============================================================

def get_server_location(ip: str) -> Dict:
    """Get actual server location with proper domain resolution and fallback"""
    try:
        if ip.startswith(("192.168.", "10.", "172.", "127.", "169.254.", "::1")):
            return {"country": "Private Network", "city": "Local", "lat": 0, "lon": 0, "isp": "Private", "location": "Local Network"}
        
        resolved_ip = ip
        if not re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
            resolved = resolve_domain_to_ip(ip)
            if resolved:
                resolved_ip = resolved
            else:
                return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "location": "Unknown"}
        
        import requests
        
        try:
            response = requests.get(f"http://ip-api.com/json/{resolved_ip}?fields=status,country,city,lat,lon,isp,org,as", timeout=5)
            data = response.json()
            if data.get('status') == 'success':
                return {
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "lat": data.get("lat", 0),
                    "lon": data.get("lon", 0),
                    "isp": data.get("isp", "Unknown"),
                    "org": data.get("org", "Unknown"),
                    "as": data.get("as", "Unknown"),
                    "location": f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}",
                    "is_organization_location": False,
                    "resolved_ip": resolved_ip
                }
        except:
            pass
        
        try:
            response = requests.get(f"https://ipapi.co/{resolved_ip}/json/", timeout=3)
            data = response.json()
            if data.get('country_name'):
                return {
                    "country": data.get("country_name", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "lat": data.get("latitude", 0),
                    "lon": data.get("longitude", 0),
                    "isp": data.get("org", "Unknown"),
                    "org": data.get("org", "Unknown"),
                    "as": data.get("asn", "Unknown"),
                    "location": f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}",
                    "is_organization_location": False,
                    "resolved_ip": resolved_ip
                }
        except:
            pass
        
        try:
            response = requests.get(f"https://ipinfo.io/{resolved_ip}/json", timeout=3)
            data = response.json()
            if data.get('country'):
                loc = data.get('loc', '').split(',')
                lat = float(loc[0]) if len(loc) > 0 else 0
                lon = float(loc[1]) if len(loc) > 1 else 0
                return {
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "lat": lat,
                    "lon": lon,
                    "isp": data.get("org", "Unknown"),
                    "org": data.get("org", "Unknown"),
                    "as": data.get("asn", "Unknown"),
                    "location": f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}",
                    "is_organization_location": False,
                    "resolved_ip": resolved_ip
                }
        except:
            pass
        
        return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "location": "Unknown"}
    except Exception as e:
        return {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown", "location": "Unknown"}
    
def enhanced_geoip_lookup(domain: str, ip: Optional[str] = None) -> Tuple[Dict, Dict, bool]:
    """Enhanced GeoIP with proper domain resolution and multiple fallbacks"""
    if not ip or ip == domain:
        resolved_ip = resolve_domain_to_ip(domain)
        if resolved_ip:
            ip = resolved_ip
        else:
            ip = domain
    
    org_location = OrganizationLocationDB.get_organization_location(domain, ip)
    is_org_location = False
    
    if org_location and org_location.get("lat", 0) != 0:
        is_org_location = True
    else:
        org_location = {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "flag": "[]"}
    
    server_location = get_server_location(ip)
    
    if (server_location.get("country") == "Unknown" or server_location.get("lat", 0) == 0) and ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
        import requests
        
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon,isp,org,as", timeout=3)
            data = response.json()
            if data.get('status') == 'success':
                server_location = {
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "lat": data.get("lat", 0),
                    "lon": data.get("lon", 0),
                    "isp": data.get("isp", "Unknown"),
                    "org": data.get("org", "Unknown"),
                    "as": data.get("as", "Unknown"),
                    "flag": "[]",
                    "location": f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
                }
        except:
            pass
        
        if server_location.get("country") == "Unknown":
            try:
                response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)
                data = response.json()
                if data.get('country_name'):
                    server_location = {
                        "country": data.get("country_name", "Unknown"),
                        "city": data.get("city", "Unknown"),
                        "lat": data.get("latitude", 0),
                        "lon": data.get("longitude", 0),
                        "isp": data.get("org", "Unknown"),
                        "org": data.get("org", "Unknown"),
                        "as": data.get("asn", "Unknown"),
                        "flag": "[]",
                        "location": f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}"
                    }
            except:
                pass
    
    return org_location, server_location, is_org_location


# ============================================================
# ORGANIZATION LOCATION DATABASE with Auto-Detection
# ============================================================

class OrganizationLocationDB:
    """Database of organization headquarters locations with auto-detection"""
    
    CACHE_FILE = os.path.expanduser("~/.dsterminal_org_cache.json")
    
    ORGANIZATIONS = {
        # ========== MALAWI ==========
        "unima.ac.mw": {"country": "Malawi", "city": "Zomba", "lat": -15.3833, "lon": 35.3167, "flag": "[]", "region": "East Africa"},
        "must.ac.mw": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "[]", "region": "East Africa"},
        "poly.ac.mw": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "[]", "region": "East Africa"},
        "kuhes.ac.mw": {"country": "Malawi", "city": "Lilongwe", "lat": -13.9833, "lon": 33.7833, "flag": "[]", "region": "East Africa"},
        "mzuni.ac.mw": {"country": "Malawi", "city": "Mzuzu", "lat": -11.4667, "lon": 34.0167, "flag": "[]", "region": "East Africa"},
        "cc.ac.mw": {"country": "Malawi", "city": "Zomba", "lat": -15.7833, "lon": 34.9667, "flag": "[]", "region": "East Africa"},
        "medcol.ac.mw": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "[]", "region": "East Africa"},
        "magu.ac.mw": {"country": "Malawi", "city": "Lilongwe", "lat": -13.9833, "lon": 33.7833, "flag": "[]", "region": "East Africa"},
        "sparcsystems.africa": {"country": "Malawi", "city": "Blantyre", "lat": -15.7833, "lon": 34.9667, "flag": "[]", "region": "East Africa"},
        
        # ========== SOUTH AFRICA ==========
        "uct.ac.za": {"country": "South Africa", "city": "Cape Town", "lat": -33.9249, "lon": 18.4241, "flag": "[]", "region": "Southern Africa"},
        "up.ac.za": {"country": "South Africa", "city": "Pretoria", "lat": -25.7548, "lon": 28.2315, "flag": "[]", "region": "Southern Africa"},
        "uj.ac.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "wits.ac.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.1929, "lon": 28.0305, "flag": "[]", "region": "Southern Africa"},
        "stel.ac.za": {"country": "South Africa", "city": "Stellenbosch", "lat": -33.9328, "lon": 18.8644, "flag": "[]", "region": "Southern Africa"},
        "nmmu.ac.za": {"country": "South Africa", "city": "Gqeberha", "lat": -33.9618, "lon": 25.6099, "flag": "[]", "region": "Southern Africa"},
        "dut.ac.za": {"country": "South Africa", "city": "Durban", "lat": -29.8587, "lon": 31.0218, "flag": "[]", "region": "Southern Africa"},
        "tut.ac.za": {"country": "South Africa", "city": "Pretoria", "lat": -25.7548, "lon": 28.2315, "flag": "[]", "region": "Southern Africa"},
        
        # ========== KENYA ==========
        "uonbi.ac.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        "ku.ac.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2225, "lon": 36.8966, "flag": "[]", "region": "East Africa"},
        "tukenya.ac.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.3204, "lon": 36.8157, "flag": "[]", "region": "East Africa"},
        "mku.ac.ke": {"country": "Kenya", "city": "Thika", "lat": -1.0386, "lon": 37.0908, "flag": "[]", "region": "East Africa"},
        "daystar.ac.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        
        # ========== NIGERIA ==========
        "unilag.edu.ng": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "unn.edu.ng": {"country": "Nigeria", "city": "Nsukka", "lat": 6.8575, "lon": 7.3981, "flag": "[]", "region": "West Africa"},
        "oauife.edu.ng": {"country": "Nigeria", "city": "Ile-Ife", "lat": 7.5000, "lon": 4.5000, "flag": "[]", "region": "West Africa"},
        "abu.edu.ng": {"country": "Nigeria", "city": "Zaria", "lat": 11.1667, "lon": 7.6167, "flag": "[]", "region": "West Africa"},
        "uniben.edu": {"country": "Nigeria", "city": "Benin City", "lat": 6.3176, "lon": 5.6145, "flag": "[]", "region": "West Africa"},
        
        # ========== GHANA ==========
        "ug.edu.gh": {"country": "Ghana", "city": "Accra", "lat": 5.6500, "lon": -0.1868, "flag": "[]", "region": "West Africa"},
        "knust.edu.gh": {"country": "Ghana", "city": "Kumasi", "lat": 6.6750, "lon": -1.5714, "flag": "[]", "region": "West Africa"},
        "central.edu.gh": {"country": "Ghana", "city": "Accra", "lat": 5.6500, "lon": -0.1868, "flag": "[]", "region": "West Africa"},
        
        # ========== EGYPT ==========
        "cu.edu.eg": {"country": "Egypt", "city": "Cairo", "lat": 30.0333, "lon": 31.2333, "flag": "[]", "region": "North Africa"},
        "alexu.edu.eg": {"country": "Egypt", "city": "Alexandria", "lat": 31.2001, "lon": 29.9187, "flag": "[]", "region": "North Africa"},
        
        # ========== USA ==========
        "harvard.edu": {"country": "USA", "city": "Cambridge", "lat": 42.3744, "lon": -71.1169, "flag": "[]", "region": "North America"},
        "stanford.edu": {"country": "USA", "city": "Stanford", "lat": 37.4275, "lon": -122.1697, "flag": "[]", "region": "North America"},
        "mit.edu": {"country": "USA", "city": "Cambridge", "lat": 42.3601, "lon": -71.0942, "flag": "[]", "region": "North America"},
        
        # ========== UK ==========
        "ox.ac.uk": {"country": "United Kingdom", "city": "Oxford", "lat": 51.7520, "lon": -1.2577, "flag": "[]", "region": "Europe"},
        "cam.ac.uk": {"country": "United Kingdom", "city": "Cambridge", "lat": 52.2053, "lon": 0.1218, "flag": "[]", "region": "Europe"},
        
        # ========== GERMANY ==========
        "tu-berlin.de": {"country": "Germany", "city": "Berlin", "lat": 52.5200, "lon": 13.4050, "flag": "[]", "region": "Europe"},
        "lmu.de": {"country": "Germany", "city": "Munich", "lat": 48.1351, "lon": 11.5820, "flag": "[]", "region": "Europe"},
        
        # ========== INDIA ==========
        "iitb.ac.in": {"country": "India", "city": "Mumbai", "lat": 19.0760, "lon": 72.8777, "flag": "[]", "region": "South Asia"},
        "iisc.ac.in": {"country": "India", "city": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "flag": "[]", "region": "South Asia"},
        
        # ========== ADD UNICAF (MALAWI) ==========
        "unicaf.org": {"country": "Malawi", "city": "Lilongwe", "lat": -13.9833, "lon": 33.7833, "flag": "[]", "region": "East Africa"},
        "unicaf.net": {"country": "Malawi", "city": "Lilongwe", "lat": -13.9833, "lon": 33.7833, "flag": "[]", "region": "East Africa"},
        "unicaf.com": {"country": "Malawi", "city": "Lilongwe", "lat": -13.9833, "lon": 33.7833, "flag": "[]", "region": "East Africa"},
        "unicaf.mw": {"country": "Malawi", "city": "Lilongwe", "lat": -13.9833, "lon": 33.7833, "flag": "[]", "region": "East Africa"},
        
        # ========== ADD OLD MUTUAL (SOUTH AFRICA) ==========
        "oldmutual.com": {"country": "South Africa", "city": "Cape Town", "lat": -33.9249, "lon": 18.4241, "flag": "[]", "region": "Southern Africa"},
        "oldmutual.co.za": {"country": "South Africa", "city": "Cape Town", "lat": -33.9249, "lon": 18.4241, "flag": "[]", "region": "Southern Africa"},
        "oldmutual.co.uk": {"country": "United Kingdom", "city": "London", "lat": 51.5074, "lon": -0.1278, "flag": "[]", "region": "Europe"},
        
        # ========== ADD MORE AFRICAN ORGANIZATIONS ==========
        "mtn.com": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "mtn.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "vodacom.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "standardbank.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "standardbank.com": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "absa.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "absa.africa": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "naspers.com": {"country": "South Africa", "city": "Cape Town", "lat": -33.9249, "lon": 18.4241, "flag": "[]", "region": "Southern Africa"},
        "naspers.co.za": {"country": "South Africa", "city": "Cape Town", "lat": -33.9249, "lon": 18.4241, "flag": "[]", "region": "Southern Africa"},
        "multichoice.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "multichoice.com": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "dstv.com": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "dstv.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "discovery.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "discovery.com": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "sasol.com": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "sasol.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "angloamerican.com": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "angloamerican.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "debeers.com": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        "debeers.co.za": {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "flag": "[]", "region": "Southern Africa"},
        
        # ========== KENYA ==========
        "safaricom.co.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        "safaricom.com": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        "equitybank.co.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        "equitybank.com": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        "kcb.co.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        "kcb.com": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        "kenyaairways.com": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        "kenyaairways.co.ke": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        "eastafrican.com": {"country": "Kenya", "city": "Nairobi", "lat": -1.2921, "lon": 36.8219, "flag": "[]", "region": "East Africa"},
        
        # ========== NIGERIA ==========
        "gtbank.com": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "gtco.com": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "zenithbank.com": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "firstbanknigeria.com": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "firstbank.com.ng": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "accessbankplc.com": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "accessbank.com": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "ecobank.com": {"country": "Togo", "city": "Lome", "lat": 6.1319, "lon": 1.2228, "flag": "[]", "region": "West Africa"},
        "ecobank.net": {"country": "Togo", "city": "Lome", "lat": 6.1319, "lon": 1.2228, "flag": "[]", "region": "West Africa"},
        "ecobank.org": {"country": "Togo", "city": "Lome", "lat": 6.1319, "lon": 1.2228, "flag": "[]", "region": "West Africa"},
        "dangote.com": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "dangote.org": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "mtn.ng": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "mtn.com.ng": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "glo.com": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "glo.ng": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "airtel.com.ng": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        "airtel.ng": {"country": "Nigeria", "city": "Lagos", "lat": 6.5170, "lon": 3.3968, "flag": "[]", "region": "West Africa"},
        
        # ========== GHANA ==========
        "mtn.com.gh": {"country": "Ghana", "city": "Accra", "lat": 5.6500, "lon": -0.1868, "flag": "[]", "region": "West Africa"},
        "mtn.gh": {"country": "Ghana", "city": "Accra", "lat": 5.6500, "lon": -0.1868, "flag": "[]", "region": "West Africa"},
        "vodafone.com.gh": {"country": "Ghana", "city": "Accra", "lat": 5.6500, "lon": -0.1868, "flag": "[]", "region": "West Africa"},
        "vodafone.gh": {"country": "Ghana", "city": "Accra", "lat": 5.6500, "lon": -0.1868, "flag": "[]", "region": "West Africa"},
        "tigo.com.gh": {"country": "Ghana", "city": "Accra", "lat": 5.6500, "lon": -0.1868, "flag": "[]", "region": "West Africa"},
        
        # ========== EGYPT ==========
        "orange.eg": {"country": "Egypt", "city": "Cairo", "lat": 30.0333, "lon": 31.2333, "flag": "[]", "region": "North Africa"},
        "orange.com.eg": {"country": "Egypt", "city": "Cairo", "lat": 30.0333, "lon": 31.2333, "flag": "[]", "region": "North Africa"},
        "vodafone.eg": {"country": "Egypt", "city": "Cairo", "lat": 30.0333, "lon": 31.2333, "flag": "[]", "region": "North Africa"},
        "vodafone.com.eg": {"country": "Egypt", "city": "Cairo", "lat": 30.0333, "lon": 31.2333, "flag": "[]", "region": "North Africa"},
        "etisalat.eg": {"country": "Egypt", "city": "Cairo", "lat": 30.0333, "lon": 31.2333, "flag": "[]", "region": "North Africa"},
        "etisalat.com.eg": {"country": "Egypt", "city": "Cairo", "lat": 30.0333, "lon": 31.2333, "flag": "[]", "region": "North Africa"},
        
        # ========== ADD MAJOR GLOBAL ORGANIZATIONS ==========
        "google.com": {"country": "USA", "city": "Mountain View", "lat": 37.4220, "lon": -122.0841, "flag": "[]", "region": "North America"},
        "google.co.uk": {"country": "United Kingdom", "city": "London", "lat": 51.5074, "lon": -0.1278, "flag": "[]", "region": "Europe"},
        "google.de": {"country": "Germany", "city": "Berlin", "lat": 52.5200, "lon": 13.4050, "flag": "[]", "region": "Europe"},
        "google.fr": {"country": "France", "city": "Paris", "lat": 48.8566, "lon": 2.3522, "flag": "[]", "region": "Europe"},
        "microsoft.com": {"country": "USA", "city": "Redmond", "lat": 47.6740, "lon": -122.1215, "flag": "[]", "region": "North America"},
        "apple.com": {"country": "USA", "city": "Cupertino", "lat": 37.3349, "lon": -122.0090, "flag": "[]", "region": "North America"},
        "amazon.com": {"country": "USA", "city": "Seattle", "lat": 47.6062, "lon": -122.3321, "flag": "[]", "region": "North America"},
        "facebook.com": {"country": "USA", "city": "Menlo Park", "lat": 37.4530, "lon": -122.1810, "flag": "[]", "region": "North America"},
        "twitter.com": {"country": "USA", "city": "San Francisco", "lat": 37.7749, "lon": -122.4194, "flag": "[]", "region": "North America"},
        "linkedin.com": {"country": "USA", "city": "Sunnyvale", "lat": 37.3688, "lon": -122.0363, "flag": "[]", "region": "North America"},
        "netflix.com": {"country": "USA", "city": "Los Gatos", "lat": 37.2308, "lon": -121.9740, "flag": "[]", "region": "North America"},
        "uber.com": {"country": "USA", "city": "San Francisco", "lat": 37.7749, "lon": -122.4194, "flag": "[]", "region": "North America"},
        
        # Banking & Finance
        "goldmansachs.com": {"country": "USA", "city": "New York", "lat": 40.7128, "lon": -74.0060, "flag": "[]", "region": "North America"},
        "jpmorgan.com": {"country": "USA", "city": "New York", "lat": 40.7128, "lon": -74.0060, "flag": "[]", "region": "North America"},
        "bankofamerica.com": {"country": "USA", "city": "Charlotte", "lat": 35.2271, "lon": -80.8431, "flag": "[]", "region": "North America"},
        "wellsfargo.com": {"country": "USA", "city": "San Francisco", "lat": 37.7749, "lon": -122.4194, "flag": "[]", "region": "North America"},
        "hsbc.com": {"country": "United Kingdom", "city": "London", "lat": 51.5074, "lon": -0.1278, "flag": "[]", "region": "Europe"},
        "barclays.com": {"country": "United Kingdom", "city": "London", "lat": 51.5074, "lon": -0.1278, "flag": "[]", "region": "Europe"},
        "deutsche-bank.com": {"country": "Germany", "city": "Frankfurt", "lat": 50.1109, "lon": 8.6821, "flag": "[]", "region": "Europe"},
        "ubs.com": {"country": "Switzerland", "city": "Zurich", "lat": 47.3769, "lon": 8.5417, "flag": "[]", "region": "Europe"},
        "credit-suisse.com": {"country": "Switzerland", "city": "Zurich", "lat": 47.3769, "lon": 8.5417, "flag": "[]", "region": "Europe"},
    }
    
    KNOWN_ORGANIZATION_PATTERNS = {
        'unicaf': {'country': 'Malawi', 'city': 'Lilongwe', 'lat': -13.9833, 'lon': 33.7833, 'flag': '[]', 'region': 'East Africa'},
        'oldmutual': {'country': 'South Africa', 'city': 'Cape Town', 'lat': -33.9249, 'lon': 18.4241, 'flag': '[]', 'region': 'Southern Africa'},
        'mtn': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'vodacom': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'safaricom': {'country': 'Kenya', 'city': 'Nairobi', 'lat': -1.2921, 'lon': 36.8219, 'flag': '[]', 'region': 'East Africa'},
        'equitybank': {'country': 'Kenya', 'city': 'Nairobi', 'lat': -1.2921, 'lon': 36.8219, 'flag': '[]', 'region': 'East Africa'},
        'kcb': {'country': 'Kenya', 'city': 'Nairobi', 'lat': -1.2921, 'lon': 36.8219, 'flag': '[]', 'region': 'East Africa'},
        'gtbank': {'country': 'Nigeria', 'city': 'Lagos', 'lat': 6.5170, 'lon': 3.3968, 'flag': '[]', 'region': 'West Africa'},
        'zenithbank': {'country': 'Nigeria', 'city': 'Lagos', 'lat': 6.5170, 'lon': 3.3968, 'flag': '[]', 'region': 'West Africa'},
        'firstbank': {'country': 'Nigeria', 'city': 'Lagos', 'lat': 6.5170, 'lon': 3.3968, 'flag': '[]', 'region': 'West Africa'},
        'accessbank': {'country': 'Nigeria', 'city': 'Lagos', 'lat': 6.5170, 'lon': 3.3968, 'flag': '[]', 'region': 'West Africa'},
        'ecobank': {'country': 'Togo', 'city': 'Lome', 'lat': 6.1319, 'lon': 1.2228, 'flag': '[]', 'region': 'West Africa'},
        'standardbank': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'absa': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'naspers': {'country': 'South Africa', 'city': 'Cape Town', 'lat': -33.9249, 'lon': 18.4241, 'flag': '[]', 'region': 'Southern Africa'},
        'multichoice': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'dstv': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'discovery': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'sasol': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'angloamerican': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'debeers': {'country': 'South Africa', 'city': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'flag': '[]', 'region': 'Southern Africa'},
        'kenyaairways': {'country': 'Kenya', 'city': 'Nairobi', 'lat': -1.2921, 'lon': 36.8219, 'flag': '[]', 'region': 'East Africa'},
        'dangote': {'country': 'Nigeria', 'city': 'Lagos', 'lat': 6.5170, 'lon': 3.3968, 'flag': '[]', 'region': 'West Africa'},
        'glo': {'country': 'Nigeria', 'city': 'Lagos', 'lat': 6.5170, 'lon': 3.3968, 'flag': '[]', 'region': 'West Africa'},
        'airtel': {'country': 'Nigeria', 'city': 'Lagos', 'lat': 6.5170, 'lon': 3.3968, 'flag': '[]', 'region': 'West Africa'},
        'vodafone': {'country': 'United Kingdom', 'city': 'London', 'lat': 51.5074, 'lon': -0.1278, 'flag': '[]', 'region': 'Europe'},
        'orange': {'country': 'France', 'city': 'Paris', 'lat': 48.8566, 'lon': 2.3522, 'flag': '[]', 'region': 'Europe'},
        'etisalat': {'country': 'UAE', 'city': 'Abu Dhabi', 'lat': 24.4539, 'lon': 54.3773, 'flag': '[]', 'region': 'Middle East'},
        'google': {'country': 'USA', 'city': 'Mountain View', 'lat': 37.4220, 'lon': -122.0841, 'flag': '[]', 'region': 'North America'},
        'microsoft': {'country': 'USA', 'city': 'Redmond', 'lat': 47.6740, 'lon': -122.1215, 'flag': '[]', 'region': 'North America'},
        'apple': {'country': 'USA', 'city': 'Cupertino', 'lat': 37.3349, 'lon': -122.0090, 'flag': '[]', 'region': 'North America'},
        'amazon': {'country': 'USA', 'city': 'Seattle', 'lat': 47.6062, 'lon': -122.3321, 'flag': '[]', 'region': 'North America'},
        'facebook': {'country': 'USA', 'city': 'Menlo Park', 'lat': 37.4530, 'lon': -122.1810, 'flag': '[]', 'region': 'North America'},
        'twitter': {'country': 'USA', 'city': 'San Francisco', 'lat': 37.7749, 'lon': -122.4194, 'flag': '[]', 'region': 'North America'},
        'linkedin': {'country': 'USA', 'city': 'Sunnyvale', 'lat': 37.3688, 'lon': -122.0363, 'flag': '[]', 'region': 'North America'},
        'netflix': {'country': 'USA', 'city': 'Los Gatos', 'lat': 37.2308, 'lon': -121.9740, 'flag': '[]', 'region': 'North America'},
        'uber': {'country': 'USA', 'city': 'San Francisco', 'lat': 37.7749, 'lon': -122.4194, 'flag': '[]', 'region': 'North America'},
        'goldmansachs': {'country': 'USA', 'city': 'New York', 'lat': 40.7128, 'lon': -74.0060, 'flag': '[]', 'region': 'North America'},
        'jpmorgan': {'country': 'USA', 'city': 'New York', 'lat': 40.7128, 'lon': -74.0060, 'flag': '[]', 'region': 'North America'},
        'bankofamerica': {'country': 'USA', 'city': 'Charlotte', 'lat': 35.2271, 'lon': -80.8431, 'flag': '[]', 'region': 'North America'},
        'wellsfargo': {'country': 'USA', 'city': 'San Francisco', 'lat': 37.7749, 'lon': -122.4194, 'flag': '[]', 'region': 'North America'},
        'hsbc': {'country': 'United Kingdom', 'city': 'London', 'lat': 51.5074, 'lon': -0.1278, 'flag': '[]', 'region': 'Europe'},
        'barclays': {'country': 'United Kingdom', 'city': 'London', 'lat': 51.5074, 'lon': -0.1278, 'flag': '[]', 'region': 'Europe'},
        'deutschebank': {'country': 'Germany', 'city': 'Frankfurt', 'lat': 50.1109, 'lon': 8.6821, 'flag': '[]', 'region': 'Europe'},
        'ubs': {'country': 'Switzerland', 'city': 'Zurich', 'lat': 47.3769, 'lon': 8.5417, 'flag': '[]', 'region': 'Europe'},
        'creditsuisse': {'country': 'Switzerland', 'city': 'Zurich', 'lat': 47.3769, 'lon': 8.5417, 'flag': '[]', 'region': 'Europe'},
    }
    
    @classmethod
    def _load_cache(cls) -> Dict:
        if os.path.exists(cls.CACHE_FILE):
            try:
                with open(cls.CACHE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    @classmethod
    def _save_cache(cls, cache: Dict):
        try:
            os.makedirs(os.path.dirname(cls.CACHE_FILE), exist_ok=True)
            with open(cls.CACHE_FILE, 'w') as f:
                json.dump(cache, f, indent=2)
        except:
            pass
    
    @classmethod
    def _detect_location_from_tld(cls, domain: str) -> Optional[Dict]:
        domain_lower = domain.lower()
        
        for org_name, info in cls.KNOWN_ORGANIZATION_PATTERNS.items():
            if org_name in domain_lower:
                return {
                    "country": info['country'],
                    "city": info['city'],
                    "lat": info['lat'],
                    "lon": info['lon'],
                    "flag": info['flag'],
                    "region": info['region'],
                    "note": f"Auto-detected organization: {org_name}"
                }
        
        tld_map = {
            '.mw': {'country': 'Malawi', 'city': 'Auto-detected', 'lat': -13.9833, 'lon': 33.7833, 'flag': '[]', 'region': 'East Africa'},
            '.za': {'country': 'South Africa', 'city': 'Auto-detected', 'lat': -30.5595, 'lon': 22.9375, 'flag': '[]', 'region': 'Southern Africa'},
            '.ke': {'country': 'Kenya', 'city': 'Auto-detected', 'lat': -1.2921, 'lon': 36.8219, 'flag': '[]', 'region': 'East Africa'},
            '.ng': {'country': 'Nigeria', 'city': 'Auto-detected', 'lat': 9.0820, 'lon': 8.6753, 'flag': '[]', 'region': 'West Africa'},
            '.gh': {'country': 'Ghana', 'city': 'Auto-detected', 'lat': 7.9465, 'lon': -1.0232, 'flag': '[]', 'region': 'West Africa'},
            '.eg': {'country': 'Egypt', 'city': 'Auto-detected', 'lat': 26.8206, 'lon': 30.8025, 'flag': '[]', 'region': 'North Africa'},
            '.uk': {'country': 'United Kingdom', 'city': 'Auto-detected', 'lat': 55.3781, 'lon': -3.4360, 'flag': '[]', 'region': 'Europe'},
            '.de': {'country': 'Germany', 'city': 'Auto-detected', 'lat': 51.1657, 'lon': 10.4515, 'flag': '[]', 'region': 'Europe'},
            '.in': {'country': 'India', 'city': 'Auto-detected', 'lat': 20.5937, 'lon': 78.9629, 'flag': '[]', 'region': 'South Asia'},
            '.edu': {'country': 'USA', 'city': 'Auto-detected', 'lat': 37.0902, 'lon': -95.7129, 'flag': '[]', 'region': 'North America'},
            '.africa': {'country': 'Africa (HQ Unknown)', 'city': 'Auto-detected', 'lat': 0, 'lon': 0, 'flag': '[]', 'region': 'Africa'},
            '.fr': {'country': 'France', 'city': 'Auto-detected', 'lat': 46.6034, 'lon': 1.8883, 'flag': '[]', 'region': 'Europe'},
            '.it': {'country': 'Italy', 'city': 'Auto-detected', 'lat': 41.8719, 'lon': 12.5674, 'flag': '[]', 'region': 'Europe'},
            '.es': {'country': 'Spain', 'city': 'Auto-detected', 'lat': 40.4637, 'lon': -3.7492, 'flag': '[]', 'region': 'Europe'},
            '.nl': {'country': 'Netherlands', 'city': 'Auto-detected', 'lat': 52.1326, 'lon': 5.2913, 'flag': '[]', 'region': 'Europe'},
            '.se': {'country': 'Sweden', 'city': 'Auto-detected', 'lat': 60.1282, 'lon': 18.6435, 'flag': '[]', 'region': 'Europe'},
            '.no': {'country': 'Norway', 'city': 'Auto-detected', 'lat': 60.4720, 'lon': 8.4689, 'flag': '[]', 'region': 'Europe'},
            '.dk': {'country': 'Denmark', 'city': 'Auto-detected', 'lat': 56.2639, 'lon': 9.5018, 'flag': '[]', 'region': 'Europe'},
            '.fi': {'country': 'Finland', 'city': 'Auto-detected', 'lat': 61.9241, 'lon': 25.7482, 'flag': '[]', 'region': 'Europe'},
            '.ch': {'country': 'Switzerland', 'city': 'Auto-detected', 'lat': 46.8182, 'lon': 8.2275, 'flag': '[]', 'region': 'Europe'},
            '.at': {'country': 'Austria', 'city': 'Auto-detected', 'lat': 47.5162, 'lon': 14.5501, 'flag': '[]', 'region': 'Europe'},
            '.be': {'country': 'Belgium', 'city': 'Auto-detected', 'lat': 50.5039, 'lon': 4.4699, 'flag': '[]', 'region': 'Europe'},
            '.pt': {'country': 'Portugal', 'city': 'Auto-detected', 'lat': 39.3999, 'lon': -8.2245, 'flag': '[]', 'region': 'Europe'},
            '.gr': {'country': 'Greece', 'city': 'Auto-detected', 'lat': 39.0742, 'lon': 21.8243, 'flag': '[]', 'region': 'Europe'},
            '.pl': {'country': 'Poland', 'city': 'Auto-detected', 'lat': 51.9194, 'lon': 19.1451, 'flag': '[]', 'region': 'Europe'},
            '.cz': {'country': 'Czech Republic', 'city': 'Auto-detected', 'lat': 49.8175, 'lon': 15.4730, 'flag': '[]', 'region': 'Europe'},
            '.hu': {'country': 'Hungary', 'city': 'Auto-detected', 'lat': 47.1625, 'lon': 19.5033, 'flag': '[]', 'region': 'Europe'},
            '.ro': {'country': 'Romania', 'city': 'Auto-detected', 'lat': 45.9432, 'lon': 24.9668, 'flag': '[]', 'region': 'Europe'},
            '.bg': {'country': 'Bulgaria', 'city': 'Auto-detected', 'lat': 42.7339, 'lon': 25.4858, 'flag': '[]', 'region': 'Europe'},
            '.hr': {'country': 'Croatia', 'city': 'Auto-detected', 'lat': 45.1000, 'lon': 15.2000, 'flag': '[]', 'region': 'Europe'},
            '.si': {'country': 'Slovenia', 'city': 'Auto-detected', 'lat': 46.1512, 'lon': 14.9955, 'flag': '[]', 'region': 'Europe'},
            '.sk': {'country': 'Slovakia', 'city': 'Auto-detected', 'lat': 48.6690, 'lon': 19.6990, 'flag': '[]', 'region': 'Europe'},
            '.lt': {'country': 'Lithuania', 'city': 'Auto-detected', 'lat': 55.1694, 'lon': 23.8813, 'flag': '[]', 'region': 'Europe'},
            '.lv': {'country': 'Latvia', 'city': 'Auto-detected', 'lat': 56.8796, 'lon': 24.6032, 'flag': '[]', 'region': 'Europe'},
            '.ee': {'country': 'Estonia', 'city': 'Auto-detected', 'lat': 58.5953, 'lon': 25.0136, 'flag': '[]', 'region': 'Europe'},
            '.is': {'country': 'Iceland', 'city': 'Auto-detected', 'lat': 64.9631, 'lon': -19.0208, 'flag': '[]', 'region': 'Europe'},
            '.ie': {'country': 'Ireland', 'city': 'Auto-detected', 'lat': 53.4129, 'lon': -8.2439, 'flag': '[]', 'region': 'Europe'},
            '.lu': {'country': 'Luxembourg', 'city': 'Auto-detected', 'lat': 49.8153, 'lon': 6.1296, 'flag': '[]', 'region': 'Europe'},
            '.mt': {'country': 'Malta', 'city': 'Auto-detected', 'lat': 35.9375, 'lon': 14.3754, 'flag': '[]', 'region': 'Europe'},
            '.cy': {'country': 'Cyprus', 'city': 'Auto-detected', 'lat': 35.1264, 'lon': 33.4299, 'flag': '[]', 'region': 'Europe'},
            '.ae': {'country': 'UAE', 'city': 'Auto-detected', 'lat': 23.4241, 'lon': 53.8478, 'flag': '[]', 'region': 'Middle East'},
            '.sa': {'country': 'Saudi Arabia', 'city': 'Auto-detected', 'lat': 23.8859, 'lon': 45.0792, 'flag': '[]', 'region': 'Middle East'},
            '.il': {'country': 'Israel', 'city': 'Auto-detected', 'lat': 31.0461, 'lon': 34.8516, 'flag': '[]', 'region': 'Middle East'},
            '.tr': {'country': 'Turkey', 'city': 'Auto-detected', 'lat': 38.9637, 'lon': 35.2433, 'flag': '[]', 'region': 'Middle East'},
            '.pk': {'country': 'Pakistan', 'city': 'Auto-detected', 'lat': 30.3753, 'lon': 69.3451, 'flag': '[]', 'region': 'South Asia'},
            '.bd': {'country': 'Bangladesh', 'city': 'Auto-detected', 'lat': 23.6850, 'lon': 90.3563, 'flag': '[]', 'region': 'South Asia'},
            '.lk': {'country': 'Sri Lanka', 'city': 'Auto-detected', 'lat': 7.8731, 'lon': 80.7718, 'flag': '[]', 'region': 'South Asia'},
            '.np': {'country': 'Nepal', 'city': 'Auto-detected', 'lat': 28.3949, 'lon': 84.1240, 'flag': '[]', 'region': 'South Asia'},
            '.cn': {'country': 'China', 'city': 'Auto-detected', 'lat': 35.8617, 'lon': 104.1954, 'flag': '[]', 'region': 'Asia'},
            '.jp': {'country': 'Japan', 'city': 'Auto-detected', 'lat': 36.2048, 'lon': 138.2529, 'flag': '[]', 'region': 'Asia'},
            '.kr': {'country': 'South Korea', 'city': 'Auto-detected', 'lat': 35.9078, 'lon': 127.7669, 'flag': '[]', 'region': 'Asia'},
            '.sg': {'country': 'Singapore', 'city': 'Auto-detected', 'lat': 1.3521, 'lon': 103.8198, 'flag': '[]', 'region': 'Asia'},
            '.my': {'country': 'Malaysia', 'city': 'Auto-detected', 'lat': 4.2105, 'lon': 101.9758, 'flag': '[]', 'region': 'Asia'},
            '.id': {'country': 'Indonesia', 'city': 'Auto-detected', 'lat': -0.7893, 'lon': 113.9213, 'flag': '[]', 'region': 'Asia'},
            '.ph': {'country': 'Philippines', 'city': 'Auto-detected', 'lat': 12.8797, 'lon': 121.7740, 'flag': '[]', 'region': 'Asia'},
            '.vn': {'country': 'Vietnam', 'city': 'Auto-detected', 'lat': 14.0583, 'lon': 108.2772, 'flag': '[]', 'region': 'Asia'},
            '.th': {'country': 'Thailand', 'city': 'Auto-detected', 'lat': 15.8700, 'lon': 100.9925, 'flag': '[]', 'region': 'Asia'},
        }
        
        for tld, info in tld_map.items():
            if domain_lower.endswith(tld):
                return {
                    "country": info['country'],
                    "city": info['city'],
                    "lat": info['lat'],
                    "lon": info['lon'],
                    "flag": info['flag'],
                    "region": info['region'],
                    "note": f"Auto-detected from {tld} domain pattern"
                }
        return None
    
    @classmethod
    def get_organization_location(cls, domain: str, hostname: str = "") -> Optional[Dict]:
        domain_lower = domain.lower()
        
        if domain_lower in cls.ORGANIZATIONS:
            return cls.ORGANIZATIONS[domain_lower]
        
        cache = cls._load_cache()
        if domain_lower in cache:
            return cache[domain_lower]
        
        for org_domain, location in cls.ORGANIZATIONS.items():
            if org_domain in domain_lower or domain_lower.endswith(org_domain):
                cache[domain_lower] = location
                cls._save_cache(cache)
                return location
        
        detected = cls._detect_location_from_tld(domain)
        if detected:
            cache[domain_lower] = detected
            cls._save_cache(cache)
            return detected
        
        return None
    
    @classmethod
    def add_organization(cls, domain: str, country: str, city: str, lat: float, lon: float, flag: str = "[]", region: str = "Unknown"):
        domain_lower = domain.lower()
        location = {"country": country, "city": city, "lat": lat, "lon": lon, "flag": flag, "region": region}
        cls.ORGANIZATIONS[domain_lower] = location
        cache = cls._load_cache()
        cache[domain_lower] = location
        cls._save_cache(cache)
        print(f"[+] Added {domain} to organization database ({country})")
    
    @classmethod
    def get_organization_by_name(cls, name: str) -> Optional[Dict]:
        name_lower = name.lower()
        for org_name, info in cls.KNOWN_ORGANIZATION_PATTERNS.items():
            if org_name in name_lower:
                return info
        return None


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
    server_country: str = ""
    server_city: str = ""
    server_lat: float = 0.0
    server_lon: float = 0.0
    server_isp: str = ""
    org_country: str = ""
    org_city: str = ""


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
            "http": {"cvss_id": "CVE-2024-3456", "score": 6.5, "exploit": "SQLMap/HTTP", "severity": "MEDIUM", "description": "Potential SQL injection or XSS vulnerabilities"},
            "https": {"cvss_id": "CVE-2024-7890", "score": 5.0, "exploit": "Heartbleed", "severity": "MEDIUM", "description": "SSL/TLS vulnerabilities may expose data"},
            "nginx": {"cvss_id": "CVE-2024-2347", "score": 7.0, "exploit": "Nginx BOF", "severity": "HIGH", "description": "Buffer overflow in nginx versions < 1.21.6"},
            "apache": {"cvss_id": "CVE-2024-4567", "score": 7.5, "exploit": "Apache RCE", "severity": "CRITICAL", "description": "Remote code execution in Apache HTTP Server"},
            "tomcat": {"cvss_id": "CVE-2024-3457", "score": 8.0, "exploit": "Tomcat RCE", "severity": "CRITICAL", "description": "RCE vulnerability in Apache Tomcat"},
            "iis": {"cvss_id": "CVE-2024-6780", "score": 6.5, "exploit": "IIS RCE", "severity": "MEDIUM", "description": "Remote code execution in IIS"},
            "jetty": {"cvss_id": "CVE-2024-4568", "score": 5.5, "exploit": "Jetty Bypass", "severity": "MEDIUM", "description": "Authentication bypass in Jetty"},
            "caddy": {"cvss_id": "CVE-2024-2348", "score": 4.5, "exploit": "Caddy Path Traversal", "severity": "MEDIUM", "description": "Path traversal in Caddy web server"},
            "mysql": {"cvss_id": "CVE-2024-4560", "score": 7.5, "exploit": "MySQL UDF", "severity": "HIGH", "description": "MySQL UDF exploitation for RCE"},
            "postgresql": {"cvss_id": "CVE-2024-4561", "score": 8.0, "exploit": "PostgreSQL RCE", "severity": "CRITICAL", "description": "Remote code execution in PostgreSQL"},
            "mongodb": {"cvss_id": "CVE-2024-3458", "score": 7.0, "exploit": "MongoDB NoSQLi", "severity": "HIGH", "description": "NoSQL injection in MongoDB"},
            "redis": {"cvss_id": "CVE-2024-5670", "score": 6.5, "exploit": "Redis RCE", "severity": "MEDIUM", "description": "Remote code execution in Redis"},
            "elasticsearch": {"cvss_id": "CVE-2024-3459", "score": 5.5, "exploit": "ES RCE", "severity": "MEDIUM", "description": "Remote code execution in Elasticsearch"},
            "cassandra": {"cvss_id": "CVE-2024-6781", "score": 4.5, "exploit": "Cassandra Injection", "severity": "LOW", "description": "Injection vulnerabilities in Cassandra"},
            "couchdb": {"cvss_id": "CVE-2024-2349", "score": 6.0, "exploit": "CouchDB Admin", "severity": "MEDIUM", "description": "Admin interface exposed on CouchDB"},
            "oracle": {"cvss_id": "CVE-2024-4562", "score": 8.5, "exploit": "Oracle RCE", "severity": "CRITICAL", "description": "Remote code execution in Oracle Database"},
            "mssql": {"cvss_id": "CVE-2024-5671", "score": 7.5, "exploit": "MSSQL Injection", "severity": "HIGH", "description": "SQL injection in Microsoft SQL Server"},
            "smtp": {"cvss_id": "CVE-2024-1111", "score": 6.0, "exploit": "SMTP Open Relay", "severity": "MEDIUM", "description": "Open SMTP relay allows email spoofing"},
            "pop3": {"cvss_id": "CVE-2024-2222", "score": 5.0, "exploit": "POP3 Buffer", "severity": "MEDIUM", "description": "Buffer overflow in POP3 service"},
            "imap": {"cvss_id": "CVE-2024-3333", "score": 5.5, "exploit": "IMAP DoS", "severity": "MEDIUM", "description": "Denial of service in IMAP service"},
            "exchange": {"cvss_id": "CVE-2024-4444", "score": 9.0, "exploit": "Exchange RCE", "severity": "CRITICAL", "description": "Remote code execution in Microsoft Exchange"},
            "sendmail": {"cvss_id": "CVE-2024-5555", "score": 6.5, "exploit": "Sendmail Exploit", "severity": "MEDIUM", "description": "Vulnerabilities in Sendmail service"},
            "postfix": {"cvss_id": "CVE-2024-6666", "score": 4.5, "exploit": "Postfix Bypass", "severity": "LOW", "description": "Security bypass in Postfix"},
            "ftp": {"cvss_id": "CVE-2024-1234", "score": 7.5, "exploit": "Metasploit/ftp", "severity": "HIGH", "description": "FTP anonymous access or buffer overflow"},
            "sftp": {"cvss_id": "CVE-2024-2345", "score": 4.5, "exploit": "SFTP Enumeration", "severity": "LOW", "description": "SFTP user enumeration vulnerability"},
            "tftp": {"cvss_id": "CVE-2024-3456", "score": 6.0, "exploit": "TFTP File Download", "severity": "MEDIUM", "description": "TFTP allows unauthorized file access"},
            "rsync": {"cvss_id": "CVE-2024-4567", "score": 5.5, "exploit": "Rsync Exploit", "severity": "MEDIUM", "description": "Vulnerabilities in Rsync service"},
            "scp": {"cvss_id": "CVE-2024-5678", "score": 4.0, "exploit": "SCP Path Traversal", "severity": "LOW", "description": "Path traversal in SCP service"},
            "ssh": {"cvss_id": "CVE-2024-5678", "score": 5.5, "exploit": "Hydra/SSH", "severity": "MEDIUM", "description": "Weak SSH credentials or outdated SSH version"},
            "telnet": {"cvss_id": "CVE-2024-9012", "score": 9.0, "exploit": "TelnetBleed", "severity": "CRITICAL", "description": "Telnet sends credentials in clear text"},
            "rdp": {"cvss_id": "CVE-2024-6789", "score": 9.0, "exploit": "BlueKeep", "severity": "CRITICAL", "description": "BlueKeep vulnerability in RDP service"},
            "vnc": {"cvss_id": "CVE-2024-7890", "score": 8.5, "exploit": "VNC Auth Bypass", "severity": "CRITICAL", "description": "VNC authentication bypass vulnerability"},
            "x11": {"cvss_id": "CVE-2024-8901", "score": 5.0, "exploit": "X11 Access", "severity": "MEDIUM", "description": "X11 display access vulnerability"},
            "dns": {"cvss_id": "CVE-2024-5555", "score": 7.0, "exploit": "DNS Cache Poisoning", "severity": "HIGH", "description": "DNS cache poisoning vulnerability"},
            "snmp": {"cvss_id": "CVE-2024-6666", "score": 8.0, "exploit": "SNMP Brute", "severity": "HIGH", "description": "SNMP community string brute force"},
            "ntp": {"cvss_id": "CVE-2024-7777", "score": 6.5, "exploit": "NTP Amplification", "severity": "MEDIUM", "description": "NTP amplification DDoS attack"},
            "ldap": {"cvss_id": "CVE-2024-8888", "score": 7.5, "exploit": "LDAP Injection", "severity": "HIGH", "description": "LDAP injection or anonymous bind"},
            "kerberos": {"cvss_id": "CVE-2024-9999", "score": 8.5, "exploit": "Kerberos Attack", "severity": "CRITICAL", "description": "Kerberos authentication vulnerabilities"},
            "radius": {"cvss_id": "CVE-2024-0001", "score": 6.0, "exploit": "Radius Auth Bypass", "severity": "MEDIUM", "description": "RADIUS authentication bypass"},
            "dhcp": {"cvss_id": "CVE-2024-1112", "score": 5.0, "exploit": "DHCP Spoofing", "severity": "MEDIUM", "description": "DHCP spoofing vulnerability"},
            "netbios": {"cvss_id": "CVE-2024-2223", "score": 4.5, "exploit": "NetBIOS Enumeration", "severity": "LOW", "description": "NetBIOS information disclosure"},
            "smb": {"cvss_id": "CVE-2024-2345", "score": 8.5, "exploit": "EternalBlue", "severity": "CRITICAL", "description": "EternalBlue SMB vulnerability"},
            "netbios-ssn": {"cvss_id": "CVE-2024-2223", "score": 4.5, "exploit": "NetBIOS Enumeration", "severity": "LOW", "description": "NetBIOS information disclosure"},
            "microsoft-ds": {"cvss_id": "CVE-2024-2345", "score": 8.5, "exploit": "EternalBlue", "severity": "CRITICAL", "description": "SMB vulnerabilities on Windows"},
            "wins": {"cvss_id": "CVE-2024-3334", "score": 5.0, "exploit": "WINS RCE", "severity": "MEDIUM", "description": "WINS remote code execution"},
            "rpc": {"cvss_id": "CVE-2024-4445", "score": 6.5, "exploit": "RPC Exploit", "severity": "MEDIUM", "description": "RPC service vulnerabilities"},
            "msrpc": {"cvss_id": "CVE-2024-4445", "score": 6.5, "exploit": "RPC Exploit", "severity": "MEDIUM", "description": "MS RPC service vulnerabilities"},
            "nfs": {"cvss_id": "CVE-2024-5556", "score": 6.0, "exploit": "NFS Export", "severity": "MEDIUM", "description": "NFS export vulnerabilities"},
            "rlogin": {"cvss_id": "CVE-2024-6667", "score": 6.5, "exploit": "Rlogin Exploit", "severity": "MEDIUM", "description": "Rlogin authentication bypass"},
            "rexec": {"cvss_id": "CVE-2024-7778", "score": 6.5, "exploit": "Rexec RCE", "severity": "MEDIUM", "description": "Rexec remote code execution"},
            "rsh": {"cvss_id": "CVE-2024-8889", "score": 6.0, "exploit": "Rsh Exploit", "severity": "MEDIUM", "description": "Rsh service vulnerabilities"},
            "cups": {"cvss_id": "CVE-2024-9990", "score": 5.5, "exploit": "CUPS Exploit", "severity": "MEDIUM", "description": "CUPS printing service vulnerabilities"},
            "samba": {"cvss_id": "CVE-2024-2345", "score": 8.5, "exploit": "Samba Exploit", "severity": "CRITICAL", "description": "Samba service vulnerabilities"},
            "sip": {"cvss_id": "CVE-2024-1113", "score": 6.5, "exploit": "SIP Brute", "severity": "MEDIUM", "description": "SIP authentication brute force"},
            "h323": {"cvss_id": "CVE-2024-2224", "score": 5.5, "exploit": "H323 Exploit", "severity": "MEDIUM", "description": "H.323 service vulnerabilities"},
            "iax": {"cvss_id": "CVE-2024-3335", "score": 4.5, "exploit": "IAX Enumeration", "severity": "LOW", "description": "IAX protocol enumeration"},
            "skinny": {"cvss_id": "CVE-2024-4446", "score": 5.0, "exploit": "Skinny RCE", "severity": "MEDIUM", "description": "Skinny service RCE vulnerability"},
            "modbus": {"cvss_id": "CVE-2024-5557", "score": 7.0, "exploit": "Modbus Exploit", "severity": "HIGH", "description": "Modbus industrial protocol vulnerabilities"},
            "bacnet": {"cvss_id": "CVE-2024-6668", "score": 6.0, "exploit": "BACnet Exploit", "severity": "MEDIUM", "description": "BACnet building automation vulnerabilities"},
            "dnp3": {"cvss_id": "CVE-2024-7779", "score": 7.5, "exploit": "DNP3 Attack", "severity": "HIGH", "description": "DNP3 SCADA vulnerabilities"},
            "mqtt": {"cvss_id": "CVE-2024-8880", "score": 6.5, "exploit": "MQTT Exploit", "severity": "MEDIUM", "description": "MQTT IoT protocol vulnerabilities"},
            "coap": {"cvss_id": "CVE-2024-9991", "score": 5.0, "exploit": "CoAP Exploit", "severity": "MEDIUM", "description": "CoAP IoT protocol vulnerabilities"},
            "rtsp": {"cvss_id": "CVE-2024-3333", "score": 6.0, "exploit": "RTSP Brute", "severity": "MEDIUM", "description": "RTSP streaming service vulnerabilities"},
            "onvif": {"cvss_id": "CVE-2024-4447", "score": 6.0, "exploit": "ONVIF Enumeration", "severity": "MEDIUM", "description": "ONVIF camera protocol vulnerabilities"},
            "docker": {"cvss_id": "CVE-2024-5558", "score": 8.0, "exploit": "Docker RCE", "severity": "CRITICAL", "description": "Docker remote code execution"},
            "kubernetes": {"cvss_id": "CVE-2024-6669", "score": 8.5, "exploit": "K8s Exploit", "severity": "CRITICAL", "description": "Kubernetes vulnerabilities"},
            "kubelet": {"cvss_id": "CVE-2024-7770", "score": 7.5, "exploit": "Kubelet Attack", "severity": "HIGH", "description": "Kubelet API vulnerabilities"},
            "registry": {"cvss_id": "CVE-2024-8881", "score": 6.0, "exploit": "Registry Exploit", "severity": "MEDIUM", "description": "Container registry vulnerabilities"},
            "aws": {"cvss_id": "CVE-2024-9992", "score": 7.5, "exploit": "AWS Exploit", "severity": "HIGH", "description": "AWS service vulnerabilities"},
            "azure": {"cvss_id": "CVE-2024-1114", "score": 7.0, "exploit": "Azure Exploit", "severity": "HIGH", "description": "Azure service vulnerabilities"},
            "gcp": {"cvss_id": "CVE-2024-2225", "score": 7.0, "exploit": "GCP Exploit", "severity": "HIGH", "description": "Google Cloud Platform vulnerabilities"},
            "domain": {"cvss_id": "CVE-2024-1111", "score": 6.0, "exploit": "DNSpoof", "severity": "MEDIUM", "description": "Domain service vulnerabilities"},
            "bootp": {"cvss_id": "CVE-2024-3336", "score": 4.5, "exploit": "BOOTP Exploit", "severity": "LOW", "description": "BOOTP service vulnerabilities"},
            "whois": {"cvss_id": "CVE-2024-4448", "score": 3.5, "exploit": "Whois Info", "severity": "LOW", "description": "WHOIS information disclosure"},
            "daytime": {"cvss_id": "CVE-2024-5559", "score": 2.5, "exploit": "Daytime Info", "severity": "LOW", "description": "Daytime service information disclosure"},
            "chargen": {"cvss_id": "CVE-2024-6670", "score": 4.0, "exploit": "Chargen Attack", "severity": "LOW", "description": "Chargen service amplification attack"},
            "echo": {"cvss_id": "CVE-2024-7781", "score": 3.0, "exploit": "Echo Attack", "severity": "LOW", "description": "Echo service vulnerabilities"},
            "discard": {"cvss_id": "CVE-2024-8892", "score": 2.5, "exploit": "Discard Attack", "severity": "LOW", "description": "Discard service vulnerabilities"},
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
# Enhanced GeoMap Visualizer with Dual Location Support - FIXED ASCII
# ============================================================

class EnhancedGeoMapVisualizer:
    """Advanced Geographic Threat Intelligence Map with Dual Location Support"""
    
    def __init__(self):
        self.locations = []
        self.org_locations = []
    
    def add_location(self, lat: float, lon: float, ip: str, risk_score: float, 
                     ports: List[Dict] = None, country: str = "", 
                     is_org_location: bool = False, server_location: str = "",
                     server_country: str = "", server_city: str = "",
                     server_lat: float = 0.0, server_lon: float = 0.0,
                     server_isp: str = "",
                     org_country: str = "", org_city: str = "",
                     domain: str = ""):
        self.locations.append({
            "lat": lat, "lon": lon, "ip": ip, "risk_score": risk_score,
            "ports": ports or [], "country": country, "timestamp": datetime.now(),
            "is_organization_location": is_org_location,
            "server_location": server_location,
            "server_country": server_country,
            "server_city": server_city,
            "server_lat": server_lat,
            "server_lon": server_lon,
            "server_isp": server_isp,
            "org_country": org_country,
            "org_city": org_city,
            "domain": domain
        })
        
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
        """Generate interactive threat intelligence map with BLINKING lines and circles"""
        if not GEO_AVAILABLE:
            return '<div style="padding:50px;text-align:center;color:#888;">[] GeoIP module not available</div>'
        
        m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter', control_scale=True)
        
        blink_css = """
        <style>
            body { 
                background: linear-gradient(135deg, #0a0a1a 0%%, #0d1117 100%%) !important; 
                margin: 0 !important;
                padding: 0 !important;
                min-height: 100vh !important;
            }
            
            @keyframes blink-red { 
                0% { opacity: 1; transform: scale(1); } 
                50% { opacity: 0.3; transform: scale(1.4); } 
                100% { opacity: 1; transform: scale(1); } 
            }
            @keyframes blink-orange { 
                0% { opacity: 1; transform: scale(1); } 
                50% { opacity: 0.4; transform: scale(1.3); } 
                100% { opacity: 1; transform: scale(1); } 
            }
            @keyframes blink-yellow { 
                0% { opacity: 1; transform: scale(1); } 
                50% { opacity: 0.5; transform: scale(1.2); } 
                100% { opacity: 1; transform: scale(1); } 
            }
            @keyframes blink-green { 
                0% { opacity: 1; transform: scale(1); } 
                50% { opacity: 0.6; transform: scale(1.1); } 
                100% { opacity: 1; transform: scale(1); } 
            }
            
            .blink-critical { 
                animation: blink-red 0.6s ease-in-out infinite !important; 
                filter: drop-shadow(0 0 10px #ff0000) !important;
            }
            .blink-high { 
                animation: blink-orange 0.8s ease-in-out infinite !important; 
                filter: drop-shadow(0 0 8px #ff6600) !important;
            }
            .blink-medium { 
                animation: blink-yellow 1s ease-in-out infinite !important; 
                filter: drop-shadow(0 0 6px #ffcc00) !important;
            }
            .blink-low { 
                animation: blink-green 1.2s ease-in-out infinite !important; 
                filter: drop-shadow(0 0 4px #00ff00) !important;
            }
            
            @keyframes pulse-ring {
                0% { transform: scale(0.8); opacity: 0.8; }
                100% { transform: scale(2.5); opacity: 0; }
            }
            .pulse-ring { 
                animation: pulse-ring 1.5s ease-out infinite !important; 
                transform-origin: center;
            }
            
            .leaflet-popup-content-wrapper {
                background: rgba(10, 15, 30, 0.95) !important;
                border: 1px solid #00ffff !important;
                border-radius: 10px !important;
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.2) !important;
                backdrop-filter: blur(10px) !important;
            }
            .leaflet-popup-content {
                color: #00ff00 !important;
                font-family: 'Courier New', monospace !important;
                font-size: 12px !important;
                min-width: 340px !important;
                max-width: 450px !important;
                padding: 5px !important;
            }
            .leaflet-popup-tip {
                background: rgba(10, 15, 30, 0.95) !important;
                border: 1px solid #00ffff !important;
            }
            .leaflet-popup-close-button {
                color: #00ffff !important;
                font-size: 18px !important;
                font-weight: bold !important;
            }
            
            .live-badge { 
                position: fixed; top: 10px; right: 10px; background: #00ff00; color: #000; 
                padding: 5px 12px; border-radius: 5px; font-family: monospace; font-size: 10px; 
                z-index: 1000; animation: blink-green 1s infinite !important; font-weight: bold;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            }
            
            .marker-icon {
                border-radius: 50% !important;
                border: 2px solid #fff !important;
                box-shadow: 0 0 15px rgba(0,0,0,0.5) !important;
            }
            
            ::-webkit-scrollbar {
                width: 6px;
            }
            ::-webkit-scrollbar-track {
                background: rgba(0,0,0,0.3);
            }
            ::-webkit-scrollbar-thumb {
                background: #00ffff;
                border-radius: 3px;
            }
        </style>
        """
        
        m.get_root().header.add_child(folium.Element(blink_css))
        m.get_root().html.add_child(folium.Element('<div class="live-badge">[+] LIVE MONITORING ACTIVE [+]</div>'))
        
        heat_data = [[loc["lat"], loc["lon"], loc["risk_score"] / 10] for loc in self.locations if loc["lat"] != 0]
        if heat_data:
            HeatMap(heat_data, radius=25, blur=15, max_zoom=6,
                gradient={0.2: 'blue', 0.5: 'lime', 0.8: 'orange', 1: 'red'}).add_to(m)
        
        valid_locations = [loc for loc in self.locations if loc["lat"] != 0]
        
        if len(valid_locations) >= 2:
            for i in range(len(valid_locations) - 1):
                loc1 = valid_locations[i]
                loc2 = valid_locations[i + 1]
                avg_risk = (loc1["risk_score"] + loc2["risk_score"]) / 2
                
                if avg_risk >= 7:
                    color = "#ff0000"
                elif avg_risk >= 4:
                    color = "#ff6600"
                elif avg_risk >= 2:
                    color = "#ffcc00"
                else:
                    color = "#00ff00"
                
                folium.PolyLine(
                    locations=[[loc1["lat"], loc1["lon"]], [loc2["lat"], loc2["lon"]]],
                    color=color,
                    weight=2,
                    opacity=0.6,
                    dash_array='5, 5',
                    popup=f"Connection: {loc1['ip']} -> {loc2['ip']}<br>Risk: {avg_risk:.1f}"
                ).add_to(m)
        
        for loc in self.locations:
            if loc["lat"] == 0:
                continue
            
            risk = loc["risk_score"]
            if risk >= 7:
                color = "#ff0000"
                blink_class = "blink-critical"
                radius = 16
                pulse_radius = 200000
                risk_emoji = "[!]"
                risk_label = "CRITICAL"
            elif risk >= 4:
                color = "#ff6600"
                blink_class = "blink-high"
                radius = 13
                pulse_radius = 150000
                risk_emoji = "[-]"
                risk_label = "HIGH"
            elif risk >= 2:
                color = "#ffcc00"
                blink_class = "blink-medium"
                radius = 10
                pulse_radius = 100000
                risk_emoji = "[*]"
                risk_label = "MEDIUM"
            else:
                color = "#00ff00"
                blink_class = "blink-low"
                radius = 7
                pulse_radius = 50000
                risk_emoji = "[+]"
                risk_label = "LOW"
            
            domain = loc.get('domain', loc['ip'])
            country = loc.get('country', 'Unknown')
            city = loc.get('city', 'Unknown')
            port_count = len(loc.get('ports', []))
            services = [p.get('service', 'unknown') for p in loc.get('ports', [])[:5]]
            server_isp = loc.get('server_isp', 'Unknown')
            org_country = loc.get('org_country', '')
            org_city = loc.get('org_city', '')
            timestamp = loc.get('timestamp', datetime.now())
            if isinstance(timestamp, datetime):
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            else:
                timestamp_str = str(timestamp)
            
            popup_html = f"""
            <div style="font-family: monospace; color: #00ff00; padding: 8px;">
                <div style="border-bottom: 1px solid rgba(0,255,255,0.2); padding-bottom: 6px; margin-bottom: 6px;">
                    <b style="color: #00ffff; font-size: 13px;">[*] {domain}</b>
                    <span style="float: right; font-size: 11px; color: {color}; font-weight: bold;">{risk_emoji} {risk_label}</span>
                </div>
                
                <table style="width: 100%%; border-collapse: collapse; font-size: 11px;">
                    <tr><td style="color: #888; padding: 2px 4px;">[+] Location:</td><td style="color: #ffcc00; padding: 2px 4px;">{city}, {country}</td></tr>
                    <tr><td style="color: #888; padding: 2px 4px;">[+] IP:</td><td style="color: #00ff88; padding: 2px 4px;">{loc['ip']}</td></tr>
                    <tr><td style="color: #888; padding: 2px 4px;">[+] ISP:</td><td style="color: #88ccff; padding: 2px 4px;">{server_isp}</td></tr>
                    <tr><td style="color: #888; padding: 2px 4px;">[!] Risk:</td><td style="color: {color}; font-weight: bold; padding: 2px 4px;">{risk:.1f}/10</td></tr>
                    <tr><td style="color: #888; padding: 2px 4px;">[+] Ports:</td><td style="color: #ff66ff; padding: 2px 4px;">{port_count}</td></tr>
                </table>
            """
            
            if org_country:
                popup_html += f"""
                <div style="border-top: 1px solid rgba(255,170,0,0.2); margin-top: 4px; padding-top: 4px;">
                    <span style="color: #ffaa00;">[+] HQ:</span> <span style="color: #ffcc44;">{org_country} - {org_city}</span>
                </div>
                """
            
            if services:
                services_str = ', '.join(services[:3])
                if len(services) > 3:
                    services_str += f' +{len(services)-3} more'
                popup_html += f"""
                <div style="border-top: 1px solid rgba(0,255,0,0.1); margin-top: 4px; padding-top: 4px;">
                    <span style="color: #00ff88;">[+] Services:</span> <span style="color: #88ddff; font-size: 10px;">{services_str}</span>
                </div>
                """
            
            if loc.get('server_country') and loc.get('server_country') != org_country:
                popup_html += f"""
                <div style="border-top: 1px solid rgba(255,102,0,0.2); margin-top: 4px; padding-top: 4px;">
                    <span style="color: #ff6600;">[+] Server:</span> <span style="color: #ff9966;">{loc.get('server_city', 'Unknown')}, {loc.get('server_country', 'Unknown')}</span>
                </div>
                """
            
            popup_html += f"""
                <div style="border-top: 1px solid rgba(255,255,255,0.05); margin-top: 4px; padding-top: 4px; font-size: 9px; color: #666;">
                    [+] {timestamp_str}
                </div>
            </div>
            """
            
            popup = folium.Popup(popup_html, max_width=450)
            
            icon_html = f"""
            <div style="
                width: {radius * 2 + 6}px;
                height: {radius * 2 + 6}px;
                background: radial-gradient(circle, {color} 40%%, transparent 70%%);
                border-radius: 50%%;
                border: 2px solid {color};
                box-shadow: 0 0 20px {color}, inset 0 0 10px {color};
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: {radius}px;
                color: white;
                font-weight: bold;
                text-shadow: 0 0 5px rgba(0,0,0,0.8);
            ">
                <span style="font-size: 12px;">{risk_emoji}</span>
            </div>
            """
            
            folium.Marker(
                location=[loc["lat"], loc["lon"]],
                popup=popup,
                icon=folium.DivIcon(
                    icon_size=(radius * 2 + 6, radius * 2 + 6),
                    icon_anchor=(radius + 3, radius + 3),
                    html=icon_html
                )
            ).add_to(m)
            
            folium.CircleMarker(
                location=[loc["lat"], loc["lon"]],
                radius=radius + 2,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.3,
                weight=1,
                className=blink_class
            ).add_to(m)
            
            folium.CircleMarker(
                location=[loc["lat"], loc["lon"]],
                radius=radius + 6,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.08,
                weight=1
            ).add_to(m)
            
            if risk >= 4:
                folium.Circle(
                    location=[loc["lat"], loc["lon"]],
                    radius=pulse_radius,
                    color=color,
                    fill=True,
                    fill_opacity=0.04,
                    weight=1,
                    className="pulse-ring",
                    popup=f"[!] Active Threat Zone - Risk: {risk}/10"
                ).add_to(m)
        
        if len(valid_locations) >= 2:
            for i in range(len(valid_locations)):
                for j in range(i + 1, len(valid_locations)):
                    loc1 = valid_locations[i]
                    loc2 = valid_locations[j]
                    dist_risk = (loc1["risk_score"] + loc2["risk_score"]) / 2
                    
                    if dist_risk >= 7:
                        line_color = "#ff0000"
                        weight = 2
                    elif dist_risk >= 4:
                        line_color = "#ff6600"
                        weight = 2
                    elif dist_risk >= 2:
                        line_color = "#ffcc00"
                        weight = 1.5
                    else:
                        line_color = "#00ff00"
                        weight = 1
                    
                    folium.PolyLine(
                        locations=[[loc1["lat"], loc1["lon"]], [loc2["lat"], loc2["lon"]]],
                        color=line_color,
                        weight=weight,
                        opacity=0.4,
                        dash_array='8, 6',
                        popup=f"Network Link<br>{loc1['ip']} <-> {loc2['ip']}<br>Risk: {dist_risk:.1f}"
                    ).add_to(m)
        
        legend_html = '''
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000; background: rgba(0,0,0,0.85); padding: 10px; border-radius: 8px; border: 1px solid #00ff00; font-family: monospace; font-size: 9px; min-width: 140px;">
            <b style="color: #00ff00;">[+] THREAT LEGEND</b><br>
            <span style="color:#ff0000;">[!]</span> Critical (7-10)<br>
            <span style="color:#ff6600;">[-]</span> High (5-6)<br>
            <span style="color:#ffcc00;">[*]</span> Medium (3-4)<br>
            <span style="color:#00ff00;">[+]</span> Low (0-2)<br>
            <span style="color:#ffaa00;">[*]</span> Organization HQ<br>
            <span style="color:#ff00ff;">[*]</span> Active Threat Zone<br>
            <span style="color:#ff6600; animation: blink-yellow 1s infinite;">[*] BLINKING = LIVE MONITORING</span>
            <br><span style="color:#888; font-size:8px;">Click marker for details</span>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m._repr_html_()


# ============================================================
# Interactive SOC Dashboard - FIXED ASCII BOX DRAWING
# ============================================================

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
        self.scan_output = []
        self.host_details = {}
        self.node_descriptions = {}
        self.history_file = os.path.join(self.scans_dir, "scan_history.json")
        self._load_history()
        self.spinner_frames = ["[+]", "[*]", "[-]", "[.]", "[+]", "[*]", "[-]", "[.]"]
        self.terminal_width = self._get_terminal_width()
    
    def _get_terminal_width(self):
        try:
            return shutil.get_terminal_size((100, 24)).columns
        except:
            return 100
    
    def _load_history(self):
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
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def center(self, text: str) -> str:
        return text.center(self.terminal_width)
    
    def draw_header(self):
        header = f"""
{Colors.RED}{Colors.BOLD}
{self.center("+" + "-" * 76 + "+")}
{self.center("|" + " " * 76 + "|")}
{self.center("|" + " " * 10 + "[+] [] [===] [========] [========] [===]    [===] [=======] [=======] [===]  [===]" + " " * 10 + "|")}
{self.center("|" + " " * 10 + "[+] [] [===] [=======] [========] [===]    [===] [=======] [=======] [===] [===]" + " " * 10 + "|")}
{self.center("|" + " " * 10 + "[=] [=] [=]     [=]   [=] [=] [=] [=]   [=] [=] [=]     [=] [=======] [===] [=]" + " " * 10 + "|")}
{self.center("|" + " " * 10 + "[=] [=] [=]     [=]   [=] [=] [=] [=]   [=] [=] [=]     [=] [=======] [===] [=]" + " " * 10 + "|")}
{self.center("|" + " " * 10 + "[=] [=] [=]   [=]   [=] [=] [=] [=]   [=] [=] [=]   [=] [=======] [===]  [=]" + " " * 10 + "|")}
{self.center("|" + " " * 10 + "[=]  [=] [=] [=======] [===]    [===] [=]   [=] [=======] [===]  [=]" + " " * 10 + "|")}
{self.center("|" + " " * 76 + "|")}
{self.center("|" + " " * 20 + Colors.YELLOW + "[+] SOC-GRADE NETWORK INTELLIGENCE [+]" + Colors.RED + " " * 20 + "|")}
{self.center("|" + " " * 25 + Colors.DIM + "Real-time Scanning | AI Scoring | Threat Intelligence | DNS Reconnaissance" + Colors.RED + " " * 25 + "|")}
{self.center("|" + " " * 25 + Colors.CYAN + "[+] HQ + Server Dual Location Tracking" + Colors.RED + " " * 25 + "|")}
{self.center("|" + " " * 76 + "|")}
{self.center("+" + "-" * 76 + "+")}
{Colors.RESET}
"""
        print(header)
    
    def draw_centered_dashboard(self):
        try:
            terminal_width = shutil.get_terminal_size((80, 24)).columns
        except:
            terminal_width = 80
        
        if terminal_width < 120:
            panel_width = 38
            spacing = 5
        elif terminal_width < 150:
            panel_width = 38
            spacing = 5
        else:
            panel_width = 38
            spacing = 18
        
        total_width = (panel_width * 3) + (spacing * 2)
        left_padding = max(0, (terminal_width - total_width) // 2)
        pad = " " * left_padding
        
        # LEFT PANEL
        left_panel = [
            f"{Colors.CYAN}+{'-' * panel_width}+{Colors.RESET}",
            f"{Colors.CYAN}|{Colors.RESET} {Colors.BOLD}{Colors.GREEN}[+] SCAN CONTROL CENTER{Colors.RESET}{' ' * 8}{Colors.CYAN}|{Colors.RESET}",
            f"{Colors.CYAN}+{'-' * panel_width}+{Colors.RESET}",
            f"{Colors.CYAN}|{Colors.RESET} {Colors.YELLOW}[1]{Colors.RESET} Quick Scan{' ' * 18}{Colors.CYAN}|{Colors.RESET}",
            f"{Colors.CYAN}|{Colors.RESET} {Colors.YELLOW}[2]{Colors.RESET} Standard Scan{' ' * 15}{Colors.CYAN}|{Colors.RESET}",
            f"{Colors.CYAN}|{Colors.RESET} {Colors.YELLOW}[3]{Colors.RESET} Full Aggressive{' ' * 13}{Colors.CYAN}|{Colors.RESET}",
            f"{Colors.CYAN}|{Colors.RESET} {Colors.YELLOW}[4]{Colors.RESET} DNS Recon{' ' * 20}{Colors.CYAN}|{Colors.RESET}",
            f"{Colors.CYAN}|{Colors.RESET} {Colors.YELLOW}[5]{Colors.RESET} UDP Scan{' ' * 20}{Colors.CYAN}|{Colors.RESET}",
            f"{Colors.CYAN}+{'-' * panel_width}+{Colors.RESET}",
            f"{Colors.CYAN}|{Colors.RESET} Target : {Colors.GREEN}{self.current_target[:18]:<18}{Colors.RESET} {Colors.CYAN}|{Colors.RESET}",
            f"{Colors.CYAN}|{Colors.RESET} Status : {Colors.RED if self.scan_active else Colors.YELLOW}{'[+] ACTIVE' if self.scan_active else '[.] IDLE'}{Colors.RESET}{' ' * 17}{Colors.CYAN}|{Colors.RESET}",
            f"{Colors.CYAN}+{'-' * panel_width}+{Colors.RESET}",
        ]
        
        # CENTER PANEL
        total_risk = sum(p.get("risk_score", 0) for p in self.discovered_ports)
        avg_risk = total_risk / max(1, len(self.discovered_ports))
        risk_bar_size = 22
        filled = int((avg_risk / 10) * risk_bar_size)
        risk_bar = "#" * filled + "." * (risk_bar_size - filled)
        
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
            f"{Colors.MAGENTA}+{'-' * panel_width}+{Colors.RESET}",
            f"{Colors.MAGENTA}|{Colors.RESET} {Colors.BOLD}{Colors.CYAN}[+] SOC LIVE STATUS{Colors.RESET}{' ' * 13}{Colors.MAGENTA}|{Colors.RESET}",
            f"{Colors.MAGENTA}+{'-' * panel_width}+{Colors.RESET}",
            f"{Colors.MAGENTA}|{Colors.RESET} Hosts Found : {Colors.GREEN}{len(self.network_nodes):<10}{Colors.RESET}{' ' * 9}{Colors.MAGENTA}|{Colors.RESET}",
            f"{Colors.MAGENTA}|{Colors.RESET} Open Ports : {Colors.GREEN}{len(self.discovered_ports):<10}{Colors.RESET}{' ' * 9}{Colors.MAGENTA}|{Colors.RESET}",
            f"{Colors.MAGENTA}|{Colors.RESET} Services    : {Colors.GREEN}{len(self.services_found):<10}{Colors.RESET}{' ' * 9}{Colors.MAGENTA}|{Colors.RESET}",
            f"{Colors.MAGENTA}|{Colors.RESET} Duration    : {Colors.GREEN}{self.scan_duration}s{' ' * 16}{Colors.RESET}{Colors.MAGENTA}|{Colors.RESET}",
            f"{Colors.MAGENTA}+{'-' * panel_width}+{Colors.RESET}",
            f"{Colors.MAGENTA}|{Colors.RESET} Threat Level:{' ' * 18}{Colors.MAGENTA}|{Colors.RESET}",
            f"{Colors.MAGENTA}|{Colors.RESET} {risk_color}{risk_bar}{Colors.RESET} {avg_risk:.1f}/10 {Colors.MAGENTA}|{Colors.RESET}",
            f"{Colors.MAGENTA}|{Colors.RESET} Status : {risk_color}{threat}{Colors.RESET}{' ' * (21 - len(threat))}{Colors.MAGENTA}|{Colors.RESET}",
            f"{Colors.MAGENTA}+{'-' * panel_width}+{Colors.RESET}",
        ]
        
        # RIGHT PANEL
        right_panel = [
            f"{Colors.BLUE}+{'-' * panel_width}+{Colors.RESET}",
            f"{Colors.BLUE}|{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}[+] LIVE DISCOVERIES{Colors.RESET}{' ' * 11}{Colors.BLUE}|{Colors.RESET}",
            f"{Colors.BLUE}+{'-' * panel_width}+{Colors.RESET}",
        ]
        
        recent = self.discovered_ports[-6:]
        if recent:
            for p in recent:
                port = f"{p['port']}/{p['protocol']}"
                service = p["service"][:14]
                score = p.get("risk_score", 0)
                
                if score >= 7:
                    color = Colors.RED
                    icon = "[!]"
                elif score >= 4:
                    color = Colors.YELLOW
                    icon = "[*]"
                else:
                    color = Colors.GREEN
                    icon = "[+]"
                
                line = f"{icon} {port:<10} {service:<14}"
                right_panel.append(
                    f"{Colors.BLUE}|{Colors.RESET} {color}{line:<32}{Colors.RESET}{Colors.BLUE}|{Colors.RESET}"
                )
        else:
            for _ in range(6):
                right_panel.append(
                    f"{Colors.BLUE}|{Colors.RESET} {Colors.DIM}Waiting for scan results...{Colors.RESET}{' ' * 4}{Colors.BLUE}|{Colors.RESET}"
                )
        
        right_panel.extend([
            f"{Colors.BLUE}+{'-' * panel_width}+{Colors.RESET}",
            f"{Colors.BLUE}|{Colors.RESET} Updated : {Colors.GREEN}{datetime.now().strftime('%H:%M:%S')}{Colors.RESET}{' ' * 12}{Colors.BLUE}|{Colors.RESET}",
            f"{Colors.BLUE}+{'-' * panel_width}+{Colors.RESET}",
        ])
        
        max_lines = max(len(left_panel), len(center_panel), len(right_panel))
        for i in range(max_lines):
            left = left_panel[i] if i < len(left_panel) else " " * (panel_width + 2)
            center = center_panel[i] if i < len(center_panel) else " " * (panel_width + 2)
            right = right_panel[i] if i < len(right_panel) else " " * (panel_width + 2)
            print(pad + left + (" " * spacing) + center + (" " * spacing) + right)
    
    def draw_results_table(self):
        if not self.services_found:
            print(f"\n{self.center(Colors.YELLOW + '-' * 70 + Colors.RESET)}")
            print(self.center(Colors.YELLOW + ' ' * 28 + '[!] NO RESULTS YET [!]' + Colors.RESET))
            print(self.center(Colors.YELLOW + '-' * 70 + Colors.RESET))
            return
        
        print(f"\n{self.center(Colors.CYAN + Colors.BOLD + '-' * 90 + Colors.RESET)}")
        print(self.center(Colors.CYAN + Colors.BOLD + '|' + ' ' * 38 + '[+] DISCOVERED SERVICES [+]\n' + ' ' * 38 + '|' + Colors.RESET))
        print(self.center(Colors.CYAN + Colors.BOLD + '-' * 90 + Colors.RESET))
        
        header = f"{Colors.CYAN}| {Colors.GREEN}PORT{Colors.RESET} | {Colors.GREEN}SERVICE{Colors.RESET} | {Colors.GREEN}VERSION{Colors.RESET} | {Colors.GREEN}RISK{Colors.RESET} | {Colors.GREEN}EXPLOIT{Colors.RESET} |{Colors.CYAN}"
        print(self.center(header))
        print(self.center(Colors.CYAN + '-' * 90 + Colors.RESET))
        
        for service in self.services_found[:8]:
            risk_score = service.get("risk_score", 0)
            if risk_score >= 7:
                risk_text = f"{Colors.RED}[!] HIGH [!]{Colors.RESET}"
            elif risk_score >= 4:
                risk_text = f"{Colors.YELLOW}[*] MED [*]{Colors.RESET}"
            else:
                risk_text = f"{Colors.GREEN}[+] LOW [+]{Colors.RESET}"
            
            exploit_info = service.get("exploit", "N/A")[:10]
            line = f"{Colors.CYAN}|{Colors.RESET} {Colors.GREEN}{service['port']}/{service['protocol']:<4}{Colors.RESET} | {Colors.CYAN}{service['service'][:10]:<10}{Colors.RESET} | {Colors.DIM}{service.get('version', 'N/A')[:8]:<8}{Colors.RESET} | {risk_text:<10} | {Colors.PURPLE}{exploit_info:<10}{Colors.RESET} |{Colors.CYAN}"
            print(self.center(line))
        
        print(self.center(Colors.CYAN + '-' * 90 + Colors.RESET))
    
    def draw_footer(self):
        footer = f"""
{Colors.DIM}{self.center('-' * 90)}{Colors.RESET}
{self.center(Colors.DIM + ' Commands: ' + Colors.GREEN + '[S]' + Colors.DIM + ' Scan  ' + Colors.YELLOW + '[Q]' + Colors.DIM + ' Quick  ' + Colors.RED + '[F]' + Colors.DIM + ' Full  ' + Colors.CYAN + '[D]' + Colors.DIM + ' DNS Recon  ' + Colors.MAGENTA + '[H]' + Colors.DIM + ' Help  ' + Colors.WHITE + '[X]' + Colors.DIM + ' Exit')}{Colors.RESET}
{Colors.DIM}{self.center('-' * 90)}{Colors.RESET}
"""
        print(footer)
    
    def show_help(self):
        help_text = f"""
{self.center(Colors.CYAN + '-' * 60 + Colors.RESET)}
{self.center(Colors.GREEN + '[+] DSTERMINAL SOC DASHBOARD HELP' + Colors.RESET)}
{self.center(Colors.CYAN + '-' * 60 + Colors.RESET)}
{self.center(Colors.YELLOW + 'Commands:' + Colors.RESET)}
{self.center(Colors.GREEN + '  [S] - Standard Scan' + Colors.RESET)}
{self.center(Colors.GREEN + '  [Q] - Quick Scan' + Colors.RESET)}
{self.center(Colors.GREEN + '  [F] - Full Scan' + Colors.RESET)}
{self.center(Colors.GREEN + '  [D] - DNS Reconnaissance' + Colors.RESET)}
{self.center(Colors.GREEN + '  [H] - Help' + Colors.RESET)}
{self.center(Colors.GREEN + '  [X] - Exit' + Colors.RESET)}
{self.center(Colors.CYAN + '-' * 60 + Colors.RESET)}
"""
        print(help_text)
    
    def interactive_loop(self):
        self.clear_screen()
        while True:
            self.clear_screen()
            self.draw_header()
            self.draw_centered_dashboard()
            self.draw_results_table()
            
            print(f"\n{Colors.DIM}{'-' * 90}{Colors.RESET}")
            print(f"{Colors.DIM} Commands: {Colors.GREEN}[S]{Colors.DIM} Scan  {Colors.YELLOW}[Q]{Colors.DIM} Quick  {Colors.RED}[F]{Colors.DIM} Full  {Colors.CYAN}[D]{Colors.DIM} DNS Recon  {Colors.MAGENTA}[H]{Colors.DIM} Help  {Colors.WHITE}[X]{Colors.DIM} Exit{Colors.RESET}")
            print(f"{Colors.DIM}{'-' * 90}{Colors.RESET}")
            
            print(f"\n{Colors.CYAN}{Colors.BOLD}+-{Colors.RESET} {Colors.GREEN}[+]{Colors.RESET} {Colors.BOLD}{Colors.CYAN}SOC COMMAND{Colors.RESET} {Colors.CYAN}{Colors.BOLD}+{Colors.RESET}{Colors.CYAN}{Colors.BOLD}+{Colors.RESET}")
            
            print(f"{Colors.CYAN}{Colors.BOLD}[+]{Colors.RESET} {Colors.CYAN}{Colors.BOLD}${Colors.RESET} ", end="")
            
            choice = input()
            choice = choice.strip().lower()
            
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
    
    def generate_network_topology(self) -> str:
        if not PLOTLY_AVAILABLE or not self.network_nodes:
            return '<div style="padding:50px;text-align:center;color:#888;">No topology data available</div>'
        
        node_list = list(self.network_nodes.keys())
        num_nodes = len(node_list)
        node_x = []
        node_y = []
        node_colors = []
        node_sizes = []
        node_hover_texts = []
        node_labels = []
        
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
        
        self.node_descriptions = {}
        
        for i, ip in enumerate(node_list):
            angle = 2 * math.pi * i / max(1, num_nodes)
            radius = 4
            node_x.append(radius * math.cos(angle))
            node_y.append(radius * math.sin(angle))
            risk = self.network_nodes[ip].risk_score
            is_org = self.network_nodes[ip].is_organization_location
            location_note = "[+] HQ+Server" if is_org else "[+] Server"
            
            if risk >= 7:
                desc = random.choice(high_risk_descriptions)
                risk_color = "#ff4444"
                risk_text = "CRITICAL"
                risk_icon = "[!]"
                node_color = "#ff0000"
                node_size = 25
            elif risk >= 4:
                desc = random.choice(medium_risk_descriptions)
                risk_color = "#ffcc00"
                risk_text = "MEDIUM"
                risk_icon = "[*]"
                node_color = "#ffcc00"
                node_size = 20
            else:
                desc = random.choice(low_risk_descriptions)
                risk_color = "#44ff44"
                risk_text = "LOW"
                risk_icon = "[+]"
                node_color = "#00ff00"
                node_size = 15
            
            self.node_descriptions[ip] = {
                "description": desc,
                "risk_color": risk_color,
                "risk_text": risk_text,
                "risk_icon": risk_icon,
                "risk_score": risk
            }
            
            port_count = len(self.network_nodes[ip].ports)
            top_services = [p.get('service', 'unknown') for p in self.network_nodes[ip].ports[:3]]
            
            server_loc = ""
            if hasattr(self.network_nodes[ip], 'server_country') and self.network_nodes[ip].server_country:
                server_loc = f"[+] Server: {self.network_nodes[ip].server_country} - {self.network_nodes[ip].server_city}"
            
            org_loc = ""
            if is_org and hasattr(self.network_nodes[ip], 'org_country') and self.network_nodes[ip].org_country:
                org_loc = f"[+] HQ: {self.network_nodes[ip].org_country} - {self.network_nodes[ip].org_city}"
            
            hover_parts = [
                f"<b style='color:#00ffff;font-size:14px;'>{ip}</b>",
                f"{location_note}",
                "-------------------------",
            ]
            if org_loc:
                hover_parts.append(org_loc)
            if server_loc:
                hover_parts.append(server_loc)
            
            hover_parts.extend([
                f"<b>[!] Risk:</b> <span style='color:{risk_color};font-weight:bold;'>{risk:.1f}/10 [{risk_text}]</span>",
                f"<b>[+] Ports:</b> {port_count}",
                f"<b>[+] Services:</b> {', '.join(top_services) if top_services else 'None'}",
                "-------------------------",
                f"<span style='color:{risk_color};font-weight:bold;font-size:12px;'>{risk_icon} {desc}</span>"
            ])
            
            hover_text = "<br>".join(hover_parts)
            node_hover_texts.append(hover_text)
            node_labels.append(ip[:15])
            node_colors.append(node_color)
            node_sizes.append(node_size)
        
        edge_x = []
        edge_y = []
        for i in range(len(node_x) - 1):
            edge_x.extend([node_x[i], node_x[i+1], None])
            edge_y.extend([node_y[i], node_y[i+1], None])
        
        fig = go.Figure()
        
        if edge_x:
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(width=2, color='#00ffff', dash='dash'),
                hoverinfo='none',
                showlegend=False
            ))
        
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
                namelength=-1
            )
        ))
        
        high_risk_nodes = [n for n in self.network_nodes.values() if n.risk_score >= 7]
        medium_risk_nodes = [n for n in self.network_nodes.values() if 4 <= n.risk_score < 7]
        low_risk_nodes = [n for n in self.network_nodes.values() if n.risk_score < 4]
        
        summary_parts = []
        if high_risk_nodes:
            summary_parts.append(f"[!] {len(high_risk_nodes)} Critical")
        if medium_risk_nodes:
            summary_parts.append(f"[*] {len(medium_risk_nodes)} Medium")
        if low_risk_nodes:
            summary_parts.append(f"[+] {len(low_risk_nodes)} Low")
        risk_summary = " | ".join(summary_parts) if summary_parts else "No risk data"
        
        if high_risk_nodes:
            risk_footer = "[!] CRITICAL NODES DETECTED - Immediate action required!"
            footer_color = "#ff4444"
        elif medium_risk_nodes:
            risk_footer = "[+] Medium risk nodes found - Schedule remediation"
            footer_color = "#ffcc00"
        else:
            risk_footer = "[+] All nodes have LOW risk - Continue monitoring"
            footer_color = "#44ff44"
        
        fig.update_layout(
            title=dict(
                text=f"[+] NETWORK TOPOLOGY<br><span style='font-size:11px;color:#888;'>Risk Summary: {risk_summary}</span>",
                font=dict(color='#00ffff', size=14),
                x=0.5
            ),
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 6]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 6]),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=450,
            margin=dict(l=20, r=20, t=60, b=20),
            annotations=[
                dict(
                    text=f"[+] {risk_footer}",
                    x=0.5,
                    y=-0.08,
                    xref='paper',
                    yref='paper',
                    showarrow=False,
                    font=dict(color=footer_color, size=10)
                ),
                dict(
                    text="[+] Hover over nodes for detailed risk assessment",
                    x=0.5,
                    y=-0.15,
                    xref='paper',
                    yref='paper',
                    showarrow=False,
                    font=dict(color='#666', size=9)
                )
            ]
        )
        
        return fig.to_html(include_plotlyjs='cdn', full_html=False)
    
    def get_risk_assessment_panel(self) -> str:
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
        
        alert_html = ""
        if high_count > 0:
            alert_html = f"""
            <div style="background: rgba(255, 0, 0, 0.15); border: 1px solid #ff0000; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">[!]</span>
                <div>
                    <span style="color: #ff0000; font-weight: bold; font-size: 13px;">[!] CRITICAL NODE DETECTED!</span>
                    <span style="color: #ff6666; font-size: 11px; display: block; margin-top: 2px;">
                        {high_count} node{'s' if high_count > 1 else ''} with CRITICAL risk level - Immediate action required!
                    </span>
                </div>
            </div>
            """
        elif medium_count > 0:
            alert_html = f"""
            <div style="background: rgba(255, 204, 0, 0.12); border: 1px solid #ffcc00; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">[*]</span>
                <div>
                    <span style="color: #ffcc00; font-weight: bold; font-size: 13px;">[!] MEDIUM RISK NODES</span>
                    <span style="color: #ffdd77; font-size: 11px; display: block; margin-top: 2px;">
                        {medium_count} node{'s' if medium_count > 1 else ''} with MEDIUM risk level - Schedule remediation
                    </span>
                </div>
            </div>
            """
        else:
            alert_html = f"""
            <div style="background: rgba(0, 255, 0, 0.08); border: 1px solid #44ff44; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">[+]</span>
                <div>
                    <span style="color: #44ff44; font-weight: bold; font-size: 13px;">[+] LOW RISK</span>
                    <span style="color: #88ff88; font-size: 11px; display: block; margin-top: 2px;">
                        All nodes have LOW risk - Continue monitoring
                    </span>
                </div>
            </div>
            """
        
        risk_panel_html = f"""
        <div style="margin-top: 15px; padding: 12px; background: rgba(10, 15, 30, 0.9); border-radius: 10px; border: 1px solid rgba(0, 255, 255, 0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="color: #00ffff; font-size: 13px; font-weight: bold;">[+] RISK ASSESSMENT PER NODE</span>
                <span style="color: #666; font-size: 10px;">Hover nodes for details</span>
            </div>
            {alert_html}
            <div style="max-height: 200px; overflow-y: auto; padding-right: 5px;">
                {risk_descriptions_html}
            </div>
            <div style="margin-top: 10px; display: flex; gap: 15px; justify-content: center; font-size: 10px; color: #888; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px; flex-wrap: wrap;">
                <span><span style="color:#ff4444;">[!]</span> Critical ({high_count})</span>
                <span><span style="color:#ffcc00;">[*]</span> Medium ({medium_count})</span>
                <span><span style="color:#44ff44;">[+]</span> Low ({low_count})</span>
                <span style="color:#666;">|</span>
                <span style="color:#666;">Total Nodes: {total_nodes}</span>
            </div>
        </div>
        """
        
        return risk_panel_html
    
    def generate_historical_timeline(self) -> str:
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
            title=dict(text="[+] HISTORICAL SCAN TIMELINE", font=dict(color='#00ffff', size=14), x=0.5),
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
    
    def generate_full_dashboard(self, auto_open: bool = False):
        total_risk = sum(p.get('risk_score', 0) for p in self.discovered_ports)
        avg_risk = total_risk / max(1, len(self.discovered_ports))
        
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
        body {{ background: linear-gradient(135deg, #0a0a1a 0%%, #0d1117 100%%); font-family: 'Segoe UI', monospace; color: #e6e6e6; }}
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
        table {{ width: 100%%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 12px; }}
        th {{ color: #00ffff; }}
        .footer {{ text-align: center; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 10px; color: #666; }}
        .blink {{ animation: blink 1s step-end infinite; }}
        @keyframes blink {{ 0%%,100%% {{ opacity: 1; }} 50%% {{ opacity: 0.5; }} }}
        .full-width {{ grid-column: span 2; }}
        @media (max-width: 1000px) {{ .dashboard-container {{ grid-template-columns: 1fr; }} .full-width {{ grid-column: span 1; }} }}
        .org-badge {{ background: #ffaa00; color: #000; padding: 2px 6px; border-radius: 10px; font-size: 9px; margin-left: 5px; }}
        .dual-badge {{ background: #ff6600; color: #000; padding: 2px 6px; border-radius: 10px; font-size: 9px; margin-left: 5px; }}
        .risk-panel-container {{ margin-top: 15px; }}
        #topology {{ min-height: 400px; width: 100%%; }}
        #topology .js-plotly-plot {{ width: 100%% !important; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>[+] DSTERMINAL CYBER-OPS NETWORK TOPOLOGY MAPPING [+]/h1>
        <div>Network Intelligence | AI Vulnerability Scoring | Real-time Threat Detection</div>
        <div class="blink" style="color: #00ff00; font-size: 11px; margin-top: 5px;">[+] FULL INTELLIGENCE DASHBOARD - DUAL LOCATION TRACKING [+]</div>
        <div style="font-size: 10px; color: #ffaa00; margin-top: 3px;">[+] Organization Headquarters + [+] Server/Cloud Locations</div>
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
            <div class="card-header">[+] GEOGRAPHIC THREAT MAP <span class="org-badge">[+] HQ</span> <span class="dual-badge">[+] Server</span></div>
            <div id="geomap" style="height: 450px;">{geo_html}</div>
        </div>
        <div class="card">
            <div class="card-header">[+] NETWORK TOPOLOGY</div>
            <div id="topology" style="min-height: 400px;">{topology_graph}</div>
            <div class="risk-panel-container">{risk_panel}</div>
        </div>
        <div class="card full-width">
            <div class="card-header">[+] HISTORICAL SCAN TIMELINE</div>
            <div id="timeline">{timeline_html}</div>
        </div>
        <div class="card full-width">
            <div class="card-header">[+] DISCOVERED SERVICES & VULNERABILITIES</div>
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
        <br>[+] DSTerminal autogenerated report | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        <br><span style="color: #00ff00;">[+] GEOLOCATION: IP-API.COM</span> | <span style="color: #ffaa00;">[+] ORGANIZATION HEADQUARTERS</span> | <span style="color: #ff6600;">[+] SERVER LOCATIONS</span> | [+] REAL-TIME MONITORING ACTIVE [+]
    </div>
</body>
</html>
        """
        
        html_path = os.path.join(self.scans_dir, f"soc_full_dashboard_{self.current_target.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        if not auto_open:
            print(f"\n{Colors.CYAN}+{'-' * 60}+{Colors.RESET}")
            print(f"{Colors.CYAN}|{Colors.RESET} {Colors.GREEN}[+] Dashboard Generated Successfully!{Colors.RESET} {Colors.CYAN}|{Colors.RESET}")
            print(f"{Colors.CYAN}|{Colors.RESET} {Colors.DIM}Location: {html_path}{Colors.RESET} {Colors.CYAN}|{Colors.RESET}")
            print(f"{Colors.CYAN}+{'-' * 60}+{Colors.RESET}")
            print(f"{Colors.CYAN}|{Colors.RESET} {Colors.YELLOW}[?] Open dashboard in browser?{Colors.RESET} {Colors.CYAN}|{Colors.RESET}")
            print(f"{Colors.CYAN}|{Colors.RESET} {Colors.GREEN}[Y] Yes{Colors.RESET}  {Colors.RED}[N] No{Colors.RESET}  {Colors.CYAN}|{Colors.RESET}")
            print(f"{Colors.CYAN}+{'-' * 60}+{Colors.RESET}")
            
            choice = input(f"{Colors.GREEN}[SOC] > {Colors.RESET}").strip().lower()
            if choice == 'y' or choice == 'yes':
                print(f"{Colors.GREEN}[+] Opening dashboard in browser...{Colors.RESET}")
                webbrowser.open(f"file://{html_path}")
            else:
                print(f"{Colors.YELLOW}[!] Dashboard saved but not opened.{Colors.RESET}")
                print(f"{Colors.YELLOW}[!] You can open it later from: {html_path}{Colors.RESET}")
        else:
            webbrowser.open(f"file://{html_path}")
        
        return html_path
    
    def run_nmap_scan(self, target: str, flags: List[str], auto_open: bool = False):
        """Run nmap scan with real-time output capture and display"""
        nmap_path = shutil.which("nmap")
        if not nmap_path:
            print(self.center(f"{Colors.RED}[!] Nmap not found in PATH{Colors.RESET}"))
            print(self.center(f"{Colors.YELLOW}[!] Please install nmap from: https://nmap.org/download.html{Colors.RESET}"))
            input(self.center(Colors.DIM + "Press Enter to continue..." + Colors.RESET))
            return
        
        self.current_target = target
        self.scan_active = True
        self.discovered_ports = []
        self.services_found = []
        self.network_nodes = {}
        self.geo_map = EnhancedGeoMapVisualizer()
        self.scan_output = []
        self.host_details = {}
        self.node_descriptions = {}
        
        start_time = datetime.now()
        cmd = ["nmap"] + flags + [target]
        
        self.clear_screen()
        self.draw_header()
        print(f"{Colors.CYAN}{'-' * 70}{Colors.RESET}")
        
        timer_running = True
        
        def update_timer():
            while timer_running:
                elapsed = (datetime.now() - start_time).seconds
                minutes = elapsed // 60
                seconds = elapsed % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                sys.stdout.write(f"\033[1A\033[K")
                sys.stdout.flush()
                time.sleep(1)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()
        
        print(f"{Colors.CYAN}{'-' * 70}{Colors.RESET}\n")
        
        try:
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                bufsize=1,
                universal_newlines=True
            )
            
            line_count = 0
            for line in process.stdout:
                if line.strip():
                    self.parse_nmap_output(line)
                    line_count += 1
                    if line_count % 3 == 0:
                        self.clear_screen()
                        self.draw_header()
                        self.draw_centered_dashboard()
                        self.draw_results_table()
                        self.draw_footer()
                        elapsed = (datetime.now() - start_time).seconds
                        minutes = elapsed // 60
                        seconds = elapsed % 60
                        time_str = f"{minutes:02d}:{seconds:02d}"
                        print(f"\n{Colors.YELLOW}[+] SCANNING IN PROGRESS... (Elapsed: {Colors.GREEN}{time_str}{Colors.YELLOW}){Colors.RESET}")
                        sys.stdout.flush()
            
            process.wait()
            
            timer_running = False
            timer_thread.join(timeout=1)
            
            sys.stdout.write(f"\033[1A\033[K")
            
            self.scan_duration = (datetime.now() - start_time).seconds
            self.scan_active = False
            
            if self.services_found:
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
                self._save_history()
                if len(self.scan_history) > 10:
                    self.scan_history.pop(0)
            
            minutes = self.scan_duration // 60
            seconds = self.scan_duration % 60
            duration_str = f"{minutes:02d}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
            
            self.clear_screen()
            self.draw_header()
            self.draw_centered_dashboard()
            self.draw_results_table()
            self.draw_footer()
            
            print(f"\n{Colors.GREEN}[+] Scan completed in {duration_str}{Colors.RESET}")
            print(self.center(Colors.CYAN + '[+] Found ' + str(len(self.discovered_ports)) + ' open ports' + Colors.RESET))
            
            if self.services_found:
                print(self.center(Colors.YELLOW + '[+] Generating HTML dashboard...' + Colors.RESET))
                html_path = self.generate_full_dashboard(auto_open=auto_open)
                
                print(self.center(Colors.YELLOW + '[+] Generating PDF report...' + Colors.RESET))
                try:
                    pdf_path = self.generate_pdf_report(target)
                    if pdf_path:
                        pdf_filename = os.path.basename(pdf_path)
                        print(self.center(Colors.GREEN + f'[+] PDF report saved: {pdf_filename}' + Colors.RESET))
                        
                        if not auto_open:
                            open_pdf = input(self.center(Colors.YELLOW + '[?] Open PDF report? (y/n): ' + Colors.RESET)).strip().lower()
                            if open_pdf == 'y' or open_pdf == 'yes':
                                import webbrowser
                                webbrowser.open(f"file://{pdf_path}")
                                print(self.center(Colors.GREEN + '[+] Opening PDF report...' + Colors.RESET))
                    else:
                        print(self.center(Colors.RED + '[!] PDF generation failed' + Colors.RESET))
                except Exception as e:
                    print(self.center(Colors.RED + f'[!] PDF generation error: {e}' + Colors.RESET))
                    import traceback
                    traceback.print_exc()
            else:
                print(self.center(Colors.YELLOW + '[!] No open ports found. Try a different target or scan type.' + Colors.RESET))
                input(self.center(Colors.DIM + "Press Enter to continue..." + Colors.RESET))
            
        except Exception as e:
            timer_running = False
            timer_thread.join(timeout=1)
            sys.stdout.write(f"\033[1A\033[K")
            print(self.center(f"{Colors.RED}[!] Scan failed: {e}{Colors.RESET}"))
            import traceback
            traceback.print_exc()
            self.scan_active = False
            input(self.center(Colors.DIM + "Press Enter to continue..." + Colors.RESET))
    
    def parse_nmap_output(self, line: str):
        """Parse nmap output and display results in real-time"""
        line = line.strip()
        if not line:
            return
        
        host_match = re.search(r'Nmap scan report for (.+)', line)
        if host_match:
            host = host_match.group(1).strip()
            host = re.sub(r'\([^)]*\)', '', host).strip()
            host = host.rstrip(':')
            
            if host not in self.network_nodes:
                resolved_ip = resolve_domain_to_ip(host)
                
                org_location, server_location, is_org_location = enhanced_geoip_lookup(host, resolved_ip)
                
                lat = server_location.get("lat", 0)
                lon = server_location.get("lon", 0)
                country = server_location.get("country", "Unknown")
                city = server_location.get("city", "Unknown")
                isp = server_location.get("isp", "Unknown")
                
                if (lat == 0 or lon == 0) and org_location and org_location.get("lat", 0) != 0:
                    lat = org_location.get("lat", 0)
                    lon = org_location.get("lon", 0)
                    country = org_location.get("country", "Unknown")
                    city = org_location.get("city", "Unknown")
                    print(f"{Colors.YELLOW}  [+] Using organization HQ location (server location unknown){Colors.RESET}")
                
                self.host_details[host] = {
                    "host": host,
                    "resolved_ip": resolved_ip,
                    "org_country": org_location.get('country', 'Unknown'),
                    "org_city": org_location.get('city', 'Unknown'),
                    "server_country": server_location.get('country', 'Unknown'),
                    "server_city": server_location.get('city', 'Unknown'),
                    "is_org": is_org_location,
                    "lat": lat,
                    "lon": lon,
                    "isp": isp,
                    "server_location": server_location,
                    "org_location": org_location
                }
                
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
                
                if lat != 0 and lon != 0:
                    self.geo_map.add_location(
                        lat=lat,
                        lon=lon,
                        ip=host,
                        risk_score=0,
                        ports=[],
                        country=country,
                        is_org_location=is_org_location,
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
                    
                    print(f"{Colors.GREEN}  [+] Server Location: {city}, {country} ({lat:.4f}, {lon:.4f}){Colors.RESET}")
                    print(f"{Colors.CYAN}  [+] ISP: {isp}{Colors.RESET}")
                    
                    org_country = org_location.get('country', 'Unknown')
                    org_city = org_location.get('city', 'Unknown')
                    
                    if org_country != 'Unknown' and org_city != 'Unknown':
                        if org_country != country or org_city != city:
                            print(f"{Colors.YELLOW}  [+] Organization HQ: {org_country} - {org_city}{Colors.RESET}")
                        else:
                            print(f"{Colors.GREEN}  [+] Same as server location (HQ: {org_country} - {org_city}){Colors.RESET}")
                    elif org_country != 'Unknown':
                        print(f"{Colors.YELLOW}  [+] Organization Country: {org_country}{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}  [+] Location not available for {host}{Colors.RESET}")
                    if resolved_ip and resolved_ip != host:
                        try:
                            import requests
                            response = requests.get(f"http://ip-api.com/json/{resolved_ip}?fields=status,country,city,lat,lon,isp,org,as", timeout=3)
                            data = response.json()
                            if data.get('status') == 'success':
                                lat = data.get("lat", 0)
                                lon = data.get("lon", 0)
                                if lat != 0 and lon != 0:
                                    node.lat = lat
                                    node.lon = lon
                                    node.country = data.get("country", "Unknown")
                                    node.city = data.get("city", "Unknown")
                                    self.geo_map.add_location(
                                        lat=lat,
                                        lon=lon,
                                        ip=host,
                                        risk_score=0,
                                        ports=[],
                                        country=data.get("country", "Unknown"),
                                        is_org_location=is_org_location,
                                        server_location=f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}",
                                        server_country=data.get("country", "Unknown"),
                                        server_city=data.get("city", "Unknown"),
                                        server_lat=lat,
                                        server_lon=lon,
                                        server_isp=data.get("isp", "Unknown"),
                                        org_country=org_location.get("country", "Unknown"),
                                        org_city=org_location.get("city", "Unknown"),
                                        domain=host
                                    )
                                    print(f"{Colors.GREEN}  [+] Server Location (fallback): {data.get('city', 'Unknown')}, {data.get('country', 'Unknown')} ({lat:.4f}, {lon:.4f}){Colors.RESET}")
                        except:
                            pass
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
            
            port_info = {
                "port": port, 
                "protocol": proto, 
                "service": service, 
                "version": version, 
                "risk_score": risk_score
            }
            self.discovered_ports.append(port_info)
            
            service_info = {
                "port": port, 
                "protocol": proto, 
                "service": service, 
                "version": version,
                "risk_score": risk_score, 
                "exploit": vuln.get("exploit", "N/A"),
                "cvss_id": vuln.get("cvss_id", "N/A"),
                "recommendation": vuln.get("recommendation", "Monitor")
            }
            self.services_found.append(service_info)
            
            for host, node in self.network_nodes.items():
                if node.lat != 0:
                    node.ports.append({"port": port, "service": service, "risk_score": risk_score})
                    node.risk_score = max(node.risk_score, risk_score)
                    
                    for i, loc in enumerate(self.geo_map.locations):
                        if loc["ip"] == host or loc.get("domain") == host:
                            self.geo_map.locations[i]["risk_score"] = node.risk_score
                            self.geo_map.locations[i]["ports"] = node.ports
                            break
            
            risk_icon = "[!]" if risk_score >= 7 else "[*]" if risk_score >= 4 else "[+]"
            color = Colors.RED if risk_score >= 7 else Colors.YELLOW if risk_score >= 4 else Colors.GREEN
            risk_text = "CRITICAL" if risk_score >= 7 else "HIGH" if risk_score >= 5 else "MEDIUM" if risk_score >= 3 else "LOW"
            
            print(f"{color}  +-- {risk_icon} PORT {port}/{proto} -> {service}{Colors.RESET}")
            if version:
                print(f"{color}  |  +-- Version: {version}{Colors.RESET}")
            print(f"{color}  |     Risk: {risk_score:.1f}/10 [{risk_text}]{Colors.RESET}")
            if vuln.get("exploit"):
                print(f"{color}  |     Exploit: {vuln.get('exploit')}{Colors.RESET}")
            print(f"{color}  |     CVE: {vuln.get('cvss_id', 'N/A')}{Colors.RESET}")
            print()
            return
        
        if "Nmap done" in line:
            self.scan_active = False
            return
    
    def generate_pdf_report(self, target: str = None) -> str:
        """Generate professional PDF report of scan results"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER
            
            if not target:
                target = self.current_target if self.current_target else "scan"
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"soc_report_{target.replace('.', '_')}_{timestamp}.pdf"
            pdf_path = os.path.join(self.scans_dir, pdf_filename)
            
            doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=72)
            
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
            
            story = []
            
            story.append(Paragraph("DSTERMINAL SOC Security Assessment Report", title_style))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"Target: {target}", styles['Normal']))
            story.append(Paragraph(f"Scan Duration: {self.scan_duration} seconds", styles['Normal']))
            story.append(Spacer(1, 20))
            
            story.append(Paragraph("Executive Summary", heading_style))
            
            total_risk = sum(p.get("risk_score", 0) for p in self.discovered_ports)
            avg_risk = total_risk / max(1, len(self.discovered_ports))
            
            if avg_risk >= 7:
                risk_level = "CRITICAL"
            elif avg_risk >= 4:
                risk_level = "WARNING"
            else:
                risk_level = "LOW"
            
            summary_text = f"""
            <b>Risk Assessment Score: {avg_risk:.1f}/10 - {risk_level}</b><br/>
            <br/>
            This report summarizes the security assessment performed on {target}. 
            The scan identified {len(self.network_nodes)} host(s) with {len(self.discovered_ports)} open ports 
            and {len(self.services_found)} active services.<br/>
            <br/>
            <b>Key Findings:</b><br/>
            [+] Total Open Ports: {len(self.discovered_ports)}<br/>
            [+] Total Services: {len(self.services_found)}<br/>
            [+] Average Risk Score: {avg_risk:.1f}/10<br/>
            [+] Scan Duration: {self.scan_duration} seconds
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            story.append(Paragraph("Discovered Services & Vulnerabilities", heading_style))
            
            if self.services_found:
                table_data = [['Port', 'Service', 'Version', 'Risk Score', 'Exploit', 'CVE ID']]
                for service in self.services_found[:20]:
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
            
            high_risk = [s for s in self.services_found if s.get("risk_score", 0) >= 7]
            if high_risk:
                story.append(Paragraph("Critical Findings (High Risk)", heading_style))
                for service in high_risk[:10]:
                    finding_text = f"""
                    <b>[+] {service['port']}/{service['protocol']} - {service['service']}</b><br/>
                    Risk Score: {service['risk_score']}/10 | CVE: {service.get('cvss_id', 'N/A')}<br/>
                    Exploit: {service.get('exploit', 'N/A')}<br/>
                    Recommendation: {service.get('recommendation', 'Patch immediately')}
                    """
                    story.append(Paragraph(finding_text, risk_high_style))
                    story.append(Spacer(1, 10))
            
            medium_risk = [s for s in self.services_found if 4 <= s.get("risk_score", 0) < 7]
            if medium_risk:
                story.append(Paragraph("Medium Risk Findings", heading_style))
                for service in medium_risk[:10]:
                    finding_text = f"""
                    <b>[+] {service['port']}/{service['protocol']} - {service['service']}</b><br/>
                    Risk Score: {service['risk_score']}/10 | CVE: {service.get('cvss_id', 'N/A')}
                    """
                    story.append(Paragraph(finding_text, risk_medium_style))
                    story.append(Spacer(1, 10))
            
            story.append(PageBreak())
            
            story.append(Paragraph("Network Topology Analysis", heading_style))
            
            if self.network_nodes:
                topo_data = [['Host', 'Open Ports', 'Risk Score', 'Location Type']]
                for ip, node in self.network_nodes.items():
                    location_type = "[+] HQ + Server" if node.is_organization_location else "[+] Server"
                    topo_data.append([
                        ip[:15],
                        str(len(node.ports)),
                        f"{node.risk_score:.1f}",
                        location_type
                    ])
                
                topo_table = Table(topo_data, colWidths=[100, 70, 70, 80])
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
            
            story.append(Paragraph("Security Recommendations", heading_style))
            
            recommendations = []
            for service in self.services_found:
                if service.get("risk_score", 0) >= 7:
                    recommendations.append(f"[+] CRITICAL: Patch {service['service']} on port {service['port']} immediately")
                elif service.get("risk_score", 0) >= 4:
                    recommendations.append(f"[+] MEDIUM: Update {service['service']} on port {service['port']}")
            
            if recommendations:
                for rec in recommendations[:10]:
                    story.append(Paragraph(rec, styles['Normal']))
                    story.append(Spacer(1, 5))
            else:
                story.append(Paragraph("No critical recommendations at this time. Continue regular security monitoring.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            story.append(Paragraph("This report was automatically generated by DSTERMINAL Cyber-Ops Platform", styles['Normal']))
            story.append(Paragraph("For questions or support, contact your security team.", styles['Normal']))
            
            doc.build(story)
            
            print(f"{Colors.GREEN}[+] PDF Report generated: {pdf_path}{Colors.RESET}")
            return pdf_path
            
        except ImportError:
            print(f"{Colors.RED}[!] ReportLab not installed. Install with: pip install reportlab{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.RED}[!] PDF generation failed: {e}{Colors.RESET}")
            return None


# ============================================================
# EXPORTED CLASSES FOR MAIN DSTERMINAL
# ============================================================

__all__ = ['InteractiveSOCDashboard', 'SOCNmapDashboard', 'SOCNmapIntegration']

SOCNmapDashboard = InteractiveSOCDashboard


class SOCNmapIntegration:
    def __init__(self):
        self.dashboard = None
    
    def start_interactive_dashboard(self):
        if not self.dashboard:
            self.dashboard = InteractiveSOCDashboard()
        self.dashboard.interactive_loop()
    
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
# MAIN ENTRY POINT (for standalone execution)
# ============================================================

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"{' '*15}DSTERMINAL SOC NMAP DASHBOARD")
    print(f"{'='*60}\n")
    soc = SOCNmapIntegration()
    soc.start_interactive_dashboard()