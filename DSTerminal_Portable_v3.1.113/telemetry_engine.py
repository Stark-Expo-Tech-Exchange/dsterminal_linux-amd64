# telemetry_engine.py - Place this in your project root

import threading
import time
import queue
from collections import deque
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[!] psutil not installed. Install with: pip install psutil")


@dataclass
class SystemMetrics:
    """System telemetry data container"""
    timestamp: datetime
    cpu_percent: float
    cpu_per_core: list
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_percent: float
    network_rx_mb: float
    network_tx_mb: float
    connections: int
    processes: int
    uptime_seconds: float
    threat_level: str


class TelemetryEngine:
    """
    Real-time system telemetry collector with background threading
    Provides live CPU, RAM, Network, and Process metrics
    """
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self._running = False
        self._thread = None
        self._metrics_queue = queue.Queue(maxsize=100)
        self._current_metrics = None
        self._history = deque(maxlen=60)  # Last 60 seconds of history
        
        # Network tracking for rate calculation
        self._last_net_time = time.time()
        self._last_net_rx = 0
        self._last_net_tx = 0
        
        # Threat level thresholds
        self.threat_level = "LOW"
    
    def start(self):
        """Start the telemetry collector thread"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the telemetry collector"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def get_metrics(self) -> Optional[SystemMetrics]:
        """Get the latest metrics (non-blocking)"""
        if self._current_metrics:
            return self._current_metrics
        return None
    
    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary for easy access"""
        if not self._current_metrics:
            return self._get_empty_metrics()
        
        return {
            "cpu": self._current_metrics.cpu_percent,
            "ram": self._current_metrics.ram_percent,
            "ram_used": self._current_metrics.ram_used_gb,
            "ram_total": self._current_metrics.ram_total_gb,
            "disk": self._current_metrics.disk_percent,
            "rx_mb": self._current_metrics.network_rx_mb,
            "tx_mb": self._current_metrics.network_tx_mb,
            "connections": self._current_metrics.connections,
            "processes": self._current_metrics.processes,
            "uptime": self._current_metrics.uptime_seconds,
            "threat_level": self._current_metrics.threat_level
        }
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics when psutil not available"""
        return {
            "cpu": 0, "ram": 0, "ram_used": 0, "ram_total": 0,
            "disk": 0, "rx_mb": 0, "tx_mb": 0, "connections": 0,
            "processes": 0, "uptime": 0, "threat_level": "UNKNOWN"
        }
    
    def _calculate_threat_level(self, cpu: float, ram: float) -> str:
        """Calculate threat level based on system load"""
        if cpu > 90 or ram > 90:
            return "CRITICAL"
        elif cpu > 80 or ram > 80:
            return "HIGH"
        elif cpu > 60 or ram > 60:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _collect_metrics(self) -> SystemMetrics:
        """Collect single metrics snapshot"""
        timestamp = datetime.now()
        
        if PSUTIL_AVAILABLE:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_per_core = psutil.cpu_percent(percpu=True)
            
            # RAM metrics
            mem = psutil.virtual_memory()
            ram_percent = mem.percent
            ram_used_gb = mem.used / (1024**3)
            ram_total_gb = mem.total / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network metrics (rate calculation)
            net = psutil.net_io_counters()
            current_time = time.time()
            time_delta = current_time - self._last_net_time
            
            if time_delta > 0:
                rx_rate = (net.bytes_recv - self._last_net_rx) / (1024**2) / time_delta
                tx_rate = (net.bytes_sent - self._last_net_tx) / (1024**2) / time_delta
            else:
                rx_rate, tx_rate = 0, 0
            
            self._last_net_time = current_time
            self._last_net_rx = net.bytes_recv
            self._last_net_tx = net.bytes_sent
            
            # Network connections
            connections = len(psutil.net_connections())
            
            # Process count
            processes = len(psutil.pids())
            
            # System uptime
            uptime_seconds = time.time() - psutil.boot_time()
            
        else:
            # Fallback simulated data
            import random
            cpu_percent = random.randint(20, 80)
            cpu_per_core = []
            ram_percent = random.randint(30, 70)
            ram_used_gb = ram_percent / 100 * 16
            ram_total_gb = 16
            disk_percent = random.randint(40, 80)
            rx_rate = random.uniform(0.1, 5.0)
            tx_rate = random.uniform(0.1, 3.0)
            connections = random.randint(20, 150)
            processes = random.randint(80, 250)
            uptime_seconds = random.randint(3600, 86400)
        
        # Calculate threat level
        threat_level = self._calculate_threat_level(cpu_percent, ram_percent)
        self.threat_level = threat_level
        
        return SystemMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            cpu_per_core=cpu_per_core,
            ram_percent=ram_percent,
            ram_used_gb=ram_used_gb,
            ram_total_gb=ram_total_gb,
            disk_percent=disk_percent,
            network_rx_mb=rx_rate,
            network_tx_mb=tx_rate,
            connections=connections,
            processes=processes,
            uptime_seconds=uptime_seconds,
            threat_level=threat_level
        )
    
    def _collect_loop(self):
        """Background collection loop"""
        while self._running:
            try:
                metrics = self._collect_metrics()
                self._current_metrics = metrics
                self._history.append(metrics)
                
                # Put in queue for consumers (non-blocking)
                try:
                    self._metrics_queue.put_nowait(metrics)
                except queue.Full:
                    pass
                    
            except Exception as e:
                print(f"Telemetry error: {e}")
            
            time.sleep(self.update_interval)
    
    def get_metrics_history(self, seconds: int = 60) -> list:
        """Get historical metrics for graphing"""
        return list(self._history)