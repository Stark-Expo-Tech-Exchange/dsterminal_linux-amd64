# ============================================================
# SIEM EVENT & ALERT TEST SCRIPT
# Generates various security events to test the dashboard
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   SIEM EVENT & ALERT GENERATOR - REAL-TIME TEST" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if dashboard is running
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/health" -TimeoutSec 2
    Write-Host "✅ Dashboard is running!" -ForegroundColor Green
    Write-Host "   http://127.0.0.1:5000" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Dashboard is NOT running!" -ForegroundColor Red
    Write-Host "   Please start it first: python network_security_realtime.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Press ENTER to start generating test events..." -ForegroundColor Yellow
Read-Host

# ============================================================
# TEST 1: Generate IP Block Events (Firewall)
# ============================================================

Write-Host ""
Write-Host "[1] Generating Firewall - IP BLOCK events..." -ForegroundColor Green

$testIPs = @(
    "10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5",
    "192.168.1.100", "192.168.1.101", "192.168.1.102",
    "172.16.0.1", "172.16.0.2"
)

$i = 0
foreach ($ip in $testIPs) {
    $i++
    $reason = "Test alert $i - $ip"
    Write-Host "  Blocking $ip..." -NoNewline
    try {
        $body = @{ip=$ip; reason=$reason} | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/firewall/block-ip" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        if ($result.success) {
            Write-Host " ✅ BLOCKED" -ForegroundColor Green
        } else {
            Write-Host " ⚠️ Already blocked" -ForegroundColor Yellow
        }
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 300
}

# ============================================================
# TEST 2: Generate Multiple Failed Logins (SIEM - Brute Force)
# ============================================================

Write-Host ""
Write-Host "[2] Generating SIEM - BRUTE FORCE events..." -ForegroundColor Green

$bruteIPs = @("192.168.1.50", "192.168.1.51", "10.0.0.10")

foreach ($ip in $bruteIPs) {
    for ($j=1; $j -le 6; $j++) {
        Write-Host "  Failed login attempt $j from $ip" -NoNewline
        try {
            $body = @{
                source="SIEM_Test"
                event_type="failed_login"
                severity="HIGH"
                message="Failed login attempt from $ip"
                data=@{
                    source_ip=$ip
                    username="admin"
                    attempt=$j
                }
            } | ConvertTo-Json -Depth 3
            $result = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/events" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
            Write-Host " ✅ Logged" -ForegroundColor Green
        } catch {
            Write-Host " ❌ Failed" -ForegroundColor Red
        }
        Start-Sleep -Milliseconds 200
    }
    Start-Sleep -Milliseconds 500
}

# ============================================================
# TEST 3: Generate Port Scan Events (IDS/IPS)
# ============================================================

Write-Host ""
Write-Host "[3] Generating IDS/IPS - PORT SCAN events..." -ForegroundColor Green

$scanIP = "10.0.0.100"
$ports = @(22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 5432, 8080, 8443)

Write-Host "  Port scan from $scanIP" -NoNewline
foreach ($port in $ports) {
    try {
        $body = @{
            source="IDS_Test"
            event_type="connection_attempt"
            severity="MEDIUM"
            message="Port scan detected from $scanIP"
            data=@{
                source_ip=$scanIP
                port=$port
                protocol="TCP"
            }
        } | ConvertTo-Json -Depth 3
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/events" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
    } catch {}
    Start-Sleep -Milliseconds 50
}
Write-Host " ✅ Logged $($ports.Count) attempts" -ForegroundColor Green

# ============================================================
# TEST 4: Generate Threat IOC Events
# ============================================================

Write-Host ""
Write-Host "[4] Generating Threat Intelligence - IOC events..." -ForegroundColor Green

$iocs = @(
    @{ip="185.130.5.253"; description="Test C2 Server"},
    @{ip="94.102.61.78"; description="Test Malware Distribution"},
    @{ip="45.155.205.233"; description="Test Phishing Host"}
)

