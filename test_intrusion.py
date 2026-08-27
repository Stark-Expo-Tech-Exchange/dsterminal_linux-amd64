#!/usr/bin/env python3
"""
SIEM EVENT & ALERT TEST SCRIPT
Generates various security events to test the dashboard
"""

import requests
import time
import sys
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def print_header(text, char="="):
    print("\n" + char * 60)
    print(text)
    print(char * 60)

def print_status(text, success=True):
    if success:
        print(f"  ✅ {text}")
    else:
        print(f"  ❌ {text}")

def wait_for_key():
    input("\nPress ENTER to continue...")

def check_dashboard():
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ Dashboard is running!")
            print(f"   {BASE_URL}")
            return True
    except:
        pass
    print("❌ Dashboard is NOT running!")
    print("   Please start it first: python network_security_realtime.py")
    return False

def test_block_ips():
    print("\n[1] Generating Firewall - IP BLOCK events...")
    test_ips = [
        "10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5",
        "192.168.1.100", "192.168.1.101", "192.168.1.102",
        "172.16.0.1", "172.16.0.2"
    ]
    for i, ip in enumerate(test_ips):
        try:
            response = requests.post(
                f"{BASE_URL}/api/firewall/block-ip",
                json={"ip": ip, "reason": f"Test alert {i+1} - {ip}"},
                timeout=2
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"  Blocking {ip}... ✅")
                else:
                    print(f"  Blocking {ip}... ⚠️ Already blocked")
            else:
                print(f"  Blocking {ip}... ❌ Failed")
        except Exception as e:
            print(f"  Blocking {ip}... ❌ Error: {e}")
            time.sleep(0.3)

def test_brute_force():
    print("\n[2] Generating SIEM - BRUTE FORCE events...")
    brute_ips = ["192.168.1.50", "192.168.1.51", "10.0.0.10"]
    for ip in brute_ips:
        for j in range(1, 7):
            try:
                response = requests.post(
                    f"{BASE_URL}/api/events",
                    json={
                        "source": "SIEM_Test",
                        "event_type": "failed_login",
                        "severity": "HIGH",
                        "message": f"Failed login attempt from {ip}",
                        "data": {
                            "source_ip": ip,
                            "username": "admin",
                            "attempt": j
                        }
                    },
                    timeout=2
                )
                print(f"  Failed login attempt {j} from {ip} ✅")
            except:
                print(f"  Failed login attempt {j} from {ip} ❌")
                time.sleep(0.2)
                time.sleep(0.5)

def test_port_scan():
    print("\n[3] Generating IDS/IPS - PORT SCAN events...")
    scan_ip = "10.0.0.100"
    ports = [22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 5432, 8080, 8443]
    print(f"  Port scan from {scan_ip}...", end="")
    for port in ports:
        try:
            requests.post(
                f"{BASE_URL}/api/events",
                json={
                    "source": "IDS_Test",
                    "event_type": "connection_attempt",
                    "severity": "MEDIUM",
                    "message": f"Port scan detected from {scan_ip}",
                    "data": {
                        "source_ip": scan_ip,
                        "port": port,
                        "protocol": "TCP"
                    }
                },
                timeout=1
            )
        except:
            pass
        time.sleep(0.05)
        print(f" ✅ Logged {len(ports)} attempts")

def test_add_iocs():
    print("\n[4] Generating Threat Intelligence - IOC events...")
    iocs = [
        {"ip": "185.130.5.253", "description": "Test C2 Server"},
        {"ip": "94.102.61.78", "description": "Test Malware Distribution"},
        {"ip": "45.155.205.233", "description": "Test Phishing Host"}
    ]
    for ioc in iocs:
        try:
            response = requests.post(
                f"{BASE_URL}/api/ioc/add",
                json=ioc,
                timeout=2
            )
            if response.status_code == 200:
                print(f"  Adding IOC: {ioc['ip']} ✅")
            else:
                print(f"  Adding IOC: {ioc['ip']} ❌")
        except:
            print(f"  Adding IOC: {ioc['ip']} ❌")
            time.sleep(0.3)

def test_threat_connections():
    print("\n[5] Simulating connections to known threat IPs...")
    threat_ips = ["185.130.5.253", "94.102.61.78", "45.155.205.233"]
    for ip in threat_ips:
        try:
            response = requests.post(
                f"{BASE_URL}/api/events",
                json={
                    "source": "IDS_Test",
                    "event_type": "known_threat_connection",
                    "severity": "CRITICAL",
                    "message": f"Connection to known threat IOC: {ip}",
                    "data": {
                        "remote_ip": ip,
                        "remote_port": 443,
                        "process": "test_process.exe"
                    }
                },
                timeout=2
            )
            print(f"  Connecting to {ip}... ✅")
        except:
            print(f"  Connecting to {ip}... ❌")
            time.sleep(0.5)

