# Save this as setup_immigration.py
import os
import sys
import sqlite3
import json
from pathlib import Path

def setup_immigration_system():
    """Complete setup for immigration system protection"""
    
    print("="*60)
    print("🏗️  SETTING UP IMMIGRATION SYSTEM PROTECTION")
    print("="*60)
    
    # Use absolute path with forward slashes
    home = str(Path.home()).replace('\\', '/')
    
    # Define all paths
    paths = {
        'system_path': f'{home}/PassportSystem',
        'database_dir': f'{home}/PassportSystem/Database',
        'database_path': f'{home}/PassportSystem/Database/passport.db',
        'config_path': f'{home}/PassportSystem/Config',
        'logs_path': f'{home}/PassportSystem/Logs',
        'biometrics_path': f'{home}/PassportSystem/Biometrics',
        'photos_path': f'{home}/PassportSystem/Photos',
        'backup_path': f'{home}/DSTerminal_Backup'
    }
    
    print("\n📁 Creating directories...")
    for name, path in paths.items():
        try:
            # Convert to Path object for proper handling
            p = Path(path)
            p.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {path}")
        except Exception as e:
            print(f"  ⚠️ Error creating {path}: {e}")
            # Try alternative approach
            try:
                os.makedirs(path, exist_ok=True)
                print(f"  ✓ Created (alt): {path}")
            except:
                pass
    
    # Create database with proper error handling
    print("\n🗄️ Creating database...")
    db_path = paths['database_path']
    
    try:
        # Ensure directory exists before creating database
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Create database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passports (
                passport_number TEXT PRIMARY KEY,
                full_name TEXT,
                date_of_birth TEXT,
                nationality TEXT,
                issue_date TEXT,
                expiry_date TEXT,
                status TEXT,
                biometric_hash TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user TEXT,
                activity TEXT,
                passport_number TEXT,
                details TEXT
            )
        ''')
        
        # Add sample data
        import datetime
        now = datetime.datetime.now().isoformat()
        
        sample_data = [
            ('MW123456', 'John Doe', '1990-01-01', 'Malawian', '2024-01-01', '2034-01-01', 'active', 'hash123', now, now),
            ('MW123457', 'Jane Smith', '1992-05-15', 'Malawian', '2024-02-01', '2034-02-01', 'active', 'hash456', now, now),
            ('MW123458', 'David Banda', '1988-10-20', 'Malawian', '2024-03-01', '2034-03-01', 'pending', 'hash789', now, now)
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO passports 
            (passport_number, full_name, date_of_birth, nationality, issue_date, expiry_date, status, biometric_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
        
        conn.commit()
        conn.close()
        
        print(f"  ✅ Database created: {db_path}")
        print(f"  ✅ Sample data added (3 records)")
        
        # Verify database exists
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"  ✅ Database size: {size} bytes")
        else:
            print(f"  ⚠️ Database file not found after creation")
            
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        print(f"  Trying alternative location...")
        
        # Try alternative location in current directory
        alt_db = "passport.db"
        try:
            conn = sqlite3.connect(alt_db)
            conn.execute('CREATE TABLE IF NOT EXISTS passports (id INTEGER PRIMARY KEY, name TEXT)')
            conn.commit()
            conn.close()
            print(f"  ✅ Created database in current directory: {alt_db}")
            paths['database_path'] = os.path.abspath(alt_db)
        except Exception as e2:
            print(f"  ❌ Alternative also failed: {e2}")
            return False
    
    # Create config file
    print("\n📝 Creating config file...")
    config = {
        "system_path": paths['system_path'],
        "database_path": paths['database_path'],
        "config_path": paths['config_path'],
        "logs_path": paths['logs_path'],
        "biometrics_path": paths['biometrics_path'],
        "photos_path": paths['photos_path'],
        "backup_path": paths['backup_path'],
        "backup_interval": 60,
        "max_backups": 100,
        "replicate_biometrics": True,
        "replicate_photos": True,
        "replicate_database": True,
        "monitor_interval": 5,
        "watch_files": True,
        "watch_processes": True,
        "auto_recovery": True,
        "recovery_test_interval": 300
    }
    
    try:
        with open('immigration_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print(f"  ✅ Config saved: immigration_config.json")
    except Exception as e:
        print(f"  ❌ Config save error: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print(f"\nDatabase: {paths['database_path']}")
    print(f"Backup: {paths['backup_path']}")
    print(f"Config: immigration_config.json")
    print("\nNow run: python immigration_integration.py")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        setup_immigration_system()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()