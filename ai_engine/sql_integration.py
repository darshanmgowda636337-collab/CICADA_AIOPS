import json
from collections import defaultdict

from database.db_connection import get_telemetry
from ai_engine.ai_pipeline import run_ai_pipeline


# Supported performance metrics
SUPPORTED_METRICS = {
    "cpu_usage": "cpu_usage",
    "cpu_percent": "cpu_usage",
    "memory_usage": "memory_usage",
    "memory_percent": "memory_usage",
    "ram_usage": "memory_usage",
    "disk_usage": "disk_usage",
    "disk_percent": "disk_usage",
    "network_usage": "network_usage",
    "network_bytes": "network_usage",
    "response_time": "response_time"
}


def convert_telemetry_to_ai_format(rows):

    grouped_data = defaultdict(dict)

    for row in rows:

        hostname = row.get("hostname", "UNKNOWN")
        metric_name = str(
            row.get("metric_name", "")
        ).lower().strip()

        metric_value = row.get("metric_value")

        # Ignore unsupported metrics such as Windows event IDs
        if metric_name not in SUPPORTED_METRICS:
            continue

        try:
            metric_value = float(metric_value)
        except (ValueError, TypeError):
            continue

        timestamp = row.get("collected_at")

        # Group metrics belonging to the same host and timestamp
        group_key = (hostname, timestamp)

        grouped_data[group_key]["hostname"] = hostname

        grouped_data[group_key][
            SUPPORTED_METRICS[metric_name]
        ] = metric_value

    return list(grouped_data.values())


def run_database_ai_pipeline(limit=500):

    print("\n===================================")
    print("CICADA MYSQL AI INTEGRATION")
    print("===================================")

    try:
        # 1. Fetch telemetry from MySQL
        print("\n[1] Fetching telemetry from MySQL...")

        database_rows = get_telemetry(limit)

        if not database_rows:
            return {
                "status": "NO_DATA",
                "message": "No telemetry records found in MySQL."
            }

        print("Database records:", len(database_rows))

        # 2. Convert database records
        print("\n[2] Converting telemetry...")

        ai_telemetry = convert_telemetry_to_ai_format(
            database_rows
        )

        if not ai_telemetry:
            return {
                "status": "WAITING_FOR_METRICS",
                "message": (
                    "MySQL contains telemetry, but no supported "
                    "performance metrics were found. "
                    "CPU, memory, disk or network metrics are required."
                ),
                "database_records": len(database_rows),
                "ai_records": 0
            }

        print("AI-compatible records:", len(ai_telemetry))

        # 3. Run AI pipeline
        print("\n[3] Running CICADA AI pipeline...")

        result = run_ai_pipeline(ai_telemetry)

        print("\n[4] AI pipeline completed!")

        return {
            "status": "SUCCESS",
            "database_records": len(database_rows),
            "ai_records": len(ai_telemetry),
            "ai_results": result
        }

    except Exception as error:

        return {
            "status": "ERROR",
            "message": str(error)
        }


if __name__ == "__main__":

    output = run_database_ai_pipeline()

    print("\n===================================")
    print("CICADA AI INTEGRATION RESULT")
    print("===================================")

    print(json.dumps(
        output,
        indent=4,
        default=str
    ))