def test_suspicious_processes():
    print("\n[6] Generating Endpoint - SUSPICIOUS PROCESS events...")
    processes = [
        {"name": "cryptominer.exe", "pid": 1234},
        {"name": "keylogger.exe", "pid": 5678},
        {"name": "backdoor.exe", "pid": 9012}
    ]
    for proc in processes:
        try:
            response = requests.post(
                f"{BASE_URL}/api/events",
                json={
                    "source": "Endpoint_Test",
                    "event_type": "suspicious_process",
                    "severity": "HIGH",
                    "message": f"Suspicious process detected: {proc['name']}",
                    "data": {
                        "pid": proc["pid"],
                        "name": proc["name"],
                        "reason": "Process name contains malicious term"
                    }
                },
                timeout=2
            )
            print(f"  Detected: {proc['name']} PID {proc['pid']} ✅")
        except:
            print(f"  Detected: {proc['name']} PID {proc['pid']} ❌")
            time.sleep(0.3)

def test_c2_communication():
    print("\n[7] Generating IDS/IPS - C2 COMMUNICATION events...")
    c2_ports = [4444, 5555, 1337, 6666, 6667]
    c2_ip = "10.0.0.200"
    for port in c2_ports:
        try:
            response = requests.post(
                f"{BASE_URL}/api/events",
                json={
                    "source": "IDS_Test",
                    "event_type": "possible_c2",
                    "severity": "CRITICAL",
                    "message": f"Possible C2 communication detected on port {port}",
                    "data": {
                        "source_ip": c2_ip,
                        "remote_port": port,
                        "process": "svchost.exe"
                    }
                },
                timeout=2
            )
            print(f"  C2 traffic on port {port} from {c2_ip} ✅")
        except:
            print(f"  C2 traffic on port {port} from {c2_ip} ❌")
            time.sleep(0.3)

def test_generate_alerts():
    print("\n[8] Generating various security alerts...")
    alerts = [
        {"severity": "CRITICAL", "title": "Ransomware Detected", "message": "Potential ransomware activity on host"},
        {"severity": "HIGH", "title": "Data Exfiltration", "message": "Large data upload detected to external IP"},
        {"severity": "MEDIUM", "title": "Unusual Network Traffic", "message": "Unusual traffic pattern detected"},
        {"severity": "LOW", "title": "System Update Required", "message": "Security patch available for installed software"},
        {"severity": "CRITICAL", "title": "Privilege Escalation", "message": "User attempted unauthorized privilege escalation"},
        {"severity": "HIGH", "title": "Malware Download", "message": "Malicious file download detected from suspicious URL"}
    ]
    for alert in alerts:
        try:
            response = requests.post(
                f"{BASE_URL}/api/events",
                json={
                    "source": "Alert_Test",
                    "event_type": alert["title"],
                    "severity": alert["severity"],
                    "message": alert["message"],
                    "data": {"timestamp": datetime.now().isoformat()}
                },
                timeout=2
            )
            print(f"  [{alert['severity']}] {alert['title']} ✅")
        except:
            print(f"  [{alert['severity']}] {alert['title']} ❌")
            time.sleep(0.4)

def test_process_scan():
    print("\n[9] Triggering process scan...")
    try:
        response = requests.post(f"{BASE_URL}/api/process/scan", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Process scan triggered - {result.get('suspicious', 0)} suspicious findings")
        else:
            print("  ❌ Failed")
    except:
        print("  ❌ Failed")

def test_check_events():
    print("\n[10] Checking for generated events...")
    try:
        response = requests.get(f"{BASE_URL}/api/events?limit=10", timeout=5)
        if response.status_code == 200:
            events = response.json()
            print(f"  ✅ Found {len(events)} recent events")
            if events:
                print("\n  Recent Events:")
                for event in events[:5]:
                    print(f"    [{event.get('severity', 'UNKNOWN')}] {event.get('event_type', 'Unknown')} - {event.get('message', '')[:50]}...")
    except:
        print("  ❌ Failed to check events")

def main():
    print_header(" SIEM EVENT & ALERT GENERATOR - REAL-TIME TEST ")

    if not check_dashboard():
        sys.exit(1)

        wait_for_key()

        test_block_ips()
        time.sleep(0.5)

        test_brute_force()
        time.sleep(0.5)

        test_port_scan()
        time.sleep(0.5)

        test_add_iocs()
        time.sleep(0.5)

        test_threat_connections()
        time.sleep(0.5)

        test_suspicious_processes()
        time.sleep(0.5)

        test_c2_communication()
        time.sleep(0.5)

        test_generate_alerts()
        time.sleep(0.5)

        test_process_scan()
        time.sleep(0.5)

        test_check_events()

        print_header(" TEST COMPLETE! ")
        print("\nDashboard URL: http://127.0.0.1:5000")
        print("\nExpected to see:")
        print("  🔴 CRITICAL: C2 Communication, Known Threat, Ransomware")
        print("  🟠 HIGH: Brute Force, Suspicious Process, Data Exfiltration")
        print("  🟡 MEDIUM: Port Scan, Unusual Traffic")
        print("  🔵 LOW: System Update Required")
        print("\nPress ENTER to exit...")
        input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Test interrupted by user")
    except Exception as e:
        print(f"\n[!] Error: {e}")
import traceback
traceback.print_exc()