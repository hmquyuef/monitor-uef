import time
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger
from src.config.settings import COLLECT_INTERVAL, AGENT_NAME
from src.collectors.system_collector import collect_cpu, collect_ram, collect_system_info, collect_network_speed
from src.collectors.storage_collector import collect_disk
from src.sender.api_sender import send_metrics

def job():
    logger.info(f"--- Starting collection cycle for {AGENT_NAME} ---")
    try:
        cpu    = collect_cpu()
        ram    = collect_ram()
        disk   = collect_disk()
        net    = collect_network_speed()   # Hàm mới, đo tốc độ thực tế
        sysinfo = collect_system_info()

        payload = {
            # === CPU ===
            "cpu_percent":     cpu["percent"],
            "cpu_cores":       cpu["logical_cores"],
            "cpu_freq_mhz":    cpu["freq_mhz"],

            # === RAM ===
            "ram_total":       ram["total"],
            "ram_used":        ram["used"],
            "ram_percent":     ram["percent"],
            "swap_total":      ram["swap_total"],
            "swap_used":       ram["swap_used"],

            # === DISK ===
            "disk_total":      disk["total"],
            "disk_used":       disk["used"],
            "disk_percent":    disk["percent"],
            "disk_read_bps":   disk["read_bytes"],
            "disk_write_bps":  disk["write_bytes"],

            # === NETWORK ===
            "net_bytes_sent":  net["bytes_sent"],
            "net_bytes_recv":  net["bytes_recv"],

            # === EXTRA (JSONB) ===
            "extra_data": {
                # CPU Topology
                "cpu_physical_cores":  cpu["physical_cores"],
                "cpu_logical_cores":   cpu["logical_cores"],
                "cpu_num_sockets":     cpu["num_sockets"],
                "cpu_cores_per_socket":cpu["cores_per_socket"],
                "cpu_freq_max_mhz":    cpu["freq_max_mhz"],
                "cpu_load_avg":        cpu["load_avg"],
                "cpu_temp_celsius":    cpu["temp_celsius"],

                # Memory detail
                "ram_free":            ram["free"],
                "ram_total":           ram["total"],
                "ram_used":            ram["used"],
                "swap_total":          ram["swap_total"],

                # Disk detail
                "disk_free":           disk["free"],
                "disk_total":          disk["total"],
                "disk_used":           disk["used"],

                # Network speed
                "net_send_bps":        net["send_bps"],
                "net_recv_bps":        net["recv_bps"],
                "net_packets_sent":    net["packets_sent"],
                "net_packets_recv":    net["packets_recv"],

                # System info
                "uptime":              sysinfo["uptime"],
                "hostname":            sysinfo["hostname"],
                "primary_ip":          sysinfo["primary_ip"],
                "ip_addresses":        sysinfo["ip_addresses"],
                "os":                  sysinfo["os"],
                "os_release":          sysinfo["os_release"],
                "os_version":          sysinfo["os_version"],
                # Distro (lsb_release -a)
                "distro_id":           sysinfo["distro_id"],
                "distro_description":  sysinfo["distro_description"],
                "distro_release":      sysinfo["distro_release"],
                "distro_codename":     sysinfo["distro_codename"],
                "distro_pretty":       sysinfo["distro_pretty"],
                "machine":             sysinfo["machine"],
                "open_sockets":        sysinfo["open_sockets"],
                "established_conn":    sysinfo["established_conn"],
                "listen_ports":        sysinfo["listen_ports"]
            }
        }

        result = send_metrics(payload)

        # Cập nhật interval động nếu server yêu cầu khác
        if result and "collect_interval" in result:
            new_interval = result["collect_interval"]
            current_job = scheduler.get_job('main_job')
            if current_job and current_job.trigger.interval.seconds != new_interval:
                logger.warning(f"Updating interval to {new_interval}s as requested by server")
                scheduler.reschedule_job('main_job', trigger='interval', seconds=new_interval)

    except Exception as e:
        logger.exception(f"Unexpected error in collection job: {str(e)}")

if __name__ == "__main__":
    logger.info(f"Monitor Agent starting... (Interval: {COLLECT_INTERVAL}s)")

    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', seconds=COLLECT_INTERVAL, id='main_job')

    # Run once at startup
    job()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Agent stopped.")
