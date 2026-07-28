"""
Quick Test Script for AI Modules
"""

import sys
import time

def test_imports():
    """Test if modules can be imported"""
    print("Testing imports...")
    try:
        import ai_ml_detection
        print("✅ ai_ml_detection imported successfully")
    except ImportError as e:
        print(f"❌ ai_ml_detection import failed: {e}")
    
    try:
        import ai_threat_intelligence
        print("✅ ai_threat_intelligence imported successfully")
    except ImportError as e:
        print(f"❌ ai_threat_intelligence import failed: {e}")

def quick_ml_test():
    """Quick test of ML detection"""
    print("\n=== Quick ML Detection Test ===")
    try:
        from ai_ml_detection import EnsembleDetectionEngine
        
        engine = EnsembleDetectionEngine()
        
        # Test samples
        test_data = [
            "Normal system operation log entry",
            "powershell -e JABlAG4AdgA6AHAAYQB0AGgA",
            "C2 communication detected on port 4444"
        ]
        
        for data in test_data:
            result = engine.detect(data)
            status = "⚠️ MALICIOUS" if result.is_malicious else "✅ BENIGN"
            print(f"  {status}: {data[:40]}... (Score: {result.score}%)")
            time.sleep(0.1)
            
    except Exception as e:
        print(f"❌ ML test failed: {e}")

def quick_ti_test():
    """Quick test of Threat Intelligence"""
    print("\n=== Quick Threat Intelligence Test ===")
    try:
        from ai_threat_intelligence import AIThreatIntelligenceEngine
        
        engine = AIThreatIntelligenceEngine()
        
        # Test with sample data
        sample = "Suspicious file detected: malware.exe at C:\\Windows\\Temp\\"
        alert = engine.analyze_threat(sample)
        
        print(f"  Alert ID: {alert.id}")
        print(f"  Severity: {alert.severity.name}")
        print(f"  Type: {alert.threat_type.value}")
        
    except Exception as e:
        print(f"❌ Threat Intelligence test failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print(" DSTERMINAL AI MODULES QUICK TEST")
    print("=" * 60)
    
    test_imports()
    quick_ml_test()
    quick_ti_test()
    
    print("\n✅ Quick test complete!")