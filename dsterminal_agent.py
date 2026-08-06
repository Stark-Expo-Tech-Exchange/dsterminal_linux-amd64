"""
DSTerminal Security Agent
Persistent background service with real-time monitoring
Auto-starts on system boot and runs silently
"""

import os
import sys
import time
import json
import threading
import logging
import socket
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import our security core
from dsterminal_production import DSTerminalSecurityCore

# Configure logging for persistent agent
LOG_DIR = os.path.join(os.environ.get('USERPROFILE', 'C:\\Users'), 'DSTerminal_Logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'security_agent.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DSTerminalAgent')


class SecurityAgent:
    """
    Persistent security agent that runs in the background
    """
    
    def __init__(self, auto_start=True):
        self.security = DSTerminalSecurityCore(enable_real_time=auto_start)
        self.is_running = False
        self.thread = None
        self.events_queue = []
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'threats_blocked': 0,
            'files_protected': 0,
            'alerts_raised': 0
        }
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("ðŸ›¡ï¸ DSTerminal Security Agent initialized")
        logger.info(f"ðŸ“ Logs directory: {LOG_DIR}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the security agent"""
        if self.is_running:
            logger.warning("Agent already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
        logger.info("âœ… Security Agent started successfully")
        self._print_banner()
    
    def _run(self):
        """Main agent loop"""
        while self.is_running:
            try:
                # Monitor security status
                status = self.security.get_security_status()
                
                # Check for threats
                if status['threat_level'] in ['HIGH_RISK', 'RANSOMWARE_DETECTED']:
                    self._handle_threat(status)
                
                # Log periodic status
                self._log_status(status)
                
                # Check for events
                self._process_events()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Agent loop error: {e}")
                time.sleep(30)
    
    def _handle_threat(self, status):
        """Handle detected threats"""
        logger.warning(f"ðŸš¨ THREAT DETECTED: {status['threat_level']}")
        self.stats['threats_blocked'] += 1
        
        # Create alert file
        alert_file = os.path.join(LOG_DIR, f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'threat_level': status['threat_level'],
            'events_monitored': status['events_monitored'],
            'quarantine_active': status['quarantine_active']
        }
        with open(alert_file, 'w') as f:
            json.dump(alert_data, f, indent=2)
        
        logger.info(f"ðŸ“„ Alert saved to: {alert_file}")
    
    def _log_status(self, status):
        """Log current status"""
        if status['threat_level'] == 'CLEAN':
            level_emoji = 'ðŸŸ¢'
        elif status['threat_level'] == 'SUSPICIOUS':
            level_emoji = 'ðŸŸ¡'
        elif status['threat_level'] == 'HIGH_RISK':
            level_emoji = 'ðŸŸ '
        else:
            level_emoji = 'ðŸ”´'
        
        logger.debug(f"{level_emoji} Status: {status['threat_level']} | "
                    f"Events: {status['events_monitored']} | "
                    f"Backups: {status['backup_points']}")
    
    def _process_events(self):
        """Process queued security events"""
        # Check for new events from the security core
        new_events = self.security.shield.event_log[-5:] if self.security.shield.event_log else []
        
        for event in new_events:
            if event not in self.events_queue:
                self.events_queue.append(event)
                self.stats['files_protected'] += 1
                
                # Log significant events
                if event.operation == 'write':
                    logger.info(f"ðŸ“ File modified: {os.path.basename(event.path)} by {event.process_name}")
    
    def _print_banner(self):
        """Print startup banner"""
        banner = f"""
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘              DSTERMINAL SECURITY AGENT ACTIVE                â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                           â•‘
â•‘  PID: {os.getpid()}                                                     â•‘
â•‘  Logs: {LOG_DIR}                                   â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"""
        print(banner)
        logger.info("Agent banner displayed")
    
    def stop(self):
        """Stop the security agent"""
        logger.info("Stopping Security Agent...")
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=5)
        
        self.security.deactivate()
        logger.info("âœ… Security Agent stopped")
    
    def get_report(self) -> Dict:
        """Generate agent report"""
        status = self.security.get_security_status()
        return {
            'agent': {
                'running': self.is_running,
                'uptime': (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds(),
                'pid': os.getpid()
            },
            'stats': self.stats,
            'security_status': status,
            'recent_events': [
                {
                    'time': datetime.fromtimestamp(e.timestamp).isoformat(),
                    'file': os.path.basename(e.path),
                    'process': e.process_name,
                    'action': e.operation
                }
                for e in self.events_queue[-10:]
            ]
        }


def create_startup_entry():
    """Create Windows startup entry for the agent"""
    try:
        import winreg
        
        # Get script path
        script_path = os.path.abspath(__file__)
        python_path = sys.executable
        
        # Create startup registry entry
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        winreg.SetValueEx(key, "DSTerminalSecurity", 0, winreg.REG_SZ, 
                         f'"{python_path}" "{script_path}" --startup')
        winreg.CloseKey(key)
        
        logger.info("âœ… Startup entry created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create startup entry: {e}")
        return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DSTerminal Security Agent')
    parser.add_argument('--startup', action='store_true', help='Run as startup service')
    parser.add_argument('--install', action='store_true', help='Install startup entry')
    parser.add_argument('--uninstall', action='store_true', help='Remove startup entry')
    args = parser.parse_args()
    
    if args.install:
        create_startup_entry()
        return
    
    if args.uninstall:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "DSTerminalSecurity")
            winreg.CloseKey(key)
            print("âœ… Startup entry removed")
        except Exception as e:
            print(f"âŒ Failed to remove: {e}")
        return
    
    # Normal run
    agent = SecurityAgent(auto_start=True)
    
    try:
        agent.start()
        
        # Keep the agent running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        agent.stop()


if __name__ == "__main__":
    main()