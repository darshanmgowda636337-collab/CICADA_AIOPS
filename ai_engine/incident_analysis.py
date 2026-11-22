from datetime import datetime, timezone


def analyse_incidents(correlation_result):

    try:

        # Extract correlated incidents
        if isinstance(correlation_result, dict):
            incidents = correlation_result.get(
                "correlated_incidents", []
            )
        else:
            incidents = correlation_result

        if not isinstance(incidents, list):
            raise TypeError("Invalid incident format")

        if not incidents:
            return {
                "status": "success",
                "message": "No incidents available for analysis",
                "total_incidents": 0,
                "incident_reports": []
            }

        reports = []

        for incident in incidents:

            events = incident.get("events", [])

            if not events:
                continue

            hostname = incident.get(
                "hostname", "Unknown"
            )

            service = incident.get(
                "service", "Unknown"
            )

            # Identify affected resources
            affected_metrics = []

            for event in events:

                for metric in [
                    "cpu_usage",
                    "memory_usage",
                    "disk_usage",
                    "response_time"
                ]:

                    if metric in event:

                        if metric not in affected_metrics:
                            affected_metrics.append(metric)

            # Determine incident category
            if "cpu_usage" in affected_metrics:
                category = "CPU Performance Issue"

            elif "memory_usage" in affected_metrics:
                category = "Memory Performance Issue"

            elif "disk_usage" in affected_metrics:
                category = "Disk Performance Issue"

            elif "response_time" in affected_metrics:
                category = "Application Performance Issue"

            else:
                category = "General System Anomaly"

            # Generate incident description
            description = (
                f"Unusual behaviour detected on {hostname}. "
                f"The affected service is {service}. "
                f"Related events detected: {len(events)}."
            )

            report = {

                "incident_id": incident.get(
                    "incident_id", "UNKNOWN"
                ),

                "hostname": hostname,

                "service": service,

                "category": category,

                "description": description,

                "affected_metrics": affected_metrics,

                "event_count": len(events),

                "status": "Under Investigation",

                "analysed_at": datetime.now(
                    timezone.utc
                ).isoformat()

            }

            reports.append(report)

        return {

            "status": "success",

            "message": "Incident analysis completed",

            "total_incidents": len(reports),

            "incident_reports": reports

        }

    except Exception as error:

        return {

            "status": "failed",

            "message": str(error),

            "incident_reports": []

        }


# Standalone testing
if __name__ == "__main__":

    sample_data = {

        "correlated_incidents": [

            {

                "incident_id": "CICADA-INC-0001",

                "hostname": "SERVER-01",

                "service": "CPU",

                "events": [

                    {
                        "cpu_usage": 98,
                        "anomaly_label": "Anomaly"
                    },

                    {
                        "cpu_usage": 95,
                        "anomaly_label": "Anomaly"
                    }

                ]

            }

        ]

    }

    result = analyse_incidents(sample_data)

    print("\n===== CICADA INCIDENT ANALYSIS =====")

    print("Status:", result["status"])

    print("Message:", result["message"])

    print("Total Incidents:", result["total_incidents"])

    for report in result["incident_reports"]:

        print("\nIncident ID:", report["incident_id"])

        print("Hostname:", report["hostname"])

        print("Category:", report["category"])

        print("Description:", report["description"])

        print("Affected Metrics:", report["affected_metrics"])

        print("Status:", report["status"])