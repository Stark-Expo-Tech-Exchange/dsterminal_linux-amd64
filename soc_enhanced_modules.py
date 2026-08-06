# soc_enhanced_modules.py
"""
SOC Enhanced Modules - Complete Integration Package
Includes:
- MITRE ATT&CK Mapping with Mitigations
- Real-time Alert Dashboard with Filters
- Enhanced Reporting with Visual Analytics
- Threat Intelligence Feeds with IOC Management
- Visual Analytics with Charts
"""

import os
import sys
import json
import time
import hashlib
import threading
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

# Try imports with fallbacks
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich import box
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ============================================================
# MITRE ATT&CK INTEGRATION
# ============================================================

class MITREAttackIntegration:
    """MITRE ATT&CK framework integration with mitigations"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.data_path = os.path.join(workspace_path, 'mitre_data')
        os.makedirs(self.data_path, exist_ok=True)
        
        # MITRE ATT&CK Tactics
        self.tactics = {
            'TA0001': 'Initial Access',
            'TA0002': 'Execution',
            'TA0003': 'Persistence',
            'TA0004': 'Privilege Escalation',
            'TA0005': 'Defense Evasion',
            'TA0006': 'Credential Access',
            'TA0007': 'Discovery',
            'TA0008': 'Lateral Movement',
            'TA0009': 'Collection',
            'TA0010': 'Exfiltration',
            'TA0011': 'Command and Control',
            'TA0040': 'Impact'
        }
        
        # MITRE ATT&CK Techniques with mitigations
        self.techniques = self._load_techniques()
        
    def _load_techniques(self) -> Dict:
        """Load MITRE ATT&CK techniques with mitigations"""
        return {
            'T1059': {
                'name': 'Command and Scripting Interpreter',
                'tactics': ['Execution'],
                'description': 'Adversaries may abuse command and script interpreters to execute commands.',
                'mitigations': [
                    'Restrict script execution policies',
                    'Monitor process creation',
                    'Implement application whitelisting',
                    'Disable unnecessary scripting engines'
                ],
                'detection': 'Monitor command-line arguments for suspicious commands'
            },
            'T1055': {
                'name': 'Process Injection',
                'tactics': ['Privilege Escalation', 'Defense Evasion'],
                'description': 'Adversaries may inject code into processes to evade defenses.',
                'mitigations': [
                    'Enable Process Mitigation Options',
                    'Monitor for process injection',
                    'Use EDR solutions'
                ],
                'detection': 'Monitor process memory for suspicious allocations'
            },
            'T1003': {
                'name': 'Credential Dumping',
                'tactics': ['Credential Access'],
                'description': 'Adversaries may attempt to dump credentials from memory.',
                'mitigations': [
                    'Enable Windows Defender Credential Guard',
                    'Limit local administrator privileges',
                    'Monitor LSASS process access'
                ],
                'detection': 'Monitor for suspicious access to LSASS process'
            },
            'T1021': {
                'name': 'Remote Services',
                'tactics': ['Lateral Movement'],
                'description': 'Adversaries may use remote services to move laterally.',
                'mitigations': [
                    'Restrict remote access',
                    'Implement network segmentation',
                    'Monitor for suspicious remote connections'
                ],
                'detection': 'Monitor for unusual remote service connections'
            },
            'T1078': {
                'name': 'Valid Accounts',
                'tactics': ['Initial Access', 'Persistence', 'Privilege Escalation'],
                'description': 'Adversaries may use valid accounts to access systems.',
                'mitigations': [
                    'Implement multi-factor authentication',
                    'Monitor for unusual account behavior',
                    'Regularly review privileged accounts'
                ],
                'detection': 'Monitor for unusual account login activity'
            },
            'T1046': {
                'name': 'Network Service Scanning',
                'tactics': ['Discovery'],
                'description': 'Adversaries may scan network services for vulnerabilities.',
                'mitigations': [
                    'Implement network segmentation',
                    'Monitor for scanning activity',
                    'Block unauthorized scanning tools'
                ],
                'detection': 'Monitor for unusual network scanning activity'
            },
            'T1486': {
                'name': 'Data Encrypted for Impact',
                'tactics': ['Impact'],
                'description': 'Adversaries may encrypt data to disrupt operations.',
                'mitigations': [
                    'Implement backup strategies',
                    'Monitor for unusual file encryption',
                    'Deploy ransomware protection'
                ],
                'detection': 'Monitor for mass file encryption events'
            }
        }
    
    def map_threat_to_attack(self, threat: Dict) -> Dict:
        """Map a threat to MITRE ATT&CK techniques"""
        mapped_techniques = []
        threat_description = threat.get('description', '').lower()
        threat_category = threat.get('category', '').lower()
        
        # Simple mapping based on keywords
        keyword_to_technique = {
            'ransomware': ['T1486', 'T1059'],
            'malware': ['T1204', 'T1105'],
            'phishing': ['T1566', 'T1598'],
            'privilege': ['T1068', 'T1078'],
            'credential': ['T1003', 'T1110'],
            'lateral': ['T1021', 'T1570'],
            'encrypt': ['T1486', 'T1490'],
            'scan': ['T1046', 'T1592'],
            'persistence': ['T1547', 'T1543'],
            'exfil': ['T1048', 'T1029']
        }
        
        for keyword, techniques in keyword_to_technique.items():
            if keyword in threat_description or keyword in threat_category:
                mapped_techniques.extend(techniques)
        
        # Get technique details
        result = {
            'threat_id': threat.get('event_id', ''),
            'mapped_techniques': [],
            'tactics': [],
            'mitigations': []
        }
        
        for tech_id in set(mapped_techniques):
            if tech_id in self.techniques:
                tech = self.techniques[tech_id]
                result['mapped_techniques'].append({
                    'id': tech_id,
                    'name': tech['name'],
                    'description': tech['description']
                })
                result['tactics'].extend(tech.get('tactics', []))
                result['mitigations'].extend(tech.get('mitigations', []))
        
        # Add tactics from the threat itself
        if 'mitre_attack' in threat:
            for tech_id in threat['mitre_attack']:
                if tech_id not in [t['id'] for t in result['mapped_techniques']]:
                    if tech_id in self.techniques:
                        tech = self.techniques[tech_id]
                        result['mapped_techniques'].append({
                            'id': tech_id,
                            'name': tech['name'],
                            'description': tech['description']
                        })
                        result['tactics'].extend(tech.get('tactics', []))
                        result['mitigations'].extend(tech.get('mitigations', []))
        
        # Remove duplicates
        result['tactics'] = list(set(result['tactics']))
        result['mitigations'] = list(set(result['mitigations']))
        
        return result
    
    def get_mitigation_recommendations(self, threat_category: str) -> List[str]:
        """Get mitigation recommendations for a threat category"""
        recommendations = {
            'ransomware': [
                'Implement regular backup strategy',
                'Deploy ransomware protection software',
                'Monitor for mass file encryption',
                'Implement least privilege access',
                'Enable file extension monitoring'
            ],
            'malware': [
                'Keep antivirus definitions updated',
                'Implement application whitelisting',
                'Use endpoint detection and response (EDR)',
                'Regularly scan for malware',
                'Disable unnecessary services'
            ],
            'phishing': [
                'Conduct security awareness training',
                'Implement email filtering',
                'Enable multi-factor authentication',
                'Monitor for suspicious emails',
                'Implement DMARC, SPF, DKIM'
            ],
            'privilege_escalation': [
                'Implement least privilege access',
                'Regularly review user privileges',
                'Monitor for privilege escalation attempts',
                'Use privilege access management (PAM)'
            ],
            'lateral_movement': [
                'Segment the network',
                'Monitor for unusual network connections',
                'Implement zero-trust architecture',
                'Restrict administrative access'
            ],
            'data_exfil': [
                'Implement data loss prevention (DLP)',
                'Monitor outbound traffic',
                'Encrypt sensitive data',
                'Restrict data transfer methods'
            ]
        }
        
        return recommendations.get(threat_category.lower(), [
            'Review security policies',
            'Conduct regular security audits',
            'Implement defense-in-depth',
            'Monitor for suspicious activity'
        ])
    
    def generate_attack_summary(self, threats: List[Dict]) -> Dict:
        """Generate a summary of ATT&CK techniques from threats"""
        summary = {
            'total_threats': len(threats),
            'techniques_used': {},
            'tactics_used': {},
            'mitigations_needed': set(),
            'high_priority': []
        }
        
        for threat in threats:
            mapping = self.map_threat_to_attack(threat)
            for tech in mapping['mapped_techniques']:
                tech_id = tech['id']
                if tech_id not in summary['techniques_used']:
                    summary['techniques_used'][tech_id] = {
                        'name': tech['name'],
                        'count': 0,
                        'threats': []
                    }
                summary['techniques_used'][tech_id]['count'] += 1
                summary['techniques_used'][tech_id]['threats'].append(
                    threat.get('event_id', 'unknown')
                )
            
            for tactic in mapping['tactics']:
                if tactic not in summary['tactics_used']:
                    summary['tactics_used'][tactic] = 0
                summary['tactics_used'][tactic] += 1
            
            for mitigation in mapping['mitigations']:
                summary['mitigations_needed'].add(mitigation)
        
        # Identify high priority techniques (used by multiple threats)
        for tech_id, data in summary['techniques_used'].items():
            if data['count'] > 1:
                summary['high_priority'].append({
                    'id': tech_id,
                    'name': data['name'],
                    'count': data['count']
                })
        
        summary['mitigations_needed'] = list(summary['mitigations_needed'])
        summary['high_priority'] = sorted(
            summary['high_priority'], 
            key=lambda x: x['count'], 
            reverse=True
        )
        
        return summary


# ============================================================
# REAL-TIME ALERT DASHBOARD
# ============================================================
# ============================================================
# REAL-TIME ALERT DASHBOARD - BACKGROUND MODE
# ============================================================

class AlertDashboard:
    """Real-time alert dashboard with filters - Background Mode"""
    
    def __init__(self, background_mode: bool = True):
        self.alerts = deque(maxlen=10000)
        self.alert_queue = deque(maxlen=1000)
        self.severity_counts = defaultdict(int)
        self.category_counts = defaultdict(int)
        self.running = False
        self.dashboard_thread = None
        self.console = Console() if RICH_AVAILABLE else None
        self.filters = {'severity': None, 'category': None, 'status': None}
        self.alert_history = []
        self.notification_callbacks = []
        self.background_mode = background_mode
        
    def start(self):
        """Start the alert dashboard"""
        self.running = True
        if RICH_AVAILABLE and self.console and not self.background_mode:
            self.dashboard_thread = threading.Thread(target=self._run_dashboard, daemon=True)
            self.dashboard_thread.start()
            return True
        else:
            # Background mode - just collect alerts
            self.dashboard_thread = threading.Thread(target=self._background_collector, daemon=True)
            self.dashboard_thread.start()
            return True
    
    def _background_collector(self):
        """Background collector for alerts without display"""
        while self.running:
            # Process any alerts in queue
            while self.alert_queue:
                alert = self.alert_queue.popleft()
                self.alerts.append(alert)
                self.severity_counts[alert.get('severity', 'INFO')] += 1
                self.category_counts[alert.get('category', 'unknown')] += 1
                self.alert_history.append(alert)
                
                # Trigger notifications
                for callback in self.notification_callbacks:
                    try:
                        callback(alert)
                    except:
                        pass
            time.sleep(0.5)
    
    def stop(self):
        """Stop the alert dashboard"""
        self.running = False
        if self.dashboard_thread:
            self.dashboard_thread.join(timeout=2)
    
    def add_alert(self, alert: Dict):
        """Add a new alert to the dashboard"""
        alert['timestamp'] = alert.get('timestamp', datetime.now().isoformat())
        self.alert_queue.append(alert)
    
    def add_notification_callback(self, callback):
        """Add a callback for new alerts"""
        self.notification_callbacks.append(callback)
    
    def get_alerts(self, limit: int = 100) -> List[Dict]:
        """Get recent alerts"""
        return list(self.alerts)[-limit:]
    
    def get_filtered_alerts(self) -> List[Dict]:
        """Get alerts based on current filters"""
        filtered = list(self.alerts)
        
        if self.filters['severity']:
            filtered = [a for a in filtered if a.get('severity') == self.filters['severity']]
        if self.filters['category']:
            filtered = [a for a in filtered if a.get('category') == self.filters['category']]
        if self.filters['status']:
            filtered = [a for a in filtered if a.get('status') == self.filters['status']]
        
        return filtered
    
    def set_filter(self, filter_type: str, value: str):
        """Set a filter on the dashboard"""
        if filter_type in self.filters:
            self.filters[filter_type] = value
    
    def reset_filters(self):
        """Reset all filters"""
        self.filters = {'severity': None, 'category': None, 'status': None}
    
    def export_alerts(self, format: str = 'json') -> str:
        """Export alerts to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"alerts_{timestamp}.{format}"
        filepath = os.path.expanduser(f"~/soc_lab_workspace/alerts/{filename}")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(list(self.alerts), f, indent=2)
        elif format == 'csv':
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'severity', 'category', 'description', 'source'])
                writer.writeheader()
                writer.writerows(list(self.alerts))
        
        return filepath
    
    def get_stats(self) -> Dict:
        """Get alert statistics"""
        return {
            'total': len(self.alerts),
            'critical': self.severity_counts.get('CRITICAL', 0),
            'high': self.severity_counts.get('HIGH', 0),
            'medium': self.severity_counts.get('MEDIUM', 0),
            'low': self.severity_counts.get('LOW', 0),
            'categories': dict(self.category_counts)
        }
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        self.severity_counts.clear()
        self.category_counts.clear()
