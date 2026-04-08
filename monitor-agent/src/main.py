import time
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger
from src.config.settings import COLLECT_INTERVAL, AGENT_NAME
from src.collectors.system_collector import collect_cpu, collect_ram, collect_system_info
from src.collectors.storage_collector import collect_disk, collect_network
from src.sender.api_sender import send_metrics

def job():
    logger.info(f"--- Starting collection cycle for {AGENT_NAME} ---")
    try:
        metrics = {
            "cpu": collect_cpu(),
            "ram": collect_ram(),
            "disk": collect_disk(),
            "network": collect_network(),
            "sys": collect_system_info()
        }
        
        # Flatten metrics for database simplicity or nesting as needed
        # Mapping to match the database columns defined earlier
        payload = {
            "cpu_percent": metrics["cpu"]["percent"],
            "cpu_cores": metrics["cpu"]["cores"],
            "cpu_freq_mhz": metrics["cpu"]["freq_mhz"],
            "ram_total": metrics["ram"]["total"],
            "ram_used": metrics["ram"]["used"],
            "ram_percent": metrics["ram"]["percent"],
            "swap_total": metrics["ram"]["swap_total"],
            "swap_used": metrics["ram"]["swap_used"],
            "disk_total": metrics["disk"]["total"],
            "disk_used": metrics["disk"]["used"],
            "disk_percent": metrics["disk"]["percent"],
            "disk_read_bps": metrics["disk"]["read_bytes"],
            "disk_write_bps": metrics["disk"]["write_bytes"],
            "net_bytes_sent": metrics["network"]["bytes_sent"],
            "net_bytes_recv": metrics["network"]["bytes_recv"],
            "extra_data": {
                "load_avg": metrics["cpu"]["load_avg"],
                "per_cpu": metrics["cpu"]["per_cpu"],
                "uptime": metrics["sys"]["uptime"],
                "total_tasks": metrics["sys"]["total_tasks"],
                "total_threads": metrics["sys"]["total_threads"],
                "packets_sent": metrics["network"]["packets_sent"],
                "packets_recv": metrics["network"]["packets_recv"],
                "disk_total": metrics["disk"]["total"],
                "disk_used": metrics["disk"]["used"],
                "disk_free": metrics["disk"]["free"],
                "ram_total": metrics["ram"]["total"],
                "ram_used": metrics["ram"]["used"],
                "swap_total": metrics["ram"]["swap_total"]
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
    # Thêm job với ID cố định để có thể tìm và đổi interval
    scheduler.add_job(job, 'interval', seconds=COLLECT_INTERVAL, id='main_job')
    
    # Run once at startup
    job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Agent stopped.")
