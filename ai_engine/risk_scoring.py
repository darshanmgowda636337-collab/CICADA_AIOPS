def calculate_risk_score(incident):

    category = incident.get("category", "").lower()

    event_count = incident.get("event_count", 1)

    # Base risk according to incident category
    category_scores = {
        "cpu performance issue": 30,
        "memory performance issue": 35,
        "disk performance issue": 40,
        "application performance issue": 30,
        "general system anomaly": 25
    }

    base_score = category_scores.get(category, 25)

    # Increase risk based on repeated events
    if event_count >= 10:
        event_score = 30
    elif event_count >= 6:
        event_score = 20
    elif event_count >= 3:
        event_score = 10
    else:
        event_score = 5

    risk_score = min(base_score + event_score, 100)

    # Determine severity
    if risk_score >= 80:
        severity = "Critical"

    elif risk_score >= 60:
        severity = "High"

    elif risk_score >= 40:
        severity = "Medium"

    else:
        severity = "Low"

    return {
        "risk_score": risk_score,
        "severity": severity
    }


def score_incidents(analysis_result):

    try:

        incidents = analysis_result.get(
            "incident_reports", []
        )

        if not incidents:
            return {
                "status": "success",
                "message": "No incidents available",
                "total_incidents": 0,
                "risk_reports": []
            }

        risk_reports = []

        for incident in incidents:

            risk = calculate_risk_score(incident)

            report = {
                "incident_id": incident.get(
                    "incident_id", "UNKNOWN"
                ),

                "hostname": incident.get(
                    "hostname", "UNKNOWN"
                ),

                "category": incident.get(
                    "category", "Unknown"
                ),

                "risk_score": risk["risk_score"],

                "severity": risk["severity"],

                "priority": risk["severity"],

                "status": "Risk Assessed"
            }

            risk_reports.append(report)

        return {
            "status": "success",
            "message": "Risk assessment completed",
            "total_incidents": len(risk_reports),
            "risk_reports": risk_reports
        }

    except Exception as error:

        return {
            "status": "failed",
            "message": str(error),
            "risk_reports": []
        }


# Standalone testing
if __name__ == "__main__":

    sample_data = {

        "incident_reports": [

            {
                "incident_id": "CICADA-INC-0001",
                "hostname": "SERVER-01",
                "category": "CPU Performance Issue",
                "event_count": 3
            },

            {
                "incident_id": "CICADA-INC-0002",
                "hostname": "SERVER-02",
                "category": "Memory Performance Issue",
                "event_count": 8
            },

            {
                "incident_id": "CICADA-INC-0003",
                "hostname": "SERVER-03",
                "category": "Disk Performance Issue",
                "event_count": 12
            }

        ]

    }

    result = score_incidents(sample_data)

    print("\n===== CICADA RISK SCORING =====")

    print("Status:", result["status"])
    print("Message:", result["message"])

    print("Total Incidents:", result["total_incidents"])

    for report in result["risk_reports"]:

        print("\nIncident ID:", report["incident_id"])
        print("Hostname:", report["hostname"])
        print("Risk Score:", report["risk_score"], "/ 100")
        print("Severity:", report["severity"])
        print("Priority:", report["priority"])