import psutil

def collect_cpu():
    return {
        "percent": psutil.cpu_percent(interval=1),
        "cores": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
        "freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
        "load_avg": psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0, 0, 0]
    }

def collect_ram():
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total": ram.total,
        "used": ram.used,
        "free": ram.available,
        "percent": ram.percent,
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent": swap.percent
    }
