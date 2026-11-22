import pandas as pd


def preprocess_telemetry(telemetry):
    """
    Clean and validate CICADA telemetry data.
    """

    try:
        # Convert incoming telemetry into DataFrame
        if isinstance(telemetry, dict):
            df = pd.DataFrame([telemetry])

        elif isinstance(telemetry, list):
            df = pd.DataFrame(telemetry)

        elif isinstance(telemetry, pd.DataFrame):
            df = telemetry.copy()

        else:
            raise TypeError("Unsupported telemetry format")

        if df.empty:
            return {
                "status": "failed",
                "message": "No telemetry data available",
                "data": []
            }

        # Remove duplicate records
        df = df.drop_duplicates()

        # Replace infinite values
        df = df.replace([float("inf"), float("-inf")], None)

        # Handle missing values
        df = df.fillna(0)

        # Reset index
        df = df.reset_index(drop=True)

        return {
            "status": "success",
            "message": "Telemetry preprocessing completed",
            "total_records": len(df),
            "data": df.to_dict(orient="records")
        }

    except Exception as error:

        return {
            "status": "failed",
            "message": str(error),
            "data": []
        }


if __name__ == "__main__":

    sample_telemetry = [
        {
            "cpu_usage": 45,
            "memory_usage": 60,
            "disk_usage": 70
        },
        {
            "cpu_usage": 95,
            "memory_usage": 92,
            "disk_usage": 85
        },
        {
            "cpu_usage": 45,
            "memory_usage": 60,
            "disk_usage": 70
        }
    ]

    result = preprocess_telemetry(sample_telemetry)

    print("\n===== CICADA TELEMETRY PREPROCESSING =====")
    print("Status:", result["status"])
    print("Message:", result["message"])
    print("Total Records:", result.get("total_records", 0))
    print("Processed Data:", result["data"])