import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(telemetry, contamination=0.1):

    try:
        # Accept preprocessed telemetry
        if isinstance(telemetry, dict) and "data" in telemetry:
            telemetry = telemetry["data"]

        # Convert telemetry into DataFrame
        if isinstance(telemetry, dict):
            df = pd.DataFrame([telemetry])

        elif isinstance(telemetry, list):
            df = pd.DataFrame(telemetry)

        elif isinstance(telemetry, pd.DataFrame):
            df = telemetry.copy()

        else:
            raise TypeError("Invalid telemetry format")

        if df.empty:
            return {
                "status": "failed",
                "message": "No telemetry available",
                "anomalies": []
            }

        # Select numeric telemetry features
        excluded_columns = {
            "id", "event_id", "user_id",
            "process_id", "timestamp"
        }

        numeric_columns = [
            col for col in df.select_dtypes(include="number").columns
            if col.lower() not in excluded_columns
        ]

        if not numeric_columns:
            raise ValueError("No numeric telemetry features found")

        if len(df) < 5:
            return {
                "status": "insufficient_data",
                "message": "At least 5 records are required",
                "anomalies": []
            }

        # Prepare model input
        X = df[numeric_columns].copy()
        X = X.replace([float("inf"), float("-inf")], float("nan"))
        X = X.fillna(X.median()).fillna(0)

        # Initialize Isolation Forest
        model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42
        )

        # Train and predict
        predictions = model.fit_predict(X)

        # Calculate anomaly scores
        scores = model.decision_function(X)

        # Add results
        df["anomaly_label"] = [
            "Anomaly" if prediction == -1 else "Normal"
            for prediction in predictions
        ]

        df["anomaly_score"] = [
            round(float(-score), 4)
            for score in scores
        ]

        anomalies = df[
            df["anomaly_label"] == "Anomaly"
        ].to_dict(orient="records")

        return {
            "status": "success",
            "algorithm": "Isolation Forest",
            "total_records": len(df),
            "anomalies_detected": len(anomalies),
            "normal_records": len(df) - len(anomalies),
            "anomalies": anomalies,
            "results": df.to_dict(orient="records")
        }

    except Exception as error:

        return {
            "status": "failed",
            "message": str(error),
            "anomalies": []
        }


# Standalone testing
if __name__ == "__main__":

    sample_telemetry = [
        {"cpu_usage": 20, "memory_usage": 30, "disk_usage": 40},
        {"cpu_usage": 22, "memory_usage": 32, "disk_usage": 42},
        {"cpu_usage": 25, "memory_usage": 35, "disk_usage": 45},
        {"cpu_usage": 21, "memory_usage": 31, "disk_usage": 41},
        {"cpu_usage": 24, "memory_usage": 34, "disk_usage": 44},
        {"cpu_usage": 23, "memory_usage": 33, "disk_usage": 43},
        {"cpu_usage": 26, "memory_usage": 36, "disk_usage": 46},
        {"cpu_usage": 22, "memory_usage": 30, "disk_usage": 40},
        {"cpu_usage": 24, "memory_usage": 32, "disk_usage": 42},
        {"cpu_usage": 99, "memory_usage": 98, "disk_usage": 97}
    ]

    result = detect_anomalies(sample_telemetry)

    print("\n===== CICADA AI ANOMALY DETECTION =====")

    print("Status:", result["status"])
    print("Algorithm:", result.get("algorithm"))
    print("Total Records:", result.get("total_records"))
    print("Anomalies Detected:", result.get("anomalies_detected"))
    print("Normal Records:", result.get("normal_records"))

    print("\nDetected Anomalies:")

    for anomaly in result.get("anomalies", []):
        print(anomaly)