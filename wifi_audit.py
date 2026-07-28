# =====================================================================
    def wifi_audit(self, interface=None):
        """
        Perform comprehensive WiFi security audit with generative writing effect.
        
        This function performs a complete WiFi security assessment including:
        - Network interface detection and analysis
        - Access point scanning and enumeration
        - Security protocol analysis (WEP, WPA, WPA2, WPA3)
        - Signal strength mapping
        - Channel analysis
        - Rogue AP detection
        - Security recommendations
        
        Args:
            interface (str, optional): Network interface to use. If None, auto-detects.
        
        Returns:
            dict: Comprehensive audit results including APs, security findings, and recommendations
        """
        import platform
        import subprocess
        import re
        import socket
        from datetime import datetime
        from pathlib import Path
        import time
        import random
        import sys
        
        # ========================================================================
        # Define type_text as a proper method before using it
        # ========================================================================
        def type_text(text, delay=0.03, variance=0.02, color=None):
            """
            Print text with a human-like typing effect.
            
            Args:
                text (str): Text to display
                delay (float): Base delay between characters (seconds)
                variance (float): Random variance to add to delay
                color (str): Colorama color code to use
            """
            # If color is provided, print it first
            if color:
                print(color, end='', flush=True)
            
            # Process the text character by character
            i = 0
            while i < len(text):
                # Check for ANSI escape sequences (like [92m, [0m, etc.)
                if i < len(text) - 1 and text[i] == '[' and text[i+1].isdigit():
                    # Find the end of the escape sequence
                    j = i + 1
                    while j < len(text) and (text[j].isdigit() or text[j] == ';'):
                        j += 1
                    if j < len(text) and text[j] == 'm':
                        # Print the entire escape sequence at once
                        esc_seq = text[i:j+1]
                        # Check if it's a color code or reset
                        if esc_seq == '[0m':
                            print(Style.RESET_ALL, end='', flush=True)
                        elif esc_seq.startswith('[9') or esc_seq.startswith('[3') or esc_seq.startswith('[1;'):
                            # Map common color codes
                            color_map = {
                                '[92m': Fore.LIGHTGREEN_EX,
                                '[91m': Fore.LIGHTRED_EX,
                                '[96m': Fore.LIGHTCYAN_EX,
                                '[95m': Fore.LIGHTMAGENTA_EX,
                                '[94m': Fore.LIGHTBLUE_EX,
                                '[93m': Fore.LIGHTYELLOW_EX,
                                '[32m': Fore.GREEN,
                                '[31m': Fore.RED,
                                '[33m': Fore.YELLOW,
                                '[34m': Fore.BLUE,
                                '[35m': Fore.MAGENTA,
                                '[36m': Fore.CYAN,
                                '[37m': Fore.WHITE,
                                '[1;32m': Fore.LIGHTGREEN_EX,
                                '[1;31m': Fore.LIGHTRED_EX,
                                '[1;33m': Fore.LIGHTYELLOW_EX,
                                '[1;34m': Fore.LIGHTBLUE_EX,
                                '[1;35m': Fore.LIGHTMAGENTA_EX,
                                '[1;36m': Fore.LIGHTCYAN_EX,
                                '[1;37m': Fore.LIGHTWHITE_EX,
                            }
                            if esc_seq in color_map:
                                print(color_map[esc_seq], end='', flush=True)
                            else:
                                # If unknown, just print the raw sequence
                                print(f'\033{esc_seq}', end='', flush=True)
                        else:
                            # Print other escape sequences
                            print(f'\033{esc_seq}', end='', flush=True)
                        i = j + 1
                        continue
                    else:
                        # Not a valid escape sequence, print character normally
                        print(text[i], end='', flush=True)
                        # Add random variation to typing speed
                        time.sleep(delay + (random.random() * variance))
                        i += 1
                else:
                    # Print character normally
                    print(text[i], end='', flush=True)
                    # Add random variation to typing speed
                    time.sleep(delay + (random.random() * variance))
                    i += 1
            
            # Reset color if it was set
            if color:
                print(Style.RESET_ALL, end='', flush=True)
            print()  # Newline after text
        
        def type_line(text, delay=0.02, variance=0.015, color=None):
            """Print a line with typing effect, then newline."""
            type_text(text, delay, variance, color)
        
        def type_status(text, delay=0.03, variance=0.02, color=Fore.CYAN):
            """Print a status message with typing effect and a decorative prefix."""
            type_text(f"[*] {text}", delay, variance, color)
        
        def type_success(text, delay=0.02, variance=0.015, color=Fore.GREEN):
            """Print a success message with typing effect."""
            type_text(f"[+] {text}", delay, variance, color)
        
        def type_error(text, delay=0.03, variance=0.02, color=Fore.RED):
            """Print an error message with typing effect."""
            type_text(f"[!] {text}", delay, variance, color)
        
        def type_warning(text, delay=0.03, variance=0.02, color=Fore.YELLOW):
            """Print a warning message with typing effect."""
            type_text(f"[?] {text}", delay, variance, color)
        
        def type_finding(text, severity="INFO", delay=0.02, variance=0.015):
            """Print a finding with appropriate color and severity prefix."""
            colors = {
                "CRITICAL": Fore.RED,
                "HIGH": Fore.YELLOW,
                "MEDIUM": Fore.CYAN,
                "LOW": Fore.GREEN,
                "INFO": Fore.WHITE
            }
            prefix = {
                "CRITICAL": "🚨",
                "HIGH": "⚠️",
                "MEDIUM": "🔍",
                "LOW": "ℹ️",
                "INFO": "📌"
            }
            color = colors.get(severity, Fore.WHITE)
            type_text(f"{prefix.get(severity, '')} {text}", delay, variance, color)
        
        def type_header(text, color=Fore.CYAN):
            """Print a header with typing effect."""
            type_text(f"\n{text}", 0.04, 0.02, color)
            type_text("━" * min(len(text), 70), 0.01, 0.005, Fore.CYAN)
        
        # ========================================================================
        # Cross-Platform Detection
        # ========================================================================
        system = platform.system().lower()
        
        # Results container
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'system': system,
            'hostname': socket.gethostname(),
            'interface': interface,
            'access_points': [],
            'security_findings': [],
            'recommendations': [],
            'summary': {
                'total_aps': 0,
                'secured_aps': 0,
                'open_aps': 0,
                'wep_aps': 0,
                'wpa_aps': 0,
                'wpa2_aps': 0,
                'wpa3_aps': 0,
                'highest_signal': 0,
                'rogue_aps': 0
            }
        }
        
        # ========================================================================
        # ASCII Art Banner - WiFi Audit
        # ========================================================================
        type_text("""
        ╔══════════════════════════════════════════════════════════════════════╗
        ║                                                                      ║
        ║    ██╗    ██╗██╗███████╗██╗    █████╗ ██╗   ██╗██████╗ ██╗████████╗ ║
        ║    ██║    ██║██║██╔════╝██║   ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝ ║
        ║    ██║ █╗ ██║██║█████╗  ██║   ███████║██║   ██║██   ██╔██║   ██║    ║
        ║    ██║███╗██║██║██╔══╝  ██║   ██╔══██║██║   ██║██   ██╗██║   ██║    ║
        ║    ╚███╔███╔╝██║██║     ██║   ██║  ██║╚██████╔╝██║█║██║██║   ██     ║
        ║     ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝    ║
        ║                                                                      ║
        ║                    🔐 WiFi Security Audit Engine                     ║
        ║                                                                      ║
        ╚══════════════════════════════════════════════════════════════════════╝
        """, delay=0.015, variance=0.01, color=Fore.CYAN)
        
        time.sleep(0.5)
        
        # ========================================================================
        # Security Impact Disclosure
        # ========================================================================
        type_header("🔐 Security Impact Assessment", Fore.CYAN)
        time.sleep(0.3)
        
        type_finding("Rogue Access Point Detection: Identifying unauthorized APs for MITM protection", "INFO")
        type_finding("Security Protocol Analysis: WEP, WPA, WPA2, WPA3 evaluation", "INFO")
        type_finding("Signal Intelligence: Physical location mapping for device detection", "INFO")
        type_finding("Compliance Verification: PCI-DSS, HIPAA, and regulatory standards", "INFO")
        
        time.sleep(0.5)
        
        # ========================================================================
        # Initialization Phase
        # ========================================================================
        type_header("\n🔧 Initializing Audit Engine", Fore.YELLOW)
        time.sleep(0.2)
        
        type_status(f"Platform: {system.upper()}", delay=0.04, color=Fore.CYAN)
        type_status(f"Host: {socket.gethostname()}", delay=0.04, color=Fore.CYAN)
        
        if interface:
            type_status(f"Interface: {interface}", delay=0.04, color=Fore.CYAN)
        else:
            type_status("Auto-detecting wireless interface...", delay=0.04, color=Fore.CYAN)
        
        time.sleep(0.5)
        
        # ========================================================================
        # Platform-Specific Implementation
        # ========================================================================
        try:
            if system == "windows":
                type_status("Using Windows native WiFi API", delay=0.04, color=Fore.CYAN)
                time.sleep(0.3)
                audit_results = self._wifi_audit_windows(interface, audit_results, type_status, type_finding, type_success, type_error, type_warning)
            elif system == "linux":
                type_status("Using Linux iwconfig/iwlist", delay=0.04, color=Fore.CYAN)
                time.sleep(0.3)
                audit_results = self._wifi_audit_linux(interface, audit_results, type_status, type_finding, type_success, type_error, type_warning)
            elif system == "darwin":  # macOS
                type_status("Using macOS airport utility", delay=0.04, color=Fore.CYAN)
                time.sleep(0.3)
                audit_results = self._wifi_audit_macos(interface, audit_results, type_status, type_finding, type_success, type_error, type_warning)
            else:
                type_error(f"Unsupported platform: {system}")
                audit_results['summary']['error'] = f"Unsupported platform: {system}"
                return audit_results
        
        except Exception as e:
            type_error(f"Error during WiFi audit: {str(e)}")
            audit_results['summary']['error'] = str(e)
            return audit_results
        
        # ========================================================================
        # Analysis Phase - Generative Processing
        # ========================================================================
        type_header("\n🔬 Analyzing Findings", Fore.MAGENTA)
        time.sleep(0.3)
        
        type_status("Processing access point data...", delay=0.04, color=Fore.CYAN)
        time.sleep(0.2)
        type_status("Evaluating security configurations...", delay=0.04, color=Fore.CYAN)
        time.sleep(0.2)
        type_status("Detecting rogue access points...", delay=0.04, color=Fore.CYAN)
        time.sleep(0.2)
        type_status("Generating threat intelligence...", delay=0.04, color=Fore.CYAN)
        time.sleep(0.3)
        
        # Analyze findings and generate security recommendations
        audit_results = self._analyze_wifi_findings(audit_results)
        
        # ========================================================================
        # Results Display Phase
        # ========================================================================
        type_header("\n📊 Audit Results", Fore.GREEN)
        time.sleep(0.3)
        
        # Display results with generative writing
        self._display_wifi_audit_results_generative(audit_results, type_text, type_finding, type_status, type_success, type_error)
        
        # ========================================================================
        # EXPORT Phase - ONLY export ONCE here
        # ========================================================================
        type_header("\n💾 Exporting Results", Fore.BLUE)
        time.sleep(0.3)
        
        export_path = self._export_wifi_audit_results(audit_results)
        if export_path:
            # The export function already prints success message, no need to duplicate
            audit_results['export_path'] = export_path
        else:
            type_warning("Failed to export results")
        
        type_text("\n🔐 WiFi Security Audit Complete", delay=0.04, color=Fore.CYAN)
        
        return audit_results

    def _wifi_audit_windows(self, interface, results, type_status=None, type_finding=None, type_success=None, type_error=None, type_warning=None):
        """Windows-specific WiFi audit implementation with generative output"""
        import subprocess
        import re
        import time
        import ctypes
        
        if type_status:
            type_status("Scanning for WiFi networks...", delay=0.04, color=Fore.YELLOW)
        time.sleep(0.5)
        
        # ========================================================================
        # Check for Admin Privileges
        # ========================================================================
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin and type_warning:
            type_warning("Running without admin privileges - scan results may be limited")
        
        # ========================================================================
        # DETECT ACTUAL WINDOWS WIRELESS INTERFACE
        # ========================================================================
        actual_interface = interface
        
        # If interface is None or looks like a Linux interface name, auto-detect
        if not interface or interface.startswith(('wlp', 'wlan', 'enp', 'eth')):
            try:
                if type_status:
                    type_status("Auto-detecting Windows wireless interface...", delay=0.04, color=Fore.CYAN)
                
                # Get list of wireless interfaces
                result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                    capture_output=True, text=True, timeout=10)
                
                # Parse interface name from output
                for line in result.stdout.split('\n'):
                    if 'Name' in line and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            iface_name = parts[1].strip()
                            if iface_name and iface_name != 'Name':
                                actual_interface = iface_name
                                if type_success:
                                    type_success(f"Found wireless interface: {actual_interface}")
                                break
                
                # If no interface found via netsh wlan, try alternative method
                if not actual_interface or actual_interface == interface:
                    result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                        capture_output=True, text=True, timeout=10)
                    for line in result.stdout.split('\n'):
                        if 'Wi-Fi' in line or 'Wireless' in line or 'WLAN' in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                potential_iface = parts[-1]
                                if potential_iface and potential_iface not in ['Connected', 'Disconnected', 'Enabled', 'Disabled']:
                                    actual_interface = potential_iface
                                    if type_success:
                                        type_success(f"Found wireless interface: {actual_interface}")
                                    break
                        
            except Exception as e:
                if type_warning:
                    type_warning(f"Interface detection warning: {str(e)}")
        
        # Fallback to common Windows wireless interface names
        if not actual_interface or actual_interface == interface:
            common_names = ['Wi-Fi', 'WiFi', 'Wireless Network Connection', 'WLAN']
            for name in common_names:
                try:
                    test_cmd = ['netsh', 'wlan', 'show', 'interfaces', f'name={name}']
                    result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
                    if 'There is no wireless interface' not in result.stdout and 'Name' in result.stdout:
                        actual_interface = name
                        if type_success:
                            type_success(f"Using wireless interface: {actual_interface}")
                        break
                except:
                    continue
        
        if not actual_interface:
            if type_error:
                type_error("No wireless interface found on Windows")
            return results
        
        # Update results with actual interface
        results['interface'] = actual_interface
        if type_status:
            type_status(f"Using interface: {actual_interface}", delay=0.04, color=Fore.CYAN)
        
        # ========================================================================
        # GET CONNECTED NETWORK INFO - FIXED BSSID PARSING
        # ========================================================================
        connected_network = {}
        connected_bssid_full = None
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                capture_output=True, text=True, timeout=10)
            
            for line in result.stdout.split('\n'):
                if 'SSID' in line and ':' in line:
                    ssid = line.split(':')[1].strip()
                    if ssid and ssid != 'SSID':
                        connected_network['ssid_from_interface'] = ssid
                if 'BSSID' in line and ':' in line:
                    # CRITICAL FIX: Store the FULL BSSID, not just a prefix
                    bssid_raw = line.split(':')[1].strip()
                    if bssid_raw and bssid_raw != 'BSSID':
                        # Remove spaces and convert to uppercase
                        connected_bssid_full = bssid_raw.replace(' ', '').upper()
                        connected_network['bssid'] = connected_bssid_full
                        # Debug output
                        if type_status:
                            type_status(f"Connected BSSID (full): {connected_bssid_full}", delay=0.04, color=Fore.CYAN)
                if 'Signal' in line and '%' in line:
                    signal_match = re.search(r'Signal\s+:\s+(\d+)%', line, re.IGNORECASE)
                    if signal_match:
                        connected_network['signal'] = int(signal_match.group(1))
                if 'Radio type' in line and ':' in line:
                    connected_network['radio_type'] = line.split(':')[1].strip()
                if 'Channel' in line and ':' in line:
                    channel_match = re.search(r'Channel\s+:\s+(\d+)', line, re.IGNORECASE)
                    if channel_match:
                        connected_network['channel'] = int(channel_match.group(1))
                if 'Authentication' in line and ':' in line:
                    auth = line.split(':')[1].strip()
                    connected_network['authentication'] = auth
                    if 'WPA3' in auth:
                        connected_network['security'] = 'WPA3'
                    elif 'WPA2' in auth:
                        connected_network['security'] = 'WPA2'
                    elif 'WPA' in auth:
                        connected_network['security'] = 'WPA'
                    elif 'WEP' in auth:
                        connected_network['security'] = 'WEP'
                    else:
                        connected_network['security'] = auth
            
            # Debug: Print connected network info
            if type_status:
                if connected_network.get('bssid'):
                    type_status(f"Connected BSSID (stored): {connected_network.get('bssid')}", delay=0.04, color=Fore.CYAN)
                type_status(f"Connected SSID (from interface): {connected_network.get('ssid_from_interface', 'Unknown')}", delay=0.04, color=Fore.CYAN)
                type_status(f"Connected Signal: {connected_network.get('signal', 'Unknown')}%", delay=0.04, color=Fore.CYAN)
                
        except Exception as e:
            if type_warning:
                type_warning(f"Failed to get connected network info: {str(e)}")
        
        # ========================================================================
        # SCAN FOR NETWORKS
        # ========================================================================
        all_networks = []
        
        try:
            # METHOD 1: netsh wlan show networks mode=bssid (requires admin)
            if type_status:
                type_status("Scanning for networks...", delay=0.04, color=Fore.CYAN)
            
            cmd = ['netsh', 'wlan', 'show', 'networks', 'mode=bssid']
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and result.stdout.strip():
                    all_networks.append(('netsh_bssid', result.stdout))
            except:
                pass
            
            # METHOD 2: netsh wlan show networks (basic - works without admin)
            try:
                result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], 
                                    capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and result.stdout.strip():
                    all_networks.append(('netsh_basic', result.stdout))
            except:
                pass
            
            # Process results
            output = None
            best_source = None
            
            # Prefer bssid mode
            for source, data in all_networks:
                if source == 'netsh_bssid' and data and 'SSID' in data and 'BSSID' in data:
                    output = data
                    best_source = 'bssid'
                    break
            
            # Fall back to basic mode
            if not output:
                for source, data in all_networks:
                    if source == 'netsh_basic' and data and 'SSID' in data:
                        output = data
                        best_source = 'basic'
                        break
            
            if not output:
                if type_warning:
                    type_warning("No network data received")
                return results
            
            if type_status:
                type_status(f"Processing scan results...", delay=0.04, color=Fore.CYAN)
            time.sleep(0.3)
            
            # Parse networks
            ap_count = 0
            if best_source == 'bssid':
                ap_count = self._parse_windows_bssid_output_fixed(
                    output, results, connected_network, type_finding
                )
            else:
                ap_count = self._parse_windows_basic_output(output, results, type_finding)
            
            if type_success:
                type_success(f"Found {ap_count} access points")
                
                # Find and show connected network info
                connected_ap = None
                for ap in results.get('access_points', []):
                    if ap.get('connected', False):
                        connected_ap = ap
                        break
                
                if connected_ap:
                    ssid = connected_ap.get('ssid', 'Unknown')
                    signal = connected_ap.get('signal', 'N/A')
                    bssid = connected_ap.get('bssid', 'Unknown')
                    type_status(f"Connected to: {ssid} (BSSID: {bssid}, Signal: {signal}%)", 
                            delay=0.04, color=Fore.GREEN)
                elif connected_network.get('bssid'):
                    bssid = connected_network.get('bssid')
                    signal = connected_network.get('signal', 'N/A')
                    ssid = connected_network.get('ssid_from_interface', 'Unknown')
                    type_status(f"Connected to: {ssid} (BSSID: {bssid}, Signal: {signal}%)", 
                            delay=0.04, color=Fore.GREEN)
                
        except subprocess.TimeoutExpired:
            if type_error:
                type_error("Scan timed out")
        except Exception as e:
            if type_error:
                type_error(f"Error during scan: {str(e)}")
        
        return results

    def _parse_windows_bssid_output_fixed(self, output, results, connected_network, type_finding=None):
        """Parse Windows netsh wlan show networks mode=bssid output - FIXED VERSION"""
        import re
        ap_count = 0
        
        # Get connected network info - ensure FULL BSSID is used
        connected_bssid = connected_network.get('bssid', '').upper().replace(' ', '')
        connected_signal = connected_network.get('signal', 0)
        connected_ssid_from_interface = connected_network.get('ssid_from_interface', '')
        
        # Debug output
        if type_finding:
            type_finding(f"Looking for connected BSSID: {connected_bssid}", "INFO")
            if connected_ssid_from_interface:
                type_finding(f"Looking for connected SSID: {connected_ssid_from_interface}", "INFO")
        
        # Split by SSID sections
        ssid_sections = re.split(r'SSID\s+\d+\s+:\s+', output)
        
        for section in ssid_sections:
            if not section.strip():
                continue
            
            ap = {}
            lines = section.split('\n')
            
            # Extract SSID
            if lines:
                ssid = lines[0].strip()
                if ssid and ssid not in ['', 'BSSID', 'Network']:
                    ap['ssid'] = ssid
                else:
                    ssid_match = re.search(r'SSID\s+\d+\s+:\s+(.+?)(?:\n|$)', section, re.IGNORECASE)
                    if ssid_match:
                        ap['ssid'] = ssid_match.group(1).strip()
                    else:
                        ap['ssid'] = '<Hidden>'
            
            # Extract BSSIDs and their signals - FIXED: Get FULL BSSID
            bssid_entries = re.findall(
                r'BSSID\s+\d+\s+:\s+([0-9a-fA-F:]+).*?Signal\s+:\s+(\d+)%', 
                section, re.DOTALL | re.IGNORECASE
            )
            
            if bssid_entries:
                # Get the FIRST BSSID (full MAC address)
                full_bssid = bssid_entries[0][0].upper().replace(' ', '')
                ap['bssid'] = full_bssid
                ap['signal'] = int(bssid_entries[0][1])
                
                # Check if this is the connected network by FULL BSSID match
                if connected_bssid and full_bssid == connected_bssid:
                    ap['connected'] = True
                    if connected_signal > 0:
                        ap['signal'] = connected_signal
                    if type_finding:
                        type_finding(f"✓ Found connected AP by BSSID: {full_bssid}", "INFO")
            
            # If no BSSID found, try alternate
            if not ap.get('bssid'):
                bssid_match = re.search(r'BSSID\s+\d+\s+:\s+([0-9a-fA-F:]+)', section, re.IGNORECASE)
                if bssid_match:
                    full_bssid = bssid_match.group(1).upper().replace(' ', '')
                    ap['bssid'] = full_bssid
                    
                    signal_match = re.search(r'Signal\s+:\s+(\d+)%', section, re.IGNORECASE)
                    if signal_match:
                        ap['signal'] = int(signal_match.group(1))
                    
                    # Check connected by FULL BSSID
                    if connected_bssid and full_bssid == connected_bssid:
                        ap['connected'] = True
                        if connected_signal > 0:
                            ap['signal'] = connected_signal
            
            # If still not connected by BSSID, check by SSID
            if not ap.get('connected', False) and connected_ssid_from_interface:
                ap_ssid = ap.get('ssid', '')
                if ap_ssid and ap_ssid == connected_ssid_from_interface:
                    ap['connected'] = True
                    if connected_signal > 0:
                        ap['signal'] = connected_signal
                    if connected_bssid and len(connected_bssid) >= 17:
                        ap['bssid'] = connected_bssid
                    if type_finding:
                        type_finding(f"✓ Found connected AP by SSID: {ap_ssid}", "INFO")
            
            # If connected, apply connected network settings
            if ap.get('connected', False):
                if connected_network.get('security'):
                    ap['security'] = connected_network['security']
                if connected_network.get('channel'):
                    ap['channel'] = connected_network['channel']
                if connected_bssid and len(connected_bssid) >= 17:
                    ap['bssid'] = connected_bssid
            
            # Extract Channel
            if not ap.get('channel'):
                channel_match = re.search(r'Channel\s+:\s+(\d+)', section, re.IGNORECASE)
                if channel_match:
                    ap['channel'] = int(channel_match.group(1))
            
            # Extract Authentication
            if not ap.get('security'):
                auth_match = re.search(r'Authentication\s+:\s+(.+)', section, re.IGNORECASE)
                if auth_match:
                    auth = auth_match.group(1).strip()
                    ap['authentication'] = auth
                    
                    if 'WPA3' in auth:
                        ap['security'] = 'WPA3'
                    elif 'WPA2' in auth:
                        ap['security'] = 'WPA2'
                    elif 'WPA' in auth:
                        ap['security'] = 'WPA'
                    elif 'WEP' in auth:
                        ap['security'] = 'WEP'
                    elif 'Open' in auth or 'None' in auth:
                        ap['security'] = 'Open'
                    else:
                        ap['security'] = auth
            
            # Extract Encryption
            enc_match = re.search(r'Encryption\s+:\s+(.+)', section, re.IGNORECASE)
            if enc_match:
                ap['encryption'] = enc_match.group(1).strip()
            
            if ap.get('ssid') or ap.get('bssid'):
                results['access_points'].append(ap)
                ap_count += 1
                
                if type_finding:
                    sig = ap.get('signal', 0)
                    is_connected = ap.get('connected', False)
                    
                    if is_connected and connected_signal > 0:
                        sig = connected_signal
                    
                    if sig > 50:
                        sig_indicator = "📶"
                    elif sig > 30:
                        sig_indicator = "📡"
                    else:
                        sig_indicator = "📻"
                    
                    display_name = ap.get('ssid', '<Hidden>')
                    bssid_display = ap.get('bssid', 'Unknown')
                    
                    if display_name == '<Hidden>' and bssid_display != 'Unknown':
                        display_name = f"<Hidden> ({bssid_display[:8]})"
                    
                    connected_marker = " [CONNECTED]" if is_connected else ""
                    
                    type_finding(
                        f"{sig_indicator} {display_name}{connected_marker} - Signal: {sig}% - {ap.get('security', 'Unknown')}",
                        "INFO"
                    )
        
        return ap_count

    def _parse_windows_bssid_output_with_connected(self, output, results, connected_network, type_finding=None):
        """Parse Windows netsh wlan show networks mode=bssid output with connected network info"""
        import re
        ap_count = 0
        
        # Get connected network info for matching
        connected_bssid = connected_network.get('bssid', '').upper().replace(' ', '')
        connected_signal = connected_network.get('signal', 0)
        connected_ssid_from_interface = connected_network.get('ssid_from_interface', '')
        
        # Split by SSID sections
        ssid_sections = re.split(r'SSID\s+\d+\s+:\s+', output)
        
        for section in ssid_sections:
            if not section.strip():
                continue
            
            ap = {}
            lines = section.split('\n')
            
            # Extract SSID (first line)
            if lines:
                ssid = lines[0].strip()
                if ssid and ssid not in ['', 'BSSID', 'Network']:
                    ap['ssid'] = ssid
                else:
                    # Try to find SSID in the section
                    ssid_match = re.search(r'SSID\s+\d+\s+:\s+(.+?)(?:\n|$)', section, re.IGNORECASE)
                    if ssid_match:
                        ap['ssid'] = ssid_match.group(1).strip()
                    else:
                        ap['ssid'] = '<Hidden>'
            
            # Extract BSSIDs and their signals
            bssid_entries = re.findall(
                r'BSSID\s+\d+\s+:\s+([0-9a-fA-F:]+).*?Signal\s+:\s+(\d+)%', 
                section, re.DOTALL | re.IGNORECASE
            )
            
            if bssid_entries:
                # Get the first BSSID
                ap['bssid'] = bssid_entries[0][0].upper().replace(' ', '')
                ap['signal'] = int(bssid_entries[0][1])
            
            # If no BSSID found in the section, try alternate method
            if not ap.get('bssid'):
                bssid_match = re.search(r'BSSID\s+\d+\s+:\s+([0-9a-fA-F:]+)', section, re.IGNORECASE)
                if bssid_match:
                    ap['bssid'] = bssid_match.group(1).upper().replace(' ', '')
                    
                    # Try to find signal for this BSSID
                    signal_match = re.search(r'Signal\s+:\s+(\d+)%', section, re.IGNORECASE)
                    if signal_match:
                        ap['signal'] = int(signal_match.group(1))
            
            # ========================================================================
            # CONNECTED NETWORK MATCHING - FULL BSSID MATCHING
            # ========================================================================
            ap_bssid = ap.get('bssid', '').upper().replace(' ', '')
            ap_ssid = ap.get('ssid', '')
            is_connected = False
            
            # Match by FULL BSSID - this is the most reliable method
            if connected_bssid and ap_bssid:
                if ap_bssid == connected_bssid:
                    is_connected = True
                # Also try matching by SSID from connected interface
                elif connected_ssid_from_interface and ap_ssid == connected_ssid_from_interface:
                    is_connected = True
            
            # Match by SSID if BSSID matching fails
            if not is_connected and connected_ssid_from_interface:
                if ap_ssid and connected_ssid_from_interface and ap_ssid == connected_ssid_from_interface:
                    is_connected = True
            
            if is_connected:
                # Use connected network signal
                if connected_signal > 0:
                    ap['signal'] = connected_signal
                if connected_network.get('security'):
                    ap['security'] = connected_network['security']
                if connected_network.get('channel'):
                    ap['channel'] = connected_network['channel']
                # Use the full BSSID from connected network if available
                if connected_bssid and len(connected_bssid) >= 17:
                    ap['bssid'] = connected_bssid
                # Mark as connected
                ap['connected'] = True
            
            # Extract Channel if not already set
            if not ap.get('channel'):
                channel_match = re.search(r'Channel\s+:\s+(\d+)', section, re.IGNORECASE)
                if channel_match:
                    ap['channel'] = int(channel_match.group(1))
            
            # Extract Authentication if not already set
            if not ap.get('security'):
                auth_match = re.search(r'Authentication\s+:\s+(.+)', section, re.IGNORECASE)
                if auth_match:
                    auth = auth_match.group(1).strip()
                    ap['authentication'] = auth
                    
                    if 'WPA3' in auth:
                        ap['security'] = 'WPA3'
                    elif 'WPA2' in auth:
                        ap['security'] = 'WPA2'
                    elif 'WPA' in auth:
                        ap['security'] = 'WPA'
                    elif 'WEP' in auth:
                        ap['security'] = 'WEP'
                    elif 'Open' in auth or 'None' in auth:
                        ap['security'] = 'Open'
                    else:
                        ap['security'] = auth
            
            # Extract Encryption
            enc_match = re.search(r'Encryption\s+:\s+(.+)', section, re.IGNORECASE)
            if enc_match:
                ap['encryption'] = enc_match.group(1).strip()
            
            if ap.get('ssid') or ap.get('bssid'):
                results['access_points'].append(ap)
                ap_count += 1
                
                if type_finding:
                    sig = ap.get('signal', 0)
                    is_connected = ap.get('connected', False)
                    
                    # For connected network, use connected signal
                    if is_connected and connected_signal > 0:
                        sig = connected_signal
                    
                    if sig > 50:
                        sig_indicator = "📶"
                    elif sig > 30:
                        sig_indicator = "📡"
                    else:
                        sig_indicator = "📻"
                    
                    # Use the SSID from the scan results
                    display_name = ap.get('ssid', '<Hidden>')
                    bssid_display = ap.get('bssid', 'Unknown')
                    
                    # Only use BSSID as display if SSID is truly hidden
                    if display_name == '<Hidden>' and bssid_display != 'Unknown':
                        display_name = f"<Hidden> ({bssid_display[:8]})"
                    
                    # Mark connected network
                    connected_marker = " [CONNECTED]" if is_connected else ""
                    
                    type_finding(
                        f"{sig_indicator} {display_name}{connected_marker} - Signal: {sig}% - {ap.get('security', 'Unknown')}",
                        "INFO"
                    )
        
        return ap_count

    def _wifi_audit_windows(self, interface, results, type_status=None, type_finding=None, type_success=None, type_error=None, type_warning=None):
        """Windows-specific WiFi audit implementation with generative output"""
        import subprocess
        import re
        import time
        import ctypes
        
        if type_status:
            type_status("Scanning for WiFi networks...", delay=0.04, color=Fore.YELLOW)
        time.sleep(0.5)
        
        # ========================================================================
        # Check for Admin Privileges
        # ========================================================================
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin and type_warning:
            type_warning("Running without admin privileges - scan results may be limited")
        
        # ========================================================================
        # DETECT ACTUAL WINDOWS WIRELESS INTERFACE
        # ========================================================================
        actual_interface = interface
        
        # If interface is None or looks like a Linux interface name, auto-detect
        if not interface or interface.startswith(('wlp', 'wlan', 'enp', 'eth')):
            try:
                if type_status:
                    type_status("Auto-detecting Windows wireless interface...", delay=0.04, color=Fore.CYAN)
                
                # Get list of wireless interfaces
                result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                    capture_output=True, text=True, timeout=10)
                
                # Parse interface name from output
                for line in result.stdout.split('\n'):
                    if 'Name' in line and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            iface_name = parts[1].strip()
                            if iface_name and iface_name != 'Name':
                                actual_interface = iface_name
                                if type_success:
                                    type_success(f"Found wireless interface: {actual_interface}")
                                break
                
                # If no interface found via netsh wlan, try alternative method
                if not actual_interface or actual_interface == interface:
                    result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                        capture_output=True, text=True, timeout=10)
                    for line in result.stdout.split('\n'):
                        if 'Wi-Fi' in line or 'Wireless' in line or 'WLAN' in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                potential_iface = parts[-1]
                                if potential_iface and potential_iface not in ['Connected', 'Disconnected', 'Enabled', 'Disabled']:
                                    actual_interface = potential_iface
                                    if type_success:
                                        type_success(f"Found wireless interface: {actual_interface}")
                                    break
                        
            except Exception as e:
                if type_warning:
                    type_warning(f"Interface detection warning: {str(e)}")
        
        # Fallback to common Windows wireless interface names
        if not actual_interface or actual_interface == interface:
            common_names = ['Wi-Fi', 'WiFi', 'Wireless Network Connection', 'WLAN']
            for name in common_names:
                try:
                    test_cmd = ['netsh', 'wlan', 'show', 'interfaces', f'name={name}']
                    result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
                    if 'There is no wireless interface' not in result.stdout and 'Name' in result.stdout:
                        actual_interface = name
                        if type_success:
                            type_success(f"Using wireless interface: {actual_interface}")
                        break
                except:
                    continue
        
        if not actual_interface:
            if type_error:
                type_error("No wireless interface found on Windows")
            return results
        
        # Update results with actual interface
        results['interface'] = actual_interface
        if type_status:
            type_status(f"Using interface: {actual_interface}", delay=0.04, color=Fore.CYAN)
        
        # ========================================================================
        # GET CONNECTED NETWORK INFO (for signal strength)
        # ========================================================================
        connected_network = {}
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                capture_output=True, text=True, timeout=10)
            
            for line in result.stdout.split('\n'):
                if 'SSID' in line and ':' in line:
                    ssid = line.split(':')[1].strip()
                    if ssid and ssid != 'SSID':
                        connected_network['ssid_from_interface'] = ssid
                if 'BSSID' in line and ':' in line:
                    bssid = line.split(':')[1].strip()
                    if bssid and bssid != 'BSSID':
                        # Normalize BSSID format
                        bssid = bssid.replace(' ', '').upper()
                        connected_network['bssid'] = bssid
                        # Store short version for matching
                        connected_network['bssid_short'] = bssid[:2]  # First 2 chars
                if 'Signal' in line and '%' in line:
                    signal_match = re.search(r'Signal\s+:\s+(\d+)%', line, re.IGNORECASE)
                    if signal_match:
                        connected_network['signal'] = int(signal_match.group(1))
                if 'Radio type' in line and ':' in line:
                    connected_network['radio_type'] = line.split(':')[1].strip()
                if 'Channel' in line and ':' in line:
                    channel_match = re.search(r'Channel\s+:\s+(\d+)', line, re.IGNORECASE)
                    if channel_match:
                        connected_network['channel'] = int(channel_match.group(1))
                if 'Authentication' in line and ':' in line:
                    auth = line.split(':')[1].strip()
                    connected_network['authentication'] = auth
                    if 'WPA3' in auth:
                        connected_network['security'] = 'WPA3'
                    elif 'WPA2' in auth:
                        connected_network['security'] = 'WPA2'
                    elif 'WPA' in auth:
                        connected_network['security'] = 'WPA'
                    elif 'WEP' in auth:
                        connected_network['security'] = 'WEP'
                    else:
                        connected_network['security'] = auth
            
            # Debug: Print connected network info
            if type_status:
                type_status(f"Connected BSSID: {connected_network.get('bssid', 'Unknown')}", delay=0.04, color=Fore.CYAN)
                type_status(f"Connected SSID (from interface): {connected_network.get('ssid_from_interface', 'Unknown')}", delay=0.04, color=Fore.CYAN)
                type_status(f"Connected Signal: {connected_network.get('signal', 'Unknown')}%", delay=0.04, color=Fore.CYAN)
                
        except Exception as e:
            if type_warning:
                type_warning(f"Failed to get connected network info: {str(e)}")
        
        # ========================================================================
        # SCAN FOR NETWORKS - MULTIPLE METHODS
        # ========================================================================
        all_networks = []
        
        try:
            # METHOD 1: netsh wlan show networks mode=bssid (requires admin)
            if type_status:
                type_status("Scanning for networks (method 1)...", delay=0.04, color=Fore.CYAN)
            
            cmd = ['netsh', 'wlan', 'show', 'networks', 'mode=bssid']
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and result.stdout.strip():
                    all_networks.append(('netsh_bssid', result.stdout))
            except:
                pass
            
            # METHOD 2: netsh wlan show networks (basic - works without admin)
            if type_status:
                type_status("Scanning for networks (method 2)...", delay=0.04, color=Fore.CYAN)
            
            try:
                result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], 
                                    capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and result.stdout.strip():
                    all_networks.append(('netsh_basic', result.stdout))
            except:
                pass
            
            # METHOD 3: netsh wlan show networks with interface
            if actual_interface:
                if type_status:
                    type_status(f"Scanning with interface {actual_interface}...", delay=0.04, color=Fore.CYAN)
                
                try:
                    result = subprocess.run(['netsh', 'wlan', 'show', 'networks', f'interface={actual_interface}'], 
                                        capture_output=True, text=True, timeout=30)
                    if result.returncode == 0 and result.stdout.strip():
                        all_networks.append(('netsh_interface', result.stdout))
                except:
                    pass
            
            # ========================================================================
            # PROCESS RESULTS FROM THE BEST SOURCE
            # ========================================================================
            output = None
            best_source = None
            
            # Prefer bssid mode (most detailed) if available and has data
            for source, data in all_networks:
                if source == 'netsh_bssid' and data and 'SSID' in data and 'BSSID' in data:
                    output = data
                    best_source = 'bssid'
                    break
            
            # Fall back to basic mode
            if not output:
                for source, data in all_networks:
                    if source == 'netsh_basic' and data and 'SSID' in data:
                        output = data
                        best_source = 'basic'
                        break
            
            # Fall back to interface mode
            if not output:
                for source, data in all_networks:
                    if source == 'netsh_interface' and data and 'SSID' in data:
                        output = data
                        best_source = 'interface'
                        break
            
            if not output:
                if type_warning:
                    type_warning("No network data received from any scan method")
                
                # Show diagnostic info
                if type_status:
                    type_status("Diagnostic: Check if WiFi is enabled", delay=0.04, color=Fore.YELLOW)
                    type_status("Run: netsh wlan show interfaces", delay=0.04, color=Fore.YELLOW)
                return results
            
            if type_status:
                type_status(f"Processing scan results (source: {best_source})...", delay=0.04, color=Fore.CYAN)
            time.sleep(0.3)
            
            # ========================================================================
            # PARSE NETWORKS WITH CONNECTED NETWORK INFO
            # ========================================================================
            ap_count = 0
            
            # Parse based on source type
            if best_source == 'bssid':
                # Parse BSSID mode output - more detailed
                ap_count = self._parse_windows_bssid_output_with_connected(
                    output, results, connected_network, type_finding
                )
            else:
                # Parse basic mode output
                ap_count = self._parse_windows_basic_output(output, results, type_finding)
            
            if type_success:
                type_success(f"Found {ap_count} access points")
                
                # Find and show connected network info from scanned results
                connected_ap = None
                for ap in results.get('access_points', []):
                    if ap.get('connected', False):
                        connected_ap = ap
                        break
                
                if connected_ap:
                    ssid = connected_ap.get('ssid', 'Unknown')
                    signal = connected_ap.get('signal', 'N/A')
                    type_status(f"Connected to: {ssid} (Signal: {signal}%)", 
                            delay=0.04, color=Fore.GREEN)
                elif connected_network.get('bssid'):
                    type_status(f"Connected to BSSID: {connected_network.get('bssid')} (Signal: {connected_network.get('signal', 'N/A')}%)", 
                            delay=0.04, color=Fore.GREEN)
                
            if ap_count == 0 and type_warning:
                type_warning("No access points found. Possible reasons:")
                type_warning("  - WiFi adapter is disabled or not connected")
                type_warning("  - Need admin privileges for full scan")
                type_warning("  - No networks in range")
                type_warning("  - WLAN service not running")
                
                # Check WLAN service
                try:
                    result = subprocess.run(['sc', 'query', 'wlansvc'], capture_output=True, text=True, timeout=5)
                    if 'RUNNING' not in result.stdout:
                        type_warning("  - WLAN AutoConfig service is NOT running")
                    else:
                        type_status("  - WLAN AutoConfig service is running", delay=0.04, color=Fore.GREEN)
                except:
                    pass
            
        except subprocess.TimeoutExpired:
            if type_error:
                type_error("Scan timed out - network may be slow or unresponsive")
        except Exception as e:
            if type_error:
                type_error(f"Error during scan: {str(e)}")
        
        return results

    def _parse_windows_bssid_output_with_connected(self, output, results, connected_network, type_finding=None):
        """Parse Windows netsh wlan show networks mode=bssid output with connected network info"""
        import re
        ap_count = 0
        
        # Get connected network info for matching
        connected_bssid = connected_network.get('bssid', '').upper().replace(' ', '')
        connected_bssid_short = connected_bssid[:2]  # First 2 chars like "B2"
        connected_signal = connected_network.get('signal', 0)
        connected_ssid_from_interface = connected_network.get('ssid_from_interface', '')
        
        # Split by SSID sections
        ssid_sections = re.split(r'SSID\s+\d+\s+:\s+', output)
        
        for section in ssid_sections:
            if not section.strip():
                continue
            
            ap = {}
            lines = section.split('\n')
            
            # Extract SSID (first line)
            if lines:
                ssid = lines[0].strip()
                if ssid and ssid not in ['', 'BSSID', 'Network']:
                    ap['ssid'] = ssid
                else:
                    # Try to find SSID in the section
                    ssid_match = re.search(r'SSID\s+\d+\s+:\s+(.+?)(?:\n|$)', section, re.IGNORECASE)
                    if ssid_match:
                        ap['ssid'] = ssid_match.group(1).strip()
                    else:
                        ap['ssid'] = '<Hidden>'
            
            # Extract BSSIDs and their signals
            bssid_entries = re.findall(
                r'BSSID\s+\d+\s+:\s+([0-9a-fA-F:]+).*?Signal\s+:\s+(\d+)%', 
                section, re.DOTALL | re.IGNORECASE
            )
            
            if bssid_entries:
                # Get the first BSSID
                ap['bssid'] = bssid_entries[0][0].upper().replace(' ', '')
                ap['signal'] = int(bssid_entries[0][1])
            
            # If no BSSID found in the section, try alternate method
            if not ap.get('bssid'):
                bssid_match = re.search(r'BSSID\s+\d+\s+:\s+([0-9a-fA-F:]+)', section, re.IGNORECASE)
                if bssid_match:
                    ap['bssid'] = bssid_match.group(1).upper().replace(' ', '')
                    
                    # Try to find signal for this BSSID
                    signal_match = re.search(r'Signal\s+:\s+(\d+)%', section, re.IGNORECASE)
                    if signal_match:
                        ap['signal'] = int(signal_match.group(1))
            
            # ========================================================================
            # CONNECTED NETWORK MATCHING - PRIORITIZE SCAN RESULTS
            # ========================================================================
            ap_bssid = ap.get('bssid', '').upper().replace(' ', '')
            ap_ssid = ap.get('ssid', '')
            is_connected = False
            
            # Match by full BSSID
            if connected_bssid and ap_bssid:
                if ap_bssid == connected_bssid:
                    is_connected = True
                # Match by BSSID short (first 2 chars) if full BSSID matches partially
                elif len(ap_bssid) >= 2 and len(connected_bssid) >= 2:
                    if ap_bssid[:2] == connected_bssid[:2] and len(ap_bssid) >= 17:
                        is_connected = True
            
            # Match by SSID from scan results (this has the REAL name "REDMI 15C")
            if not is_connected and connected_bssid:
                # If BSSID from scan starts with connected BSSID prefix
                if ap_bssid and connected_bssid[:2] == ap_bssid[:2]:
                    is_connected = True
            
            if is_connected:
                # USE THE SSID FROM THE SCAN RESULTS (which is "REDMI 15C")
                # This is the REAL network name, not the truncated "b2"
                # Keep ap['ssid'] as-is from the scan results
                
                # Use connected network signal
                if connected_signal > 0:
                    ap['signal'] = connected_signal
                if connected_network.get('security'):
                    ap['security'] = connected_network['security']
                if connected_network.get('channel'):
                    ap['channel'] = connected_network['channel']
                # Use the full BSSID from connected network if available
                if connected_bssid and len(connected_bssid) >= 17:
                    ap['bssid'] = connected_bssid
                # Mark as connected
                ap['connected'] = True
                
                # IMPORTANT: DO NOT override ap['ssid'] - keep the scan result
                # The scan result has "REDMI 15C", which is correct
            
            # Extract Channel if not already set
            if not ap.get('channel'):
                channel_match = re.search(r'Channel\s+:\s+(\d+)', section, re.IGNORECASE)
                if channel_match:
                    ap['channel'] = int(channel_match.group(1))
            
            # Extract Authentication if not already set
            if not ap.get('security'):
                auth_match = re.search(r'Authentication\s+:\s+(.+)', section, re.IGNORECASE)
                if auth_match:
                    auth = auth_match.group(1).strip()
                    ap['authentication'] = auth
                    
                    if 'WPA3' in auth:
                        ap['security'] = 'WPA3'
                    elif 'WPA2' in auth:
                        ap['security'] = 'WPA2'
                    elif 'WPA' in auth:
                        ap['security'] = 'WPA'
                    elif 'WEP' in auth:
                        ap['security'] = 'WEP'
                    elif 'Open' in auth or 'None' in auth:
                        ap['security'] = 'Open'
                    else:
                        ap['security'] = auth
            
            # Extract Encryption
            enc_match = re.search(r'Encryption\s+:\s+(.+)', section, re.IGNORECASE)
            if enc_match:
                ap['encryption'] = enc_match.group(1).strip()
            
            if ap.get('ssid') or ap.get('bssid'):
                results['access_points'].append(ap)
                ap_count += 1
                
                if type_finding:
                    sig = ap.get('signal', 0)
                    is_connected = ap.get('connected', False)
                    
                    # For connected network, use connected signal
                    if is_connected and connected_signal > 0:
                        sig = connected_signal
                    
                    if sig > 50:
                        sig_indicator = "📶"
                    elif sig > 30:
                        sig_indicator = "📡"
                    else:
                        sig_indicator = "📻"
                    
                    # Use the SSID from the scan results (which is the real name)
                    display_name = ap.get('ssid', '<Hidden>')
                    
                    # Only use BSSID as display if SSID is truly hidden
                    if display_name == '<Hidden>' and ap.get('bssid'):
                        display_name = f"<Hidden> ({ap.get('bssid', '')[:8]})"
                    
                    # Mark connected network
                    connected_marker = " [CONNECTED]" if is_connected else ""
                    
                    type_finding(
                        f"{sig_indicator} {display_name}{connected_marker} - Signal: {sig}% - {ap.get('security', 'Unknown')}",
                        "INFO"
                    )
        
        return ap_count

    def _wifi_audit_linux(self, interface, results, type_status=None, type_finding=None, type_success=None, type_error=None, type_warning=None):
        """Linux-specific WiFi audit implementation with generative output"""
        if type_status:
            type_status("Scanning for WiFi networks...", delay=0.04, color=Fore.YELLOW)
        time.sleep(0.5)
        
        # If no interface specified, try to find one
        if not interface:
            try:
                if type_status:
                    type_status("Discovering wireless interfaces...", delay=0.04, color=Fore.CYAN)
                iwconfig_result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=10)
                for line in iwconfig_result.stdout.split('\n'):
                    if 'IEEE 802.11' in line:
                        interface = line.split()[0]
                        break
            except:
                pass
        
        if not interface:
            if type_error:
                type_error("No wireless interface found")
            return results
        
        if type_status:
            type_status(f"Using interface: {interface}", delay=0.04, color=Fore.CYAN)
        results['interface'] = interface
        
        try:
            # Check if connected
            iwconfig_result = subprocess.run(['iwconfig', interface], capture_output=True, text=True, timeout=10)
            if "unassociated" in iwconfig_result.stdout:
                if type_warning:
                    type_warning("Interface not associated with any network")
            
            # Scan for access points using iwlist
            if type_status:
                type_status("Performing passive scan...", delay=0.04, color=Fore.CYAN)
            time.sleep(0.5)
            
            scan_result = subprocess.run(['sudo', 'iwlist', interface, 'scan'], 
                                        capture_output=True, text=True, timeout=30)
            
            if scan_result.returncode != 0:
                if type_warning:
                    type_warning("Scan may require root privileges. Trying without sudo...")
                scan_result = subprocess.run(['iwlist', interface, 'scan'], 
                                            capture_output=True, text=True, timeout=30)
            
            output = scan_result.stdout
            
            # Parse the scan results
            cells = output.split('Cell ')
            
            if type_status:
                type_status("Analyzing discovered networks...", delay=0.04, color=Fore.CYAN)
            time.sleep(0.5)
            
            for cell in cells[1:]:  # Skip the first empty cell
                ap = {}
                
                # Extract BSSID/Address
                addr_match = re.search(r'Address: ([0-9a-fA-F:]+)', cell)
                if addr_match:
                    ap['bssid'] = addr_match.group(1).upper()
                
                # Extract ESSID
                essid_match = re.search(r'ESSID:"([^"]+)"', cell)
                if essid_match:
                    ap['ssid'] = essid_match.group(1)
                else:
                    ap['ssid'] = '<Hidden>'
                
                # Extract Channel
                channel_match = re.search(r'Channel:(\d+)', cell)
                if channel_match:
                    ap['channel'] = int(channel_match.group(1))
                
                # Extract Frequency
                freq_match = re.search(r'Frequency:([0-9.]+) GHz', cell)
                if freq_match:
                    ap['frequency'] = float(freq_match.group(1))
                
                # Extract Quality/Signal
                quality_match = re.search(r'Quality=(\d+)/(\d+)', cell)
                if quality_match:
                    quality = int(quality_match.group(1))
                    max_quality = int(quality_match.group(2))
                    ap['signal'] = int((quality / max_quality) * 100)
                
                # Extract Encryption key
                enc_match = re.search(r'Encryption key:(\w+)', cell)
                if enc_match:
                    ap['encryption'] = 'On' if enc_match.group(1) == 'on' else 'Off'
                
                # Extract IE (Information Elements) for security type
                if 'WPA2' in cell or 'IEEE 802.11i' in cell:
                    ap['security'] = 'WPA2'
                elif 'WPA' in cell:
                    ap['security'] = 'WPA'
                elif 'WEP' in cell:
                    ap['security'] = 'WEP'
                elif ap.get('encryption') == 'Off':
                    ap['security'] = 'Open'
                else:
                    ap['security'] = 'Unknown'
                
                if ap:
                    results['access_points'].append(ap)
                    if type_finding:
                        sig = ap.get('signal', 0)
                        sig_indicator = "📶" if sig > 50 else "📡" if sig > 30 else "📻"
                        type_finding(f"{sig_indicator} {ap.get('ssid', 'Unknown')} ({ap.get('bssid', '')}) - Signal: {sig}% - {ap.get('security', 'Unknown')}", "INFO")
            
            if type_success:
                type_success(f"Found {len(results['access_points'])} access points")
            
        except subprocess.TimeoutExpired:
            if type_error:
                type_error("Scan timed out")
        except Exception as e:
            if type_error:
                type_error(f"Error: {str(e)}")
        
        return results

    def _wifi_audit_macos(self, interface, results, type_status=None, type_finding=None, type_success=None, type_error=None, type_warning=None):
        """macOS-specific WiFi audit implementation with generative output"""
        if type_status:
            type_status("Scanning for WiFi networks...", delay=0.04, color=Fore.YELLOW)
        time.sleep(0.5)
        
        try:
            # Use airport command for scanning
            airport_path = None
            common_paths = [
                '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport',
                '/usr/sbin/airport'
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    airport_path = path
                    break
            
            if not airport_path:
                if type_warning:
                    type_warning("Airport command not found")
                return results
            
            if type_status:
                type_status("Using airport utility...", delay=0.04, color=Fore.CYAN)
            time.sleep(0.3)
            
            # Get WiFi networks
            scan_result = subprocess.run([airport_path, '-s'], capture_output=True, text=True, timeout=30)
            
            if scan_result.returncode != 0:
                if type_error:
                    type_error("Failed to scan networks")
                return results
            
            lines = scan_result.stdout.split('\n')
            
            # Parse header to find column positions
            if len(lines) > 1:
                header = lines[0]
                
                # Find column positions
                columns = ['SSID', 'BSSID', 'RSSI', 'CHANNEL', 'SECURITY']
                col_positions = {}
                
                for col in columns:
                    pos = header.find(col)
                    if pos != -1:
                        col_positions[col] = pos
                
                if type_status:
                    type_status("Analyzing discovered networks...", delay=0.04, color=Fore.CYAN)
                time.sleep(0.5)
                
                # Parse data lines
                for line in lines[1:]:
                    if not line.strip():
                        continue
                    
                    ap = {}
                    
                    # Extract SSID
                    if 'SSID' in col_positions:
                        ssid_start = col_positions['SSID']
                        ssid_end = col_positions.get('BSSID', len(line))
                        ap['ssid'] = line[ssid_start:ssid_end].strip()
                    
                    # Extract BSSID
                    if 'BSSID' in col_positions:
                        bssid_start = col_positions['BSSID']
                        bssid_end = col_positions.get('RSSI', len(line))
                        bssid = line[bssid_start:bssid_end].strip()
                        if bssid and ':' in bssid:
                            ap['bssid'] = bssid.upper()
                    
                    # Extract RSSI (signal)
                    if 'RSSI' in col_positions:
                        rssi_start = col_positions['RSSI']
                        rssi_end = col_positions.get('CHANNEL', len(line))
                        rssi = line[rssi_start:rssi_end].strip()
                        if rssi:
                            try:
                                ap['signal'] = int(rssi)
                            except:
                                pass
                    
                    # Extract Channel
                    if 'CHANNEL' in col_positions:
                        channel_start = col_positions['CHANNEL']
                        channel_end = col_positions.get('SECURITY', len(line))
                        channel = line[channel_start:channel_end].strip()
                        if channel:
                            try:
                                ap['channel'] = int(channel.split()[0])
                            except:
                                pass
                    
                    # Extract Security
                    if 'SECURITY' in col_positions:
                        sec_start = col_positions['SECURITY']
                        sec = line[sec_start:].strip()
                        if sec:
                            ap['security'] = sec
                            if 'WPA3' in sec:
                                ap['security_type'] = 'WPA3'
                            elif 'WPA2' in sec:
                                ap['security_type'] = 'WPA2'
                            elif 'WPA' in sec:
                                ap['security_type'] = 'WPA'
                            elif 'WEP' in sec:
                                ap['security_type'] = 'WEP'
                            elif sec == 'NONE' or 'Open' in sec:
                                ap['security_type'] = 'Open'
                    
                    if ap and 'ssid' in ap:
                        results['access_points'].append(ap)
                        if type_finding:
                            sig = ap.get('signal', 0)
                            sig_indicator = "📶" if sig > -50 else "📡" if sig > -70 else "📻"
                            type_finding(f"{sig_indicator} {ap.get('ssid', 'Unknown')} ({ap.get('bssid', '')}) - Signal: {sig} dBm - {ap.get('security_type', ap.get('security', 'Unknown'))}", "INFO")
            
            if type_success:
                type_success(f"Found {len(results['access_points'])} access points")
            
        except subprocess.TimeoutExpired:
            if type_error:
                type_error("Scan timed out")
        except Exception as e:
            if type_error:
                type_error(f"Error: {str(e)}")
        
        return results

    def _analyze_wifi_findings(self, results):
        """Analyze WiFi findings and generate security recommendations"""
        aps = results.get('access_points', [])
        
        # Update summary
        results['summary']['total_aps'] = len(aps)
        
        # Security analysis
        security_counts = {
            'Open': 0,
            'WEP': 0,
            'WPA': 0,
            'WPA2': 0,
            'WPA3': 0,
            'Unknown': 0
        }
        
        for ap in aps:
            sec = ap.get('security', 'Unknown')
            
            # Normalize security type
            if 'WPA3' in sec:
                sec_type = 'WPA3'
            elif 'WPA2' in sec:
                sec_type = 'WPA2'
            elif 'WPA' in sec:
                sec_type = 'WPA'
            elif 'WEP' in sec:
                sec_type = 'WEP'
            elif sec == 'Open' or sec == 'NONE' or sec == 'None':
                sec_type = 'Open'
            else:
                sec_type = 'Unknown'
            
            ap['security_type'] = sec_type
            security_counts[sec_type] = security_counts.get(sec_type, 0) + 1
            
            # Check for security findings
            finding = {
                'ap': ap.get('ssid', 'Unknown'),
                'bssid': ap.get('bssid', 'Unknown'),
                'finding': None,
                'severity': None
            }
            
            if sec_type == 'Open':
                finding['finding'] = 'Open network - No encryption'
                finding['severity'] = 'CRITICAL'
                results['security_findings'].append(finding)
            elif sec_type == 'WEP':
                finding['finding'] = 'WEP encryption - Vulnerable to attacks'
                finding['severity'] = 'HIGH'
                results['security_findings'].append(finding)
            elif sec_type == 'WPA':
                finding['finding'] = 'WPA encryption - Deprecated, vulnerable to KRACK'
                finding['severity'] = 'MEDIUM'
                results['security_findings'].append(finding)
            
            # Check for weak signal
            if ap.get('signal', 0) < 20 and ap.get('signal', 0) > 0:
                if sec_type != 'Open':
                    finding = {
                        'ap': ap.get('ssid', 'Unknown'),
                        'bssid': ap.get('bssid', 'Unknown'),
                        'finding': 'Weak signal strength - Possible rogue AP',
                        'severity': 'MEDIUM'
                    }
                    results['security_findings'].append(finding)
            
            # Check for duplicate SSID (potential rogue AP)
            ssid = ap.get('ssid', '')
            if ssid and ssid != '<Hidden>':
                same_ssid_aps = [a for a in aps if a.get('ssid') == ssid]
                if len(same_ssid_aps) > 1:
                    for other_ap in same_ssid_aps:
                        if other_ap.get('security_type') == 'Open' and ap.get('security_type') != 'Open':
                            finding = {
                                'ap': ssid,
                                'bssid': other_ap.get('bssid', 'Unknown'),
                                'finding': 'Potential rogue AP - Duplicate SSID with different security',
                                'severity': 'CRITICAL'
                            }
                            results['security_findings'].append(finding)
                            results['summary']['rogue_aps'] += 1
        
        # Update summary
        results['summary']['secured_aps'] = len(aps) - security_counts.get('Open', 0)
        results['summary']['open_aps'] = security_counts.get('Open', 0)
        results['summary']['wep_aps'] = security_counts.get('WEP', 0)
        results['summary']['wpa_aps'] = security_counts.get('WPA', 0)
        results['summary']['wpa2_aps'] = security_counts.get('WPA2', 0)
        results['summary']['wpa3_aps'] = security_counts.get('WPA3', 0)
        
        # Generate recommendations
        recommendations = []
        
        if security_counts.get('Open', 0) > 0:
            recommendations.append("🔴 Open networks detected - Disable open networks or implement WPA3 encryption")
        
        if security_counts.get('WEP', 0) > 0:
            recommendations.append("🔴 WEP encryption detected - Upgrade to WPA3 immediately (WEP can be cracked in minutes)")
        
        if security_counts.get('WPA', 0) > 0:
            recommendations.append("🟡 WPA encryption detected - Upgrade to WPA2/WPA3 (WPA is deprecated and vulnerable)")
        
        if results['summary'].get('rogue_aps', 0) > 0:
            recommendations.append("🔴 Rogue Access Points detected - Investigate and remove unauthorized APs immediately")
        
        if security_counts.get('WPA3', 0) == 0 and security_counts.get('WPA2', 0) > 0:
            recommendations.append("🟢 WPA2 detected - Consider upgrading to WPA3 for enhanced security")
        
        if not recommendations:
            recommendations.append("✅ No critical security issues found - Continue monitoring")
        
        results['recommendations'] = recommendations
        
        return results

    def _export_wifi_audit_results(self, results):
        """Export WiFi audit results to file - with duplicate prevention"""
        try:
            from datetime import datetime
            from pathlib import Path
            import json
            
            # Check if we've already exported this result set
            export_key = results.get('timestamp', '')
            if hasattr(self, '_last_export_key') and self._last_export_key == export_key:
                # Already exported these results
                return self._last_export_path if hasattr(self, '_last_export_path') else None
            
            export_dir = Path.home() / "DSTerminal" / "reports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = export_dir / f"wifi_audit_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Store the export key to prevent duplicates
            self._last_export_key = export_key
            self._last_export_path = str(filename)
            
            # Use console print instead of type_text to avoid duplication
            from colorama import Fore, Style
            print(f"\n{Fore.GREEN}✅ Results exported to: {filename}{Style.RESET_ALL}")
            return str(filename)
            
        except Exception as e:
            from colorama import Fore, Style
            print(f"{Fore.YELLOW}⚠️ Failed to export results: {str(e)}{Style.RESET_ALL}")
            return None
    
    def _display_wifi_audit_results_generative(self, results, type_text=None, type_finding=None, type_status=None, type_success=None, type_error=None):
        """Display WiFi audit results with hacking-style colorful centered boxes with glitch effects"""
        import shutil
        import time
        import random
        
        if not type_text:
            return self._display_wifi_audit_results_fallback(results)
        
        # Get terminal width for centering
        try:
            term_width = shutil.get_terminal_size().columns
            if term_width < 80:
                term_width = 80
            if term_width > 120:
                term_width = 120
        except:
            term_width = 80
        
        summary = results.get('summary', {})
        
        # ========================================================================
        # Summary Box - Hacking Style
        # ========================================================================
        type_text("\n", delay=0.01)
        
        # Top border
        top_border = "╔" + "═" * 38 + "╗"
        type_text(" " * ((term_width - 40) // 2) + top_border, delay=0.01, color=Fore.LIGHTGREEN_EX)
        
        # Header with blink effect
        header = "  ⚡ WIFI AUDIT SUMMARY ⚡  "
        type_text(" " * ((term_width - 40) // 2) + "║" + header + " " * (40 - len(header) - 2) + "║", delay=0.02, color=Fore.LIGHTGREEN_EX)
        
        # Bottom border
        bottom_border = "╚" + "═" * 38 + "╝"
        type_text(" " * ((term_width - 40) // 2) + bottom_border, delay=0.01, color=Fore.LIGHTGREEN_EX)
        time.sleep(0.2)
        
        # Stats with colors
        stats = [
            (f"  Total Access Points: {summary.get('total_aps', 0)}", Fore.LIGHTCYAN_EX),
            (f"  Secured Networks: {summary.get('secured_aps', 0)}", Fore.LIGHTGREEN_EX),
            (f"  Open Networks: {summary.get('open_aps', 0)}", Fore.LIGHTRED_EX),
        ]
        
        for stat, color in stats:
            type_text(" " * ((term_width - len(stat)) // 2) + stat, delay=0.02, color=color)
            time.sleep(0.05)
        
        time.sleep(0.3)
        
        # ========================================================================
        # Security Distribution Box
        # ========================================================================
        type_text("\n", delay=0.01)
        
        top_border = "┌" + "─" * 40 + "┐"
        type_text(" " * ((term_width - 42) // 2) + top_border, delay=0.01, color=Fore.LIGHTMAGENTA_EX)
        
        header = "  🔐 SECURITY DISTRIBUTION  "
        type_text(" " * ((term_width - 42) // 2) + "│" + header + " " * (42 - len(header) - 2) + "│", delay=0.02, color=Fore.LIGHTMAGENTA_EX)
        
        separator = "├" + "─" * 40 + "┤"
        type_text(" " * ((term_width - 42) // 2) + separator, delay=0.01, color=Fore.LIGHTMAGENTA_EX)
        
        security_types = {
            'WPA3': (summary.get('wpa3_aps', 0), Fore.LIGHTGREEN_EX),
            'WPA2': (summary.get('wpa2_aps', 0), Fore.GREEN),
            'WPA': (summary.get('wpa_aps', 0), Fore.YELLOW),
            'WEP': (summary.get('wep_aps', 0), Fore.LIGHTRED_EX),
            'Open': (summary.get('open_aps', 0), Fore.RED)
        }
        
        for sec_type, (count, color) in security_types.items():
            line = f"  {sec_type:<6}: {count}"
            type_text(" " * ((term_width - 42) // 2) + "│" + line + " " * (42 - len(line) - 2) + "│", delay=0.015, color=color)
            time.sleep(0.03)
        
        bottom_border = "└" + "─" * 40 + "┘"
        type_text(" " * ((term_width - 42) // 2) + bottom_border, delay=0.01, color=Fore.LIGHTMAGENTA_EX)
        time.sleep(0.3)
        
        # ========================================================================
        # Recommendations Box
        # ========================================================================
        recommendations = results.get('recommendations', [])
        if recommendations:
            type_text("\n", delay=0.01)
            
            top_border = "╔" + "═" * 47 + "╗"
            type_text(" " * ((term_width - 49) // 2) + top_border, delay=0.01, color=Fore.LIGHTCYAN_EX)
            
            header = "  💡 RECOMMENDATIONS  "
            type_text(" " * ((term_width - 49) // 2) + "║" + header + " " * (49 - len(header) - 2) + "║", delay=0.02, color=Fore.LIGHTCYAN_EX)
            
            separator = "╠" + "═" * 47 + "╣"
            type_text(" " * ((term_width - 49) // 2) + separator, delay=0.01, color=Fore.LIGHTCYAN_EX)
            
            for rec in recommendations[:3]:
                if '🔴' in rec:
                    color = Fore.LIGHTRED_EX
                elif '🟡' in rec:
                    color = Fore.LIGHTYELLOW_EX
                elif '🟢' in rec:
                    color = Fore.LIGHTGREEN_EX
                else:
                    color = Fore.WHITE
                
                line = "  " + rec[:45]
                type_text(" " * ((term_width - 49) // 2) + "║" + line + " " * (49 - len(line) - 2) + "║", delay=0.02, color=color)
                time.sleep(0.05)
            
            bottom_border = "╚" + "═" * 47 + "╝"
            type_text(" " * ((term_width - 49) // 2) + bottom_border, delay=0.01, color=Fore.LIGHTCYAN_EX)
        
        time.sleep(0.3)
        
        # ========================================================================
        # Security Score Box
        # ========================================================================
        total_aps = summary.get('total_aps', 0)
        if total_aps > 0:
            secured = summary.get('secured_aps', 0)
            security_score = int((secured / total_aps) * 100) if total_aps > 0 else 0
            
            type_text("\n", delay=0.01)
            
            top_border = "┌" + "─" * 35 + "┐"
            type_text(" " * ((term_width - 37) // 2) + top_border, delay=0.01, color=Fore.LIGHTYELLOW_EX)
            
            header = "  📊 SECURITY SCORE  "
            type_text(" " * ((term_width - 37) // 2) + "│" + header + " " * (37 - len(header) - 2) + "│", delay=0.02, color=Fore.LIGHTYELLOW_EX)
            
            separator = "├" + "─" * 35 + "┤"
            type_text(" " * ((term_width - 37) // 2) + separator, delay=0.01, color=Fore.LIGHTYELLOW_EX)
            
            if security_score >= 90:
                score_color = Fore.LIGHTGREEN_EX
                status_text = "EXCELLENT"
            elif security_score >= 70:
                score_color = Fore.LIGHTYELLOW_EX
                status_text = "GOOD"
            elif security_score >= 50:
                score_color = Fore.MAGENTA
                status_text = "FAIR"
            else:
                score_color = Fore.LIGHTRED_EX
                status_text = "POOR"
            
            line = f"  {security_score}/100 - {status_text}"
            type_text(" " * ((term_width - 37) // 2) + "│" + line + " " * (37 - len(line) - 2) + "│", delay=0.02, color=score_color)
            
            # Security bar
            bar_length = 25
            filled = int((security_score / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            if security_score >= 70:
                bar_color = Fore.LIGHTGREEN_EX
            elif security_score >= 50:
                bar_color = Fore.LIGHTYELLOW_EX
            else:
                bar_color = Fore.LIGHTRED_EX
            
            line = f"  [{bar}]"
            type_text(" " * ((term_width - 37) // 2) + "│" + line + " " * (37 - len(line) - 2) + "│", delay=0.01, color=bar_color)
            
            bottom_border = "└" + "─" * 35 + "┘"
            type_text(" " * ((term_width - 37) // 2) + bottom_border, delay=0.01, color=Fore.LIGHTYELLOW_EX)
        
        time.sleep(0.3)
        
        # ========================================================================
        # Access Points Box - IMPROVED DISPLAY
        # ========================================================================
        access_points = results.get('access_points', [])
        if access_points:
            type_text("\n", delay=0.01)
            
            top_border = "╔" + "═" * 65 + "╗"
            type_text(" " * ((term_width - 67) // 2) + top_border, delay=0.01, color=Fore.LIGHTBLUE_EX)
            
            header = "  📡 ACCESS POINTS  "
            type_text(" " * ((term_width - 67) // 2) + "║" + header + " " * (65 - len(header) - 2) + "║", delay=0.02, color=Fore.LIGHTBLUE_EX)
            
            separator = "╠" + "═" * 65 + "╣"
            type_text(" " * ((term_width - 67) // 2) + separator, delay=0.01, color=Fore.LIGHTBLUE_EX)
            
            # Sort access points: connected first, then by signal strength
            sorted_aps = sorted(access_points, key=lambda x: (not x.get('connected', False), x.get('signal', 0)), reverse=True)
            
            for ap in sorted_aps[:10]:
                # Get display name - ensure we display the full SSID
                ssid = ap.get('ssid', '<Hidden>')[:28]
                bssid = ap.get('bssid', 'Unknown')[:17]
                signal = ap.get('signal', 0)
                
                # Fix signal display
                if signal == 0 and bssid != 'Unknown':
                    signal_display = "N/A"
                else:
                    signal_display = f"{signal}%"
                
                security = ap.get('security_type', ap.get('security', 'Unknown'))[:10]
                
                # Color-code signal
                if signal > 70:
                    sig_color = Fore.LIGHTGREEN_EX
                    sig_indicator = "📶"
                elif signal > 40:
                    sig_color = Fore.LIGHTYELLOW_EX
                    sig_indicator = "📡"
                else:
                    sig_color = Fore.LIGHTRED_EX
                    sig_indicator = "📻"
                
                # Color-code security
                if security in ['Open', 'WEP']:
                    sec_color = Fore.LIGHTRED_EX
                elif security == 'WPA':
                    sec_color = Fore.LIGHTYELLOW_EX
                else:
                    sec_color = Fore.LIGHTGREEN_EX
                
                # Add connected marker
                connected_marker = "🔗" if ap.get('connected', False) else " "
                
                # Build display line with proper spacing
                line = f"  {sig_indicator} {ssid:<28} {bssid:<17} {signal_display:<6} {security:<10} {connected_marker}"
                # Truncate if too long
                if len(line) > 63:
                    line = line[:60] + "..."
                type_text(" " * ((term_width - 67) // 2) + "║" + line + " " * (65 - len(line) - 2) + "║", delay=0.015, color=Fore.WHITE)
                time.sleep(0.05)
            
            if len(access_points) > 10:
                line = f"  ... and {len(access_points) - 10} more"
                type_text(" " * ((term_width - 67) // 2) + "║" + line + " " * (65 - len(line) - 2) + "║", delay=0.02, color=Fore.LIGHTYELLOW_EX)
            
            bottom_border = "╚" + "═" * 65 + "╝"
            type_text(" " * ((term_width - 67) // 2) + bottom_border, delay=0.01, color=Fore.LIGHTBLUE_EX)
        
        time.sleep(0.3)
        
        # ========================================================================
        # Hacking Matrix Footer
        # ========================================================================
        type_text("\n", delay=0.01)
        
        # Matrix-style footer
        matrix_chars = ['0', '1', ' ', '░', '▒', '▓']
        footer = "▸ ⚡ WiFi Audit Complete ◂"
        type_text(" " * ((term_width - len(footer)) // 2) + footer, delay=0.02, color=Fore.LIGHTGREEN_EX)
        
        # Random matrix rain effect
        for _ in range(3):
            matrix_rain = ''.join(random.choice(matrix_chars) for _ in range(random.randint(20, 40)))
            type_text(" " * ((term_width - len(matrix_rain)) // 2) + matrix_rain, delay=0.005, color=Fore.GREEN)
            time.sleep(0.02)
        
        type_text(" " * ((term_width - 50) // 2) + "=" * 50, delay=0.01, color=Fore.LIGHTBLACK_EX)
        type_text("\n", delay=0.01)

    def _display_wifi_audit_results_fallback(self, results):
        """Fallback display without generative writing"""
        from colorama import Fore, Style
        import json
        from datetime import datetime
        
        print(f"\n{Fore.CYAN}╔{'═' * 70}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}📊 WIFI AUDIT RESULTS{Style.RESET_ALL}                          {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 70}╝{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Audit Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}System: {results.get('system', 'Unknown').upper()}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Host: {results.get('hostname', 'Unknown')}{Style.RESET_ALL}")
        if results.get('interface'):
            print(f"{Fore.CYAN}Interface: {results['interface']}{Style.RESET_ALL}")
        
        summary = results.get('summary', {})
        
        # ========================================================================
        # Summary Statistics
        # ========================================================================
        print(f"\n{Fore.CYAN}📈 Summary Statistics:{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}Total Access Points:{Style.RESET_ALL} {summary.get('total_aps', 0)}")
        print(f"  {Fore.GREEN}Secured Networks:{Style.RESET_ALL} {summary.get('secured_aps', 0)}")
        print(f"  {Fore.RED}Open Networks:{Style.RESET_ALL} {summary.get('open_aps', 0)}")
        print(f"  {Fore.RED}WEP Networks:{Style.RESET_ALL} {summary.get('wep_aps', 0)}")
        print(f"  {Fore.YELLOW}WPA Networks:{Style.RESET_ALL} {summary.get('wpa_aps', 0)}")
        print(f"  {Fore.GREEN}WPA2 Networks:{Style.RESET_ALL} {summary.get('wpa2_aps', 0)}")
        print(f"  {Fore.GREEN}WPA3 Networks:{Style.RESET_ALL} {summary.get('wpa3_aps', 0)}")
        print(f"  {Fore.RED}Rogue APs Detected:{Style.RESET_ALL} {summary.get('rogue_aps', 0)}")
        
        # ========================================================================
        # Security Findings
        # ========================================================================
        security_findings = results.get('security_findings', [])
        if security_findings:
            print(f"\n{Fore.RED}🚨 Security Findings:{Style.RESET_ALL}")
            for finding in security_findings:
                severity = finding.get('severity', 'UNKNOWN')
                if severity == 'CRITICAL':
                    severity_color = Fore.RED
                elif severity == 'HIGH':
                    severity_color = Fore.YELLOW
                elif severity == 'MEDIUM':
                    severity_color = Fore.CYAN
                else:
                    severity_color = Fore.WHITE
                
                print(f"  {severity_color}[{severity}]{Style.RESET_ALL} {finding.get('finding', 'Unknown finding')} ({finding.get('ap', 'Unknown')})")
        
        # ========================================================================
        # Recommendations
        # ========================================================================
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"\n{Fore.CYAN}💡 Recommendations:{Style.RESET_ALL}")
            for rec in recommendations:
                if '🔴' in rec:
                    rec_color = Fore.RED
                elif '🟡' in rec:
                    rec_color = Fore.YELLOW
                elif '🟢' in rec:
                    rec_color = Fore.GREEN
                else:
                    rec_color = Fore.WHITE
                print(f"  {rec_color}{rec}{Style.RESET_ALL}")
        
        # ========================================================================
        # Access Points Table
        # ========================================================================
        access_points = results.get('access_points', [])
        if access_points:
            print(f"\n{Fore.CYAN}📡 Access Points:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
            print(f"{'SSID':<25} {'BSSID':<18} {'Signal':<8} {'Sec':<10} {'Channel':<8}")
            print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
            
            for ap in access_points[:20]:
                ssid = ap.get('ssid', '<Hidden>')[:24]
                bssid = ap.get('bssid', 'Unknown')
                signal = f"{ap.get('signal', 0)}%"
                security = ap.get('security_type', ap.get('security', 'Unknown'))[:10]
                channel = str(ap.get('channel', 'N/A'))
                
                # Color-code signal strength
                sig = ap.get('signal', 0)
                if sig > 70:
                    sig_color = Fore.GREEN
                elif sig > 40:
                    sig_color = Fore.YELLOW
                else:
                    sig_color = Fore.RED
                
                # Color-code security
                if security == 'Open':
                    sec_color = Fore.RED
                elif security == 'WEP':
                    sec_color = Fore.RED
                elif security == 'WPA':
                    sec_color = Fore.YELLOW
                elif security == 'WPA2':
                    sec_color = Fore.GREEN
                elif security == 'WPA3':
                    sec_color = Fore.GREEN
                else:
                    sec_color = Fore.WHITE
                
                print(f"{ssid:<25} {bssid:<18} {sig_color}{signal:<8}{Style.RESET_ALL} {sec_color}{security:<10}{Style.RESET_ALL} {channel:<8}")
            
            if len(access_points) > 20:
                print(f"{Fore.CYAN}... and {len(access_points) - 20} more{Style.RESET_ALL}")
        
        # ========================================================================
        # Detailed Security Analysis
        # ========================================================================
        print(f"\n{Fore.CYAN}🔍 Detailed Security Analysis:{Style.RESET_ALL}")
        
        # Analyze security types
        security_types = {}
        for ap in access_points:
            sec = ap.get('security_type', ap.get('security', 'Unknown'))
            security_types[sec] = security_types.get(sec, 0) + 1
        
        if security_types:
            print(f"  {Fore.YELLOW}Security Distribution:{Style.RESET_ALL}")
            for sec_type, count in sorted(security_types.items(), key=lambda x: x[1], reverse=True):
                if sec_type == 'Open':
                    sec_color = Fore.RED
                elif sec_type == 'WEP':
                    sec_color = Fore.RED
                elif sec_type == 'WPA':
                    sec_color = Fore.YELLOW
                elif sec_type == 'WPA2':
                    sec_color = Fore.GREEN
                elif sec_type == 'WPA3':
                    sec_color = Fore.GREEN
                else:
                    sec_color = Fore.WHITE
                print(f"    {sec_color}{sec_type}: {count}{Style.RESET_ALL}")
        
        # ========================================================================
        # Signal Strength Analysis
        # ========================================================================
        if access_points:
            signals = [ap.get('signal', 0) for ap in access_points if ap.get('signal', 0) > 0]
            if signals:
                avg_signal = sum(signals) / len(signals)
                max_signal = max(signals)
                min_signal = min(signals)
                
                print(f"\n  {Fore.YELLOW}Signal Statistics:{Style.RESET_ALL}")
                print(f"    Average: {avg_signal:.1f}%")
                print(f"    Maximum: {max_signal}%")
                print(f"    Minimum: {min_signal}%")
                
                # Signal strength assessment
                if avg_signal > 70:
                    print(f"    {Fore.GREEN}✓ Excellent signal strength{Style.RESET_ALL}")
                elif avg_signal > 50:
                    print(f"    {Fore.YELLOW}⚠️ Good signal strength{Style.RESET_ALL}")
                else:
                    print(f"    {Fore.RED}✗ Weak signal strength - Possible interference or distance{Style.RESET_ALL}")
        
        # ========================================================================
        # Channel Analysis
        # ========================================================================
        if access_points:
            channels = [ap.get('channel', 0) for ap in access_points if ap.get('channel', 0) > 0]
            if channels:
                from collections import Counter
                channel_counts = Counter(channels)
                
                print(f"\n  {Fore.YELLOW}Channel Distribution:{Style.RESET_ALL}")
                for channel, count in sorted(channel_counts.items()):
                    # Determine channel congestion
                    if count > 3:
                        channel_color = Fore.RED
                        status = "CONGESTED"
                    elif count > 1:
                        channel_color = Fore.YELLOW
                        status = "MODERATE"
                    else:
                        channel_color = Fore.GREEN
                        status = "CLEAR"
                    
                    print(f"    {channel_color}Channel {channel}: {count} APs ({status}){Style.RESET_ALL}")
                
                # Recommended channels
                if 1 in channels or 6 in channels or 11 in channels:
                    print(f"\n  {Fore.CYAN}Recommendation: Consider using channels 1, 6, or 11 for 2.4GHz{Style.RESET_ALL}")
        
        # ========================================================================
        # Security Score
        # ========================================================================
        total_aps = summary.get('total_aps', 0)
        if total_aps > 0:
            secured = summary.get('secured_aps', 0)
            security_score = int((secured / total_aps) * 100) if total_aps > 0 else 0
            
            print(f"\n  {Fore.YELLOW}Security Score:{Style.RESET_ALL}")
            if security_score >= 90:
                score_color = Fore.GREEN
                score_status = "EXCELLENT"
            elif security_score >= 70:
                score_color = Fore.YELLOW
                score_status = "GOOD"
            elif security_score >= 50:
                score_color = Fore.MAGENTA
                score_status = "FAIR"
            else:
                score_color = Fore.RED
                score_status = "POOR"
            
            print(f"    {score_color}{security_score}/100 ({score_status}){Style.RESET_ALL}")
            
            # Security bar
            bar_length = 40
            filled = int((security_score / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            if security_score >= 70:
                bar_color = Fore.GREEN
            elif security_score >= 50:
                bar_color = Fore.YELLOW
            else:
                bar_color = Fore.RED
            
            print(f"    {bar_color}[{bar}] {security_score}%{Style.RESET_ALL}")
        
        # ========================================================================
        # Rogue AP Detection Details
        # ========================================================================
        rogue_aps = summary.get('rogue_aps', 0)
        if rogue_aps > 0:
            print(f"\n  {Fore.RED}⚠️ Rogue Access Point Details:{Style.RESET_ALL}")
            print(f"    {Fore.RED}Found {rogue_aps} potential rogue APs{Style.RESET_ALL}")
            
            # List rogue APs
            for ap in access_points:
                if ap.get('security_type') == 'Open' and ap.get('ssid') != '<Hidden>':
                    print(f"    {Fore.RED}  • {ap.get('ssid')} ({ap.get('bssid')}) - Open network{Style.RESET_ALL}")
        
        # ========================================================================
        # Footer
        # ========================================================================
        print(f"\n{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔐 WiFi Audit Complete{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📁 Results exported to: {results.get('export_path', 'Not exported')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}\n")
        
        # ========================================================================
        # Export results to file
        # ========================================================================
        try:
            export_dir = Path.home() / "DSTerminal" / "reports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = export_dir / f"wifi_audit_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            results['export_path'] = str(filename)
            print(f"{Fore.GREEN}✅ Results exported to: {filename}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Failed to export results: {str(e)}{Style.RESET_ALL}")
        
        return results
