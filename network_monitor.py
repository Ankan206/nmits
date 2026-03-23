"""
network_monitor.py
------------------
Checks host availability using:
  1. TCP socket connection (works on Render / cloud)
  2. HTTP request fallback
  3. ICMP ping (works locally only)
"""
import subprocess
import platform
import re
import socket
import time
import urllib.request
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler


# ── Main check function ──────────────────────────────────────────────────────

def ping_host(host: str) -> dict:
    """
    Check if a host is reachable using multiple methods.
    Returns {'status': 'UP'|'DOWN', 'latency_ms': float|None}
    """

    # Method 1: TCP socket (most reliable on cloud servers)
    result = _tcp_check(host)
    if result['status'] == 'UP':
        return result

    # Method 2: HTTP/HTTPS request
    result = _http_check(host)
    if result['status'] == 'UP':
        return result

    # Method 3: ICMP ping (works locally, blocked on most cloud)
    result = _icmp_ping(host)
    return result


# ── TCP Socket Check ─────────────────────────────────────────────────────────

def _tcp_check(host: str) -> dict:
    """
    Try connecting to common ports (80, 443, 22, 53).
    If any port responds → host is UP.
    """
    ports = [80, 443, 22, 53, 8080, 8443]

    for port in ports:
        try:
            start = time.time()
            sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            elapsed = (time.time() - start) * 1000
            sock.close()

            if result == 0:
                return {'status': 'UP', 'latency_ms': round(elapsed, 2)}
        except Exception:
            continue

    return {'status': 'DOWN', 'latency_ms': None}


# ── HTTP Check ───────────────────────────────────────────────────────────────

def _http_check(host: str) -> dict:
    """
    Try HTTP and HTTPS requests to the host.
    """
    urls = [f'http://{host}', f'https://{host}']

    for url in urls:
        try:
            start   = time.time()
            req     = urllib.request.urlopen(url, timeout=3)
            elapsed = (time.time() - start) * 1000
            req.close()
            return {'status': 'UP', 'latency_ms': round(elapsed, 2)}
        except Exception:
            continue

    return {'status': 'DOWN', 'latency_ms': None}


# ── ICMP Ping ────────────────────────────────────────────────────────────────

def _icmp_ping(host: str) -> dict:
    """
    Traditional ping — works locally but blocked on most cloud servers.
    """
    system = platform.system().lower()

    if system == 'windows':
        cmd = ['ping', '-n', '1', '-w', '2000', host]
    else:
        cmd = ['ping', '-c', '1', '-W', '2', host]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if result.returncode == 0:
            output  = result.stdout.decode('utf-8', errors='ignore')
            latency = _parse_latency(output, system)
            return {'status': 'UP', 'latency_ms': latency}
        else:
            return {'status': 'DOWN', 'latency_ms': None}
    except Exception:
        return {'status': 'DOWN', 'latency_ms': None}


def _parse_latency(output: str, system: str):
    """Extract round-trip time from ping output."""
    try:
        if system == 'windows':
            match = re.search(r'Average\s*=\s*(\d+)ms', output)
            if not match:
                match = re.search(r'time[=<](\d+)ms', output)
        else:
            match = re.search(r'time[=<]([\d.]+)\s*ms', output)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return None


# ── Background Scheduler ─────────────────────────────────────────────────────

_scheduler = BackgroundScheduler()


def _poll_all_devices(app):
    """Job: check every device and write a NetworkLog row."""
    from models import db, NetworkDevice, NetworkLog

    with app.app_context():
        devices = NetworkDevice.query.all()
        for device in devices:
            result = ping_host(device.host)
            log = NetworkLog(
                device_id  = device.id,
                status     = result['status'],
                latency_ms = result['latency_ms'],
                checked_at = datetime.now(timezone.utc)
            )
            db.session.add(log)
        db.session.commit()


def start_scheduler(app, interval_seconds: int = 60):
    """Start the background polling job."""
    if not _scheduler.running:
        _scheduler.add_job(
            _poll_all_devices,
            'interval',
            seconds=interval_seconds,
            args=[app],
            id='poll_devices',
            replace_existing=True
        )
        _scheduler.start()


def stop_scheduler():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
