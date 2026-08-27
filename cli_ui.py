#!python
#!/usr/bin/env python3
"""
DSTerminal Dynamic SOC Dashboard
Multiple chart types with real-time WebSocket updates
"""

import os
import sys
import time
import random
import threading
import webbrowser
import subprocess
from datetime import datetime

try:
    from flask import Flask, render_template_string, jsonify
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[!] Flask not installed. Install with: pip install flask flask-socketio")
    sys.exit(1)


class DynamicSOCDashboard:
    """Dynamic SOC Dashboard with multiple chart types"""
    
    def __init__(self, port=5000):
        self.port = port
        self.running = False
        self.update_interval = 1.0
        
        # ============================================================
        # METRICS
        # ============================================================
        self.metrics = {
            'total_alerts': random.randint(10000, 50000),
            'critical': random.randint(5, 30),
            'high': random.randint(20, 60),
            'medium': random.randint(50, 150),
            'low': random.randint(100, 300),
            'incidents': random.randint(8, 25),
            'risk_score': random.randint(65, 88),
            'uptime': '99.97%',
            'threat_level': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            'active_sessions': random.randint(50, 200),
            'blocked_ips': random.randint(100, 500),
            'response_time': f"{random.uniform(0.5, 3.0):.1f}s",
        }
        
        # ============================================================
        # CHART 1: Line Chart - Hourly Trend
        # ============================================================
        self.hourly_trend = [random.randint(10, 50) for _ in range(24)]
        
        # ============================================================
        # CHART 2: Pie Chart - Threat Distribution
        # ============================================================
        self.threat_dist = {
            'Malware': random.randint(20, 40),
            'Phishing': random.randint(15, 35),
            'Ransomware': random.randint(10, 25),
            'DDoS': random.randint(5, 20),
            'Insider': random.randint(5, 15),
            'APT': random.randint(5, 15),
        }
        
        # ============================================================
        # CHART 3: Donut Chart - Security Posture
        # ============================================================
        self.security_posture = {
            'Secure': random.randint(40, 70),
            'At Risk': random.randint(20, 40),
            'Critical': random.randint(5, 20),
        }
        
        # ============================================================
        # CHART 4: Horizontal Bar - Security Scores
        # ============================================================
        self.security_scores = {
            'Endpoint': random.randint(65, 95),
            'Network': random.randint(60, 90),
            'Identity': random.randint(70, 92),
            'Data': random.randint(60, 88),
            'Compliance': random.randint(72, 95),
            'Cloud': random.randint(60, 85),
        }
        
        # ============================================================
        # CHART 5: MITRE ATT&CK - Radar/Bar
        # ============================================================
        self.mitre_activity = [
            {'id': 'T1021', 'name': 'Lateral Movement', 'level': random.randint(30, 90)},
            {'id': 'T1059', 'name': 'Command Scripting', 'level': random.randint(25, 85)},
            {'id': 'T1566', 'name': 'Phishing', 'level': random.randint(40, 95)},
            {'id': 'T1003', 'name': 'Credential Dumping', 'level': random.randint(20, 75)},
            {'id': 'T1078', 'name': 'Valid Accounts', 'level': random.randint(35, 85)},
            {'id': 'T1047', 'name': 'WMI Abuse', 'level': random.randint(15, 65)},
        ]
        
        # ============================================================
        # CHART 6: Top Attackers - Bar Chart
        # ============================================================
        self.top_attackers = [
            {'ip': '192.168.1.105', 'count': random.randint(50, 200)},
            {'ip': '10.0.0.57', 'count': random.randint(30, 150)},
            {'ip': '172.16.0.23', 'count': random.randint(25, 120)},
            {'ip': '192.168.1.200', 'count': random.randint(20, 100)},
            {'ip': '10.0.1.88', 'count': random.randint(15, 80)},
        ]
        
        # ============================================================
        # CHART 7: Events Timeline
        # ============================================================
        self.events = []
        self._generate_events()
        
        # ============================================================
        # CHART 8: System Resources - Gauge style
        # ============================================================
        self.system_resources = {
            'cpu': random.randint(20, 80),
            'memory': random.randint(30, 70),
            'disk': random.randint(40, 75),
            'network': random.randint(10, 60),
        }
        
        # ============================================================
        # CHART 9: Alert Severity - Bar Chart
        # ============================================================
        self.severity_dist = {
            'Critical': random.randint(5, 20),
            'High': random.randint(20, 40),
            'Medium': random.randint(40, 60),
            'Low': random.randint(60, 100),
        }
        
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'soc-dashboard-key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        self._setup_routes()

    def _generate_events(self):
        event_types = [
            ('ðŸ›¡ï¸', 'Firewall Block', 'critical'),
            ('âš ï¸', 'Auth Failure', 'warning'),
            ('ðŸ”¥', 'Malware Detected', 'critical'),
            ('ðŸ“¡', 'Lateral Movement', 'warning'),
            ('ðŸ”', 'Suspicious Process', 'info'),
            ('ðŸš¨', 'IDS Alert', 'critical'),
            ('ðŸ“Š', 'SIEM Correlation', 'info'),
            ('ðŸŽ¯', 'Phishing Attempt', 'warning'),
            ('ðŸ’€', 'Ransomware', 'critical'),
            ('ðŸ”', 'Privilege Escalation', 'critical'),
            ('ðŸŒ', 'C2 Communication', 'warning'),
        ]
        for _ in range(20):
            ts = datetime.now().strftime("%H:%M:%S")
            icon, event, severity = random.choice(event_types)
            self.events.append({'time': ts, 'icon': icon, 'event': event, 'severity': severity})

    def _update_metrics(self):
        """Update all data in real-time"""
        m = self.metrics
        
        m['total_alerts'] += random.randint(-30, 60)
        m['total_alerts'] = max(5000, min(60000, m['total_alerts']))
        m['critical'] = max(2, min(40, m['critical'] + random.randint(-1, 2)))
        m['high'] = max(10, min(80, m['high'] + random.randint(-2, 3)))
        m['medium'] = max(30, min(180, m['medium'] + random.randint(-3, 5)))
        m['low'] = max(50, min(350, m['low'] + random.randint(-5, 8)))
        m['incidents'] = max(5, min(30, m['incidents'] + random.randint(-1, 2)))
        m['risk_score'] = max(50, min(95, m['risk_score'] + random.randint(-2, 3)))
        m['active_sessions'] = max(30, min(250, m['active_sessions'] + random.randint(-2, 4)))
        m['blocked_ips'] = max(50, min(600, m['blocked_ips'] + random.randint(-3, 8)))
        m['response_time'] = f"{random.uniform(0.5, 3.0):.1f}s"
        
        if m['risk_score'] > 80:
            m['threat_level'] = 'CRITICAL'
        elif m['risk_score'] > 65:
            m['threat_level'] = 'HIGH'
        elif m['risk_score'] > 50:
            m['threat_level'] = 'MEDIUM'
        else:
            m['threat_level'] = 'LOW'
        
        # Update hourly trend
        new_value = max(5, min(80, self.hourly_trend[-1] + random.randint(-6, 6)))
        self.hourly_trend.append(new_value)
        if len(self.hourly_trend) > 24:
            self.hourly_trend.pop(0)
        
        # Update threat distribution
        for key in self.threat_dist:
            self.threat_dist[key] = max(5, min(45, self.threat_dist[key] + random.randint(-2, 2)))
        
        # Update security posture
        for key in self.security_posture:
            self.security_posture[key] = max(5, min(75, self.security_posture[key] + random.randint(-2, 3)))
        
        # Update security scores
        for key in self.security_scores:
            self.security_scores[key] = max(50, min(98, self.security_scores[key] + random.randint(-2, 3)))
        
        # Update MITRE
        for tech in self.mitre_activity:
            tech['level'] = max(10, min(95, tech['level'] + random.randint(-3, 4)))
        
        # Update attackers
        for attacker in self.top_attackers:
            attacker['count'] = max(10, min(250, attacker['count'] + random.randint(-3, 6)))
        
        # Update resources
        self.system_resources['cpu'] = max(10, min(90, self.system_resources['cpu'] + random.randint(-3, 4)))
        self.system_resources['memory'] = max(20, min(85, self.system_resources['memory'] + random.randint(-2, 3)))
        self.system_resources['disk'] = max(30, min(85, self.system_resources['disk'] + random.randint(-1, 2)))
        self.system_resources['network'] = max(5, min(70, self.system_resources['network'] + random.randint(-2, 3)))
        
        # Update severity
        for key in self.severity_dist:
            self.severity_dist[key] = max(5, min(120, self.severity_dist[key] + random.randint(-3, 4)))
        
        # Generate new event
        if random.random() < 0.2:
            ts = datetime.now().strftime("%H:%M:%S")
            event_types = [
                ('ðŸ›¡ï¸', 'Firewall Block', 'critical'),
                ('âš ï¸', 'Auth Failure', 'warning'),
                ('ðŸ”¥', 'Malware Detected', 'critical'),
                ('ðŸ“¡', 'Lateral Movement', 'warning'),
                ('ðŸš¨', 'IDS Alert', 'critical'),
                ('ðŸ”', 'Suspicious Process', 'info'),
                ('ðŸ“Š', 'SIEM Correlation', 'info'),
            ]
            icon, event, severity = random.choice(event_types)
            self.events.insert(0, {'time': ts, 'icon': icon, 'event': event, 'severity': severity})
            if len(self.events) > 20:
                self.events.pop()

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return render_template_string(self._get_template(), 
                metrics=self.metrics,
                hourly_trend=self.hourly_trend,
                threat_dist=self.threat_dist,
                security_posture=self.security_posture,
                security_scores=self.security_scores,
                mitre=self.mitre_activity,
                attackers=self.top_attackers,
                events=self.events,
                resources=self.system_resources,
                severity=self.severity_dist,
                now=now
            )
        
        @self.app.route('/api/data')
        def api_data():
            return jsonify({
                'metrics': self.metrics,
                'hourly_trend': self.hourly_trend,
                'threat_dist': self.threat_dist,
                'security_posture': self.security_posture,
                'security_scores': self.security_scores,
                'mitre': self.mitre_activity,
                'attackers': self.top_attackers,
                'events': self.events,
                'resources': self.system_resources,
                'severity': self.severity_dist,
            })
        
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')
            emit('connected', {'data': 'Connected'})
        
        @self.socketio.on('request_update')
        def handle_update():
            self._update_metrics()
            self.socketio.emit('data_update', self._get_update_data())

    def _get_update_data(self):
        return {
            'metrics': self.metrics,
            'hourly_trend': self.hourly_trend,
            'threat_dist': self.threat_dist,
            'security_posture': self.security_posture,
            'security_scores': self.security_scores,
            'mitre': self.mitre_activity,
            'attackers': self.top_attackers,
            'events': self.events,
            'resources': self.system_resources,
            'severity': self.severity_dist,
        }

    def _get_template(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DSTerminal SOC Dashboard</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #0d1117;
                    color: #c9d1d9;
                    min-height: 100vh;
                    width: 100%;
                }
                .dashboard {
                    width: 100%;
                    padding: 12px 16px;
                    max-width: 100%;
                }
                
                /* Header */
                .header {
                    background: #161b22;
                    padding: 12px 20px;
                    border-radius: 10px;
                    border: 1px solid #30363d;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                    flex-wrap: wrap;
                    gap: 8px;
                    width: 100%;
                }
                .header h1 {
                    color: #58a6ff;
                    font-size: 1.2em;
                    font-weight: 600;
                }
                .header h1 span { color: #3fb950; }
                .header .status {
                    display: flex;
                    gap: 12px;
                    align-items: center;
                    font-size: 0.8em;
                    flex-wrap: wrap;
                }
                .dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #3fb950;
                    animation: pulse 1s infinite;
                }
                @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.2; } }
                .status-item { color: #8b949e; }
                .status-item strong { color: #f0f6fc; }
                .threat-badge {
                    padding: 2px 10px;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 0.8em;
                }
                .threat-badge.critical { background: #f8514933; color: #f85149; }
                .threat-badge.high { background: #d2992233; color: #d29922; }
                .threat-badge.medium { background: #1f6feb33; color: #58a6ff; }
                .threat-badge.low { background: #3fb95033; color: #3fb950; }
                .fullscreen-btn {
                    background: transparent;
                    border: 1px solid #30363d;
                    color: #8b949e;
                    padding: 4px 14px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 0.8em;
                    transition: all 0.2s;
                }
                .fullscreen-btn:hover { border-color: #58a6ff; color: #58a6ff; }
                
                /* Metrics Grid */
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                    gap: 8px;
                    margin-bottom: 12px;
                    width: 100%;
                }
                .metric-card {
                    background: #161b22;
                    padding: 10px 12px;
                    border-radius: 8px;
                    border: 1px solid #30363d;
                    text-align: center;
                    transition: all 0.3s;
                }
                .metric-card:hover { border-color: #58a6ff; }
                .metric-card .value {
                    font-size: 1.4em;
                    font-weight: 600;
                    color: #f0f6fc;
                    transition: color 0.3s;
                }
                .metric-card .value.critical { color: #f85149; }
                .metric-card .value.warning { color: #d29922; }
                .metric-card .value.good { color: #3fb950; }
                .metric-card .label {
                    font-size: 0.55em;
                    color: #8b949e;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-top: 2px;
                }
                
                /* Charts Grid */
                .charts-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 12px;
                    margin-bottom: 12px;
                    width: 100%;
                }
                .chart-card {
                    background: #161b22;
                    border-radius: 8px;
                    border: 1px solid #30363d;
                    padding: 14px;
                    transition: border-color 0.3s;
                }
                .chart-card:hover { border-color: #58a6ff; }
                .chart-card h3 {
                    color: #58a6ff;
                    font-size: 0.8em;
                    font-weight: 500;
                    margin-bottom: 10px;
                    letter-spacing: 0.5px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .chart-card h3 .live-badge {
                    font-size: 0.6em;
                    color: #3fb950;
                    font-weight: 400;
                    animation: blink 1s infinite;
                }
                @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
                
                /* Bar Chart */
                .bar-chart {
                    display: flex;
                    align-items: flex-end;
                    gap: 2px;
                    height: 100px;
                    padding: 4px 0;
                }
                .bar-item {
                    flex: 1;
                    border-radius: 2px 2px 0 0;
                    min-height: 3px;
                    transition: height 0.4s ease;
                    cursor: pointer;
                }
                .bar-item:hover { opacity: 0.7; }
                .bar-item.critical { background: #f85149; }
                .bar-item.warning { background: #d29922; }
                .bar-item.good { background: #3fb950; }
                .bar-item.info { background: #1f6feb; }
                
                /* Horizontal Bar */
                .h-bar {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    margin: 3px 0;
                    font-size: 0.75em;
                }
                .h-bar .label { color: #8b949e; min-width: 65px; }
                .h-bar .track {
                    flex: 1;
                    height: 5px;
                    background: #0d1117;
                    border-radius: 3px;
                    overflow: hidden;
                }
                .h-bar .fill {
                    height: 100%;
                    border-radius: 3px;
                    transition: width 0.4s ease;
                }
                .h-bar .fill.critical { background: #f85149; }
                .h-bar .fill.high { background: #d29922; }
                .h-bar .fill.medium { background: #1f6feb; }
                .h-bar .fill.low { background: #3fb950; }
                .h-bar .value {
                    min-width: 32px;
                    text-align: right;
                    font-weight: 500;
                    font-size: 0.8em;
                }
                .h-bar .value.critical { color: #f85149; }
                .h-bar .value.warning { color: #d29922; }
                .h-bar .value.good { color: #3fb950; }
                
                /* Pie Chart */
                .pie-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 20px;
                    padding: 8px 0;
                    flex-wrap: wrap;
                }
                .pie {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    position: relative;
                    transition: all 0.4s;
                }
                .pie-center {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 50px;
                    height: 50px;
                    background: #161b22;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 0.6em;
                    color: #8b949e;
                    text-align: center;
                }
                .pie-legend {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 3px 12px;
                    font-size: 0.75em;
                }
                .pie-legend .item {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                .pie-legend .color {
                    width: 10px;
                    height: 10px;
                    border-radius: 3px;
                    flex-shrink: 0;
                }
                .pie-legend .name { color: #8b949e; }
                .pie-legend .val { color: #f0f6fc; font-weight: 500; }
                
                /* Donut Chart */
                .donut {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    position: relative;
                    transition: all 0.4s;
                }
                .donut-center {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 60px;
                    height: 60px;
                    background: #161b22;
                    border-radius: 50%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                }
                .donut-center .num { font-size: 1.2em; font-weight: 600; color: #f0f6fc; }
                .donut-center .lbl { font-size: 0.5em; color: #8b949e; }
                
                /* Events */
                .events-list {
                    max-height: 150px;
                    overflow-y: auto;
                }
                .events-list::-webkit-scrollbar { width: 3px; }
                .events-list::-webkit-scrollbar-thumb { background: #30363d; border-radius: 2px; }
                .event-item {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    padding: 3px 0;
                    border-bottom: 1px solid #0d1117;
                    font-size: 0.75em;
                    animation: slideIn 0.3s ease;
                }
                @keyframes slideIn {
                    from { opacity: 0; transform: translateX(-10px); }
                    to { opacity: 1; transform: translateX(0); }
                }
                .event-item .time { color: #8b949e; min-width: 36px; font-size: 0.8em; }
                .event-item .icon { font-size: 0.9em; }
                .event-item .text { flex: 1; }
                .event-item.critical { border-left: 2px solid #f85149; padding-left: 5px; }
                .event-item.warning { border-left: 2px solid #d29922; padding-left: 5px; }
                .event-item.info { border-left: 2px solid #1f6feb; padding-left: 5px; }
                
                /* Gauge Style */
                .gauge-container {
                    display: flex;
                    justify-content: space-around;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: 8px;
                    padding: 6px 0;
                }
                .gauge-item {
                    text-align: center;
                    flex: 1;
                    min-width: 60px;
                }
                .gauge-ring {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    position: relative;
                    margin: 0 auto;
                    transition: all 0.4s;
                }
                .gauge-ring .center {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 0.8em;
                    font-weight: 600;
                    color: #f0f6fc;
                }
                .gauge-ring .label {
                    font-size: 0.55em;
                    color: #8b949e;
                    margin-top: 4px;
                }
                
                .full-width { grid-column: 1 / -1; }
                
                @media (max-width: 768px) {
                    .dashboard { padding: 8px 10px; }
                    .header { padding: 10px 14px; }
                    .header h1 { font-size: 1em; }
                    .metrics-grid { grid-template-columns: repeat(auto-fit, minmax(90px, 1fr)); }
                    .charts-grid { grid-template-columns: 1fr; }
                    .pie-container { flex-direction: column; }
                    .metric-card .value { font-size: 1.2em; }
                    .bar-chart { height: 80px; }
                    .gauge-ring { width: 50px; height: 50px; }
                }
                @media (max-width: 480px) {
                    .metrics-grid { grid-template-columns: repeat(2, 1fr); }
                    .header .status { font-size: 0.7em; gap: 6px; }
                }
            </style>
        </head>
        <body>
            <div class="dashboard">
                <!-- Header -->
                <div class="header">
                    <h1>ðŸ›¡ï¸ DSTERMINAL <span>SOC</span></h1>
                    <div class="status">
                        <span class="dot"></span>
                        <span class="status-item">LIVE</span>
                        <span class="status-item">|</span>
                        <span class="status-item">Risk: <strong id="riskDisplay">{{ metrics.risk_score }}</strong></span>
                        <span class="status-item">|</span>
                        <span class="status-item" id="clock">{{ now }}</span>
                        <span class="status-item">|</span>
                        <span class="threat-badge {{ metrics.threat_level.lower() }}" id="threatBadge">{{ metrics.threat_level }}</span>
                        <button class="fullscreen-btn" onclick="toggleFullscreen()">â›¶ Fullscreen</button>
                    </div>
                </div>
                
                <!-- Metrics -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="value" id="totalAlerts">{{ metrics.total_alerts }}</div>
                        <div class="label">Total Alerts</div>
                    </div>
                    <div class="metric-card">
                        <div class="value critical" id="critical">{{ metrics.critical }}</div>
                        <div class="label">Critical</div>
                    </div>
                    <div class="metric-card">
                        <div class="value warning" id="high">{{ metrics.high }}</div>
                        <div class="label">High</div>
                    </div>
                    <div class="metric-card">
                        <div class="value" id="incidents">{{ metrics.incidents }}</div>
                        <div class="label">Incidents</div>
                    </div>
                    <div class="metric-card">
                        <div class="value" id="riskScore">{{ metrics.risk_score }}</div>
                        <div class="label">Risk Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="value good" id="uptime">{{ metrics.uptime }}</div>
                        <div class="label">Uptime</div>
                    </div>
                    <div class="metric-card">
                        <div class="value" id="sessions">{{ metrics.active_sessions }}</div>
                        <div class="label">Sessions</div>
                    </div>
                    <div class="metric-card">
                        <div class="value" id="blocked">{{ metrics.blocked_ips }}</div>
                        <div class="label">Blocked IPs</div>
                    </div>
                </div>
                
                <!-- Row 1: Line Chart + Pie Chart -->
                <div class="charts-grid">
                    <!-- Hourly Trend - Line Chart -->
                    <div class="chart-card">
                        <h3>ðŸ“ˆ Hourly Alert Trend <span class="live-badge">â— LIVE</span></h3>
                        <div class="bar-chart" id="hourlyChart">
                            {% for value in hourly_trend %}
                            <div class="bar-item {% if value > 60 %}critical{% elif value > 35 %}warning{% else %}good{% endif %}" 
                                 style="height: {{ value }}%;" title="{{ value }} alerts"></div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <!-- Threat Distribution - Pie Chart -->
                    <div class="chart-card">
                        <h3>ðŸŽ¯ Threat Distribution <span class="live-badge">â— LIVE</span></h3>
                        <div class="pie-container">
                            <div class="pie" id="pieChart">
                                <div class="pie-center">Threats</div>
                            </div>
                            <div class="pie-legend" id="pieLegend">
                                {% for name, value in threat_dist.items() %}
                                <div class="item">
                                    <span class="color" style="background: {{ ['#f85149','#d29922','#1f6feb','#3fb950','#58a6ff','#8b949e'][loop.index0] }}"></span>
                                    <span class="name">{{ name }}</span>
                                    <span class="val" id="pieVal{{ loop.index0 }}">{{ value }}%</span>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Row 2: Donut Chart + Security Scores -->
                <div class="charts-grid">
                    <!-- Security Posture - Donut Chart -->
                    <div class="chart-card">
                        <h3>ðŸ›¡ï¸ Security Posture <span class="live-badge">â— LIVE</span></h3>
                        <div class="pie-container">
                            <div class="donut" id="donutChart">
                                <div class="donut-center">
                                    <span class="num" id="securePct">{{ security_posture.Secure }}%</span>
                                    <span class="lbl">Secure</span>
                                </div>
                            </div>
                            <div class="pie-legend" id="donutLegend">
                                {% for name, value in security_posture.items() %}
                                <div class="item">
                                    <span class="color" style="background: {{ ['#3fb950','#d29922','#f85149'][loop.index0] }}"></span>
                                    <span class="name">{{ name }}</span>
                                    <span class="val" id="donutVal{{ loop.index0 }}">{{ value }}%</span>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Security Scores - Horizontal Bars -->
                    <div class="chart-card">
                        <h3>ðŸ“Š Security Scores <span class="live-badge">â— LIVE</span></h3>
                        {% for name, score in security_scores.items() %}
                        <div class="h-bar" id="scoreRow{{ loop.index0 }}">
                            <span class="label">{{ name }}</span>
                            <div class="track">
                                <div class="fill {% if score > 80 %}low{% elif score > 60 %}medium{% else %}critical{% endif %}" 
                                     style="width: {{ score }}%;" id="scoreFill{{ loop.index0 }}"></div>
                            </div>
                            <span class="value {% if score > 80 %}good{% elif score > 60 %}warning{% else %}critical{% endif %}" id="scoreVal{{ loop.index0 }}">
                                {{ score }}%
                            </span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <!-- Row 3: MITRE + Top Attackers -->
                <div class="charts-grid">
                    <!-- MITRE ATT&CK -->
                    <div class="chart-card">
                        <h3>ðŸŽ¯ MITRE ATT&CK <span class="live-badge">â— LIVE</span></h3>
                        {% for tech in mitre %}
                        <div class="h-bar" id="mitreRow{{ loop.index0 }}">
                            <span class="label" style="min-width: 45px; color: #d29922;">{{ tech.id }}</span>
                            <span style="color: #8b949e; font-size: 0.7em; min-width: 80px;">{{ tech.name }}</span>
                            <div class="track">
                                <div class="fill {% if tech.level > 70 %}critical{% elif tech.level > 40 %}high{% else %}low{% endif %}" 
                                     style="width: {{ tech.level }}%;" id="mitreFill{{ loop.index0 }}"></div>
                            </div>
                            <span class="value {% if tech.level > 70 %}critical{% elif tech.level > 40 %}warning{% else %}good{% endif %}" id="mitreVal{{ loop.index0 }}">
                                {{ tech.level }}%
                            </span>
                        </div>
                        {% endfor %}
                    </div>
                    
                    <!-- Top Attackers - Bar Chart -->
                    <div class="chart-card">
                        <h3>ðŸ‘¤ Top Attackers <span class="live-badge">â— LIVE</span></h3>
                        {% for attacker in attackers %}
                        <div class="h-bar" id="attackerRow{{ loop.index0 }}">
                            <span class="label" style="min-width: 100px; font-family: monospace; color: #f85149;">{{ attacker.ip }}</span>
                            <div class="track">
                                <div class="fill critical" style="width: {{ (attacker.count / 250) * 100 }}%;" id="attackerFill{{ loop.index0 }}"></div>
                            </div>
                            <span class="value critical" id="attackerVal{{ loop.index0 }}">{{ attacker.count }}</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <!-- Row 4: Events + System Resources -->
                <div class="charts-grid">
                    <!-- Events -->
                    <div class="chart-card">
                        <h3>âš¡ Recent Events <span class="live-badge">â— LIVE</span></h3>
                        <div class="events-list" id="eventsList">
                            {% for event in events %}
                            <div class="event-item {{ event.severity }}">
                                <span class="time">{{ event.time }}</span>
                                <span class="icon">{{ event.icon }}</span>
                                <span class="text">{{ event.event }}</span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <!-- System Resources - Gauge -->
                    <div class="chart-card">
                        <h3>ðŸ’» System Resources <span class="live-badge">â— LIVE</span></h3>
                        <div class="gauge-container">
                            {% for name, value in resources.items() %}
                            <div class="gauge-item">
                                <div class="gauge-ring" id="gauge{{ loop.index0 }}" 
                                     style="background: conic-gradient(
                                        {% if value > 75 %}#f85149{% elif value > 50 %}#d29922{% else %}#3fb950{% endif %} 
                                        {{ value }}%, #161b22 {{ value }}%
                                     );">
                                    <div class="center" id="gaugeVal{{ loop.index0 }}">{{ value }}%</div>
                                </div>
                                <div class="label">{{ name|capitalize }}</div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                
                <!-- Alert Severity - Full Width -->
                <div class="charts-grid">
                    <div class="chart-card full-width">
                        <h3>ðŸ“Š Alert Severity Distribution <span class="live-badge">â— LIVE</span></h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; padding: 6px 0;">
                            {% for name, value in severity.items() %}
                            <div id="severityRow{{ loop.index0 }}">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75em; margin-bottom: 3px;">
                                    <span style="color: #8b949e;">{{ name }}</span>
                                    <span style="color: #f0f6fc; font-weight: 500;" id="severityVal{{ loop.index0 }}">{{ value }}</span>
                                </div>
                                <div class="track" style="height: 6px; background: #0d1117; border-radius: 3px; overflow: hidden;">
                                    <div class="fill {% if name == 'Critical' %}critical{% elif name == 'High' %}high{% elif name == 'Medium' %}medium{% else %}low{% endif %}" 
                                         style="width: {{ (value / 120) * 100 if value < 120 else 100 }}%; height: 100%;" 
                                         id="severityFill{{ loop.index0 }}"></div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Clock
                function updateClock() {
                    const now = new Date();
                    document.getElementById('clock').textContent = 
                        now.toLocaleTimeString('en-US', { hour12: false });
                }
                setInterval(updateClock, 1000);
                updateClock();
                
                // Fullscreen
                function toggleFullscreen() {
                    if (!document.fullscreenElement) {
                        document.documentElement.requestFullscreen().catch(err => {});
                    } else {
                        if (document.exitFullscreen) document.exitFullscreen();
                    }
                }
                
                // ============================================================
                // WEBSOCKET - AUTOMATIC REAL-TIME UPDATES
                // ============================================================
                let socket = io();
                
                socket.on('connect', function() {
                    console.log('Connected to SOC Dashboard');
                    socket.emit('request_update');
                });
                
                socket.on('data_update', function(data) {
                    // Update metrics
                    const m = data.metrics;
                    document.getElementById('totalAlerts').textContent = m.total_alerts.toLocaleString();
                    document.getElementById('critical').textContent = m.critical;
                    document.getElementById('high').textContent = m.high;
                    document.getElementById('incidents').textContent = m.incidents;
                    document.getElementById('riskScore').textContent = m.risk_score;
                    document.getElementById('uptime').textContent = m.uptime;
                    document.getElementById('sessions').textContent = m.active_sessions;
                    document.getElementById('blocked').textContent = m.blocked_ips;
                    document.getElementById('riskDisplay').textContent = m.risk_score;
                    
                    const badge = document.getElementById('threatBadge');
                    badge.textContent = m.threat_level;
                    badge.className = 'threat-badge ' + m.threat_level.toLowerCase();
                    
                    // Update hourly chart
                    const hourlyData = data.hourly_trend || [];
                    const hourlyBars = document.querySelectorAll('#hourlyChart .bar-item');
                    hourlyData.forEach((value, index) => {
                        if (hourlyBars[index]) {
                            hourlyBars[index].style.height = value + '%';
                            hourlyBars[index].title = value + ' alerts';
                            hourlyBars[index].className = 'bar-item';
                            if (value > 60) hourlyBars[index].classList.add('critical');
                            else if (value > 35) hourlyBars[index].classList.add('warning');
                            else hourlyBars[index].classList.add('good');
                        }
                    });
                    
                    // Update pie chart
                    const pieColors = ['#f85149', '#d29922', '#1f6feb', '#3fb950', '#58a6ff', '#8b949e'];
                    const threatData = data.threat_dist || {};
                    const pie = document.getElementById('pieChart');
                    if (pie) {
                        let values = Object.values(threatData);
                        let total = values.reduce((a, b) => a + b, 0) || 1;
                        let startAngle = 0;
                        let conicGradient = '';
                        values.forEach((val, idx) => {
                            let angle = (val / total) * 360;
                            conicGradient += `${pieColors[idx % pieColors.length]} ${startAngle}deg ${startAngle + angle}deg, `;
                            startAngle += angle;
                        });
                        pie.style.background = `conic-gradient(${conicGradient.slice(0, -2)})`;
                    }
                    
                    let idx = 0;
                    for (const [name, value] of Object.entries(threatData)) {
                        const el = document.getElementById('pieVal' + idx);
                        if (el) el.textContent = value + '%';
                        idx++;
                    }
                    
                    // Update donut chart
                    const postureData = data.security_posture || {};
                    const donut = document.getElementById('donutChart');
                    if (donut) {
                        let values = Object.values(postureData);
                        let total = values.reduce((a, b) => a + b, 0) || 1;
                        let startAngle = 0;
                        let conicGradient = '';
                        const colors = ['#3fb950', '#d29922', '#f85149'];
                        values.forEach((val, idx) => {
                            let angle = (val / total) * 360;
                            conicGradient += `${colors[idx]} ${startAngle}deg ${startAngle + angle}deg, `;
                            startAngle += angle;
                        });
                        donut.style.background = `conic-gradient(${conicGradient.slice(0, -2)})`;
                    }
                    
                    let dIdx = 0;
                    for (const [name, value] of Object.entries(postureData)) {
                        const el = document.getElementById('donutVal' + dIdx);
                        if (el) el.textContent = value + '%';
                        dIdx++;
                    }
                    document.getElementById('securePct').textContent = (postureData.Secure || 0) + '%';
                    
                    // Update security scores
                    const scores = data.security_scores || {};
                    let sIdx = 0;
                    for (const [name, score] of Object.entries(scores)) {
                        const fill = document.getElementById('scoreFill' + sIdx);
                        const val = document.getElementById('scoreVal' + sIdx);
                        if (fill) {
                            fill.style.width = score + '%';
                            fill.className = 'fill';
                            if (score > 80) fill.classList.add('low');
                            else if (score > 60) fill.classList.add('medium');
                            else fill.classList.add('critical');
                        }
                        if (val) {
                            val.textContent = score + '%';
                            val.className = 'value';
                            if (score > 80) val.classList.add('good');
                            else if (score > 60) val.classList.add('warning');
                            else val.classList.add('critical');
                        }
                        sIdx++;
                    }
                    
                    // Update MITRE
                    const mitreData = data.mitre || [];
                    mitreData.forEach((tech, index) => {
                        const fill = document.getElementById('mitreFill' + index);
                        const val = document.getElementById('mitreVal' + index);
                        if (fill) {
                            fill.style.width = tech.level + '%';
                            fill.className = 'fill';
                            if (tech.level > 70) fill.classList.add('critical');
                            else if (tech.level > 40) fill.classList.add('high');
                            else fill.classList.add('low');
                        }
                        if (val) {
                            val.textContent = tech.level + '%';
                            val.className = 'value';
                            if (tech.level > 70) val.classList.add('critical');
                            else if (tech.level > 40) val.classList.add('warning');
                            else val.classList.add('good');
                        }
                    });
                    
                    // Update attackers
                    const attackers = data.attackers || [];
                    attackers.forEach((attacker, index) => {
                        const fill = document.getElementById('attackerFill' + index);
                        const val = document.getElementById('attackerVal' + index);
                        if (fill) {
                            fill.style.width = (attacker.count / 250) * 100 + '%';
                        }
                        if (val) val.textContent = attacker.count;
                    });
                    
                    // Update gauge
                    const resources = data.resources || {};
                    let rIdx = 0;
                    for (const [name, value] of Object.entries(resources)) {
                        const gauge = document.getElementById('gauge' + rIdx);
                        const val = document.getElementById('gaugeVal' + rIdx);
                        if (gauge) {
                            const color = value > 75 ? '#f85149' : value > 50 ? '#d29922' : '#3fb950';
                            gauge.style.background = `conic-gradient(${color} ${value}%, #161b22 ${value}%)`;
                        }
                        if (val) val.textContent = value + '%';
                        rIdx++;
                    }
                    
                    // Update severity
                    const severity = data.severity || {};
                    let sevIdx = 0;
                    for (const [name, value] of Object.entries(severity)) {
                        const fill = document.getElementById('severityFill' + sevIdx);
                        const val = document.getElementById('severityVal' + sevIdx);
                        if (fill) {
                            const pct = Math.min((value / 120) * 100, 100);
                            fill.style.width = pct + '%';
                        }
                        if (val) val.textContent = value;
                        sevIdx++;
                    }
                    
                    // Update events
                    const events = data.events || [];
                    const eventsList = document.getElementById('eventsList');
                    if (eventsList) {
                        let html = '';
                        for (const event of events) {
                            html += `
                                <div class="event-item ${event.severity}">
                                    <span class="time">${event.time}</span>
                                    <span class="icon">${event.icon}</span>
                                    <span class="text">${event.event}</span>
                                </div>
                            `;
                        }
                        eventsList.innerHTML = html;
                    }
                });
                
                // Auto-reconnect
                socket.on('disconnect', function() {
                    console.log('Disconnected, reconnecting...');
                    setTimeout(function() { socket.connect(); }, 1000);
                });
                
                // Fallback polling
                setInterval(function() {
                    if (!socket || !socket.connected) {
                        fetch('/api/data')
                            .then(response => response.json())
                            .then(data => {
                                const m = data.metrics;
                                document.getElementById('totalAlerts').textContent = m.total_alerts.toLocaleString();
                                document.getElementById('critical').textContent = m.critical;
                                document.getElementById('high').textContent = m.high;
                                document.getElementById('incidents').textContent = m.incidents;
                                document.getElementById('riskScore').textContent = m.risk_score;
                                document.getElementById('uptime').textContent = m.uptime;
                                document.getElementById('sessions').textContent = m.active_sessions;
                                document.getElementById('blocked').textContent = m.blocked_ips;
                                document.getElementById('riskDisplay').textContent = m.risk_score;
                            })
                            .catch(err => console.log('Polling error:', err));
                    }
                }, 3000);
            </script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>
        </body>
        </html>
        """

    def start(self):
        self.running = True
        
        def update_loop():
            while self.running:
                time.sleep(self.update_interval)
                if self.socketio:
                    self._update_metrics()
                    self.socketio.emit('data_update', self._get_update_data())
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
        url = f"http://localhost:{self.port}"
        
        print(f"\n{'='*60}")
        print("ðŸ›¡ï¸ DSTERMINAL DYNAMIC SOC DASHBOARD")
        print(f"{'='*60}")
        print(f"ðŸ“ URL: {url}")
        print(f"â±ï¸  Update Interval: {self.update_interval}s")
        print(f"ðŸ“Š Multiple Chart Types (Bar, Pie, Donut, Gauge, Horizontal Bar)")
        print(f"ðŸ”„ Real-time WebSocket Updates - NO Page Refresh")
        print(f"{'='*60}\n")
        
        try:
            chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if os.path.exists(chrome):
                subprocess.Popen([chrome, "--kiosk", url])
                print("âœ… Chrome opened in fullscreen mode")
            else:
                webbrowser.open(url)
        except:
            webbrowser.open(url)
        
        print("\nðŸ”„ Press Ctrl+C to stop\n")
        
        try:
            self.socketio.run(self.app, host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        print("\nâœ… Dashboard stopped")


if __name__ == "__main__":
    dashboard = DynamicSOCDashboard(port=5000)
    dashboard.start()