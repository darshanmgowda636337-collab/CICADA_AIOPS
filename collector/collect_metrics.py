
import platform
import socket
import psutil
import logging
from datetime import datetime


def collect_system_metrics():
    """
    Collect real-time system performance metrics
    for CICADA AIOps.
    """

    try:
        hostname = socket.gethostname()

        # CPU metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_cores = psutil.cpu_count(logical=True)

        # Memory metrics
        memory = psutil.virtual_memory()

        total_memory = round(memory.total / (1024 ** 3), 2)
        used_memory = round(memory.used / (1024 ** 3), 2)
        memory_usage = memory.percent

        # Disk metrics
        disk = psutil.disk_usage("C:\\")

        total_disk = round(disk.total / (1024 ** 3), 2)
        used_disk = round(disk.used / (1024 ** 3), 2)
        disk_usage = disk.percent

        # Network metrics
        network = psutil.net_io_counters()

        bytes_sent = network.bytes_sent
        bytes_received = network.bytes_recv

        # System information
        system_name = platform.system()
        system_version = platform.version()
        processor = platform.processor()

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        metrics = {
            "hostname": hostname,
            "source": "system_metrics",
            "event_type": "performance",
            "metric_name": "system_health",
            "cpu_usage": cpu_usage,
            "cpu_cores": cpu_cores,
            "memory_usage": memory_usage,
            "total_memory_gb": total_memory,
            "used_memory_gb": used_memory,
            "disk_usage": disk_usage,
            "total_disk_gb": total_disk,
            "used_disk_gb": used_disk,
            "bytes_sent": bytes_sent,
            "bytes_received": bytes_received,
            "system": system_name,
            "system_version": system_version,
            "processor": processor,
            "timestamp": timestamp
        }

        return metrics

    except Exception as error:
        logging.exception("System metrics collection failed: %s", error)
        return None


if __name__ == "__main__":

    print("\n========== CICADA AIOPS METRICS COLLECTOR ==========\n")

    system_metrics = collect_system_metrics()

    if system_metrics:

        for key, value in system_metrics.items():
            print(f"{key}: {value}")

        print("\nMETRICS COLLECTION: PASSED")

    else:
        print("\nMETRICS COLLECTION: FAILED")
