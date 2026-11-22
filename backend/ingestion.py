# ==========================================================
# CICADA AIOPS
# TELEMETRY INGESTION MODULE
# ==========================================================

import math
import json
import logging

from mysql.connector import Error

from backend.database import insert_telemetry


# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================

logger = logging.getLogger("CICADA.INGESTION")


# ==========================================================
# REQUIRED TELEMETRY FIELDS
# ==========================================================

REQUIRED_FIELDS = [
    "hostname",
    "source",
    "event_type",
    "metric_name",
    "metric_value"
]


# ==========================================================
# FIELD LENGTH LIMITS
# ==========================================================

FIELD_LIMITS = {
    "hostname": 150,
    "source": 100,
    "event_type": 100,
    "metric_name": 100,
    "severity": 30,
    "message": 1000
}


# ==========================================================
# VALIDATE TELEMETRY PAYLOAD
# ==========================================================

def validate_telemetry(payload):

    if not isinstance(payload, dict):

        return False, "Payload must be a JSON object"

    # Check required fields

    for field in REQUIRED_FIELDS:

        if field not in payload:

            return False, f"Missing required field: {field}"

    # Validate string fields

    for field in REQUIRED_FIELDS[:-1]:

        value = payload.get(field)

        if not isinstance(value, str):

            return False, f"{field} must be a string"

        if not value.strip():

            return False, f"{field} cannot be empty"

    # Validate optional string fields

    for field in ["severity", "message"]:

        value = payload.get(field)

        if value is not None:

            if not isinstance(value, str):

                return False, f"{field} must be a string"

    # Validate field lengths

    for field, maximum in FIELD_LIMITS.items():

        value = payload.get(field)

        if value is not None and len(value) > maximum:

            return False, f"{field} exceeds maximum length"

    # Validate metric value

    try:

        if isinstance(payload["metric_value"], bool):
            return False, "Metric value must be numeric"

        metric_value = float(payload["metric_value"])

        if not math.isfinite(metric_value):

            return False, "Metric value must be finite"

    except (ValueError, TypeError):

        return False, "Metric value must be numeric"

    # Validate metadata

    metadata = payload.get("metadata", {})

    if not isinstance(metadata, dict):

        return False, "Metadata must be a JSON object"

    # Ensure metadata can be serialized

    try:

        json.dumps(metadata)

    except (TypeError, ValueError):

        return False, "Metadata contains invalid JSON values"

    return True, "Telemetry validation successful"


# ==========================================================
# PREPARE TELEMETRY PAYLOAD
# ==========================================================

def prepare_telemetry(payload):

    approved_data = {

        "hostname": payload["hostname"].strip(),

        "source": payload["source"].strip(),

        "event_type": payload["event_type"].strip(),

        "metric_name": payload["metric_name"].strip(),

        "metric_value": float(payload["metric_value"]),

        "severity": payload.get("severity", "INFO").strip().upper(),

        "message": payload.get("message", ""),

        "metadata": payload.get("metadata", {})

    }

    return approved_data


# ==========================================================
# TELEMETRY INGESTION
# ==========================================================

def ingest_telemetry(payload):

    try:

        # Step 1: Validate payload

        valid, message = validate_telemetry(payload)

        if not valid:

            logger.warning("Telemetry validation failed: %s", message)

            return {

                "success": False,

                "message": message

            }, 400

        # Step 2: Prepare approved telemetry

        approved_data = prepare_telemetry(payload)

        logger.info(
            "Processing telemetry from host: %s",
            approved_data["hostname"]
        )

        # Step 3: Insert into MySQL

        record_id = insert_telemetry(approved_data)

        if not record_id:

            logger.error("Telemetry database insertion failed")

            return {

                "success": False,

                "message": "Database insertion failed"

            }, 500

        # Step 4: Successful response

        logger.info(
            "Telemetry successfully stored. ID: %s",
            record_id
        )

        return {

            "success": True,

            "message": "Telemetry ingested successfully",

            "telemetry_id": record_id,

            "hostname": approved_data["hostname"],

            "severity": approved_data["severity"]

        }, 201

    except Error:

        logger.exception("MySQL telemetry insertion error")

        return {

            "success": False,

            "message": "MySQL telemetry insertion failed"

        }, 500

    except Exception:

        logger.exception("Unexpected telemetry ingestion error")

        return {

            "success": False,

            "message": "Internal telemetry processing error"

        }, 500


# ==========================================================
# TEST TELEMETRY VALIDATION
# ==========================================================

def test_telemetry_validation():

    sample_payload = {

        "hostname": "CICADA-SERVER-01",

        "source": "system_monitor",

        "event_type": "performance",

        "metric_name": "cpu_usage",

        "metric_value": 45.5,

        "severity": "INFO",

        "message": "CPU usage normal",

        "metadata": {

            "environment": "development",

            "platform": "windows"

        }

    }

    valid, message = validate_telemetry(sample_payload)

    print("\n===================================")

    print("CICADA TELEMETRY VALIDATION TEST")

    print("===================================")

    print("Result:", "PASSED" if valid else "FAILED")

    print("Message:", message)

    print("===================================\n")

    return valid


# ==========================================================
# DIRECT EXECUTION
# ==========================================================

if __name__ == "__main__":

    test_telemetry_validation()