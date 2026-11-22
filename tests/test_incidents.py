from database.db_connection import (
    insert_incident,
    get_incidents
)

import mysql.connector
from database.db_connection import get_db_connection


# =================================
# CICADA INCIDENT MANAGEMENT
# =================================

print("\n===== CICADA INCIDENT TEST =====")


# SAMPLE AI-DETECTED INCIDENT
incident_data = {
    "title": "High CPU Utilization",
    "description": "CPU usage exceeded 90%. Anomaly detected by CICADA AI Engine.",
    "severity": "CRITICAL",
    "status": "open",
    "source": "ai_engine"
}


# INSERT INCIDENT
print("\n[1] Inserting incident...")

incident_id = insert_incident(incident_data)

if incident_id:
    print("INCIDENT INSERTED SUCCESSFULLY")
    print("Incident ID:", incident_id)
else:
    print("INCIDENT INSERTION FAILED")
    raise SystemExit(1)


# RETRIEVE INCIDENTS
print("\n[2] Retrieving incidents...")

incidents = get_incidents()

for incident in incidents:
    print("\n------------------------")
    print("ID:", incident["id"])
    print("Title:", incident["title"])
    print("Severity:", incident["severity"])
    print("Status:", incident["status"])


# UPDATE INCIDENT STATUS
print("\n[3] Updating incident status...")

connection = get_db_connection()

if connection:
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE incidents SET status = %s WHERE id = %s",
        ("investigating", incident_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    print("INCIDENT STATUS UPDATED SUCCESSFULLY")


# RESOLVE INCIDENT
print("\n[4] Resolving incident...")

connection = get_db_connection()

if connection:
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE incidents
        SET status = %s, resolved_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        ("resolved", incident_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    print("INCIDENT RESOLVED SUCCESSFULLY")


print("\n===== INCIDENT TEST COMPLETED =====")