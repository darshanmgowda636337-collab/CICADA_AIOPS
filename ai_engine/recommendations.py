# ==========================================================
# CICADA AIOPS - AI RECOMMENDATION ENGINE
# ==========================================================

from datetime import datetime

from backend.database import get_telemetry, get_incidents


# ==========================================================
# CONFIGURATION
# ==========================================================

CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 85
DISK_THRESHOLD = 90


# ==========================================================
# HELPER FUNCTION
# ==========================================================

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ==========================================================
# GENERATE RECOMMENDATIONS
# ==========================================================

def generate_recommendations():

    recommendations = []

    try:

        telemetry_records = get_telemetry(limit=200)
        incidents = get_incidents()

        if telemetry_records is None:
            telemetry_records = []

        if incidents is None:
            incidents = []

        # --------------------------------------------------
        # 1. ANALYZE TELEMETRY
        # --------------------------------------------------

        for record in telemetry_records:

            metric_name = str(
                record.get("metric_name", "")
            ).lower()

            metric_value = safe_float(
                record.get("metric_value")
            )

            hostname = record.get(
                "hostname", "Unknown"
            )

            severity = str(
                record.get("severity", "")
            ).upper()

            if metric_value is None:
                continue

            # CPU ANALYSIS
            if "cpu" in metric_name:

                if metric_value >= CPU_THRESHOLD:

                    recommendations.append({
                        "type": "CPU",
                        "severity": "CRITICAL",
                        "hostname": hostname,
                        "metric_value": metric_value,
                        "message": "High CPU utilization detected.",
                        "recommendation":
                            "Identify resource-intensive processes, "
                            "optimize workloads and scale CPU resources "
                            "if required."
                    })

                elif metric_value >= 70:

                    recommendations.append({
                        "type": "CPU",
                        "severity": "WARNING",
                        "hostname": hostname,
                        "metric_value": metric_value,
                        "message": "CPU utilization is increasing.",
                        "recommendation":
                            "Monitor CPU usage and review running processes."
                    })

            # MEMORY ANALYSIS
            if "memory" in metric_name or "ram" in metric_name:

                if metric_value >= MEMORY_THRESHOLD:

                    recommendations.append({
                        "type": "MEMORY",
                        "severity": "CRITICAL",
                        "hostname": hostname,
                        "metric_value": metric_value,
                        "message": "High memory utilization detected.",
                        "recommendation":
                            "Identify memory-consuming processes, "
                            "release unused resources and increase RAM "
                            "capacity if necessary."
                    })

            # DISK ANALYSIS
            if "disk" in metric_name:

                if metric_value >= DISK_THRESHOLD:

                    recommendations.append({
                        "type": "DISK",
                        "severity": "CRITICAL",
                        "hostname": hostname,
                        "metric_value": metric_value,
                        "message": "Disk utilization is critically high.",
                        "recommendation":
                            "Remove unnecessary files, clean temporary "
                            "storage and increase disk capacity."
                    })

            # SEVERITY ANALYSIS
            if severity == "CRITICAL":

                recommendations.append({
                    "type": "SYSTEM",
                    "severity": "CRITICAL",
                    "hostname": hostname,
                    "metric_value": metric_value,
                    "message": "Critical telemetry event detected.",
                    "recommendation":
                        "Investigate the event immediately and "
                        "check related system logs."
                })

        # --------------------------------------------------
        # 2. ANALYZE INCIDENTS
        # --------------------------------------------------

        for incident in incidents:

            status = str(
                incident.get("status", "")
            ).lower()

            severity = str(
                incident.get("severity", "")
            ).upper()

            if status not in ("resolved", "closed"):

                recommendations.append({
                    "type": "INCIDENT",
                    "severity": severity or "WARNING",
                    "hostname": "System",
                    "metric_value": None,
                    "message": incident.get(
                        "title",
                        incident.get(
                            "description",
                            "Unresolved incident detected."
                        )
                    ),
                    "recommendation":
                        "Investigate the incident, identify its root "
                        "cause and resolve it as soon as possible."
                })

        # --------------------------------------------------
        # 3. DEFAULT RECOMMENDATION
        # --------------------------------------------------

        if not recommendations:

            recommendations.append({
                "type": "SYSTEM",
                "severity": "INFO",
                "hostname": "CICADA",
                "metric_value": None,
                "message": "No critical system issues detected.",
                "recommendation":
                    "Continue monitoring system telemetry and "
                    "maintain regular infrastructure health checks."
            })

        # --------------------------------------------------
        # 4. SORT BY PRIORITY
        # --------------------------------------------------

        priority = {
            "CRITICAL": 1,
            "HIGH": 2,
            "WARNING": 3,
            "MEDIUM": 4,
            "INFO": 5,
            "LOW": 6
        }

        recommendations.sort(
            key=lambda item: priority.get(
                item["severity"], 7
            )
        )

        return recommendations

    except Exception as error:

        print(
            "[AI RECOMMENDATION ERROR]",
            str(error)
        )

        raise


# ==========================================================
# AI ENGINE HEALTH CHECK
# ==========================================================

def test_recommendation_engine():

    try:

        result = generate_recommendations()

        return {
            "success": True,
            "engine": "CICADA AI Recommendation Engine",
            "recommendation_count": len(result),
            "recommendations": result
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }