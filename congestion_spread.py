import pandas as pd

# ==============================
# LOAD DATA
# ==============================

df = pd.read_csv("traffic_data.csv")

# ==============================
# ROAD CONNECTIONS
# ==============================

road_connections = {
    "GST Road": [
        "Mount Road",
        "Velachery Main Road"
    ],

    "OMR Road": [
        "ECR Road",
        "Velachery Main Road"
    ],

    "Anna Salai": [
        "Mount Road",
        "Poonamallee High Road"
    ],

    "Poonamallee High Road": [
        "Anna Salai",
        "GST Road"
    ],

    "Mount Road": [
        "Anna Salai",
        "GST Road"
    ],

    "ECR Road": [
        "OMR Road",
        "GST Road"
    ],

    "Velachery Main Road": [
        "GST Road",
        "OMR Road"
    ]
}

# ==============================
# CURRENT ROAD
# ==============================

current_road = df.iloc[-1]["location"]

current_vehicles = int(
    df.iloc[-1]["vehicle_count"]
)

road_capacity = int(
    df.iloc[-1]["road_capacity"]
)

# ==============================
# CURRENT CONGESTION SCORE
# ==============================

traffic_ratio = (
    current_vehicles / road_capacity
)

if traffic_ratio >= 0.80:
    current_status = "HIGH"

elif traffic_ratio >= 0.50:
    current_status = "MEDIUM"

else:
    current_status = "LOW"

# ==============================
# FIND NEARBY ROADS
# ==============================

nearby_roads = road_connections.get(
    current_road,
    []
)

print("\n================================")
print("   CONGESTION SPREAD PREDICTION")
print("================================")

print("Current Road       :", current_road)
print("Current Vehicles   :", current_vehicles)
print("Current Status     :", current_status)

# ==============================
# SPREAD PREDICTION
# ==============================

results = []

for road in nearby_roads:

    road_data = df[
        df["location"] == road
    ]

    if len(road_data) == 0:
        continue

    latest = road_data.iloc[-1]

    nearby_vehicles = int(
        latest["vehicle_count"]
    )

    nearby_capacity = int(
        latest["road_capacity"]
    )

    nearby_ratio = (
        nearby_vehicles / nearby_capacity
    )

    # Calculate spread risk
    if current_status == "HIGH":

        spread_risk = 0.75

    elif current_status == "MEDIUM":

        spread_risk = 0.45

    else:

        spread_risk = 0.20

    # Existing traffic effect
    spread_risk += nearby_ratio * 0.20

    spread_risk = min(
        spread_risk,
        0.99
    )

    probability = round(
        spread_risk * 100,
        2
    )

    if probability >= 70:

        predicted_status = "HIGH"

    elif probability >= 40:

        predicted_status = "MEDIUM"

    else:

        predicted_status = "LOW"

    # Estimated propagation time
    if probability >= 70:

        propagation_time = 10

    elif probability >= 40:

        propagation_time = 20

    else:

        propagation_time = 30

    results.append({

        "source_road": current_road,

        "affected_road": road,

        "spread_probability":
            probability,

        "estimated_time_minutes":
            propagation_time,

        "predicted_status":
            predicted_status
    })

# ==============================
# DISPLAY
# ==============================

if len(results) == 0:

    print("\nNo connected road data available.")

else:

    result_df = pd.DataFrame(results)

    print("\nAffected Roads:\n")

    for _, row in result_df.iterrows():

        print(
            f"{row['affected_road']} → "
            f"{row['predicted_status']} "
            f"({row['spread_probability']}%) "
            f"in approximately "
            f"{row['estimated_time_minutes']} minutes"
        )

    # ==============================
    # SAVE RESULT
    # ==============================

    result_df.to_csv(
        "congestion_spread.csv",
        index=False
    )

    print(
        "\nSaved: congestion_spread.csv"
    )

print(
    "\nCongestion spread prediction completed!"
)