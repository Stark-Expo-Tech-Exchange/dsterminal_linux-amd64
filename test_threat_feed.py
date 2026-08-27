#!/usr/bin/env python3
"""
Test the threat feed with real events
"""

import requests
import time
import json

BASE = "http://127.0.0.1:5000"

print("\n" + "="*60)
print("   TEST THREAT FEED")
print("="*60 + "\n")

# Check if running
try:
    r = requests.get(f"{BASE}/api/health", timeout=2)
    print("✅ Dashboard is running!")
except:
    print("❌ Dashboard is NOT running!")
    exit(1)

    print("\nGenerating events for threat feed...\n")

    # Generate events that should appear in threat feed
    events = [
        {"severity": "CRITICAL", "type": "Ransomware Detected", "msg": "Ransomware activity detected on host!"},
        {"severity": "HIGH", "type": "Data Exfiltration", "msg": "Large data upload detected to external IP"},
        {"severity": "CRITICAL", "type": "Privilege Escalation", "msg": "User attempted unauthorized privilege escalation"},
        {"severity": "HIGH", "type": "Malware Download", "msg": "Malicious file download detected from suspicious URL"},
        {"severity": "CRITICAL", "type": "C2 Communication", "msg": "C2 communication detected on port 4444"},
    ]

    for i, event in enumerate(events, 1):
        print(f"[{i}] {event['severity']} {event['type']}...", end="")
        try:
            r = requests.post(f"{BASE}/api/events", json={
                "source": "Test_Feed",
                "event_type": event["type"],
                "severity": event["severity"],
                "message": event["msg"],
                "data": {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
            })
            if r.status_code == 200:
                print(" ✅ Sent")
            else:
                print(f" ❌ Failed ({r.status_code})")
        except Exception as e:
            print(f" ❌ Error: {e}")
            time.sleep(0.5)

            print("\n" + "="*60)
            print("✅ Events sent! Check the dashboard threat feed.")
            print(f"Dashboard: {BASE}")
            print("="*60 + "\n")