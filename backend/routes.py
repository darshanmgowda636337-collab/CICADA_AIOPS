
# ==========================================================
# CICADA AIOPS - COMPLETE API ROUTES
# ==========================================================

from flask import Blueprint, request, jsonify
from mysql.connector import Error

from backend.database import (
    get_connection,
    check_database,
    get_telemetry,
    get_incidents
)

from backend.ingestion import ingest_telemetry


# ==========================================================
# API BLUEPRINT
# ==========================================================

api = Blueprint("api", __name__, url_prefix="/api")


# ==========================================================
# 1. API HEALTH
# ==========================================================

@api.route("/health", methods=["GET"])
def health():

    try:
        db_status = check_database()

        return jsonify({
            "success": True,
            "application": "CICADA AIOps",
            "backend": "running",
            "database": "connected" if db_status else "disconnected"
        }), 200 if db_status else 503

    except Exception as error:
        print("[HEALTH ERROR]", error)

        return jsonify({
            "success": False,
            "message": "Health check failed"
        }), 500


# ==========================================================
# 2. TELEMETRY INGESTION
# ==========================================================

@api.route("/ingest", methods=["POST"])
def ingest():

    payload = request.get_json(silent=True)

    if payload is None:
        return jsonify({
            "success": False,
            "message": "Invalid JSON payload"
        }), 400

    result, status_code = ingest_telemetry(payload)

    return jsonify(result), status_code


# ==========================================================
# 3. TELEMETRY RETRIEVAL
# ==========================================================

@api.route("/telemetry", methods=["GET"])
def telemetry():

    try:
        limit = request.args.get("limit", 100, type=int)

        if limit is None or limit < 1:
            return jsonify({
                "success": False,
                "message": "Invalid limit"
            }), 400

        records = get_telemetry(limit)

        return jsonify({
            "success": True,
            "count": len(records),
            "telemetry": records
        }), 200

    except Exception as error:
        print("[TELEMETRY ERROR]", error)

        return jsonify({
            "success": False,
            "message": "Unable to fetch telemetry"
        }), 500


# ==========================================================
# 4. DASHBOARD STATISTICS
# ==========================================================

@api.route("/dashboard", methods=["GET"])
def dashboard():

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return jsonify({
                "success": False,
                "message": "Database unavailable"
            }), 503

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT COUNT(*) AS total FROM telemetry"
        )
        total_telemetry = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM alerts"
        )
        total_alerts = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM incidents"
        )
        total_incidents = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM incidents
            WHERE LOWER(COALESCE(status, '')) NOT IN
            ('resolved', 'closed')
        """)

        open_incidents = cursor.fetchone()["total"]

        return jsonify({
            "success": True,
            "dashboard": {
                "total_telemetry": total_telemetry,
                "total_alerts": total_alerts,
                "total_incidents": total_incidents,
                "open_incidents": open_incidents
            }
        }), 200

    except Error as error:
        print("[DASHBOARD ERROR]", error)

        return jsonify({
            "success": False,
            "message": "Dashboard query failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==========================================================
# 5. ALERTS
# ==========================================================

@api.route("/alerts", methods=["GET"])
def alerts():

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return jsonify({
                "success": False,
                "message": "Database unavailable"
            }), 503

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM alerts
            ORDER BY created_at DESC
            LIMIT 100
        """)

        records = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(records),
            "alerts": records
        }), 200

    except Error as error:
        print("[ALERT ERROR]", error)

        return jsonify({
            "success": False,
            "message": "Unable to fetch alerts"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==========================================================
# 6. INCIDENTS
# ==========================================================

@api.route("/incidents", methods=["GET"])
def incidents():

    try:
        records = get_incidents()

        return jsonify({
            "success": True,
            "count": len(records),
            "incidents": records
        }), 200

    except Exception as error:
        print("[INCIDENT ERROR]", error)

        return jsonify({
            "success": False,
            "message": "Unable to fetch incidents"
        }), 500


# ==========================================================
# 7. SECURITY EVENT MONITORING
# ==========================================================

@api.route("/security-events", methods=["GET"])
def security_events():

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return jsonify({
                "success": False,
                "message": "Database unavailable"
            }), 503

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM telemetry
            WHERE
                LOWER(COALESCE(event_type, '')) REGEXP
                'security|login|authentication|access|intrusion|firewall|malware|unauthorized'

                OR LOWER(COALESCE(source, '')) REGEXP
                'security|authentication|firewall|access'

                OR LOWER(COALESCE(message, '')) REGEXP
                'unauthorized|failed login|authentication failure|intrusion|malware|suspicious access'

            ORDER BY collected_at DESC
            LIMIT 100
        """)

        records = cursor.fetchall()

        return jsonify({
            "success": True,
            "module": "CICADA Security Monitoring",
            "total_events": len(records),
            "security_events": records
        }), 200

    except Error as error:
        print("[SECURITY ERROR]", error)

        return jsonify({
            "success": False,
            "message": "Security monitoring failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==========================================================
# 8. AI RECOMMENDATIONS
# ==========================================================

@api.route("/recommendations", methods=["GET"])
def recommendations():

    try:
        from ai_engine.recommendations import (
            generate_recommendations
        )

        result = generate_recommendations()

        return jsonify({
            "success": True,
            "module": "CICADA AI Recommendation Engine",
            "count": len(result),
            "recommendations": result
        }), 200

    except Exception as error:
        print("[AI RECOMMENDATION ERROR]", error)

        return jsonify({
            "success": False,
            "message": "Recommendation generation failed"
        }), 500
