"""
DSTerminal Security Integration Module
Integrates the security dashboard into the main DSTerminal class
"""

import os
import sys
import threading
import webbrowser
import time
from datetime import datetime

# Import shield core
try:
    from shield_core import ShieldCore, ThreatLevel
    SHIELD_AVAILABLE = True
except ImportError:
    SHIELD_AVAILABLE = False
    print("[!] ShieldCore not available")

# Import Flask
try:
    from flask import Flask, render_template_string, jsonify, request
    from flask_socketio import SocketIO, emit
    import psutil
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[!] Flask not available")

class DSTerminalSecurity:
    """
    Security module for DSTerminal
    Integrates shield core and dashboard
    """
    
    def __init__(self, workspace_dir=None):
        self.is_running = False
        self.dashboard_thread = None
        self.dashboard_url = "http://localhost:5000"
        self.port = 5000
        self.workspace_dir = workspace_dir or os.path.expanduser("~/dsterminal_workspace")
        
        # Initialize shield
        if SHIELD_AVAILABLE:
            self.shield = ShieldCore(self.workspace_dir)
            self.shield.start_monitoring()
            print(f"[SECURITY] Shield Core initialized")
            print(f"[SECURITY] Threat Level: {self.shield.threat_level.name}")
        else:
            self.shield = None
            print("[SECURITY] Shield Core not available")
        
        # Initialize Flask app
        if FLASK_AVAILABLE:
            self._init_flask()
            print("[SECURITY] Dashboard ready")
        else:
            print("[SECURITY] Dashboard not available")
    
    def _init_flask(self):
        """Initialize Flask app and routes"""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'dsterminal-security-2026'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # HTML template
        self._create_template()
        
        # Routes
        @self.app.route('/')
        def index():
            return render_template_string(self.html_template)
        
        @self.app.route('/api/status')
        def get_status():
            if self.shield:
                status = self.shield.get_status()
                return jsonify({
                    'threat_level': status['threat_level'],
                    'events': status['events_monitored'],
                    'honeypots': status['honeypots'],
                    'cpu': psutil.cpu_percent(),
                    'memory': psutil.virtual_memory().percent,
                    'timestamp': datetime.now().isoformat()
                })
            return jsonify({'status': 'shield_not_available'})
        
        @self.app.route('/api/events')
        def get_events():
            if self.shield:
                events = []
                for e in self.shield.event_log[-20:]:
                    events.append({
                        'time': datetime.fromtimestamp(e.timestamp).isoformat(),
                        'file': os.path.basename(e.path),
                        'process': e.process_name,
                        'operation': e.operation
                    })
                return jsonify(events)
            return jsonify([])
        
        @self.app.route('/api/quarantine', methods=['POST'])
        def quarantine():
            if not self.shield:
                return jsonify({'success': False, 'error': 'Shield not available'})
            data = request.json
            file_path = data.get('file_path')
            if file_path:
                result = self.shield.quarantine_file(file_path)
                return jsonify({'success': result})
            return jsonify({'success': False, 'error': 'No file path'})
        
        # WebSocket
        @self.socketio.on('connect')
        def handle_connect():
            print('[DASHBOARD] Client connected')
            emit('connected', {'status': 'connected'})
        
        @self.socketio.on('subscribe_updates')
        def handle_subscribe():
            client_sid = request.sid
            def send_updates():
                while True:
                    try:
                        with self.app.app_context():
                            status = get_status().get_json()
                            self.socketio.emit('status_update', status, room=client_sid)
                            time.sleep(2)
                    except Exception as e:
                        print(f'[DASHBOARD] Update error: {e}')
                        time.sleep(5)
            threading.Thread(target=send_updates, daemon=True).start()
    
    def _create_template(self):
        """Create HTML template"""
        self.html_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>DSTerminal Security</title>
            <meta charset="UTF-8">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.0/socket.io.min.js"></script>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    background: #0a0e17;
                    color: #00ff88;
                    font-family: 'Segoe UI', monospace;
                    padding: 20px;
                }
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 2px solid rgba(0,255,136,0.15);
                    margin-bottom: 20px;
                }
                .header h1 {
                    font-size: 28px;
                    background: linear-gradient(135deg, #00ff88, #00ccff);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .card {
                    background: rgba(0,255,136,0.03);
                    border: 1px solid rgba(0,255,136,0.12);
                    border-radius: 10px;
                    padding: 20px;
                }
                .card-title {
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    color: #2a5a4a;
                    margin-bottom: 10px;
                }
                .value {
                    font-size: 32px;
                    font-weight: bold;
                    color: #fff;
                }
                .badge {
                    padding: 5px 20px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 16px;
                    display: inline-block;
                }
                .badge-clean { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid #00ff88; }
                .badge-ransomware { background: rgba(255,0,51,0.2); color: #ff0033; border: 1px solid #ff0033; animation: pulse 1s infinite; }
                @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
                .event-log {
                    max-height: 200px;
                    overflow-y: auto;
                    background: rgba(0,0,0,0.3);
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 12px;
                }
                .event-item {
                    padding: 5px 0;
                    border-bottom: 1px solid rgba(0,255,136,0.04);
                    display: flex;
                    justify-content: space-between;
                }
                .event-item .time { color: #2a5a4a; }
                .event-item .proc { color: #00ccff; }
                .event-item .file { color: #fff; }
                .quarantine-btn {
                    background: rgba(255,0,51,0.15);
                    border: 1px solid #ff0033;
                    color: #ff0033;
                    padding: 5px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-family: monospace;
                }
                .quarantine-btn:hover { background: rgba(255,0,51,0.25); }
                .text-center { text-align: center; }
                .text-muted { color: #2a5a4a; }
                .footer {
                    text-align: center;
                    margin-top: 20px;
                    color: #2a5a4a;
                    font-size: 10px;
                    border-top: 1px solid rgba(0,255,136,0.05);
                    padding-top: 10px;
                }
                .alert-box {
                    background: rgba(255,0,51,0.1);
                    border: 2px solid #ff0033;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 20px;
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    color: #ff0033;
                    animation: pulse 0.5s infinite;
                }
                .alert-box.hidden { display: none; }
            </style>
        </head>
        <body>
            <div id="alertBox" class="alert-box hidden">🚨 RANSOMWARE DETECTED - QUARANTINE FILE IMMEDIATELY 🚨</div>
            <div class="header">
                <h1>🔮 DSTERMINAL SECURITY</h1>
                <span id="statusText" style="color:#2a5a4a;">🟢 PROTECTED</span>
            </div>
            <div class="grid">
                <div class="card">
                    <div class="card-title">🛡️ Threat Level</div>
                    <div id="threatDisplay"><span class="badge badge-clean">CLEAN</span></div>
                </div>
                <div class="card">
                    <div class="card-title">📁 Events</div>
                    <div class="value" id="eventCount">0</div>
                </div>
                <div class="card">
                    <div class="card-title">🍯 Honeypots</div>
                    <div class="value" id="honeypotCount">0</div>
                </div>
                <div class="card">
                    <div class="card-title">💻 CPU</div>
                    <div class="value" id="cpuValue">0%</div>
                </div>
            </div>
            <div class="grid">
                <div class="card">
                    <div class="card-title">🔒 Quarantine</div>
                    <div id="quarantineList"><div class="text-muted text-center">No files pending</div></div>
                </div>
                <div class="card">
                    <div class="card-title">🚨 Detected Files</div>
                    <div id="detectedFiles"><div class="text-muted text-center">None</div></div>
                </div>
            </div>
            <div class="grid">
                <div class="card">
                    <div class="card-title">📋 Event Log</div>
                    <div class="event-log" id="eventLog"><div class="text-muted text-center">Monitoring...</div></div>
                </div>
            </div>
            <div class="footer">DSTERMINAL CYBER OPS v3.1.113 • <span id="footerTime"></span> • 🛡️ PROTECTED</div>
            <script>
                const socket = io();
                function quarantineFile(filePath) {
                    fetch('/api/quarantine', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ file_path: filePath })
                    }).then(r => r.json()).then(data => {
                        if (data.success) { alert('✅ File quarantined!'); fetch('/api/status').then(r => r.json()).then(updateStatus); }
                        else { alert('❌ Failed: ' + (data.error || 'Unknown')); }
                    }).catch(err => console.error(err));
                }
                function updateStatus(data) {
                    const map = {
                        'CLEAN': { class: 'badge-clean', text: 'CLEAN', alert: false },
                        'RANSOMWARE_DETECTED': { class: 'badge-ransomware', text: '🚨 RANSOMWARE!', alert: true }
                    };
                    const t = map[data.threat_level] || map['CLEAN'];
                    document.getElementById('threatDisplay').innerHTML = `<span class="badge ${t.class}">${t.text}</span>`;
                    document.getElementById('statusText').textContent = t.alert ? '🔴 ATTACK' : '🟢 PROTECTED';
                    document.getElementById('alertBox').className = 'alert-box' + (t.alert ? '' : ' hidden');
                    document.getElementById('eventCount').textContent = data.events || 0;
                    document.getElementById('honeypotCount').textContent = data.honeypots || 0;
                    document.getElementById('cpuValue').textContent = Math.round(data.cpu || 0) + '%';
                    document.getElementById('footerTime').textContent = new Date().toLocaleString();
                    if (data.pending_quarantine && data.pending_quarantine.length > 0) {
                        document.getElementById('quarantineList').innerHTML = data.pending_quarantine.map(item =>
                            `<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(0,255,136,0.04);">
                                <span style="color:#ff0033;">🔴 ${item.path.split('\\\\').pop()}</span>
                                <button class="quarantine-btn" onclick="quarantineFile('${item.path}')">QUARANTINE</button>
                            </div>`
                        ).join('');
                    } else {
                        document.getElementById('quarantineList').innerHTML = '<div class="text-muted text-center">No files pending</div>';
                    }
                }
                function updateEvents(events) {
                    const log = document.getElementById('eventLog');
                    if (events && events.length > 0) {
                        events.forEach(e => {
                            const div = document.createElement('div');
                            div.className = 'event-item';
                            div.innerHTML = `<span class="time">${new Date(e.time).toLocaleTimeString()}</span><span class="proc">[${e.process}]</span><span class="file">${e.file}</span><span style="color:#ffcc00;">${e.operation}</span>`;
                            log.insertBefore(div, log.firstChild);
                            if (log.children.length > 50) log.removeChild(log.lastChild);
                        });
                    }
                }
                socket.on('connect', () => { console.log('Connected'); socket.emit('subscribe_updates'); });
                socket.on('status_update', updateStatus);
                socket.on('events_update', updateEvents);
                fetch('/api/status').then(r => r.json()).then(updateStatus);
            </script>
        </body>
        </html>
        '''
    
    # ============================================================
    # COMMANDS FOR DSTERMINAL
    # ============================================================
    
    def start_dashboard(self):
        """Start the security dashboard"""
        if self.is_running:
            return "[!] Dashboard is already running"
        
        if not FLASK_AVAILABLE:
            return "[!] Flask not available. Install with: pip install flask flask-socketio"
        
        def run_dashboard():
            try:
                print("\n" + "=" * 60)
                print("🔮 DSTERMINAL SECURITY DASHBOARD")
                print("=" * 60)
                print(f"📍 Dashboard URL: {self.dashboard_url}")
                print(f"🛡️ Threat Level: {self.shield.threat_level.name if self.shield else 'N/A'}")
                print("=" * 60 + "\n")
                self.socketio.run(self.app, debug=False, host='0.0.0.0', port=self.port, allow_unsafe_werkzeug=True)
            except Exception as e:
                print(f"[!] Dashboard error: {e}")
        
        self.dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        self.dashboard_thread.start()
        self.is_running = True
        
        time.sleep(2)
        try:
            webbrowser.open(self.dashboard_url)
            return f"[+] Dashboard started at {self.dashboard_url} (opened in browser)"
        except:
            return f"[+] Dashboard started at {self.dashboard_url} (open manually)"
    
    def stop_dashboard(self):
        """Stop the dashboard"""
        if not self.is_running:
            return "[!] Dashboard is not running"
        self.is_running = False
        return "[+] Dashboard stopped"
    
    def status(self):
        """Get security status"""
        if self.shield:
            status = self.shield.get_status()
            return f"""
[SECURITY STATUS]
  Threat Level: {status['threat_level']}
  Events: {status['events_monitored']}
  Honeypots: {status['honeypots']}
  Dashboard: {'RUNNING' if self.is_running else 'STOPPED'}
  Workspace: {self.workspace_dir}
"""
        return "[!] Shield Core not available"
    
    def scan(self, path=None):
        """Scan a file or directory"""
        if not self.shield:
            return "[!] Shield Core not available"
        if path and os.path.exists(path):
            result = self.shield.pre_install_scan(path)
            return f"[+] Scan result: {'CLEAN' if result else 'SUSPICIOUS'}"
        return "[!] Path not found"
    
    def quarantine(self, file_path):
        """Quarantine a file"""
        if not self.shield:
            return "[!] Shield Core not available"
        result = self.shield.quarantine_file(file_path)
        return f"[+] Quarantine: {'SUCCESS' if result else 'FAILED'}"
    
    def report(self):
        """Generate a forensic report"""
        if not self.shield:
            return "[!] Shield Core not available"
        report = self.shield.generate_forensic_report()
        return f"[+] Report generated at: {report}"

# ============================================================
# SINGLETON INSTANCE
# ============================================================

security = DSTerminalSecurity()

# ============================================================
# COMMAND FUNCTIONS FOR DSTERMINAL
# ============================================================

def cmd_security_dashboard(args):
    """Start the security dashboard"""
    return security.start_dashboard()

def cmd_security_stop(args):
    """Stop the security dashboard"""
    return security.stop_dashboard()

def cmd_security_status(args):
    """Show security status"""
    return security.status()

def cmd_security_scan(args):
    """Scan a file or directory"""
    return security.scan(args)

def cmd_security_quarantine(args):
    """Quarantine a file"""
    return security.quarantine(args)

def cmd_security_report(args):
    """Generate a forensic report"""
    return security.report()

def cmd_security_help(args):
    """Show security commands"""
    return """
╔══════════════════════════════════════════════════════════════╗
║              DSTERMINAL SECURITY COMMANDS                   ║
╠══════════════════════════════════════════════════════════════╣
║  security dashboard    - Start the security dashboard       ║
║  security stop         - Stop the dashboard                 ║
║  security status       - Show security status               ║
║  security scan <file>  - Scan a file or directory           ║
║  security quarantine   - Quarantine a file                  ║
║  security report       - Generate forensic report           ║
║  security help         - Show this help                     ║
╚══════════════════════════════════════════════════════════════╝
"""

# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 DSTERMINAL SECURITY MODULE TEST")
    print("=" * 60)
    print(security.status())
    print("\nType 'security dashboard' to start the dashboard")
    print("Type 'security help' for all commands\n")
    
    # Run interactive test
    while True:
        try:
            cmd = input("> ").strip().lower()
            if cmd == "exit" or cmd == "quit":
                break
            elif cmd == "security dashboard":
                print(security.start_dashboard())
            elif cmd == "security stop":
                print(security.stop_dashboard())
            elif cmd == "security status":
                print(security.status())
            elif cmd == "security help":
                print(cmd_security_help(None))
            else:
                print("Unknown command. Type 'security help' for commands.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break