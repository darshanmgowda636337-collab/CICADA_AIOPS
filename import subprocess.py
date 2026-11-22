import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


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
            timeout=15
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        root = ET.fromstring(
            f"<Events>{result.stdout}</Events>"
        )

        for event in root.findall("Event"):

            system = event.find("System")

            if system is None:
                continue

            event_id = system.find("EventID")
            level = system.find("Level")
            provider = system.find("Provider")
            timestamp = system.find("TimeCreated")

            logs.append({

                "event_id": (
                    event_id.text if event_id is not None else None
                ),

                "level": (
                    level.text if level is not None else None
                ),

                "provider": (
                    provider.attrib.get("Name")
                    if provider is not None else None
                ),

                "timestamp": (
                    timestamp.attrib.get("SystemTime")
                    if timestamp is not None else None
                )

            })

        return logs

    except Exception as error:

        print("Log collection error:", error)

        return []


if __name__ == "__main__":

    print("\n===== CICADA SYSTEM LOG COLLECTOR =====\n")

    system_logs = collect_system_logs()

    for log in system_logs:
        print(log)

    print("\nTotal events collected:", len(system_logs))