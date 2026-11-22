
from datetime import datetime


# ==========================================
# CICADA AIOPS - METADATA BUILDER
# ==========================================

ALLOWED_FIELDS = {
    "hostname",
    "source",
    "event_type",
    "metric_name",
    "cpu_usage",
    "cpu_cores",
    "memory_usage",
    "total_memory_gb",
    "used_memory_gb",
    "disk_usage",
    "total_disk_gb",
    "used_disk_gb",
    "bytes_sent",
    "bytes_received",
    "system",
    "system_version",
    "processor",
    "event_id",
    "event_level",
    "provider",
    "timestamp"
}


def build_metadata(metrics=None, event=None):

    """
    Build approved metadata payload.

    Raw log messages are not included.
    """

    payload = {}

    # Add system metrics
    if metrics and isinstance(metrics, dict):

        for key, value in metrics.items():

            if key in ALLOWED_FIELDS:
                payload[key] = value

    # Add Windows event metadata
    if event and isinstance(event, dict):

        event_mapping = {
            "event_id": "event_id",
            "level": "event_level",
            "provider": "provider",
            "timestamp": "timestamp",
            "hostname": "hostname"
        }

        for original_key, target_key in event_mapping.items():

            if original_key in event:
                payload[target_key] = event[original_key]

    # Ensure required metadata
    payload.setdefault("hostname", "unknown")
    payload.setdefault("source", "cicada_collector")
    payload.setdefault("event_type", "performance")
    payload.setdefault("metric_name", "system_health")

    payload.setdefault(
        "timestamp",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return payload


def validate_metadata(payload):

    """
    Validate approved telemetry metadata.
    """

    if not isinstance(payload, dict):
        return False

    required_fields = [
        "hostname",
        "source",
        "event_type",
        "metric_name",
        "timestamp"
    ]

    for field in required_fields:

        if field not in payload:
            return False

        if payload[field] is None:
            return False

    # Reject fields outside the allowlist
    for field in payload:

        if field not in ALLOWED_FIELDS:
            return False

    return True


def main():

    print("\n====================================")
    print("       CICADA METADATA BUILDER")
    print("====================================")

    sample_metrics = {
        "hostname": "CICADA-PC",
        "source": "system_metrics",
        "event_type": "performance",
        "metric_name": "system_health",
        "cpu_usage": 25.5,
        "memory_usage": 65.2,
        "disk_usage": 70.4,
        "bytes_sent": 102400,
        "bytes_received": 204800,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    payload = build_metadata(metrics=sample_metrics)

    print("\nAPPROVED TELEMETRY PAYLOAD\n")

    for key, value in payload.items():
        print(f"{key}: {value}")

    if validate_metadata(payload):
        print("\nMETADATA VALIDATION: PASSED")
    else:
        print("\nMETADATA VALIDATION: FAILED")


if __name__ == "__main__":
    main()
