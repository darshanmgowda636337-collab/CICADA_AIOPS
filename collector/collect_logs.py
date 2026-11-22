
import subprocess
import xml.etree.ElementTree as ET
import platform

from database.db_connection import insert_telemetry


def collect_system_logs(limit=10):

    logs = []

    try:

        result = subprocess.run(
            [
                "wevtutil",
                "qe",
                "System",
                f"/c:{limit}",
                "/rd:true",
                "/f:xml"
            ],
            capture_output=True,
            text=True,
            timeout=20
        )

        if result.returncode != 0:
            print("Windows Event Log Error:", result.stderr)
            return logs

        if not result.stdout.strip():
            print("No event data returned by Windows.")
            return logs

        root = ET.fromstring(
            f"<Events>{result.stdout}</Events>"
        )

        for event in root.iter():

            if not event.tag.endswith("Event"):
                continue

            system = event.find("{*}System")

            if system is None:
                continue

            def get_text(element, tag):

                item = element.find(f"{{*}}{tag}")

                return item.text if item is not None else None

            event_id = get_text(system, "EventID")
            level = get_text(system, "Level")

            provider_element = system.find("{*}Provider")

            provider = (
                provider_element.attrib.get("Name")
                if provider_element is not None
                else None
            )

            timestamp_element = system.find("{*}TimeCreated")

            timestamp = (
                timestamp_element.attrib.get("SystemTime")
                if timestamp_element is not None
                else None
            )

            log_data = {
                "event_id": event_id,
                "level": level,
                "provider": provider,
                "timestamp": timestamp
            }

            logs.append(log_data)

    except Exception as error:

        print("Log collection error:", error)

        return []

    return logs


def store_logs_in_database(logs):

    successful = 0

    for log in logs:

        try:

            level = log.get("level")

            # Windows Event Log levels:
            # 1 = Critical, 2 = Error,
            # 3 = Warning, 4 = Information

            severity_map = {
                "1": "CRITICAL",
                "2": "HIGH",
                "3": "MEDIUM",
                "4": "LOW"
            }

            severity = severity_map.get(level, "UNKNOWN")

            telemetry_data = {

                "hostname": platform.node(),

                "source": "windows_event_log",

                "event_type": "SYSTEM_EVENT",

                "metric_name": "event_id",

                "metric_value": (
                    float(log["event_id"])
                    if log.get("event_id", "").isdigit()
                    else None
                ),

                "severity": severity,

                "message": (
                    f"Windows Event ID: {log.get('event_id')} | "
                    f"Provider: {log.get('provider')} | "
                    f"Level: {level}"
                ),

                "metadata": log

            }

            record_id = insert_telemetry(telemetry_data)

            if record_id:
                successful += 1

        except Exception as error:

            print("Telemetry storage error:", error)

    print("\nSuccessfully stored:", successful)

    print("Failed:", len(logs) - successful)


if __name__ == "__main__":

    print("\n====================================")
    print("     CICADA SYSTEM LOG COLLECTOR")
    print("====================================")

    system_logs = collect_system_logs(limit=10)

    for log in system_logs:
        print("\nEVENT:")
        print(log)

    print("\nTotal events collected:", len(system_logs))

    print("\nStoring events in MySQL...")

    store_logs_in_database(system_logs)

    print("\n====================================")
