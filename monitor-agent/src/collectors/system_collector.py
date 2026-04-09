import psutil
import time
import platform
import socket as sock

def collect_cpu():
    cpu_freq = psutil.cpu_freq()
    load = psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0, 0, 0]
    
    # CPU Topology
    physical_cores = psutil.cpu_count(logical=False) or 1
    logical_cores  = psutil.cpu_count(logical=True)  or 1
    
    # Số socket ước tính: mỗi socket thường có số physical core bằng nhau
    # Nếu không lấy được, mặc định là 1 socket
    try:
        import subprocess, re
        result = subprocess.run(
            ["lscpu"], capture_output=True, text=True, timeout=3
        )
        socket_match = re.search(r"Socket\(s\):\s*(\d+)", result.stdout)
        cores_per_socket_match = re.search(r"Core\(s\) per socket:\s*(\d+)", result.stdout)
        num_sockets = int(socket_match.group(1)) if socket_match else 1
        cores_per_socket = int(cores_per_socket_match.group(1)) if cores_per_socket_match else physical_cores
    except Exception:
        num_sockets = 1
        cores_per_socket = physical_cores

    # CPU Temperature (nếu hỗ trợ)
    cpu_temp = None
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for key in ("coretemp", "cpu_thermal", "k10temp", "zenpower"):
                if key in temps and temps[key]:
                    cpu_temp = round(temps[key][0].current, 1)
                    break
    except Exception:
        cpu_temp = None

    return {
        "percent": psutil.cpu_percent(interval=1),
        "logical_cores": logical_cores,
        "physical_cores": physical_cores,
        "num_sockets": num_sockets,
        "cores_per_socket": cores_per_socket,
        "freq_mhz": round(cpu_freq.current, 1) if cpu_freq else 0,
        "freq_max_mhz": round(cpu_freq.max, 1) if cpu_freq else 0,
        "load_avg": [round(x, 2) for x in load],
        "temp_celsius": cpu_temp
    }

def collect_ram():
    ram  = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total":        ram.total,
        "used":         ram.used,
        "free":         ram.available,
        "percent":      ram.percent,
        "swap_total":   swap.total,
        "swap_used":    swap.used,
        "swap_percent": swap.percent
    }

def collect_system_info():
    """Thu thập thông tin hệ thống: OS, distro, uptime, hostname, IP, socket mạng."""
    uptime = time.time() - psutil.boot_time()

    # ── Distro (Ubuntu 22.04 / CentOS 8, ...) ──────────────────────────────
    distro_name    = ""
    distro_version = ""
    distro_pretty  = ""
    try:
        with open("/etc/os-release", "r") as f:
            kv = {}
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    kv[k] = v.strip('"')
        distro_name    = kv.get("NAME", "")
        distro_version = kv.get("VERSION_ID", "")
        distro_pretty  = kv.get("PRETTY_NAME", distro_name)
    except Exception:
        distro_name    = platform.system()
        distro_version = platform.release()
        distro_pretty  = f"{platform.system()} {platform.release()}"

    # ── IP Addresses ────────────────────────────────────────────────────────
    ip_addresses = {}
    try:
        # Lấy tất cả địa chỉ IP của từng interface (bỏ qua loopback)
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                # AF_INET = IPv4 (2), AF_INET6 = IPv6 (10/23)
                if addr.family == 2 and not addr.address.startswith("127."):      # IPv4
                    ip_addresses[iface] = addr.address
                    break
    except Exception:
        pass

    # Lấy IP chính (IP mà máy dùng để ra ngoài internet)
    primary_ip = ""
    try:
        with sock.socket(sock.AF_INET, sock.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            primary_ip = s.getsockname()[0]
    except Exception:
        primary_ip = next(iter(ip_addresses.values()), "")

    # ── Network Connections ─────────────────────────────────────────────────
    try:
        connections      = psutil.net_connections()
        open_sockets     = len(connections)
        established_conn = len([c for c in connections if c.status == "ESTABLISHED"])
        listen_ports     = len([c for c in connections if c.status == "LISTEN"])
    except Exception:
        open_sockets = established_conn = listen_ports = 0

    return {
        "uptime":           round(uptime),
        "hostname":         platform.node(),
        "primary_ip":       primary_ip,
        "ip_addresses":     ip_addresses,
        "os":               platform.system(),
        "os_release":       platform.release(),
        "os_version":       platform.version(),
        "distro_name":      distro_name,
        "distro_version":   distro_version,
        "distro_pretty":    distro_pretty,
        "machine":          platform.machine(),
        "open_sockets":     open_sockets,
        "established_conn": established_conn,
        "listen_ports":     listen_ports,
    }

def collect_network_speed():
    """Đo tốc độ mạng thực tế (bytes/s) bằng cách đọc 2 lần cách nhau 1s."""
    t1 = psutil.net_io_counters()
    time.sleep(1)
    t2 = psutil.net_io_counters()
    return {
        "bytes_sent":     t2.bytes_sent,
        "bytes_recv":     t2.bytes_recv,
        "packets_sent":   t2.packets_sent,
        "packets_recv":   t2.packets_recv,
        "send_bps":       t2.bytes_sent - t1.bytes_sent,  # bytes per second
        "recv_bps":       t2.bytes_recv - t1.bytes_recv
    }
