import platform
import time
import psutil


# ============================================================
# CPU
# ============================================================

def get_cpu():
    return {
        "usage": round(psutil.cpu_percent(interval=0.2), 1),
        "cores": psutil.cpu_count(logical=False) or 0,
        "threads": psutil.cpu_count(logical=True) or 0
    }


# ============================================================
# MEMORY / RAM
# ============================================================

def get_memory():
    memory = psutil.virtual_memory()

    return {
        "usage": round(memory.percent, 1),
        "used_gb": round(memory.used / (1024 ** 3), 2),
        "total_gb": round(memory.total / (1024 ** 3), 2)
    }


# ============================================================
# DISK
# ============================================================

def get_disk():
    try:
        disk = psutil.disk_usage("C:\\")

        return {
            "usage": round(disk.percent, 1),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "total_gb": round(disk.total / (1024 ** 3), 2)
        }

    except Exception:
        return {
            "usage": 0,
            "used_gb": 0,
            "total_gb": 0
        }


# ============================================================
# NETWORK
# ============================================================

_previous_network = None
_previous_time = None


def get_network():
    global _previous_network
    global _previous_time

    current = psutil.net_io_counters()
    current_time = time.time()

    if _previous_network is None:
        _previous_network = current
        _previous_time = current_time

        return {
            "download_mbps": 0,
            "upload_mbps": 0,
            "status": "INITIALIZING"
        }

    elapsed = current_time - _previous_time

    if elapsed <= 0:
        elapsed = 1

    download_bytes = (
        current.bytes_recv -
        _previous_network.bytes_recv
    )

    upload_bytes = (
        current.bytes_sent -
        _previous_network.bytes_sent
    )

    download_mbps = (
        download_bytes * 8
    ) / elapsed / 1_000_000

    upload_mbps = (
        upload_bytes * 8
    ) / elapsed / 1_000_000

    _previous_network = current
    _previous_time = current_time

    return {
        "download_mbps": round(max(download_mbps, 0), 2),
        "upload_mbps": round(max(upload_mbps, 0), 2),
        "status": "OPTIMAL"
    }


# ============================================================
# BATTERY
# ============================================================

def get_battery():
    battery = psutil.sensors_battery()

    if battery is None:
        return {
            "available": False,
            "percent": None,
            "plugged": None
        }

    return {
        "available": True,
        "percent": round(battery.percent, 1),
        "plugged": battery.power_plugged
    }


# ============================================================
# CPU TEMPERATURE
# ============================================================

def get_temperature():

    try:

        temperatures = psutil.sensors_temperatures()

        if not temperatures:
            return None

        preferred_names = [
            "cpu",
            "coretemp",
            "k10temp",
            "zenpower",
            "acpitz"
        ]

        for name in preferred_names:

            if name in temperatures:

                for entry in temperatures[name]:

                    if entry.current is not None:
                        return round(entry.current, 1)

        for entries in temperatures.values():

            for entry in entries:

                if entry.current is not None:
                    return round(entry.current, 1)

    except Exception:
        pass

    return None


# ============================================================
# UPTIME
# ============================================================

def get_uptime():

    boot_time = psutil.boot_time()

    uptime_seconds = (
        time.time() -
        boot_time
    )

    days = int(
        uptime_seconds // 86400
    )

    hours = int(
        (uptime_seconds % 86400) // 3600
    )

    minutes = int(
        (uptime_seconds % 3600) // 60
    )

    return {
        "days": days,
        "hours": hours,
        "minutes": minutes
    }


# ============================================================
# COMPLETE SYSTEM TELEMETRY
# ============================================================

def get_system_stats():

    return {

        "system": {
            "platform": platform.system(),
            "hostname": platform.node()
        },

        "cpu": get_cpu(),

        "memory": get_memory(),

        "disk": get_disk(),

        "temperature": get_temperature(),

        "network": get_network(),

        "battery": get_battery(),

        "uptime": get_uptime(),

        "timestamp": time.time()
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    import json

    print()
    print("=" * 60)
    print("             ALFRED PC MONITOR")
    print("=" * 60)

    print(
        json.dumps(
            get_system_stats(),
            indent=4
        )
    )

    print("=" * 60)