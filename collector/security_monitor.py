
import subprocess
import xml.etree.ElementTree as ET
import platform
import socket
import logging

from datetime import datetime, timezone


# ==========================================
# CICADA AIOPS - SECURITY MONITOR
# ==========================================

SECURITY_EVENT_IDS = {
    4625: "FAILED_LOGIN",
    4740: "ACCOUNT_LOCKOUT",
    4720: "ACCOUNT_CREATED",
    1102: "SECURITY_LOG_CLEARED",
}

SEVERITY_LEVELS = {
    4625: "MEDIUM",
    4740: "HIGH",
    4720: "MEDIUM",
    1102: "CRITICAL",
}


def collect_security_events(limit=20):

    """
    Collect important Windows security events
    using Windows Event Viewer.
    """

    if platform.system() != "Windows":
        logging.error("Security monitor requires Windows.")
        return []

    event_filter = " or ".join(
        f"EventID={event_id}"
        for event_id in SECURITY_EVENT_IDS
    )

    query = f"*[System[({event_filter})]]"

    command = [
        "wevtutil",
        "qe",
        "Security",
        f"/q:{query}",
        "/f:xml",
        "/rd:true",
        f"/c:{limit}"
    ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )

        if not result.stdout.strip():
            return []

        root = ET.fromstring(result.stdout)

        events = []

        for event in root.findall("Event"):

            system = event.find("System")

            if system is None:
                continue

            event_id_element = system.find("EventID")

            if event_id_element is None:
                continue

            event_id = int(event_id_element.text)

            if event_id not in SECURITY_EVENT_IDS:
                continue

            provider = system.find("Provider")
            time_created = system.find("TimeCreated")
            record_id = system.find("EventRecordID")

            hostname = socket.gethostname()

            provider_name = (
                provider.get("Name", "Unknown")
                if provider is not None
                else "Unknown"
            )

            timestamp = (
                time_created.get("SystemTime")
                if time_created is not None
                else datetime.now(timezone.utc).isoformat()
            )

            # Extract only approved security metadata.
            approved_data = {}

            event_data = event.find("EventData")

            if event_data is not None:

                allowed_fields = {
                    "LogonType",
                    "Status",
                    "SubStatus"
                }

                for data in event_data.findall("Data"):

                    name = data.get("Name")
                    value = data.text

                    if name in allowed_fields and value:
                        approved_data[name.lower()] = value

            security_event = {

                "hostname": hostname,

                "source": "windows_security",

                "event_type": "security",

                "metric_name": "security_event",

                "event_id": event_id,

                "event_name": SECURITY_EVENT_IDS[event_id],

                "severity": SEVERITY_LEVELS[event_id],

                "provider": provider_name,

                "event_record_id": (
                    int(record_id.text)
                    if record_id is not None
                    and record_id.text
                    else None
                ),

                "timestamp": timestamp,

                "metadata": approved_data

            }

            events.append(security_event)

        return events

    except subprocess.TimeoutExpired:

        logging.error("Windows security log collection timed out.")

    except subprocess.CalledProcessError as error:

        logging.error(
            "Windows security log access failed: %s",
            error.stderr
        )

    except ET.ParseError:

        logging.error("Unable to parse Windows security event XML.")

    except Exception:

        logging.exception("Security monitoring failed.")

    return []


def main():

    print("\n==========================================")
    print("       CICADA AIOPS SECURITY MONITOR")
    print("==========================================")

    events = collect_security_events(limit=20)

    print(f"\nSecurity events collected: {len(events)}\n")

    for event in events:

        print("------------------------------------------")

        print("Event ID:", event["event_id"])

        print("Event:", event["event_name"])

        print("Severity:", event["severity"])

        print("Hostname:", event["hostname"])

        print("Timestamp:", event["timestamp"])

        print("Approved Metadata:", event["metadata"])

    print("\n==========================================")

    if events:
        print("SECURITY MONITOR: PASSED")
    else:
        print("NO SECURITY EVENTS FOUND OR ACCESS FAILED")

    print("==========================================\n")


if __name__ == "__main__":
    main()
