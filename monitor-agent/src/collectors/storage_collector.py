import psutil

def collect_disk():
    # Thống kê tổng hợp các phân vùng chính
    disk = psutil.disk_usage('/')
    io = psutil.disk_io_counters()
    return {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent,
        "read_bytes": io.read_bytes if io else 0,
        "write_bytes": io.write_bytes if io else 0
    }

def collect_network():
    net_io = psutil.net_io_counters()
    return {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv
    }
