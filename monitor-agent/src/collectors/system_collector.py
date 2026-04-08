import psutil
import time

def collect_cpu():
    return {
        "percent": psutil.cpu_percent(interval=1),
        "per_cpu": psutil.cpu_percent(interval=1, percpu=True),
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

def collect_system_info():
    """Thu thập thông tin tổng quan hệ thống: uptime, tasks, threads"""
    uptime = time.time() - psutil.boot_time()
    
    # Đếm số task (pids) và tổng số thread
    pids = psutil.pids()
    total_threads = 0
    for pid in pids:
        try:
            p = psutil.Process(pid)
            total_threads += p.num_threads()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    return {
        "uptime": uptime,
        "total_tasks": len(pids),
        "total_threads": total_threads
    }
