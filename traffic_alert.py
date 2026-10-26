import pandas as pd
import os
from datetime import datetime

# ============================================================
# IIC TRAFFIC AI - AUTOMATIC TRAFFIC ALERT SYSTEM
# ============================================================

PREDICTION_FILE = "prediction_result.csv"
ALERT_FILE = "traffic_alerts.csv"


# ============================================================
# CHECK PREDICTION FILE
# ============================================================

if not os.path.exists(PREDICTION_FILE):
    print("ERROR: prediction_result.csv not found!")
    print("First run:")
    print("python prediction.py")
    exit()


# ============================================================
# LOAD PREDICTION
# ============================================================

df = pd.read_csv(PREDICTION_FILE)

latest = df.iloc[-1]


# ============================================================
# GET VALUES
# ============================================================

predicted_vehicles = int(
    latest["predicted_vehicle_count"]
)

traffic_status = str(
    latest["predicted_status"]
)

next_time = latest["next_time"]


# ============================================================
# CREATE ALERT
# ============================================================

if "HIGH" in traffic_status.upper():

    alert_level = "CRITICAL"

    alert_message = (
        "🚨 HIGH TRAFFIC ALERT! "
        f"Approximately {predicted_vehicles} vehicles "
        "are predicted. "
        "Please consider using an alternative route."
    )

elif "MEDIUM" in traffic_status.upper():

    alert_level = "WARNING"

    alert_message = (
        "⚠️ MEDIUM TRAFFIC WARNING! "
        f"Approximately {predicted_vehicles} vehicles "
        "are predicted. "
        "Consider an alternative route if available."
    )

else:

    alert_level = "NORMAL"

    alert_message = (
        "🟢 TRAFFIC NORMAL. "
        f"Approximately {predicted_vehicles} vehicles "
        "are predicted. "
        "No alternative route is currently required."
    )


# ============================================================
# DISPLAY ALERT
# ============================================================

print()
print("=" * 60)
print("             IIC TRAFFIC AI")
print("          AUTOMATIC ALERT SYSTEM")
print("=" * 60)

print()
print("Prediction Time :", next_time)
print("Vehicles        :", predicted_vehicles)
print("Traffic Status  :", traffic_status)
print("Alert Level     :", alert_level)

print()
print("ALERT MESSAGE")
print("-" * 60)
print(alert_message)

print("=" * 60)


# ============================================================
# SAVE ALERT
# ============================================================

alert_data = pd.DataFrame({

    "timestamp": [
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ],

    "prediction_time": [
        next_time
    ],

    "predicted_vehicles": [
        predicted_vehicles
    ],

    "traffic_status": [
        traffic_status
    ],

    "alert_level": [
        alert_level
    ],

    "alert_message": [
        alert_message
    ]

})


alert_data.to_csv(
    ALERT_FILE,
    index=False
)


print()
print("Alert saved to:", ALERT_FILE)
print()
print("Traffic alert system completed successfully.")