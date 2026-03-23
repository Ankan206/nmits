"""
network_monitor.py
------------------
Handles ping checks and the background scheduler that polls all devices.
"""
import subprocess
import platform
import re
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler


def ping_host(host: str) -> dict:
    """
    Ping a host and return {'status': 'UP'|'DOWN', 'latency_ms': float|None}.
    Works on Windows, Linux, and macOS.
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
            output = result.stdout.decode('utf-8', errors='ignore')
            latency = _parse_latency(output, system)
            return {'status': 'UP', 'latency_ms': latency}
        else:
            return {'status': 'DOWN', 'latency_ms': None}
    except Exception:
        return {'status': 'DOWN', 'latency_ms': None}


def _parse_latency(output: str, system: str) -> float | None:
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


# ── Background Scheduler ────────────────────────────────────────────────────

_scheduler = BackgroundScheduler()


def _poll_all_devices(app):
    """Job function: ping every device and write a NetworkLog row."""
    from models import db, NetworkDevice, NetworkLog

    with app.app_context():
        devices = NetworkDevice.query.all()
        for device in devices:
            result = ping_host(device.host)
            log = NetworkLog(
                device_id  = device.id,
                status     = result['status'],
                latency_ms = result['latency_ms'],
                checked_at = datetime.utcnow()
            )
            db.session.add(log)
        db.session.commit()


def start_scheduler(app, interval_seconds: int = 60):
    """Start the background polling job (called once at app startup)."""
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
