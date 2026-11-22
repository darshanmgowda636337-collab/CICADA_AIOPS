from database.db_connection import insert_telemetry, get_telemetry

telemetry_data = {
    "hostname": "CICADA-CLIENT-01",
    "source": "system_monitor",
    "event_type": "CPU",
    "metric_name": "cpu_usage",
    "metric_value": 85.5,
    "severity": "HIGH",
    "message": "High CPU utilization detected",
    "metadata": {
        "platform": "Windows",
        "processor": "AMD Ryzen 7"
    }
}

# Insert telemetry
record_id = insert_telemetry(telemetry_data)

if record_id:
    print("Telemetry inserted successfully!")
    print("Record ID:", record_id)
else:
    print("Telemetry insertion failed!")

# Retrieve telemetry
records = get_telemetry(limit=10)

print("\nStored telemetry:")

for record in records:
    print(record)