import json

from .preprocess import preprocess_telemetry
from .anomaly_detection import detect_anomalies
from .correlation import correlate_events
from .incident_analysis import analyse_incidents
from .risk_scoring import score_incidents
from .recommendations import generate_recommendations

def run_ai_pipeline(telemetry):

    ("\n======================================")
    ("       CICADA AIOPS AI ENGINE")
    ("======================================")

    try:

        # STEP 1: TELEMETRY PREPROCESSING
        print("\n[1/6] Preprocessing telemetry...")

        processed = preprocess_telemetry(telemetry)

        if processed["status"] != "success":
            raise ValueError(processed["message"])

        print("SUCCESS: Telemetry preprocessing completed")

        # STEP 2: ANOMALY DETECTION
        print("\n[2/6] Detecting anomalies...")

        anomaly_result = detect_anomalies(processed)

        if anomaly_result["status"] != "success":
            raise ValueError(anomaly_result["message"])

        print("SUCCESS: Anomaly detection completed")
        print(
            "Anomalies detected:",
            anomaly_result["anomalies_detected"]
        )

        # STEP 3: EVENT CORRELATION
        print("\n[3/6] Correlating events...")

        correlation_result = correlate_events(anomaly_result)

        if correlation_result["status"] != "success":
            raise ValueError(correlation_result["message"])

        print("SUCCESS: Event correlation completed")

        # STEP 4: INCIDENT ANALYSIS
        print("\n[4/6] Analysing incidents...")

        incident_result = analyse_incidents(correlation_result)

        if incident_result["status"] != "success":
            raise ValueError(incident_result["message"])

        print("SUCCESS: Incident analysis completed")

        # STEP 5: RISK SCORING
        print("\n[5/6] Calculating incident risk...")

        risk_result = score_incidents(incident_result)

        if risk_result["status"] != "success":
            raise ValueError(risk_result["message"])

        print("SUCCESS: Risk assessment completed")

        # STEP 6: RECOMMENDATIONS
        print("\n[6/6] Generating recommendations...")

        recommendation_result = generate_recommendations(
            risk_result
        )

        if recommendation_result["status"] != "success":
            raise ValueError(recommendation_result["message"])

        print("SUCCESS: Recommendations generated")

        # FINAL OUTPUT
        final_result = {

            "project": "CICADA AIOps",

            "pipeline_status": "SUCCESS",

            "telemetry_records": processed["total_records"],

            "anomalies_detected": anomaly_result[
                "anomalies_detected"
            ],

            "correlated_incidents": correlation_result[
                "correlated_incident_count"
            ],

            "incident_reports": incident_result[
                "incident_reports"
            ],

            "risk_assessment": risk_result[
                "risk_reports"
            ],

            "recommendations": recommendation_result[
                "recommendations"
            ]

        }

        print("\n======================================")
        print("       CICADA AI PIPELINE COMPLETE")
        print("======================================")

        print(json.dumps(final_result, indent=4))

        return final_result

    except Exception as error:

        print("\nAI PIPELINE FAILED:", str(error))

        return {
            "project": "CICADA AIOps",
            "pipeline_status": "FAILED",
            "error": str(error)
        }


# STANDALONE TESTING
if __name__ == "__main__":

    sample_telemetry = [

        {"hostname": "SERVER-01", "cpu_usage": 20,
         "memory_usage": 30, "disk_usage": 40},

        {"hostname": "SERVER-01", "cpu_usage": 22,
         "memory_usage": 32, "disk_usage": 42},

        {"hostname": "SERVER-01", "cpu_usage": 25,
         "memory_usage": 35, "disk_usage": 45},

        {"hostname": "SERVER-01", "cpu_usage": 21,
         "memory_usage": 31, "disk_usage": 41},

        {"hostname": "SERVER-01", "cpu_usage": 24,
         "memory_usage": 34, "disk_usage": 44},

        {"hostname": "SERVER-01", "cpu_usage": 23,
         "memory_usage": 33, "disk_usage": 43},

        {"hostname": "SERVER-01", "cpu_usage": 26,
         "memory_usage": 36, "disk_usage": 46},

        {"hostname": "SERVER-01", "cpu_usage": 22,
         "memory_usage": 30, "disk_usage": 40},

        {"hostname": "SERVER-01", "cpu_usage": 24,
         "memory_usage": 32, "disk_usage": 42},

        {"hostname": "SERVER-01", "cpu_usage": 99,
         "memory_usage": 98, "disk_usage": 97}

    ]

    run_ai_pipeline(sample_telemetry)