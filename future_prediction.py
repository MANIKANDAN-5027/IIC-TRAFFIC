import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

# ==============================
# LOAD DATA
# ==============================

df = pd.read_csv("traffic_data.csv")

print("Traffic dataset loaded!")
print("Records:", len(df))

# ==============================
# PREPARE DATA
# ==============================

df["hour"] = pd.to_datetime(
    df["time"],
    format="%H:%M"
).dt.hour

day_encoder = LabelEncoder()
location_encoder = LabelEncoder()
weather_encoder = LabelEncoder()

df["day_encoded"] = day_encoder.fit_transform(
    df["day_of_week"]
)

df["location_encoded"] = location_encoder.fit_transform(
    df["location"]
)

df["weather_encoded"] = weather_encoder.fit_transform(
    df["weather"]
)

# ==============================
# FEATURES
# ==============================

features = [
    "hour",
    "day_encoded",
    "location_encoded",
    "vehicle_count",
    "avg_speed",
    "road_capacity",
    "weather_encoded",
    "accident",
    "road_work",
    "event"
]

X = df[features]
y = df["congestion_level"]

# ==============================
# TRAIN MODEL
# ==============================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X, y)

print("AI model trained!")

# ==============================
# CURRENT DATA
# ==============================

current = df.iloc[-1]

current_time = pd.to_datetime(
    current["time"],
    format="%H:%M"
)

# ==============================
# FUTURE TIME = 30 MINUTES
# ==============================

future_time = current_time + pd.Timedelta(minutes=30)

future_hour = future_time.hour

# ==============================
# ESTIMATE FUTURE VEHICLES
# ==============================

current_vehicles = int(current["vehicle_count"])

if 7 <= future_hour <= 9:
    traffic_factor = 1.20

elif 17 <= future_hour <= 20:
    traffic_factor = 1.25

elif 22 <= future_hour or future_hour <= 5:
    traffic_factor = 0.75

else:
    traffic_factor = 1.05

future_vehicles = int(
    current_vehicles * traffic_factor
)

# Keep within dataset range
future_vehicles = max(
    int(df["vehicle_count"].min()),
    min(
        future_vehicles,
        int(df["vehicle_count"].max())
    )
)

# ==============================
# FUTURE DAY
# ==============================

future_day = future_time.strftime("%A")

future_day_encoded = day_encoder.transform(
    [future_day]
)[0]

# ==============================
# FUTURE INPUT
# ==============================

future_data = pd.DataFrame([{

    "hour": future_hour,

    "day_encoded":
        future_day_encoded,

    "location_encoded":
        current["location_encoded"],

    "vehicle_count":
        future_vehicles,

    "avg_speed":
        current["avg_speed"],

    "road_capacity":
        current["road_capacity"],

    "weather_encoded":
        current["weather_encoded"],

    "accident":
        current["accident"],

    "road_work":
        current["road_work"],

    "event":
        current["event"]

}])

# Correct feature order
future_data = future_data[features]

# ==============================
# PREDICTION
# ==============================

prediction = model.predict(
    future_data
)[0]

probabilities = model.predict_proba(
    future_data
)[0]

confidence = max(probabilities) * 100

# ==============================
# DISPLAY RESULT
# ==============================

print("\n================================")
print("   30-MINUTE FUTURE PREDICTION")
print("================================")

print(
    "Location          :",
    current["location"]
)

print(
    "Current Time      :",
    current["time"]
)

print(
    "Future Time       :",
    future_time.strftime("%H:%M")
)

print(
    "Current Vehicles  :",
    current_vehicles
)

print(
    "Predicted Vehicles:",
    future_vehicles
)

print(
    "Traffic Prediction:",
    prediction
)

print(
    "AI Confidence     :",
    round(confidence, 2),
    "%"
)

# ==============================
# ALERT
# ==============================

if prediction == "High":
    print("\n🚨 ALERT: HIGH TRAFFIC EXPECTED!")

elif prediction == "Medium":
    print("\n⚠️ WARNING: MEDIUM TRAFFIC EXPECTED.")

else:
    print("\n✅ Traffic expected to remain LOW.")

# ==============================
# SAVE RESULT
# ==============================

result = pd.DataFrame([{

    "location": current["location"],
    "current_time": current["time"],
    "future_time": future_time.strftime("%H:%M"),
    "current_vehicle_count": current_vehicles,
    "predicted_vehicle_count": future_vehicles,
    "predicted_traffic": prediction,
    "confidence": round(confidence, 2)

}])

result.to_csv(
    "future_prediction.csv",
    index=False
)

print("\nSaved: future_prediction.csv")
print("Future prediction completed successfully!")