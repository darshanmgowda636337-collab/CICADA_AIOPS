# ==========================================================
# CICADA AIOPS
# INTELLIGENT AI-POWERED IT OPERATIONS MONITORING PLATFORM
# ==========================================================


# ==========================================================
# 1. IMPORT LIBRARIES
# ==========================================================

import logging
from pathlib import Path

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    jsonify,
    session,
    request,
    flash
)

from flask_cors import CORS

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ==========================================================
# 2. PROJECT IMPORTS
# ==========================================================

from config import Config

from backend.routes import api

from database.db_connection import get_db_connection

from backend.database import (
    create_user,
    get_user_by_email
)


# ==========================================================
# 3. PROJECT DIRECTORIES
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR / "frontend"

TEMPLATE_DIR = FRONTEND_DIR / "templates"

STATIC_DIR = FRONTEND_DIR / "static"


# ==========================================================
# 4. APPLICATION CONFIGURATION
# ==========================================================

APP_NAME = "CICADA AIOps"

APP_VERSION = "1.0.0"

APP_HOST = "127.0.0.1"

APP_PORT = 5000


# ==========================================================
# 5. LOGGING CONFIGURATION
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("CICADA")


# ==========================================================
# 6. FLASK APPLICATION FACTORY
# ==========================================================

def create_app():

    app = Flask(
        __name__,
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
        static_url_path="/static"
    )

    # ------------------------------------------------------
    # LOAD CONFIGURATION
    # ------------------------------------------------------

    app.config.from_object(Config)

    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

    app.config["SESSION_COOKIE_HTTPONLY"] = True

    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # ------------------------------------------------------
    # ENABLE CORS
    # ------------------------------------------------------

    CORS(app)

    # ------------------------------------------------------
    # REGISTER BACKEND API
    # ------------------------------------------------------

    app.register_blueprint(api)

    # ------------------------------------------------------
    # INITIALIZATION LOGS
    # ------------------------------------------------------

    logger.info("CICADA AIOps initialized")

    logger.info("Template directory: %s", TEMPLATE_DIR)

    logger.info("Static directory: %s", STATIC_DIR)


    # ======================================================
    # PART 1A - HOME PAGE
    # ======================================================

    @app.route("/")
    def home():

        return redirect(url_for("login"))


    # ======================================================
    # PART 1B - USER REGISTRATION
    # ======================================================

    @app.route("/register", methods=["GET", "POST"])
    def register():

        errors = []

        if request.method == "POST":

            username = request.form.get(
                "name", ""
            ).strip()

            email = request.form.get(
                "email", ""
            ).strip().lower()

            password = request.form.get("password", "")

            confirm_password = request.form.get(
                "confirm_password", ""
            )

            # ----------------------------------------------
            # VALIDATION
            # ----------------------------------------------

            if not username:
                errors.append("Full name is required.")

            if len(username) > 100:
                errors.append("Name must not exceed 100 characters.")

            if not email or len(email) > 254:
                errors.append("Enter a valid email address.")

            if len(password) < 8:
                errors.append(
                    "Password must contain at least 8 characters."
                )

            if password != confirm_password:
                errors.append("Passwords do not match.")

            # ----------------------------------------------
            # CHECK EXISTING USER
            # ----------------------------------------------

            if not errors:

                existing_user = get_user_by_email(email)

                if existing_user:

                    errors.append(
                        "This email is already registered."
                    )

            # ----------------------------------------------
            # CREATE USER
            # ----------------------------------------------

            if not errors:

                password_hash = generate_password_hash(
                    password
                )

                user_id = create_user(
                    username,
                    email,
                    password_hash
                )

                if user_id:

                    session.clear()

                    session["user_id"] = user_id

                    session["username"] = username

                    session["email"] = email

                    session["role"] = "user"

                    logger.info(
                        "New user registered: %s",
                        email
                    )

                    flash(
                        "Registration successful!",
                        "success"
                    )

                    return redirect(
                        url_for("dashboard")
                    )

                errors.append(
                    "Registration failed. Please try again."
                )

        return render_template(
            "register.html",
            errors=errors
        )


    # ======================================================
    # PART 1C - USER LOGIN
    # ======================================================

    @app.route("/login", methods=["GET", "POST"])
    def login():

        errors = []

        if request.method == "POST":

            email = request.form.get(
                "email", ""
            ).strip().lower()

            password = request.form.get(
                "password", ""
            )

            # ----------------------------------------------
            # VALIDATION
            # ----------------------------------------------

            if not email or not password:

                errors.append(
                    "Email and password are required."
                )

            else:

                # ------------------------------------------
                # FETCH USER FROM MYSQL
                # ------------------------------------------

                user = get_user_by_email(email)

                # ------------------------------------------
                # VERIFY PASSWORD
                # ------------------------------------------

                if user and check_password_hash(
                    user["password_hash"],
                    password
                ):

                    session.clear()

                    session["user_id"] = user["id"]

                    session["username"] = user["username"]

                    session["email"] = user["email"]

                    session["role"] = user["role"]

                    logger.info(
                        "User logged in: %s",
                        email
                    )

                    flash(
                        "Login successful!",
                        "success"
                    )

                    return redirect(
                        url_for("dashboard")
                    )

                errors.append(
                    "Invalid email or password."
                )

        return render_template(
            "login.html",
            errors=errors
        )


    # ======================================================
    # PART 1 COMPLETED
    # ======================================================
        # ======================================================
    # PART 2A - DASHBOARD PAGE
    # ======================================================

    @app.route("/dashboard")
    def dashboard():

        # --------------------------------------------------
        # CHECK USER SESSION
        # --------------------------------------------------

        if "user_id" not in session:

            flash(
                "Please login to access the dashboard.",
                "warning"
            )

            return redirect(url_for("login"))

        connection = None
        cursor = None

        try:

            # --------------------------------------------------
            # CONNECT TO MYSQL
            # --------------------------------------------------

            connection = get_db_connection()

            if connection is None:

                return "MySQL database unavailable", 503

            cursor = connection.cursor(dictionary=True)

            # --------------------------------------------------
            # FETCH TELEMETRY
            # --------------------------------------------------

            cursor.execute("""
                SELECT *
                FROM telemetry
                LIMIT 100
            """)

            telemetry = cursor.fetchall()

            # --------------------------------------------------
            # FETCH ALERTS
            # --------------------------------------------------

            cursor.execute("""
                SELECT *
                FROM alerts
            """)

            alert_rows = cursor.fetchall()

            # --------------------------------------------------
            # FETCH INCIDENTS
            # --------------------------------------------------

            cursor.execute("""
                SELECT *
                FROM incidents
                LIMIT 10
            """)

            incidents = cursor.fetchall()

            # --------------------------------------------------
            # DATABASE STATISTICS
            # --------------------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM telemetry
            """)

            total_telemetry = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM alerts
            """)

            total_alerts = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM incidents
            """)

            total_incidents = cursor.fetchone()["total"]

            # --------------------------------------------------
            # OPEN INCIDENT COUNT
            # --------------------------------------------------

            open_incidents = sum(
                1
                for row in incidents
                if str(
                    row.get("status", "")
                ).lower() == "open"
            )

            # --------------------------------------------------
            # FORMAT ALERTS
            # --------------------------------------------------

            alerts = []

            for row in alert_rows:

                alerts.append({

                    "short_context": (
                        row.get("message")
                        or row.get("description")
                        or "Alert detected"
                    ),

                    "event_category": (
                        row.get("event_type")
                        or row.get("type")
                        or "System"
                    ),

                    "severity": row.get(
                        "severity", "Unknown"
                    ),

                    "collector_id": (
                        row.get("hostname")
                        or row.get("source")
                        or "Unknown"
                    ),

                    "event_time_utc": (
                        row.get("created_at")
                        or row.get("detected_at")
                        or ""
                    )

                })

            # --------------------------------------------------
            # LATEST INCIDENT
            # --------------------------------------------------

            latest_incident = (
                incidents[0] if incidents else {}
            )

            incident = {

                "title": (
                    latest_incident.get("title")
                    or "No incidents detected"
                ),

                "cause": (
                    latest_incident.get("description")
                    or "No incident details available"
                ),

                "confidence": "N/A",

                "action": (
                    "Continue monitoring system activity"
                )

            }

            # --------------------------------------------------
            # LATEST METRICS
            # --------------------------------------------------

            metrics_view = []

            for row in telemetry[:5]:

                metrics_view.append({

                    "name": row.get(
                        "metric_name", "Metric"
                    ),

                    "value": row.get(
                        "metric_value", 0
                    )

                })

            # --------------------------------------------------
            # SEVERITY SUMMARY
            # --------------------------------------------------

            health_states = []

            for severity in [
                "critical",
                "high",
                "medium",
                "low"
            ]:

                count = sum(
                    1
                    for row in telemetry
                    if str(
                        row.get("severity", "")
                    ).lower() == severity
                )

                health_states.append({

                    "name": severity.title(),

                    "count": count

                })

            # --------------------------------------------------
            # COLLECTOR SUMMARY
            # --------------------------------------------------

            collector_map = {}

            for row in telemetry:

                hostname = (
                    row.get("hostname") or "Unknown"
                )

                if hostname not in collector_map:

                    collector_map[hostname] = {

                        "collector_id": hostname,

                        "status": "Active",

                        "health": row.get(
                            "severity", "Normal"
                        ),

                        "last_seen": (
                            row.get("collected_at")
                            or row.get("created_at")
                            or ""
                        )

                    }

            collectors = list(
                collector_map.values()
            )

            # --------------------------------------------------
            # DASHBOARD STATISTICS
            # --------------------------------------------------

            stats = [

                {
                    "name": "Telemetry Records",
                    "value": total_telemetry,
                    "detail": "Collected records"
                },

                {
                    "name": "Total Alerts",
                    "value": total_alerts,
                    "detail": "Recorded alerts"
                },

                {
                    "name": "Incidents",
                    "value": total_incidents,
                    "detail": "Detected incidents"
                },

                {
                    "name": "Open Incidents",
                    "value": open_incidents,
                    "detail": "Currently open"
                }

            ]

            # --------------------------------------------------
            # LOG COUNTS
            # --------------------------------------------------

            log_counts_view = [

                {
                    "name": "Telemetry",
                    "value": total_telemetry
                },

                {
                    "name": "Alerts",
                    "value": total_alerts
                }

            ]

            # --------------------------------------------------
            # LATEST EVENT
            # --------------------------------------------------

            latest_event = None

            if telemetry:

                latest_event = (
                    telemetry[0].get("collected_at")
                    or telemetry[0].get("created_at")
                )

            # --------------------------------------------------
            # RENDER DASHBOARD
            # --------------------------------------------------

            return render_template(

                "dashboard.html",

                user={
                    "name": session.get(
                        "username", "CICADA User"
                    )
                },

                tenant_id="Default",

                stats=stats,

                metrics_view=metrics_view,

                log_counts_view=log_counts_view,

                health_states=health_states,

                latest_event=latest_event,

                alerts=alerts,

                incident=incident,

                collectors=collectors

            )

        except Exception:

            logger.exception(
                "Dashboard loading failed"
            )

            return (
                "Dashboard loading failed. "
                "Check Flask terminal.",
                500
            )

        finally:

            if cursor is not None:
                cursor.close()

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.close()


    # ======================================================
    # PART 2B - INDEX PAGE
    # ======================================================

    @app.route("/index")
    def index():

        if "user_id" not in session:

            return redirect(url_for("login"))

        return render_template("index.html")


    # ======================================================
    # PART 2C - LOCAL DATA PAGE
    # ======================================================

    @app.route("/local-data")
    def local_data():

        if "user_id" not in session:

            return redirect(url_for("login"))

        return render_template(
            "local_data.html"
        )


    # ======================================================
    # PART 2D - LOGOUT
    # ======================================================

    @app.route("/logout")
    def logout():

        session.clear()

        flash(
            "You have been logged out successfully.",
            "success"
        )

        return redirect(
            url_for("login")
        )


    # ======================================================
    # PART 2 COMPLETED
    # ======================================================
        # ======================================================
    # PART 3A - APPLICATION HEALTH MONITORING
    # ======================================================

    @app.route("/health", methods=["GET"])
    def application_health():

        connection = None
        cursor = None

        try:

            # ----------------------------------------------
            # CONNECT TO MYSQL
            # ----------------------------------------------

            connection = get_db_connection()

            if connection is None:

                return jsonify({

                    "success": False,

                    "application": APP_NAME,

                    "database": "disconnected",

                    "status": "unhealthy"

                }), 503

            # ----------------------------------------------
            # VERIFY DATABASE
            # ----------------------------------------------

            cursor = connection.cursor()

            cursor.execute("SELECT 1")

            cursor.fetchone()

            # ----------------------------------------------
            # SUCCESS RESPONSE
            # ----------------------------------------------

            return jsonify({

                "success": True,

                "application": APP_NAME,

                "version": APP_VERSION,

                "database": "connected",

                "status": "healthy"

            }), 200

        except Exception as error:

            logger.exception(
                "Health check failed: %s",
                error
            )

            return jsonify({

                "success": False,

                "application": APP_NAME,

                "database": "error",

                "status": "unhealthy"

            }), 503

        finally:

            if cursor is not None:

                cursor.close()

            if (
                connection is not None
                and connection.is_connected()
            ):

                connection.close()


    # ======================================================
    # PART 3B - API INFORMATION
    # ======================================================

    @app.route("/api", methods=["GET"])
    def api_information():

        return jsonify({

            "application": APP_NAME,

            "version": APP_VERSION,

            "status": "running",

            "database": "MySQL",

            "api_prefix": "/api",

            "available_pages": [

                "/",

                "/login",

                "/register",

                "/dashboard",

                "/index",

                "/local-data",

                "/logout",

                "/health"

            ],

            "message": (
                "CICADA AIOps API is running successfully."
            )

        }), 200


    # ======================================================
    # PART 3C - DATABASE STATUS
    # ======================================================

    @app.route("/database-status", methods=["GET"])
    def database_status():

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            if connection is None:

                return jsonify({

                    "success": False,

                    "database": "MySQL",

                    "connection": "disconnected"

                }), 503

            cursor = connection.cursor()

            cursor.execute("SELECT DATABASE()")

            database_name = cursor.fetchone()[0]

            return jsonify({

                "success": True,

                "database": database_name,

                "connection": "connected"

            }), 200

        except Exception as error:

            logger.exception(
                "Database status check failed: %s",
                error
            )

            return jsonify({

                "success": False,

                "database": "MySQL",

                "connection": "error"

            }), 503

        finally:

            if cursor is not None:

                cursor.close()

            if (
                connection is not None
                and connection.is_connected()
            ):

                connection.close()


    # ======================================================
    # PART 3 COMPLETED
    # ======================================================
        # ======================================================
    # PART 4A - 404 ERROR HANDLER
    # ======================================================

    @app.errorhandler(404)
    def page_not_found(error):

        logger.warning("404 error: %s", error)

        return jsonify({

            "success": False,

            "error": "Page not found",

            "status_code": 404

        }), 404


    # ======================================================
    # PART 4B - 405 ERROR HANDLER
    # ======================================================

    @app.errorhandler(405)
    def method_not_allowed(error):

        logger.warning("405 error: %s", error)

        return jsonify({

            "success": False,

            "error": "Method not allowed",

            "status_code": 405

        }), 405


    # ======================================================
    # PART 4C - 413 ERROR HANDLER
    # ======================================================

    @app.errorhandler(413)
    def request_entity_too_large(error):

        logger.warning("413 error: %s", error)

        return jsonify({

            "success": False,

            "error": "Uploaded file is too large",

            "maximum_size": "1 MB",

            "status_code": 413

        }), 413


       # ======================================================
    # PART 4A - 404 ERROR HANDLER
    # ======================================================

    @app.errorhandler(404)
    def page_not_found(error):

        logger.warning("404 error: %s", error)

        return jsonify({
            "success": False,
            "error": "Page not found",
            "status_code": 404
        }), 404


    # ======================================================
    # PART 4B - 405 ERROR HANDLER
    # ======================================================

    @app.errorhandler(405)
    def method_not_allowed(error):

        logger.warning("405 error: %s", error)

        return jsonify({
            "success": False,
            "error": "Method not allowed",
            "status_code": 405
        }), 405


    # ======================================================
    # PART 4C - 413 ERROR HANDLER
    # ======================================================

    @app.errorhandler(413)
    def request_entity_too_large(error):

        logger.warning("413 error: %s", error)

        return jsonify({
            "success": False,
            "error": "Uploaded file is too large",
            "maximum_size": "1 MB",
            "status_code": 413
        }), 413


    # ======================================================
    # PART 4D - 500 ERROR HANDLER
    # ======================================================

    @app.errorhandler(500)
    def internal_server_error(error):

        logger.error(
            "Internal server error: %s",
            error
        )

        return jsonify({
            "success": False,
            "error": "Internal server error",
            "status_code": 500
        }), 500


    # ======================================================
    # PART 4E - APPLICATION INITIALIZATION
    # ======================================================

    logger.info(
        "%s application initialized successfully.",
        APP_NAME
    )

    return app


# ==========================================================
# CREATE FLASK APPLICATION
# ==========================================================

app = create_app()


# ==========================================================
# RUN CICADA AIOPS APPLICATION
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")

    print("       CICADA AIOps APPLICATION")

    print("==========================================")

    print("Application : ", APP_NAME)

    print("Version     : ", APP_VERSION)

    print("Host        : ", APP_HOST)

    print("Port        : ", APP_PORT)

    print("URL         : http://127.0.0.1:5000")

    print("==========================================\n")

    app.run(
        host=APP_HOST,
        port=APP_PORT,
        debug=True
    )