# ============================================================
# THREAT INTELLIGENCE FEEDS
# ============================================================

# ============================================================
# THREAT INTELLIGENCE FEEDS - FIXED
# ============================================================

class ThreatIntelligence:
    """Threat intelligence feed integration with IOC management"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.intel_path = os.path.join(workspace_path, 'threat_intel')
        os.makedirs(self.intel_path, exist_ok=True)
        
        # IOC storage - using sets for efficient lookup
        self.iocs = {
            'hash': {'malicious': set(), 'suspicious': set(), 'clean': set()},
            'domain': {'malicious': set(), 'suspicious': set(), 'clean': set()},
            'ip': {'malicious': set(), 'suspicious': set(), 'clean': set()},
            'url': {'malicious': set(), 'suspicious': set(), 'clean': set()},
            'file': {'malicious': set(), 'suspicious': set(), 'clean': set()},
            'registry': {'malicious': set(), 'suspicious': set(), 'clean': set()}
        }
        
        # Additional metadata for IOCs
        self.ioc_metadata = {}  # Store additional info about each IOC
        self.last_update = None
        self._load_iocs()
    
    def _load_iocs(self):
        """Load IOCs from disk"""
        ioc_file = os.path.join(self.intel_path, 'iocs.json')
        if os.path.exists(ioc_file):
            try:
                with open(ioc_file, 'r') as f:
                    data = json.load(f)
                    # Load IOC data
                    if 'iocs' in data:
                        for ioc_type, categories in data['iocs'].items():
                            if ioc_type in self.iocs:
                                for category, values in categories.items():
                                    if category in self.iocs[ioc_type]:
                                        self.iocs[ioc_type][category] = set(values)
                    # Load metadata
                    if 'metadata' in data:
                        self.ioc_metadata = data['metadata']
                    print(f"âœ… Loaded {self.get_total_iocs()} IOCs from disk")
            except Exception as e:
                print(f"âš ï¸ Failed to load IOCs: {e}")
    
    def _save_iocs(self):
        """Save IOCs to disk"""
        ioc_file = os.path.join(self.intel_path, 'iocs.json')
        try:
            data = {
                'iocs': {},
                'metadata': self.ioc_metadata,
                'last_updated': datetime.now().isoformat()
            }
            
            for ioc_type, categories in self.iocs.items():
                data['iocs'][ioc_type] = {}
                for category, values in categories.items():
                    data['iocs'][ioc_type][category] = list(values)
            
            with open(ioc_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"âŒ Failed to save IOCs: {e}")
            return False
    
    def add_ioc(self, ioc_type: str, value: str, category: str = 'malicious'):
        """Add an IOC - FIXED"""
        # Normalize inputs
        ioc_type = ioc_type.lower()
        category = category.lower()
        value = value.strip()
        
        # Validate inputs
        if ioc_type not in self.iocs:
            print(f"âŒ Invalid IOC type: {ioc_type}")
            return False
        
        if category not in ['malicious', 'suspicious', 'clean']:
            print(f"âŒ Invalid category: {category}")
            return False
        
        if not value:
            print("âŒ IOC value cannot be empty")
            return False
        
        # Add to appropriate set
        self.iocs[ioc_type][category].add(value)
        
        # Store metadata
        if value not in self.ioc_metadata:
            self.ioc_metadata[value] = {
                'type': ioc_type,
                'category': category,
                'added': datetime.now().isoformat(),
                'source': 'manual'
            }
        
        # Save to disk
        self._save_iocs()
        print(f"âœ… IOC added: {ioc_type} - {value} ({category})")
        return True
    
    def check_ioc(self, ioc_type: str, value: str) -> Dict:
        """Check an IOC against threat intelligence"""
        result = {
            'value': value,
            'type': ioc_type,
            'status': 'unknown',
            'reputation': 0,
            'sources': [],
            'details': {}
        }
        
        ioc_type = ioc_type.lower()
        value_lower = value.lower()
        
        if ioc_type in self.iocs:
            for category, values in self.iocs[ioc_type].items():
                if value_lower in values:
                    result['status'] = category
                    result['reputation'] = 100 if category == 'malicious' else 50 if category == 'suspicious' else 0
                    result['sources'].append('local')
                    
                    # Add metadata if available
                    if value in self.ioc_metadata:
                        result['details'] = self.ioc_metadata[value]
                    break
        
        return result
    
    def get_ioc_stats(self) -> Dict:
        """Get IOC statistics"""
        stats = {}
        for ioc_type, categories in self.iocs.items():
            stats[ioc_type] = {}
            for category, values in categories.items():
                stats[ioc_type][category] = len(values)
        return stats
    
    def get_total_iocs(self) -> int:
        """Get total number of IOCs"""
        total = 0
        for ioc_type, categories in self.iocs.items():
            for category, values in categories.items():
                total += len(values)
        return total
    
    def get_all_iocs(self) -> Dict:
        """Get all IOCs"""
        result = {}
        for ioc_type, categories in self.iocs.items():
            result[ioc_type] = {}
            for category, values in categories.items():
                result[ioc_type][category] = list(values)
        return result
    
    def remove_ioc(self, ioc_type: str, value: str) -> bool:
        """Remove an IOC"""
        ioc_type = ioc_type.lower()
        value_lower = value.lower()
        
        if ioc_type not in self.iocs:
            return False
        
        removed = False
        for category in ['malicious', 'suspicious', 'clean']:
            if value_lower in self.iocs[ioc_type][category]:
                self.iocs[ioc_type][category].remove(value_lower)
                removed = True
                if value in self.ioc_metadata:
                    del self.ioc_metadata[value]
                break
        
        if removed:
            self._save_iocs()
        
        return removed
    def update_feeds(self):
        """Update threat intelligence feeds"""
        self.last_update = datetime.now()
        # In production, fetch from external sources


# ============================================================
# ENHANCED REPORT GENERATOR WITH VISUAL ANALYTICS
# ============================================================

class EnhancedReportGenerator:
    """Enhanced report generation with visual analytics and charts"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.reports_path = os.path.join(workspace_path, 'reports')
        os.makedirs(self.reports_path, exist_ok=True)
        self.charts_path = os.path.join(self.reports_path, 'charts')
        os.makedirs(self.charts_path, exist_ok=True)
    
    def generate_comprehensive_report(self, threats: List[Dict], stats: Dict, 
                                     process_stats: Dict, mitre_summary: Dict,
                                     ioc_stats: Dict) -> Dict:
        """Generate a comprehensive report with analytics"""
        
        report = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'version': 'v4.0.0.113',
                'platform': 'DSTERMINAL Cyber Ops Platform'
            },
            'executive_summary': self._generate_executive_summary(threats, stats),
            'threat_analytics': self._analyze_threats(threats),
            'temporal_analysis': self._analyze_timeline(threats),
            'mitre_analysis': mitre_summary,
            'process_analytics': self._analyze_processes(process_stats),
            'risk_assessment': self._assess_risk(threats),
            'ioc_summary': ioc_stats,
            'recommendations': self._generate_recommendations(threats, mitre_summary),
            'charts': self._generate_charts(threats)
        }
        
        return report
    
    def _generate_executive_summary(self, threats: List[Dict], stats: Dict) -> Dict:
        """Generate executive summary"""
        severity_counts = defaultdict(int)
        for t in threats:
            severity_counts[t.get('severity', 'INFO')] += 1
        
        return {
            'total_threats': len(threats),
            'critical': severity_counts.get('CRITICAL', 0),
            'high': severity_counts.get('HIGH', 0),
            'medium': severity_counts.get('MEDIUM', 0),
            'low': severity_counts.get('LOW', 0),
            'risk_score': self._calculate_risk_score(severity_counts),
            'status': 'ðŸŸ¢ SECURE' if len(threats) == 0 else 'ðŸŸ¡ ACTIVE' if len(threats) < 10 else 'ðŸ”´ CRITICAL'
        }
    
    def _calculate_risk_score(self, severity_counts: Dict) -> int:
        """Calculate overall risk score"""
        score = 0
        score += severity_counts.get('CRITICAL', 0) * 25
        score += severity_counts.get('HIGH', 0) * 15
        score += severity_counts.get('MEDIUM', 0) * 8
        score += severity_counts.get('LOW', 0) * 3
        return min(score, 100)
    
    def _analyze_threats(self, threats: List[Dict]) -> Dict:
        """Analyze threats for patterns"""
        categories = defaultdict(int)
        sources = defaultdict(int)
        
        for t in threats:
            categories[t.get('category', 'unknown')] += 1
            sources[t.get('source', 'unknown')] += 1
        
        return {
            'categories': dict(categories),
            'sources': dict(sources),
            'top_category': max(categories.items(), key=lambda x: x[1])[0] if categories else 'none',
            'top_source': max(sources.items(), key=lambda x: x[1])[0] if sources else 'none'
        }
    
    def _analyze_timeline(self, threats: List[Dict]) -> Dict:
        """Analyze threat timeline"""
        if not threats:
            return {'trend': 'stable', 'description': 'No threats detected'}
        
        hourly = defaultdict(int)
        for t in threats:
            try:
                timestamp = t.get('timestamp', '')
                if timestamp:
                    hour = timestamp[:13]
                    hourly[hour] += 1
            except:
                continue
        
        if not hourly:
            return {'trend': 'stable', 'description': 'No temporal data'}
        
        hours = sorted(hourly.keys())
        if len(hours) < 2:
            return {'trend': 'stable', 'description': 'Insufficient data'}
        
        first_half = sum(hourly[h] for h in hours[:len(hours)//2])
        second_half = sum(hourly[h] for h in hours[len(hours)//2:])
        
        if second_half > first_half * 1.5:
            trend = 'increasing'
            desc = 'Threat activity is increasing - immediate attention required'
        elif second_half < first_half * 0.5:
            trend = 'decreasing'
            desc = 'Threat activity is decreasing - good progress'
        else:
            trend = 'stable'
            desc = 'Threat activity is stable - maintain monitoring'
        
        return {
            'trend': trend,
            'description': desc,
            'hourly_data': dict(hourly),
            'peak_hour': max(hourly.items(), key=lambda x: x[1])[0] if hourly else 'unknown'
        }
    
    def _analyze_processes(self, process_stats: Dict) -> Dict:
        """Analyze process statistics"""
        return {
            'total': process_stats.get('total_processes', 0),
            'system': process_stats.get('system_processes', 0),
            'user': process_stats.get('user_processes', 0),
            'threatened': process_stats.get('processes_with_threats', 0),
            'threat_percentage': self._calculate_percentage(
                process_stats.get('processes_with_threats', 0),
                process_stats.get('total_processes', 1)
            )
        }
    
    def _calculate_percentage(self, part: int, whole: int) -> float:
        """Calculate percentage"""
        if whole == 0:
            return 0
        return round((part / whole) * 100, 1)
    
    def _assess_risk(self, threats: List[Dict]) -> Dict:
        """Assess overall risk"""
        severity_counts = defaultdict(int)
        for t in threats:
            severity_counts[t.get('severity', 'INFO')] += 1
        
        critical = severity_counts.get('CRITICAL', 0)
        high = severity_counts.get('HIGH', 0)
        
        risk_level = 'LOW'
        if critical > 0:
            risk_level = 'CRITICAL'
        elif high > 3:
            risk_level = 'HIGH'
        elif high > 0:
            risk_level = 'MEDIUM'
        
        return {
            'level': risk_level,
            'score': self._calculate_risk_score(severity_counts),
            'critical_count': critical,
            'high_count': high,
            'description': self._get_risk_description(risk_level)
        }
    
    def _get_risk_description(self, risk_level: str) -> str:
        """Get risk description"""
        descriptions = {
            'CRITICAL': 'Immediate action required - active threats detected',
            'HIGH': 'High priority - multiple threats detected',
            'MEDIUM': 'Medium priority - threats detected, monitor closely',
            'LOW': 'Low risk - minimal threats detected'
        }
        return descriptions.get(risk_level, 'Unknown risk level')
    
    def _generate_recommendations(self, threats: List[Dict], mitre_summary: Dict) -> List[str]:
        """Generate recommendations based on threats and MITRE analysis"""
        recommendations = []
        
        if mitre_summary:
            for mitigation in mitre_summary.get('mitigations_needed', []):
                if mitigation not in recommendations:
                    recommendations.append(f"ðŸ”§ {mitigation}")
        
        categories = [t.get('category', '') for t in threats]
        if 'ransomware' in categories:
            recommendations.append("ðŸš¨ Implement ransomware protection and backup strategy")
        if 'malware' in categories:
            recommendations.append("ðŸ›¡ï¸ Update antivirus and endpoint protection")
        if 'phishing' in categories:
            recommendations.append("ðŸŽ“ Conduct security awareness training")
        if 'data_exfiltration' in categories:
            recommendations.append("ðŸ”’ Implement data loss prevention (DLP)")
        if 'privilege_escalation' in categories:
            recommendations.append("ðŸ” Review and restrict user privileges")
        if 'lateral_movement' in categories:
            recommendations.append("ðŸŒ Segment network and implement zero-trust model")
        
        if not recommendations:
            recommendations.append("âœ… System appears secure - maintain monitoring")
        else:
            recommendations.append("ðŸ“Š Regular security audits and reviews")
            recommendations.append("ðŸ”„ Keep all systems and software updated")
            recommendations.append("ðŸ“ Document and review incident response plans")
        
        return list(set(recommendations))
    
    def _generate_charts(self, threats: List[Dict]) -> Dict:
        """Generate charts for the report"""
        charts = {}
        
        if not MATPLOTLIB_AVAILABLE:
            return {'available': False, 'message': 'Matplotlib not installed'}
        
        # Severity Distribution Chart
        severity_counts = defaultdict(int)
        for t in threats:
            severity_counts[t.get('severity', 'INFO')] += 1
        
        if severity_counts:
            fig, ax = plt.subplots(figsize=(8, 4))
            colors = ['red', 'yellow', 'blue', 'green', 'cyan']
            severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
            values = [severity_counts.get(s, 0) for s in severities]
            
            filtered_data = [(s, v) for s, v in zip(severities, values) if v > 0]
            if filtered_data:
                filtered_severities, filtered_values = zip(*filtered_data)
                filtered_colors = colors[:len(filtered_data)]
                
                bars = ax.bar(filtered_severities, filtered_values, color=filtered_colors)
                ax.set_xlabel('Severity')
                ax.set_ylabel('Count')
                ax.set_title('Threat Severity Distribution')
                
                for bar, value in zip(bars, filtered_values):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                           str(value), ha='center', va='bottom')
                
                chart_path = os.path.join(self.charts_path, 'severity_distribution.png')
                plt.savefig(chart_path, dpi=100, bbox_inches='tight')
                plt.close()
                charts['severity_distribution'] = chart_path
        
        # Category Distribution Chart
        category_counts = defaultdict(int)
        for t in threats:
            category_counts[t.get('category', 'unknown')] += 1
        
        if category_counts and len(category_counts) > 1:
            fig, ax = plt.subplots(figsize=(8, 4))
            categories = list(category_counts.keys())[:10]
            values = [category_counts[c] for c in categories]
            
            bars = ax.barh(categories, values, color='skyblue')
            ax.set_xlabel('Count')
            ax.set_ylabel('Category')
            ax.set_title('Threat Categories')
            
            for bar, value in zip(bars, values):
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                       str(value), ha='left', va='center')
            
            chart_path = os.path.join(self.charts_path, 'category_distribution.png')
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts['category_distribution'] = chart_path
        
        # Timeline Chart
        if len(threats) > 10:
            fig, ax = plt.subplots(figsize=(10, 4))
            
            hourly = defaultdict(int)
            for t in threats:
                try:
                    timestamp = t.get('timestamp', '')
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp[:19])
                        hour = dt.strftime('%Y-%m-%d %H:00')
                        hourly[hour] += 1
                except:
                    continue
            
            if hourly:
                hours = sorted(hourly.keys())
                counts = [hourly[h] for h in hours]
                
                ax.plot(hours, counts, marker='o', linestyle='-', color='blue')
                ax.set_xlabel('Time')
                ax.set_ylabel('Threat Count')
                ax.set_title('Threat Timeline')
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.3)
                
                chart_path = os.path.join(self.charts_path, 'timeline.png')
                plt.savefig(chart_path, dpi=100, bbox_inches='tight')
                plt.close()
                charts['timeline'] = chart_path
        
        return charts
    
    def generate_html_report(self, report: Dict) -> str:
        """Generate an HTML report with visualizations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"comprehensive_report_{timestamp}.html"
        filepath = os.path.join(self.reports_path, filename)
        
        html = self._generate_html_content(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath
    
    def _generate_html_content(self, report: Dict) -> str:
        """Generate HTML content for the report"""
        exec_summary = report.get('executive_summary', {})
        threat_analytics = report.get('threat_analytics', {})
        temporal = report.get('temporal_analysis', {})
        risk = report.get('risk_assessment', {})
        process = report.get('process_analytics', {})
        recommendations = report.get('recommendations', [])
        mitre = report.get('mitre_analysis', {})
        ioc_summary = report.get('ioc_summary', {})
        metadata = report.get('metadata', {})
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Security Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin: 20px;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ margin: 0; font-size: 32px; }}
        .header .subtitle {{ opacity: 0.9; margin-top: 10px; }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            text-align: center;
        }}
        .summary-card .value {{ font-size: 32px; font-weight: bold; color: #333; }}
        .summary-card .label {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .risk-critical {{ border-left-color: #dc3545; }}
        .risk-high {{ border-left-color: #fd7e14; }}
        .risk-medium {{ border-left-color: #ffc107; }}
        .risk-low {{ border-left-color: #28a745; }}
        
        .section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        
        .chart-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .chart-item {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            text-align: center;
        }}
        .chart-item img {{ max-width: 100%; height: auto; border-radius: 5px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f5f5f5; }}
        
        .severity-CRITICAL {{ color: #dc3545; font-weight: bold; }}
        .severity-HIGH {{ color: #fd7e14; font-weight: bold; }}
        .severity-MEDIUM {{ color: #ffc107; font-weight: bold; }}
        .severity-LOW {{ color: #28a745; font-weight: bold; }}
        .severity-INFO {{ color: #17a2b8; font-weight: bold; }}
        
        .recommendations {{ background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .recommendations ul {{ list-style-type: none; padding: 0; }}
        .recommendations li {{ padding: 8px 0; padding-left: 25px; position: relative; }}
        .recommendations li::before {{ content: "âœ…"; position: absolute; left: 0; }}
        
        .mitre-section {{ background: #f0f0f0; padding: 15px; border-radius: 10px; margin: 15px 0; }}
        .mitre-item {{ background: white; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #667eea; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
        .badge-critical {{ background: #dc3545; color: white; }}
        .badge-high {{ background: #fd7e14; color: white; }}
        .badge-medium {{ background: #ffc107; color: black; }}
        .badge-low {{ background: #28a745; color: white; }}
        .badge-info {{ background: #17a2b8; color: white; }}
        
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0; text-align: center; color: #666; font-size: 12px; }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            .chart-container {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ðŸ›¡ï¸ SOC Automated Lab - Comprehensive Security Report</h1>
            <div class="subtitle">Generated: {metadata.get('generated', 'Unknown')}</div>
            <div class="subtitle">{metadata.get('platform', '')} {metadata.get('version', '')}</div>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card {self._get_risk_class(exec_summary.get('risk_score', 0))}">
                <div class="value">{exec_summary.get('risk_score', 0)}</div>
                <div class="label">Risk Score</div>
            </div>
            <div class="summary-card">
                <div class="value">{exec_summary.get('total_threats', 0)}</div>
                <div class="label">Total Threats</div>
            </div>
            <div class="summary-card risk-critical">
                <div class="value" style="color: #dc3545;">{exec_summary.get('critical', 0)}</div>
                <div class="label">Critical</div>
            </div>
            <div class="summary-card risk-high">
                <div class="value" style="color: #fd7e14;">{exec_summary.get('high', 0)}</div>
                <div class="label">High</div>
            </div>
            <div class="summary-card">
                <div class="value">{exec_summary.get('medium', 0)}</div>
                <div class="label">Medium</div>
            </div>
            <div class="summary-card">
                <div class="value">{exec_summary.get('low', 0)}</div>
                <div class="label">Low</div>
            </div>
        </div>
        
        <div class="section">
            <h2>ðŸ“Š Executive Summary</h2>
            <p><strong>Status:</strong> {exec_summary.get('status', 'UNKNOWN')}</p>
            <p><strong>Risk Level:</strong> {risk.get('level', 'UNKNOWN')}</p>
            <p><strong>Risk Score:</strong> {risk.get('score', 0)}/100</p>
            <p><strong>Description:</strong> {risk.get('description', 'No assessment')}</p>
        </div>
        
        <div class="section">
            <h2>ðŸ“ˆ Threat Analytics</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h3>Top Categories</h3>
                    <table>
                        <tr><th>Category</th><th>Count</th></tr>
                        {''.join(f'<tr><td>{cat}</td><td>{count}</td></tr>' for cat, count in list(threat_analytics.get('categories', {}).items())[:5])}
                    </table>
                </div>
                <div>
                    <h3>Timeline Analysis</h3>
                    <p><strong>Trend:</strong> {temporal.get('trend', 'stable')}</p>
                    <p><strong>Description:</strong> {temporal.get('description', 'N/A')}</p>
                    <p><strong>Peak Hour:</strong> {temporal.get('peak_hour', 'N/A')}</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>ðŸŽ¯ MITRE ATT&CK Analysis</h2>
            <div class="mitre-section">
                <h3>Techniques Detected</h3>
                {''.join(f'<div class="mitre-item"><strong>{data.get("name", tech)}</strong> - Used {data.get("count", 0)} times</div>' for tech, data in mitre.get('techniques_used', {}).items())}
            </div>
            <div class="mitre-section">
                <h3>Mitigations Needed</h3>
                <ul>
                    {''.join(f'<li>ðŸ”§ {mitigation}</li>' for mitigation in mitre.get('mitigations_needed', [])[:10])}
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>ðŸ–¥ï¸ Process Analytics</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                <div class="summary-card">
                    <div class="value">{process.get('total', 0)}</div>
                    <div class="label">Total Processes</div>
                </div>
                <div class="summary-card">
                    <div class="value">{process.get('system', 0)}</div>
                    <div class="label">System</div>
                </div>
                <div class="summary-card">
                    <div class="value">{process.get('user', 0)}</div>
                    <div class="label">User</div>
                </div>
                <div class="summary-card risk-critical">
                    <div class="value" style="color: #dc3545;">{process.get('threatened', 0)}</div>
                    <div class="label">Threatened</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>ðŸ” Threat Intelligence</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                <div class="summary-card">
                    <div class="value">{ioc_summary.get('hashes', {}).get('malicious', 0)}</div>
                    <div class="label">Malicious Hashes</div>
                </div>
                <div class="summary-card">
                    <div class="value">{ioc_summary.get('domains', {}).get('malicious', 0)}</div>
                    <div class="label">Malicious Domains</div>
                </div>
                <div class="summary-card">
                    <div class="value">{ioc_summary.get('ips', {}).get('malicious', 0)}</div>
                    <div class="label">Malicious IPs</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>ðŸ“‹ Recommendations</h2>
            <div class="recommendations">
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in recommendations)}
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by SOC Automated Lab {metadata.get('version', '')}</p>
            <p>Â© 2024 DSTERMINAL Cyber Ops Platform | All Rights Reserved</p>
            <p>This report is for EDUCATIONAL & AUTHORIZED SECURITY TESTING purposes only.</p>
        </div>
    </div>
</body>
</html>'''
    
    def _get_risk_class(self, risk_score: int) -> str:
        """Get CSS class for risk level"""
        if risk_score >= 70:
            return 'risk-critical'
        elif risk_score >= 40:
            return 'risk-high'
        elif risk_score >= 20:
            return 'risk-medium'
        else:
            return 'risk-low'


# ============================================================
# ENHANCED MODULES MANAGER
# ============================================================
# ============================================================
# ENHANCED MODULES MANAGER - FIXED
# ============================================================

class EnhancedModulesManager:
    """Manager for all enhanced modules"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        
        # Initialize all modules
        self.mitre = MITREAttackIntegration(workspace_path)
        self.alert_dashboard = AlertDashboard(background_mode=True)
        self.threat_intel = ThreatIntelligence(workspace_path)
        self.report_generator = EnhancedReportGenerator(workspace_path)
        
        # Link modules together
        self.alert_dashboard.add_notification_callback(self._on_alert)
        
        self.is_running = False
    
    def _on_alert(self, alert: Dict):
        """Handle new alert - check against threat intelligence"""
        # Check if alert contains an IOC
        if 'ioc' in alert:
            ioc_type = alert.get('ioc_type', 'unknown')
            ioc_value = alert.get('ioc_value', '')
            if ioc_type and ioc_value:
                result = self.threat_intel.check_ioc(ioc_type, ioc_value)
                if result.get('status') == 'malicious':
                    alert['severity'] = 'CRITICAL'
                    alert['description'] = f"[THREAT INTEL] {alert.get('description', '')} - Matched malicious IOC"
    
    def start(self):
        """Start all modules"""
        self.is_running = True
        self.alert_dashboard.start()
        print("âœ… Enhanced Modules started (Background Mode)")
    
    def stop(self):
        """Stop all modules"""
        self.is_running = False
        self.alert_dashboard.stop()
        print("âœ… Enhanced Modules stopped")
    
    def add_ioc(self, ioc_type: str, value: str, category: str = 'malicious') -> bool:
        """Add an IOC - FIXED"""
        return self.threat_intel.add_ioc(ioc_type, value, category)
    
    def remove_ioc(self, ioc_type: str, value: str) -> bool:
        """Remove an IOC"""
        return self.threat_intel.remove_ioc(ioc_type, value)
    
    def check_ioc(self, ioc_type: str, value: str) -> Dict:
        """Check an IOC"""
        return self.threat_intel.check_ioc(ioc_type, value)
    
    def get_ioc_stats(self) -> Dict:
        """Get IOC statistics"""
        return self.threat_intel.get_ioc_stats()
    
    def get_all_iocs(self) -> Dict:
        """Get all IOCs"""
        return self.threat_intel.get_all_iocs()
    
    def generate_full_report(self, threats: List[Dict], stats: Dict, process_stats: Dict) -> str:
        """Generate a full report with all analytics"""
        mitre_summary = self.mitre.generate_attack_summary(threats)
        ioc_stats = self.threat_intel.get_ioc_stats()
        
        report_data = self.report_generator.generate_comprehensive_report(
            threats, stats, process_stats, mitre_summary, ioc_stats
        )
        
        return self.report_generator.generate_html_report(report_data)
    
    def get_status(self) -> Dict:
        """Get status of all modules"""
        alert_stats = self.alert_dashboard.get_stats()
        return {
            'mitre': {
                'techniques': len(self.mitre.techniques),
                'tactics': len(self.mitre.tactics)
            },
            'alert_dashboard': {
                'running': self.alert_dashboard.running,
                'alerts': alert_stats['total'],
                'critical': alert_stats['critical'],
                'high': alert_stats['high'],
                'medium': alert_stats['medium']
            },
            'threat_intel': {
                'iocs': self.threat_intel.get_ioc_stats(),
                'total_iocs': self.threat_intel.get_total_iocs(),
                'last_update': str(self.threat_intel.last_update)
            },
            'running': self.is_running
        }
        """Get status of all modules"""
        alert_stats = self.alert_dashboard.get_stats()
        return {
            'mitre': {
                'techniques': len(self.mitre.techniques),
                'tactics': len(self.mitre.tactics)
            },
            'alert_dashboard': {
                'running': self.alert_dashboard.running,
                'alerts': alert_stats['total'],
                'critical': alert_stats['critical'],
                'high': alert_stats['high'],
                'medium': alert_stats['medium']
            },
            'threat_intel': {
                'iocs': self.threat_intel.get_ioc_stats(),
                'last_update': str(self.threat_intel.last_update)
            },
            'running': self.is_running
        }