foreach ($ioc in $iocs) {
    Write-Host "  Adding IOC: $($ioc.ip)" -NoNewline
    try {
        $body = $ioc | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/ioc/add" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        Write-Host " ✅ Added" -ForegroundColor Green
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 300
}

# ============================================================
# TEST 5: Generate Connection to Known Threat IPs
# ============================================================

Write-Host ""
Write-Host "[5] Simulating connections to known threat IPs..." -ForegroundColor Green

$threatIPs = @("185.130.5.253", "94.102.61.78", "45.155.205.233")

foreach ($ip in $threatIPs) {
    Write-Host "  Connecting to $ip..." -NoNewline
    try {
        $body = @{
            source="IDS_Test"
            event_type="known_threat_connection"
            severity="CRITICAL"
            message="Connection to known threat IOC: $ip"
            data=@{
                remote_ip=$ip
                remote_port=443
                process="test_process.exe"
            }
        } | ConvertTo-Json -Depth 3
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/events" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        Write-Host " ✅ Logged" -ForegroundColor Green
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

# ============================================================
# TEST 6: Generate Suspicious Process Events
# ============================================================

Write-Host ""
Write-Host "[6] Generating Endpoint - SUSPICIOUS PROCESS events..." -ForegroundColor Green

$suspiciousProcesses = @(
    @{name="cryptominer.exe"; pid=1234},
    @{name="keylogger.exe"; pid=5678},
    @{name="backdoor.exe"; pid=9012}
)

foreach ($proc in $suspiciousProcesses) {
    Write-Host "  Detected: $($proc.name) PID $($proc.pid)" -NoNewline
    try {
        $body = @{
            source="Endpoint_Test"
            event_type="suspicious_process"
            severity="HIGH"
            message="Suspicious process detected: $($proc.name)"
            data=@{
                pid=$proc.pid
                name=$proc.name
                reason="Process name contains malicious term"
            }
        } | ConvertTo-Json -Depth 3
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/events" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        Write-Host " ✅ Logged" -ForegroundColor Green
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 300
}

# ============================================================
# TEST 7: Generate C2 Communication Events
# ============================================================

Write-Host ""
Write-Host "[7] Generating IDS/IPS - C2 COMMUNICATION events..." -ForegroundColor Green

$c2Ports = @(4444, 5555, 1337, 6666, 6667)
$c2IP = "10.0.0.200"

foreach ($port in $c2Ports) {
    Write-Host "  C2 traffic on port $port from $c2IP" -NoNewline
    try {
        $body = @{
            source="IDS_Test"
            event_type="possible_c2"
            severity="CRITICAL"
            message="Possible C2 communication detected on port $port"
            data=@{
                source_ip=$c2IP
                remote_port=$port
                process="svchost.exe"
            }
        } | ConvertTo-Json -Depth 3
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/events" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        Write-Host " ✅ Logged" -ForegroundColor Green
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 300
}

# ============================================================
# TEST 8: Generate Multiple Alert Types
# ============================================================

Write-Host ""
Write-Host "[8] Generating various security alerts..." -ForegroundColor Green

$alerts = @(
    @{severity="CRITICAL"; title="Ransomware Detected"; message="Potential ransomware activity on host"},
    @{severity="HIGH"; title="Data Exfiltration"; message="Large data upload detected to external IP"},
    @{severity="MEDIUM"; title="Unusual Network Traffic"; message="Unusual traffic pattern detected"},
    @{severity="LOW"; title="System Update Required"; message="Security patch available for installed software"},
    @{severity="CRITICAL"; title="Privilege Escalation"; message="User attempted unauthorized privilege escalation"},
    @{severity="HIGH"; title="Malware Download"; message="Malicious file download detected from suspicious URL"}
)

foreach ($alert in $alerts) {
    Write-Host "  [$($alert.severity)] $($alert.title)" -NoNewline
    try {
        $body = @{
            source="Alert_Test"
            event_type=$alert.title
            severity=$alert.severity
            message=$alert.message
            data=@{timestamp=(Get-Date -Format "yyyy-MM-ddTHH:mm:ss")}
        } | ConvertTo-Json -Depth 3
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/events" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        Write-Host " ✅ Logged" -ForegroundColor Green
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 400
}

# ============================================================
# TEST 9: Generate Process Scan
# ============================================================

Write-Host ""
Write-Host "[9] Triggering process scan..." -ForegroundColor Green
try {
    $result = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/process/scan" -Method Post -ErrorAction Stop
    Write-Host "  ✅ Process scan triggered - $($result.suspicious) suspicious findings" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed" -ForegroundColor Red
}

# ============================================================
# TEST 10: Check for Events
# ============================================================

Write-Host ""
Write-Host "[10] Checking for generated events..." -ForegroundColor Green
try {
    $events = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/events?limit=10" -ErrorAction Stop
    Write-Host "  ✅ Found $($events.Count) recent events" -ForegroundColor Green
    if ($events.Count -gt 0) {
        Write-Host ""
        Write-Host "  Recent Events:" -ForegroundColor Cyan
        foreach ($event in $events | Select-Object -First 5) {
            Write-Host "    [$($event.severity)] $($event.event_type) - $($event.message)" -ForegroundColor White
        }
    }
} catch {
    Write-Host "  ❌ Failed to check events" -ForegroundColor Red
}

# ============================================================
# COMPLETE
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ TEST COMPLETE! Check the dashboard for alerts." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard URL: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Expected to see:" -ForegroundColor White
Write-Host "  🔴 CRITICAL: C2 Communication, Known Threat, Ransomware" -ForegroundColor Red
Write-Host "  🟠 HIGH: Brute Force, Suspicious Process, Data Exfiltration" -ForegroundColor Yellow
Write-Host "  🟡 MEDIUM: Port Scan, Unusual Traffic" -ForegroundColor Yellow
Write-Host "  🔵 LOW: System Update Required" -ForegroundColor Blue
Write-Host ""
Write-Host "Press ENTER to exit..." -ForegroundColor Yellow
Read-Host