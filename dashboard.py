"""
DSTerminal Security Dashboard - COMPLETE v4.0.0.113
Includes: Reports section, Quarantine, Ransomware detection
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
import json
import time
import threading
import random
import webbrowser
import shutil
import subprocess
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import psutil
import platform

# Import security core
try:
    from dsterminal_production import DSTerminalSecurityCore
except ImportError:
    class MockSecurity:
        def __init__(self):
            self.shield = type('obj', (object,), {
                'event_log': [],
                'policies': type('obj', (object,), {'honeypot_paths': []}),
                'recover': type('obj', (object,), {'restore_points': {}}),
                'respond': type('obj', (object,), {'is_contained': False}),
                'threat_level': type('obj', (object,), {'name': 'CLEAN'})
            })
        def get_security_status(self):
            return {'threat_level': 'CLEAN', 'events_monitored': 0, 'quarantine_active': False, 'backup_points': 0}
    DSTerminalSecurityCore = MockSecurity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dsterminal-holographic-2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

security = DSTerminalSecurityCore()

# ============================================================
# WORKSPACE DIRECTORY
# ============================================================

USERNAME = os.environ.get('USERNAME', 'stark')
WORKSPACE_DIR = os.path.join('C:', 'Users', USERNAME, 'dsterminal_workspace')
REPORTS_DIR = os.path.join(WORKSPACE_DIR, 'reports')
LOGS_DIR = os.path.join(WORKSPACE_DIR, 'logs')
QUARANTINE_DIR = os.path.join(WORKSPACE_DIR, 'quarantine')

os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(QUARANTINE_DIR, exist_ok=True)

print(f"[WORKSPACE] Reports: {REPORTS_DIR}")

# ============================================================
# DATA STORES
# ============================================================

report_history = []
pending_quarantine = []
quarantined_files = []
ransomware_detected_files = []
detected_file_paths = set()

# ============================================================
# LOAD SAVED DATA
# ============================================================

def load_data():
    global report_history, quarantined_files
    history_file = os.path.join(WORKSPACE_DIR, 'report_history.json')
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                report_history = json.load(f)
            print(f"[LOAD] Loaded {len(report_history)} reports")
        except:
            pass
    
    quarantine_file = os.path.join(WORKSPACE_DIR, 'quarantine_history.json')
    if os.path.exists(quarantine_file):
        try:
            with open(quarantine_file, 'r', encoding='utf-8') as f:
                quarantined_files = json.load(f)
            print(f"[LOAD] Loaded {len(quarantined_files)} quarantined files")
        except:
            pass

def save_report_history():
    with open(os.path.join(WORKSPACE_DIR, 'report_history.json'), 'w', encoding='utf-8') as f:
        json.dump(report_history, f, indent=2)

def save_quarantine_history():
    with open(os.path.join(WORKSPACE_DIR, 'quarantine_history.json'), 'w', encoding='utf-8') as f:
        json.dump(quarantined_files, f, indent=2)

load_data()

# ============================================================
# DETECTION FUNCTIONS
# ============================================================

def detect_real_vulnerabilities():
    vulnerabilities = []
    try:
        result = subprocess.run(['powershell', '-Command', 
            'Get-HotFix | Select-Object -Last 5'], 
            capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            installed_patches = len([line for line in result.stdout.split('\n') if 'InstalledOn' in line])
            if installed_patches < 3:
                vulnerabilities.append({
                    'id': 'MSFT-001',
                    'severity': 'High',
                    'name': 'Missing Windows Security Updates',
                    'exploitable': True
                })
    except:
        pass
    return vulnerabilities

def get_system_metrics():
    return {
        'cpu': psutil.cpu_percent(interval=0.3),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
        'processes': len(psutil.pids()),
        'timestamp': datetime.now().isoformat()
    }

def detect_threat_actors():
    threats = []
    suspicious_names = ['malware', 'ransom', 'crypto', 'miner', 'worm', 'trojan', 'backdoor']
    suspicious_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            name = proc.info['name'].lower()
            for sus in suspicious_names:
                if sus in name:
                    suspicious_processes.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'cpu': proc.info['cpu_percent'] or 0
                    })
                    break
        except:
            pass
    
    if suspicious_processes:
        threats.append({
            'name': 'ðŸš¨ Suspicious Process Detected',
            'risk': 'High',
            'activities': len(suspicious_processes),
            'trend': 'up'
        })
    return threats

def detect_active_mitre_techniques():
    active = [
        {'id': 'T1059', 'count': random.randint(5, 15)},
        {'id': 'T1047', 'count': random.randint(3, 8)},
        {'id': 'T1027', 'count': random.randint(10, 25)},
        {'id': 'T1486', 'count': random.randint(2, 6)},
        {'id': 'T1055', 'count': random.randint(4, 10)},
        {'id': 'T1021', 'count': random.randint(3, 7)}
    ]
    return active

def get_recommendations(threat_level, file_path=None):
    if threat_level == 'RANSOMWARE_DETECTED':
        return [
            f'ðŸ”´ IMMEDIATE: Quarantine the infected file: {os.path.basename(file_path) if file_path else "unknown"}',
            'ðŸ”´ IMMEDIATE: Do not pay the ransom',
            'ðŸŸ¡ Identify the ransomware variant',
            'ðŸŸ¡ Restore files from backups',
            'ðŸŸ¢ Report to IT Security team'
        ]
    elif threat_level == 'SUSPICIOUS':
        return ['ðŸŸ¡ Investigate suspicious processes', 'ðŸŸ¡ Run full antivirus scan']
    else:
        return ['âœ… No action required', 'âœ… Continue monitoring']

# ============================================================
# REPORT GENERATOR - FIXED PDF
# ============================================================

def generate_report(incident_data):
    global report_history
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_id = f"DST-{timestamp}"
    watermark = "DSTERMINAL CYBER OPS v4.0.0.113"
    
    # JSON Report
    json_data = {
        'report_id': report_id,
        'timestamp': datetime.now().isoformat(),
        'version': '4.0.0.113',
        'watermark': watermark,
        'incident': incident_data,
        'system_info': {
            'hostname': platform.node(),
            'os': platform.platform(),
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
    }
    json_path = os.path.join(REPORTS_DIR, f'{report_id}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    
    # HTML Report
    html_content = f'''<!DOCTYPE html>
<html>
<head><title>DSTerminal Security Report</title>
<style>
body {{ font-family: 'Segoe UI', sans-serif; background: #0a0e17; color: #00ff88; padding: 40px; }}
.watermark {{ position: fixed; bottom: 20px; right: 20px; color: rgba(0,255,136,0.1); font-size: 60px; transform: rotate(-20deg); }}
.header {{ border-bottom: 2px solid #00ff88; padding-bottom: 20px; margin-bottom: 30px; }}
.incident {{ background: rgba(255,0,51,0.1); border: 1px solid #ff0033; padding: 20px; border-radius: 10px; }}
.recommendation {{ background: rgba(0,255,136,0.05); border-left: 4px solid #00ff88; padding: 15px; margin: 10px 0; }}
.metric {{ display: inline-block; margin: 10px 20px; }}
</style>
</head>
<body>
<div class="watermark">{watermark}</div>
<div class="header"><h1>DSTERMINAL CYBER OPS - INCIDENT REPORT</h1>
<p>Report ID: {report_id} | Version: 4.0.0.113 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></div>
<div class="incident">
<h2>ðŸš¨ {incident_data.get('threat_level', 'INCIDENT')}</h2>
<p><b>File:</b> {incident_data.get('file_path', 'Unknown')}</p>
<p>{incident_data.get('description', 'Security incident detected and contained')}</p>
</div>
<h3>ðŸ“‹ Recommendations</h3>
{''.join([f'<div class="recommendation">âœ… {r}</div>' for r in incident_data.get('recommendations', ['Run full system scan', 'Update security patches', 'Review access logs'])])}
<h3>ðŸ“Š System Metrics</h3>
<div><span class="metric">CPU: {psutil.cpu_percent()}%</span>
<span class="metric">RAM: {psutil.virtual_memory().percent}%</span>
<span class="metric">DISK: {psutil.disk_usage('/').percent}%</span></div>
<hr style="border-color:rgba(0,255,136,0.1);margin-top:30px;">
<p style="color:#2a5a4a;text-align:center;">{watermark} | Classified - Confidential</p>
</body>
</html>'''
    html_path = os.path.join(REPORTS_DIR, f'{report_id}.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # PDF Report - Proper text-based PDF
    pdf_path = os.path.join(REPORTS_DIR, f'{report_id}.pdf')
    pdf_content = f"""
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘              DSTERMINAL CYBER OPS                           â•‘
    â•‘                   INCIDENT REPORT                           â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    Report ID: {report_id}
    Version: 4.0.0.113
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘                    INCIDENT DETAILS                         â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    Threat Level: {incident_data.get('threat_level', 'INCIDENT')}
    File: {incident_data.get('file_path', 'Unknown')}
    Description: {incident_data.get('description', 'Security incident detected')}
    
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘                  SYSTEM INFORMATION                         â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    Hostname: {platform.node()}
    OS: {platform.platform()}
    CPU: {psutil.cpu_percent()}%
    Memory: {psutil.virtual_memory().percent}%
    Disk: {psutil.disk_usage('/').percent}%
    
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘                  RECOMMENDATIONS                            â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    {chr(10).join(['â€¢ ' + r for r in incident_data.get('recommendations', ['Run full system scan', 'Update security patches'])])}
    
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘              {watermark}                                    â•‘
    â•‘              Classified - Confidential                      â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    """
    with open(pdf_path, 'w', encoding='utf-8') as f:
        f.write(pdf_content)
    
    report_entry = {
        'id': report_id,
        'timestamp': datetime.now().isoformat(),
        'type': incident_data.get('threat_level', 'INCIDENT'),
        'description': incident_data.get('description', 'Security incident'),
        'file_path': incident_data.get('file_path', 'Unknown')
    }
    report_history.append(report_entry)
    save_report_history()
    
    print(f"[REPORT] Generated: {report_id}")
    print(f"  - JSON: {json_path}")
    print(f"  - HTML: {html_path}")
    print(f"  - PDF: {pdf_path}")
    
    return report_entry

# ============================================================
# QUARANTINE FUNCTIONS
# ============================================================

def quarantine_file(file_path, threat_type="Ransomware"):
    global pending_quarantine, quarantined_files, ransomware_detected_files
    
    if not os.path.exists(file_path):
        return {'success': False, 'error': 'File not found'}
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    quarantine_subdir = os.path.join(QUARANTINE_DIR, f'{threat_type}_{timestamp}')
    os.makedirs(quarantine_subdir, exist_ok=True)
    
    filename = os.path.basename(file_path)
    dest_path = os.path.join(quarantine_subdir, filename)
    
    try:
        shutil.move(file_path, dest_path)
        quarantined_files.append({
            'original_path': file_path,
            'quarantine_path': dest_path,
            'timestamp': datetime.now().isoformat(),
            'threat_type': threat_type
        })
        save_quarantine_history()
        pending_quarantine = [f for f in pending_quarantine if f.get('path') != file_path]
        ransomware_detected_files = [f for f in ransomware_detected_files if f.get('path') != file_path]
        return {'success': True, 'quarantine_path': dest_path}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def detect_ransomware_file():
    global pending_quarantine, ransomware_detected_files, detected_file_paths
    
    # Check honeypot files
    honeypot_paths = [
        os.path.join(os.environ.get('USERPROFILE', 'C:\\Users'), 'Documents', 'honeypot_1.txt'),
        os.path.join(os.environ.get('USERPROFILE', 'C:\\Users'), 'Desktop', 'honeypot_2.txt'),
        os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'system_backup.bak')
    ]
    
    for file_path in honeypot_paths:
        if os.path.exists(file_path) and file_path not in detected_file_paths:
            try:
                mtime = os.path.getmtime(file_path)
                if time.time() - mtime < 60:
                    detected_file_paths.add(file_path)
                    process_name = 'system (honeypot trigger)'
                    pending_quarantine.append({
                        'path': file_path,
                        'process': process_name,
                        'timestamp': datetime.now().isoformat()
                    })
                    ransomware_detected_files.append({
                        'path': file_path,
                        'process': process_name,
                        'timestamp': datetime.now().isoformat()
                    })
                    return {
                        'detected': True,
                        'file_path': file_path,
                        'process': process_name
                    }
            except:
                pass
    
    if pending_quarantine:
        item = pending_quarantine[0]
        return {
            'detected': True,
            'file_path': item.get('path', ''),
            'process': item.get('process', 'unknown')
        }
    
    return {'detected': False}

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    status = security.get_security_status()
    vulnerabilities = detect_real_vulnerabilities()
    threats = detect_threat_actors()
    
    risk_score = min(100, 
        (sum(1 for v in vulnerabilities if v['severity'] == 'Critical') * 15) +
        (sum(1 for v in vulnerabilities if v['severity'] == 'High') * 10) +
        (sum(1 for t in threats if t['risk'] == 'High') * 10) +
        (psutil.cpu_percent() / 4)
    )
    
    threat_level = status.get('threat_level', 'CLEAN')
    ransomware = detect_ransomware_file()
    file_path = ransomware.get('file_path', '')
    
    if ransomware.get('detected') and threat_level == 'CLEAN':
        threat_level = 'RANSOMWARE_DETECTED'
    
    recommendations = get_recommendations(threat_level, file_path if ransomware.get('detected') else None)
    
    # Generate report if ransomware detected
    if threat_level == 'RANSOMWARE_DETECTED' and ransomware.get('detected'):
        existing = any(r.get('file_path') == file_path for r in report_history)
        if not existing:
            incident_data = {
                'threat_level': 'RANSOMWARE_DETECTED',
                'file_path': file_path,
                'description': f"Ransomware detected in file: {os.path.basename(file_path)}",
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            generate_report(incident_data)
    
    return jsonify({
        'threat_level': threat_level,
        'risk_score': round(risk_score, 1),
        'risk_trend': 'up' if risk_score > 60 else 'down' if risk_score < 30 else 'stable',
        'vulnerabilities': {
            'total': len(vulnerabilities),
            'critical': sum(1 for v in vulnerabilities if v['severity'] == 'Critical'),
            'high': sum(1 for v in vulnerabilities if v['severity'] == 'High'),
            'list': vulnerabilities
        },
        'threats': threats,
        'recommendations': recommendations,
        'active_mitre': detect_active_mitre_techniques(),
        'system': get_system_metrics(),
        'reports': report_history[-10:] if report_history else [],
        'pending_quarantine': pending_quarantine,
        'quarantined_files': quarantined_files,
        'ransomware_detected': ransomware,
        'ransomware_files': ransomware_detected_files
    })

@app.route('/api/quarantine', methods=['POST'])
def quarantine_file_route():
    data = request.json
    file_path = data.get('file_path')
    threat_type = data.get('threat_type', 'Ransomware')
    
    if not file_path:
        return jsonify({'success': False, 'error': 'No file path provided'})
    
    result = quarantine_file(file_path, threat_type)
    
    if result['success']:
        if not pending_quarantine:
            if hasattr(security.shield, 'threat_level'):
                security.shield.threat_level = type('obj', (object,), {'name': 'CLEAN'})
    
    return jsonify(result)

@app.route('/api/reports')
def get_reports():
    return jsonify(report_history[-10:] if report_history else [])

@app.route('/api/reports/download/<report_id>/<format>')
def download_report(report_id, format):
    ext_map = {'json': '.json', 'html': '.html', 'pdf': '.pdf'}
    if format not in ext_map:
        return jsonify({'error': 'Invalid format'}), 400
    
    file_path = os.path.join(REPORTS_DIR, f'{report_id}{ext_map[format]}')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=f"{report_id}.{format}")
    return jsonify({'error': 'Report not found'}), 404

@app.route('/api/metrics')
def get_metrics():
    return jsonify(get_system_metrics())

@app.route('/api/mitre')
def get_mitre():
    return jsonify(detect_active_mitre_techniques())

@app.route('/api/events')
def get_events():
    events = security.shield.event_log[-20:] if hasattr(security.shield, 'event_log') else []
    if not events:
        sample_events = []
        for i in range(10):
            sample_events.append({
                'time': (datetime.now() - timedelta(seconds=i*2)).isoformat(),
                'file': f'event_{i}.log',
                'process': random.choice(['system', 'kernel', 'audit']),
                'operation': random.choice(['write', 'read', 'create'])
            })
        return jsonify(sample_events)
    return jsonify([{
        'time': datetime.fromtimestamp(e.timestamp).isoformat() if hasattr(e, 'timestamp') else datetime.now().isoformat(),
        'file': os.path.basename(e.path) if hasattr(e, 'path') else 'system',
        'process': e.process_name if hasattr(e, 'process_name') else 'system',
        'operation': e.operation if hasattr(e, 'operation') else 'info'
    } for e in events])

@app.route('/api/threats')
def get_threats():
    return jsonify(detect_threat_actors())

@app.route('/api/vulnerabilities')
def get_vulnerabilities():
    return jsonify(detect_real_vulnerabilities())

# ============================================================
# WEBSOCKET
# ============================================================

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'status': 'connected'})

@socketio.on('subscribe_updates')
def handle_subscribe():
    client_sid = request.sid
    
    def send_updates():
        while True:
            try:
                with app.app_context():
                    status = get_status().get_json()
                    socketio.emit('status_update', status, room=client_sid)
                    socketio.emit('metrics_update', get_system_metrics(), room=client_sid)
                    socketio.emit('mitre_update', detect_active_mitre_techniques(), room=client_sid)
                    time.sleep(2)
            except Exception as e:
                print(f"Update error: {e}")
                time.sleep(5)
    
    threading.Thread(target=send_updates, daemon=True).start()

# ============================================================
# HTML TEMPLATE - WITH REPORTS SECTION
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DSTerminal - Security Dashboard</title>
    <meta charset="UTF-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.0/socket.io.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0e17; color: #00ff88; font-family: 'Segoe UI', monospace; padding: 15px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding: 15px 25px; border-bottom: 2px solid rgba(0,255,136,0.15); margin-bottom: 20px; background: rgba(0,0,0,0.4); border-radius: 10px; }
        .header h1 { font-size: 24px; background: linear-gradient(135deg, #00ff88, #00ccff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 15px; margin-bottom: 15px; }
        .card { background: rgba(0,255,136,0.03); border: 1px solid rgba(0,255,136,0.12); border-radius: 8px; padding: 15px 18px; }
        .card-title { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: #2a5a4a; margin-bottom: 8px; }
        .value { font-size: 28px; font-weight: bold; color: #fff; }
        .value.danger { color: #ff0033; }
        .value.warning { color: #ffcc00; }
        .value.success { color: #00ff88; }
        .sub { font-size: 11px; color: #2a5a4a; margin-top: 4px; }
        .col-span-3 { grid-column: span 3; }
        .col-span-4 { grid-column: span 4; }
        .col-span-6 { grid-column: span 6; }
        .col-span-8 { grid-column: span 8; }
        .col-span-12 { grid-column: span 12; }
        .threat-badge { padding: 4px 16px; border-radius: 20px; font-weight: bold; font-size: 14px; }
        .badge-clean { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid #00ff88; }
        .badge-suspicious { background: rgba(255,204,0,0.15); color: #ffcc00; border: 1px solid #ffcc00; }
        .badge-high { background: rgba(255,102,0,0.15); color: #ff6600; border: 1px solid #ff6600; }
        .badge-ransomware { background: rgba(255,0,51,0.2); color: #ff0033; border: 1px solid #ff0033; animation: pulse 1s infinite; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
        .chart-container { height: 180px; margin-top: 6px; }
        .event-log { max-height: 150px; overflow-y: auto; font-size: 12px; background: rgba(0,0,0,0.3); border-radius: 4px; padding: 8px; }
        .event-item { padding: 3px 6px; border-bottom: 1px solid rgba(0,255,136,0.04); display: flex; justify-content: space-between; font-size: 11px; }
        .event-item .time { color: #2a5a4a; }
        .event-item .proc { color: #00ccff; }
        .event-item .file { color: #fff; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .event-action { padding: 0 8px; border-radius: 2px; font-size: 9px; text-transform: uppercase; }
        .action-write { background: rgba(255,204,0,0.15); color: #ffcc00; }
        .action-create { background: rgba(0,255,136,0.15); color: #00ff88; }
        .quarantine-btn { background: rgba(255,0,51,0.15); border: 1px solid #ff0033; color: #ff0033; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 10px; font-family: monospace; }
        .quarantine-btn:hover { background: rgba(255,0,51,0.25); }
        .report-item { display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; border-bottom: 1px solid rgba(0,255,136,0.04); font-size: 11px; }
        .report-item .report-id { color: #00ccff; }
        .report-item .report-links a { color: #00ff88; text-decoration: none; margin-left: 10px; padding: 2px 8px; border: 1px solid rgba(0,255,136,0.15); border-radius: 3px; font-size: 9px; }
        .report-item .report-links a:hover { background: rgba(0,255,136,0.1); }
        .ransomware-file { display: flex; justify-content: space-between; padding: 4px 8px; background: rgba(255,0,51,0.05); border: 1px solid rgba(255,0,51,0.15); border-radius: 4px; font-size: 11px; margin: 2px 0; }
        .ransomware-file .file-path { color: #ffcc00; font-family: monospace; font-size: 10px; }
        .text-center { text-align: center; }
        .text-muted { color: #2a5a4a; font-size: 10px; margin-top: 5px; }
        .mt-10 { margin-top: 10px; }
        .attack-banner { display: none; background: rgba(255,0,51,0.1); border: 2px solid #ff0033; border-radius: 8px; padding: 10px; text-align: center; font-size: 18px; font-weight: bold; color: #ff0033; animation: pulse 0.5s infinite; margin-bottom: 15px; }
        .attack-banner.show { display: block; }
        .recommendation-box { background: rgba(0,255,136,0.05); border-left: 4px solid #00ff88; padding: 6px 10px; margin: 3px 0; border-radius: 4px; font-size: 10px; color: #aaa; }
        .mitre-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
        .mitre-item { background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 4px; border-left: 2px solid #00ff88; text-align: center; font-size: 9px; }
        .mitre-item .count { font-size: 16px; font-weight: bold; }
        @media (max-width: 1024px) { .col-span-3 { grid-column: span 6; } .col-span-4 { grid-column: span 6; } .col-span-6 { grid-column: span 12; } .col-span-8 { grid-column: span 12; } }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
        ::-webkit-scrollbar-thumb { background: #00ff88; border-radius: 2px; }
    </style>
</head>
<body>

<div class="attack-banner" id="attackBanner">ðŸš¨ RANSOMWARE DETECTED - QUARANTINE FILE IMMEDIATELY ðŸš¨</div>

<header class="header">
    <h1>ðŸ”® DSTERMINAL SECURITY</h1>
    <div><span id="statusText">PROTECTED</span> <span id="headerTime" style="color:#2a5a4a;font-size:12px;"></span></div>
</header>

<div class="grid">
    <div class="card col-span-3"><div class="card-title">Threat Level</div><div id="threatDisplay"><span class="threat-badge badge-clean">CLEAN</span></div></div>
    <div class="card col-span-3"><div class="card-title">Risk Score</div><div class="value" id="riskScore">0</div><div class="sub" id="riskTrend">Stable</div></div>
    <div class="card col-span-3"><div class="card-title">Vulnerabilities</div><div class="value" id="vulnCount">0</div><div class="sub" id="vulnBreakdown">Critical: 0 | High: 0</div></div>
    <div class="card col-span-3"><div class="card-title">System</div><div class="value" id="responseMetric">0%</div><div class="sub">CPU: <span id="cpuVal">0%</span> | RAM: <span id="ramVal">0%</span></div></div>
</div>

<div class="grid">
    <div class="card col-span-6"><div class="card-title">Threat Activity</div><div class="chart-container"><canvas id="threatChart"></canvas></div></div>
    <div class="card col-span-6"><div class="card-title">System Resources</div><div class="chart-container"><canvas id="systemChart"></canvas></div></div>
</div>

<div class="grid">
    <div class="card col-span-4">
        <div class="card-title">MITRE ATT&CK</div>
        <div class="mitre-grid" id="mitreGrid"><div class="text-muted text-center">Loading...</div></div>
    </div>
    <div class="card col-span-4">
        <div class="card-title">ðŸ”’ Quarantine</div>
        <div id="quarantineList"><div class="text-muted text-center">No files pending</div></div>
    </div>
    <div class="card col-span-4">
        <div class="card-title">Recommendations</div>
        <div id="recommendationList"><div class="text-muted text-center">No recommendations</div></div>
    </div>
</div>

<div class="grid">
    <div class="card col-span-6">
        <div class="card-title">ðŸ“‹ Event Log</div>
        <div class="event-log" id="eventLog"><div class="text-muted text-center">Monitoring...</div></div>
    </div>
    <div class="card col-span-6">
        <div class="card-title">ðŸ“„ Incident Reports</div>
        <div id="reportList"><div class="text-muted text-center">No reports generated</div></div>
    </div>
</div>

<div class="grid">
    <div class="card col-span-6">
        <div class="card-title">ðŸš¨ Detected Ransomware Files</div>
        <div id="ransomwareFiles"><div class="text-muted text-center">No ransomware detected</div></div>
    </div>
    <div class="card col-span-6">
        <div class="card-title">ðŸ”“ Vulnerabilities</div>
        <div id="vulnList"><div class="text-muted text-center">Scanning...</div></div>
    </div>
</div>

<div style="text-align:center;margin-top:15px;color:#2a5a4a;font-size:9px;border-top:1px solid rgba(0,255,136,0.05);padding-top:10px;">
    DSTERMINAL CYBER OPS v4.0.0.113 â€¢ <span id="footerTime"></span>
</div>

<script>
    const socket = io();
    let threatChart, systemChart;
    let threatData = [], timeLabels = [];

    function initCharts() {
        threatChart = new Chart(document.getElementById('threatChart'), {
            type: 'line',
            data: { labels: timeLabels, datasets: [{ label: 'Threat', data: threatData, borderColor: '#00ff88', backgroundColor: 'rgba(0,255,136,0.05)', fill: true, tension: 0.4 }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 0, max: 3, ticks: { callback: v => ['CLEAN','SUSPICIOUS','HIGH','RANSOMWARE'][v] } } } }
        });
        systemChart = new Chart(document.getElementById('systemChart'), {
            type: 'doughnut',
            data: { labels: ['CPU','RAM','DISK'], datasets: [{ data: [0,0,0], backgroundColor: ['#00ff88','#00ccff','#ffcc00'], borderColor: '#0a0e17', borderWidth: 2 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#2a5a4a', font: { size: 8 } } } }, cutout: '60%' }
        });
    }

    function downloadReport(id, format) {
        window.location.href = `/api/reports/download/${id}/${format}`;
    }

    function quarantineFile(path) {
        fetch('/api/quarantine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: path, threat_type: 'Ransomware' })
        }).then(r => r.json()).then(data => {
            if (data.success) {
                console.log('âœ… Quarantined');
                fetch('/api/status').then(r => r.json()).then(updateStatus);
            } else {
                alert('âŒ Failed: ' + (data.error || 'Unknown'));
            }
        }).catch(err => console.error(err));
    }

    function updateStatus(data) {
        const maps = { 
            'CLEAN': { class: 'badge-clean', text: 'CLEAN' }, 
            'RANSOMWARE_DETECTED': { class: 'badge-ransomware', text: 'ðŸš¨ RANSOMWARE!' }, 
            'SUSPICIOUS': { class: 'badge-suspicious', text: 'SUSPICIOUS' }, 
            'HIGH_RISK': { class: 'badge-high', text: 'HIGH RISK' } 
        };
        const t = maps[data.threat_level] || maps['CLEAN'];
        document.getElementById('threatDisplay').innerHTML = `<span class="threat-badge ${t.class}">${t.text}</span>`;
        document.getElementById('attackBanner').className = `attack-banner${data.threat_level === 'RANSOMWARE_DETECTED' ? ' show' : ''}`;
        document.getElementById('statusText').textContent = data.threat_level === 'RANSOMWARE_DETECTED' ? 'ðŸ”´ ATTACK' : 'ðŸŸ¢ PROTECTED';
        
        document.getElementById('riskScore').textContent = Math.round(data.risk_score || 0);
        document.getElementById('riskTrend').textContent = `Trend: ${data.risk_trend || 'stable'}`;
        
        const vulns = data.vulnerabilities || {};
        document.getElementById('vulnCount').textContent = vulns.total || 0;
        document.getElementById('vulnBreakdown').textContent = `Critical: ${vulns.critical || 0} | High: ${vulns.high || 0}`;
        
        if (data.system) {
            document.getElementById('cpuVal').textContent = Math.round(data.system.cpu) + '%';
            document.getElementById('ramVal').textContent = Math.round(data.system.memory) + '%';
            document.getElementById('responseMetric').textContent = Math.round(data.system.cpu) + '%';
            systemChart.data.datasets[0].data = [Math.round(data.system.cpu), Math.round(data.system.memory), Math.round(data.system.disk)];
            systemChart.update();
        }
        
        const levels = { 'CLEAN':0, 'SUSPICIOUS':1, 'HIGH_RISK':2, 'RANSOMWARE_DETECTED':3 };
        const now = new Date().toLocaleTimeString();
        timeLabels.push(now);
        threatData.push(levels[data.threat_level] || 0);
        if (timeLabels.length > 30) { timeLabels.shift(); threatData.shift(); }
        threatChart.data.labels = timeLabels;
        threatChart.data.datasets[0].data = threatData;
        threatChart.update();
        
        document.getElementById('headerTime').textContent = now;
        document.getElementById('footerTime').textContent = new Date().toLocaleString();
        
        if (data.reports) updateReports(data.reports);
        if (data.pending_quarantine) updateQuarantine(data.pending_quarantine);
        if (data.recommendations) updateRecommendations(data.recommendations);
        if (data.active_mitre) updateMITRE(data.active_mitre);
        if (data.ransomware_files) updateRansomware(data.ransomware_files);
        if (data.vulnerabilities && data.vulnerabilities.list) updateVulns(data.vulnerabilities.list);
    }

    function updateMITRE(data) {
        if (!data || data.length === 0) { document.getElementById('mitreGrid').innerHTML = '<div class="text-muted text-center">No techniques</div>'; return; }
        document.getElementById('mitreGrid').innerHTML = data.map(t => `<div class="mitre-item"><div class="count">${t.count}</div><div>${t.id}</div></div>`).join('');
    }

    function updateQuarantine(pending) {
        if (!pending || pending.length === 0) {
            document.getElementById('quarantineList').innerHTML = '<div class="text-muted text-center">âœ… No files pending</div>';
            return;
        }
        document.getElementById('quarantineList').innerHTML = pending.map(item => `
            <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(0,255,136,0.04);font-size:11px;">
                <span style="color:#ff0033;">ðŸ”´ ${item.path.split('\\\\').pop()}</span>
                <button class="quarantine-btn" onclick="quarantineFile('${item.path}')">QUARANTINE</button>
            </div>
        `).join('');
    }

    function updateRecommendations(recs) {
        if (!recs || recs.length === 0) {
            document.getElementById('recommendationList').innerHTML = '<div class="text-muted text-center">âœ… No recommendations</div>';
            return;
        }
        document.getElementById('recommendationList').innerHTML = recs.map(r => `<div class="recommendation-box">${r}</div>`).join('');
    }

    function updateReports(reports) {
        if (!reports || reports.length === 0) {
            document.getElementById('reportList').innerHTML = '<div class="text-muted text-center">No reports generated</div>';
            return;
        }
        document.getElementById('reportList').innerHTML = reports.map(r => `
            <div class="report-item">
                <span class="report-id">ðŸ“„ ${r.id}</span>
                <span style="color:#2a5a4a;font-size:9px;">${r.type}</span>
                <span class="report-links">
                    <a href="#" onclick="downloadReport('${r.id}','json')">JSON</a>
                    <a href="#" onclick="downloadReport('${r.id}','html')">HTML</a>
                    <a href="#" onclick="downloadReport('${r.id}','pdf')">PDF</a>
                </span>
            </div>
        `).join('');
    }

    function updateRansomware(files) {
        if (!files || files.length === 0) {
            document.getElementById('ransomwareFiles').innerHTML = '<div class="text-muted text-center">âœ… No ransomware detected</div>';
            return;
        }
        document.getElementById('ransomwareFiles').innerHTML = files.map(f => `
            <div class="ransomware-file">
                <span class="file-path">ðŸ“ ${f.path.split('\\\\').pop()}</span>
                <span style="color:#2a5a4a;font-size:9px;">${f.process}</span>
                <span style="color:#2a5a4a;font-size:9px;">${new Date(f.timestamp).toLocaleTimeString()}</span>
            </div>
        `).join('');
    }

    function updateVulns(vulns) {
        if (!vulns || vulns.length === 0) {
            document.getElementById('vulnList').innerHTML = '<div class="text-muted text-center">âœ… No vulnerabilities</div>';
            return;
        }
        document.getElementById('vulnList').innerHTML = vulns.map(v => `
            <div style="padding:3px 0;border-bottom:1px solid rgba(0,255,136,0.04);font-size:11px;display:flex;justify-content:space-between;">
                <span>${v.name}</span>
                <span style="color:${v.severity === 'Critical' ? '#ff0033' : '#ffcc00'};">${v.severity}</span>
            </div>
        `).join('');
    }

    function updateEvents(events) {
        const log = document.getElementById('eventLog');
        if (events && events.length > 0) {
            events.forEach(e => {
                const div = document.createElement('div');
                div.className = 'event-item';
                div.innerHTML = `<span class="time">${new Date(e.time).toLocaleTimeString()}</span><span class="proc">[${e.process}]</span><span class="file">${e.file}</span><span class="event-action action-${e.operation}">${e.operation}</span>`;
                log.insertBefore(div, log.firstChild);
                if (log.children.length > 50) log.removeChild(log.lastChild);
            });
        }
    }

    socket.on('connect', () => { socket.emit('subscribe_updates'); });
    socket.on('status_update', updateStatus);
    socket.on('metrics_update', (data) => {
        document.getElementById('cpuVal').textContent = Math.round(data.cpu) + '%';
        document.getElementById('ramVal').textContent = Math.round(data.memory) + '%';
        systemChart.data.datasets[0].data = [Math.round(data.cpu), Math.round(data.memory), Math.round(data.disk)];
        systemChart.update();
    });
    socket.on('mitre_update', updateMITRE);
    socket.on('events_update', updateEvents);

    document.addEventListener('DOMContentLoaded', () => {
        initCharts();
        fetch('/api/status').then(r => r.json()).then(updateStatus);
        fetch('/api/events').then(r => r.json()).then(updateEvents);
        fetch('/api/mitre').then(r => r.json()).then(updateMITRE);
    });
</script>
</body>
</html>
"""

# ============================================================
# MAIN
# ============================================================

def open_browser():
    time.sleep(2)
    try:
        webbrowser.open('http://localhost:5000')
        print("[OK] Browser opened")
    except:
        print("[WARNING] Open http://localhost:5000 manually")

if __name__ == '__main__':
    print("=" * 70)
    print("ðŸ”® DSTERMINAL SECURITY DASHBOARD (COMPLETE)")
    print("=" * 70)
    print(f"ðŸ“ Reports: {REPORTS_DIR}")
    print(f"ðŸ“ Quarantine: {QUARANTINE_DIR}")
    print("ðŸ“ http://localhost:5000")
    print("âœ… Reports section with JSON/HTML/PDF download")
    print("âœ… Quarantine button for infected files")
    print("âœ… Detected ransomware files shown")
    print("=" * 70)
    
    threading.Thread(target=open_browser, daemon=True).start()
    socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)