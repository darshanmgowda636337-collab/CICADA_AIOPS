from datetime import datetime, timezone


def correlate_events(events):
    """
    Correlate related anomalies into incidents.
    """

    try:
        if isinstance(events, dict):
            events = events.get("anomalies", events.get("results", []))

        if not isinstance(events, list):
            raise TypeError("Events must be a list")

        if not events:
            return {
                "status": "success",
                "message": "No events available for correlation",
                "total_events": 0,
                "correlated_incidents": []
            }

        # Group events using host and service information
        groups = {}

        for event in events:

            if not isinstance(event, dict):
                continue

            if event.get("anomaly_label") == "Normal":
                continue

            host = event.get(
                "hostname",
                event.get("host", "unknown_host")
            )

            service = event.get(
                "service",
                event.get("process_name", "unknown_service")
            )

            key = (host, service)

            if key not in groups:
                groups[key] = []

            groups[key].append(event)

        incidents = []

        for index, ((host, service), related_events) in enumerate(
            groups.items(), start=1
        ):

            incidents.append({
                "incident_id": f"CICADA-INC-{index:04d}",
                "hostname": host,
                "service": service,
                "event_count": len(related_events),
                "events": related_events,
                "correlation_status": "Correlated",
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat()
            })

        return {
            "status": "success",
            "message": "Event correlation completed",
            "total_events": len(events),
            "correlated_incident_count": len(incidents),
            "correlated_incidents": incidents
        }

    except Exception as error:

        return {
            "status": "failed",
            "message": str(error),
            "correlated_incidents": []
        }


# Standalone testing
if __name__ == "__main__":

    sample_events = [

        {
            "hostname": "SERVER-01",
            "service": "CPU",
            "cpu_usage": 98,
            "anomaly_label": "Anomaly"
        },

        {
            "hostname": "SERVER-01",
            "service": "CPU",
            "cpu_usage": 95,
            "anomaly_label": "Anomaly"
        },

        {
            "hostname": "SERVER-02",
            "service": "Memory",
            "memory_usage": 99,
            "anomaly_label": "Anomaly"
        },

        {
            "hostname": "SERVER-01",
            "service": "CPU",
            "cpu_usage": 40,
            "anomaly_label": "Normal"
        }

    ]

    result = correlate_events(sample_events)

    print("\n===== CICADA EVENT CORRELATION =====")

    print("Status:", result["status"])

    print("Total Events:", result["total_events"])

    print(
        "Correlated Incidents:",
        result.get("correlated_incident_count", 0)
    )

    for incident in result.get("correlated_incidents", []):

        print("\nIncident ID:", incident["incident_id"])
        print("Hostname:", incident["hostname"])
        print("Service:", incident["service"])
        print("Related Events:", incident["event_count"])
        print("Status:", incident["correlation_status"])