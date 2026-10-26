import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# ==============================
# LOAD CSV
# ==============================

df = pd.read_csv("traffic_data.csv")

print("\n==============================")
print("       TRAFFIC DATA")
print("==============================")

print(df.head())
print("\nData Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())


# ==============================
# CLEAN DATA
# ==============================

df.columns = df.columns.str.strip()

df["simulation_time"] = pd.to_numeric(
    df["simulation_time"], errors="coerce"
)

df["vehicle_count"] = pd.to_numeric(
    df["vehicle_count"], errors="coerce"
)

df["average_speed"] = pd.to_numeric(
    df["average_speed"], errors="coerce"
)

df["dbscan_clusters"] = pd.to_numeric(
    df["dbscan_clusters"], errors="coerce"
)

df = df.dropna()

print("\nCleaned Data:")
print(df.head())


# ==============================
# GRAPH 1
# VEHICLE COUNT
# ==============================

plt.figure(figsize=(10, 5))

plt.plot(
    df["simulation_time"],
    df["vehicle_count"]
)

plt.title("Vehicle Count Over Time")
plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of Vehicles")
plt.grid(True)

plt.savefig("vehicle_count_graph.png", dpi=300)

plt.show()


# ==============================
# GRAPH 2
# AVERAGE SPEED
# ==============================

plt.figure(figsize=(10, 5))

plt.plot(
    df["simulation_time"],
    df["average_speed"]
)

plt.title("Average Vehicle Speed Over Time")
plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Average Speed (m/s)")
plt.grid(True)

plt.savefig("average_speed_graph.png", dpi=300)

plt.show()


# ==============================
# GRAPH 3
# VEHICLE COUNT + SPEED
# ==============================

fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(
    df["simulation_time"],
    df["vehicle_count"]
)

ax1.set_xlabel("Simulation Time (seconds)")
ax1.set_ylabel("Vehicle Count")

ax2 = ax1.twinx()

ax2.plot(
    df["simulation_time"],
    df["average_speed"]
)

ax2.set_ylabel("Average Speed (m/s)")

plt.title("Traffic Flow Analysis")

plt.grid(True)

plt.savefig("traffic_analysis.png", dpi=300)

plt.show()


# ==============================
# ML PREDICTION
# PREDICT FUTURE VEHICLE COUNT
# ==============================

print("\n==============================")
print("       ML PREDICTION")
print("==============================")


features = [
    "simulation_time",
    "average_speed",
    "dbscan_clusters"
]

target = "vehicle_count"

X = df[features]
y = df[target]


# ==============================
# TRAIN / TEST SPLIT
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ==============================
# RANDOM FOREST MODEL
# ==============================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# ==============================
# TEST PREDICTION
# ==============================

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel Performance")
print("-------------------------")
print("MAE :", round(mae, 2))
print("R2  :", round(r2, 2))


# ==============================
# NEXT TIME PREDICTION
# ==============================

last_time = df["simulation_time"].iloc[-1]

next_time = last_time + 1

last_speed = df["average_speed"].iloc[-1]

last_cluster = df["dbscan_clusters"].iloc[-1]


next_data = pd.DataFrame({
    "simulation_time": [next_time],
    "average_speed": [last_speed],
    "dbscan_clusters": [last_cluster]
})


prediction = model.predict(next_data)

predicted_vehicle_count = round(prediction[0])


print("\n==============================")
print("   FUTURE TRAFFIC PREDICTION")
print("==============================")

print("Current Time        :", last_time)
print("Next Time           :", next_time)
print("Current Speed       :", round(last_speed, 2), "m/s")
print("Predicted Vehicles  :", predicted_vehicle_count)


# ==============================
# PREDICTED TRAFFIC STATUS
# ==============================

if predicted_vehicle_count >= 10:
    status = "HIGH TRAFFIC"

elif predicted_vehicle_count >= 5:
    status = "MEDIUM TRAFFIC"

else:
    status = "LOW TRAFFIC"


print("Predicted Status    :", status)

print("==============================")