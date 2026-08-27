#!python
"""
Test Ransomware Detection for DSTerminal Dashboard
Run this to simulate ransomware activity and test the quarantine feature
"""
import os
import time
import sys

def simulate_ransomware():
    print("=" * 60)
    print("🧪 DSTERMINAL RANSOMWARE DETECTION TEST")
    print("=" * 60)
    
    # Define honeypot path
    username = os.environ.get('USERNAME', 'DSTERMINAL-V3.1.113')
    honeypot_path = f"C:\\Users\\{username}\\Documents\\honeypot_1.txt"
    
    print(f"\n📁 Using honeypot: {honeypot_path}")
    print("\n⚠️ This will simulate ransomware activity on the honeypot file.")
    print("⚠️ The dashboard should detect this as ransomware.")
    
    confirm = input("\nContinue? (y/n): ")
    if confirm.lower() != 'y':
        print("Test cancelled.")
        return
    
    print("\n[1/4] Creating honeypot file...")
    try:
        with open(honeypot_path, 'w') as f:
            f.write("HONEYPOT_FILE_DO_NOT_MODIFY")
        print("✅ Honeypot file created")
    except Exception as e:
        print(f"❌ Failed to create honeypot: {e}")
        return
    
    print("\n[2/4] Waiting 5 seconds...")
    time.sleep(5)
    
    print("\n[3/4] Modifying honeypot file (simulating ransomware encryption)...")
    try:
        with open(honeypot_path, 'w') as f:
            f.write("ENCRYPTED_BY_RANSOMWARE_SIMULATION_XYZ123")
        print("✅ Honeypot file modified")
    except Exception as e:
        print(f"❌ Failed to modify: {e}")
        return
    
    print("\n[4/4] Triggering dashboard update...")
    print("\n✅ Ransomware simulation complete!")
    print("\n📊 Check the DSTerminal dashboard:")
    print("   http://localhost:5000")
    print("\nExpected changes:")
    print("   🔴 Threat Level: RANSOMWARE_DETECTED")
    print("   🔴 Status: ATTACK")
    print("   📁 File in quarantine list")
    print("   🚨 Attack banner displayed")
    print("\nPress the QUARANTINE button in the dashboard to isolate the file.")

if __name__ == "__main__":
    try:
        simulate_ransomware()
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")