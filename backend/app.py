import os
import logging
from pathlib import Path
from flask_wtf.csrf import CSRFProtect

from flask import (
    Flask,
    jsonify,
    render_template,
    redirect,
    url_for
)

from flask_cors import CORS

from backend.routes import api
from backend.database import get_connection


# ==========================================
# CICADA PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"
TEMPLATE_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"


# ==========================================
# APPLICATION FACTORY
# ==========================================

def create_app():

    app = Flask(
        __name__,
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
        static_url_path="/static"
    )

    # ======================================
    # CONFIGURATION
    # ======================================

    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

    if not app.config["SECRET_KEY"]:
        raise RuntimeError(
            "FLASK_SECRET_KEY is missing from the .env file"
        )

    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
    app.config["JSON_SORT_KEYS"] = False

    CORS(app)

    # ======================================
    # LOGGING
    # ======================================

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    app.logger.setLevel(logging.INFO)

    # ======================================
    # REGISTER API BLUEPRINT
    # ======================================

    app.register_blueprint(api)

    # ======================================
    # FRONTEND ROUTES
    # ======================================

    @app.route("/")
    def home():
        return redirect(url_for("login_page"))

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/dashboard")
def dashboard():
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch telemetry
        cursor.execute("""
            SELECT *
            FROM telemetry
            ORDER BY collected_at DESC
            LIMIT 100
        """)
        telemetry = cursor.fetchall()

        # Fetch alerts
        cursor.execute("SELECT * FROM alerts")
        alert_rows = cursor.fetchall()

        # Fetch incidents
        cursor.execute("""
            SELECT *
            FROM incidents
            ORDER BY detected_at DESC
            LIMIT 10
        """)
        incidents = cursor.fetchall()

        cursor.close()

        # Dashboard metrics
        total_telemetry = len(telemetry)
        total_alerts = len(alert_rows)
        total_incidents = len(incidents)

        open_incidents = sum(
            1 for item in incidents
            if str(item.get("status", "")).lower() == "open"
        )

        # Convert alerts to dashboard format
        alerts = []

        for alert in alert_rows:
            alerts.append({
                "short_context": alert.get("message", alert.get("description", "Alert detected")),
                "event_category": alert.get("event_type", alert.get("type", "System")),
                "severity": alert.get("severity", "Unknown"),
                "collector_id": alert.get("hostname", alert.get("source", "Unknown")),
                "event_time_utc": alert.get("created_at", alert.get("detected_at", ""))
            })

        # Latest incident
        latest_incident = incidents[0] if incidents else {}

        incident = {
            "title": latest_incident.get("title", "No incidents detected"),
            "cause": latest_incident.get("description", "No incident details available"),
            "confidence": "N/A",
            "action": "Monitor system activity"
        }

        # Latest metrics
        metrics_view = [
            {
                "name": item.get("metric_name", "Metric"),
                "value": item.get("metric_value", 0)
            }
            for item in telemetry[:5]
        ]

        # Severity summary
        health_states = []

        for severity in ["critical", "high", "medium", "low"]:
            count = sum(
                1 for item in telemetry
                if str(item.get("severity", "")).lower() == severity
            )
            health_states.append({
                "name": severity.title(),
                "count": count
            })

        # Collector summary from telemetry hostnames
        collectors_map = {}

        for item in telemetry:
            hostname = item.get("hostname", "Unknown")
            collectors_map[hostname] = {
                "collector_id": hostname,
                "status": "Active",
                "health": item.get("severity", "Normal"),
                "last_seen": item.get("collected_at", "")
            }

        collectors = list(collectors_map.values())

        stats = [
            {"name": "Telemetry Records", "value": total_telemetry, "detail": "Collected records"},
            {"name": "Total Alerts", "value": total_alerts, "detail": "Recorded alerts"},
            {"name": "Incidents", "value": total_incidents, "detail": "Detected incidents"},
            {"name": "Open Incidents", "value": open_incidents, "detail": "Currently open"}
        ]

        log_counts_view = [
            {"name": "Telemetry", "value": total_telemetry},
            {"name": "Alerts", "value": total_alerts}
        ]

        return render_template(
            "dashboard.html",
            user={"name": "CICADA User"},
            tenant_id="Default",
            stats=stats,
            metrics_view=metrics_view,
            log_counts_view=log_counts_view,
            health_states=health_states,
            latest_event=telemetry[0].get("collected_at") if telemetry else None,
            alerts=alerts,
            incident=incident,
            collectors=collectors
        )

    except Exception:
        app.logger.exception("Dashboard loading failed")
        return "Dashboard loading failed. Check the Flask terminal for details.", 500

    finally:
        if connection:
            connection.close()

    @app.route("/local-data")
    def local_data_page():
        return render_template("local_data.html")

    # ======================================
    # ROOT API
    # ======================================

    @app.route("/api", methods=["GET"])
    def api_information():

        return jsonify({
            "application": "CICADA AIOps",
            "version": "1.0",
            "status": "running",
            "backend": "Flask",
            "database": "MySQL"
        })

    # ======================================
    # ERROR HANDLERS
    # ======================================

    @app.errorhandler(404)
    def not_found(error):

        return jsonify({
            "success": False,
            "message": "Requested resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):

        return jsonify({
            "success": False,
            "message": "HTTP method not allowed"
        }), 405

    @app.errorhandler(413)
    def payload_too_large(error):

        return jsonify({
            "success": False,
            "message": "Request payload too large"
        }), 413

    @app.errorhandler(500)
    def internal_error(error):

        original = getattr(error, "original_exception", None)

        if original:
            app.logger.error(
                "CICADA INTERNAL ERROR",
                exc_info=(
                    type(original),
                    original,
                    original.__traceback__
                )
            )
        else:
            app.logger.error(
                "CICADA INTERNAL ERROR: %s",
                error
            )

        return jsonify({
            "success": False,
            "message": "Internal server error. Check Flask terminal logs."
        }), 500

    # ======================================
    # STARTUP VALIDATION
    # ======================================

    app.logger.info("CICADA AIOps application initialized")
    app.logger.info("Frontend: %s", FRONTEND_DIR)
    app.logger.info("Templates: %s", TEMPLATE_DIR)
    app.logger.info("Static: %s", STATIC_DIR)

    if not TEMPLATE_DIR.exists():
        raise RuntimeError("Frontend templates directory not found")

    if not STATIC_DIR.exists():
        raise RuntimeError("Frontend static directory not found")

    return app


# ==========================================
# CREATE APPLICATION
# ==========================================

app = create_app()


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    print("=" * 45)
    print("       CICADA AIOps BACKEND")
    print("=" * 45)

    print("Frontend:", FRONTEND_DIR)
    print("Templates:", TEMPLATE_DIR)
    print("Static:", STATIC_DIR)

    print("Starting Flask server...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )