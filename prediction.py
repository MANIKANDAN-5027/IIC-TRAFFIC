import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("traffic_data.csv")

print("Dataset loaded successfully!")
print("Total records:", len(df))

# Convert time to hour
df["hour"] = pd.to_datetime(df["time"], format="%H:%M").dt.hour

# Encode categorical data
day_encoder = LabelEncoder()
location_encoder = LabelEncoder()
weather_encoder = LabelEncoder()

df["day_encoded"] = day_encoder.fit_transform(df["day_of_week"])
df["location_encoded"] = location_encoder.fit_transform(df["location"])
df["weather_encoded"] = weather_encoder.fit_transform(df["weather"])

# Features
X = df[
    [
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
]

# Target
y = df["congestion_level"]

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Random Forest model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

print("\nTraining AI model...")

model.fit(X_train, y_train)

print("Model training completed!")

# Prediction
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("      MODEL PERFORMANCE")
print("==============================")

print("Accuracy:", round(accuracy * 100, 2), "%")

# Example prediction
sample = X_test.iloc[[0]]

prediction = model.predict(sample)[0]

print("\n==============================")
print("       TRAFFIC PREDICTION")
print("==============================")

print("Predicted Traffic:", prediction)

# Save predictions
result = X_test.copy()
result["actual_traffic"] = y_test.values
result["predicted_traffic"] = y_pred

result.to_csv("prediction_result.csv", index=False)

print("\nPrediction saved to: prediction_result.csv")
print("\nPrediction completed successfully!")