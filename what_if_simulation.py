import pandas as pd

# ==============================
# LOAD DATA
# ==============================

df = pd.read_csv("traffic_data.csv")

# ==============================
# USER SCENARIO
# ==============================

road = "GST Road"

block_duration = 30

print("\n================================")
print("      WHAT-IF TRAFFIC SIMULATION")
print("================================")

print("Road              :", road)
print("Block Duration    :", block_duration, "minutes")

# ==============================
# GET CURRENT ROAD DATA
# ==============================

road_data = df[df["location"] == road]

if len(road_data) == 0:
    print("Road not found!")
    exit()

current = road_data.iloc[-1]

current_vehicles = int(current["vehicle_count"])
road_capacity = int(current["road_capacity"])

# ==============================
# CONNECTED ROADS
# ==============================

connections = {
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

affected_roads = connections.get(road, [])

# ==============================
# SIMULATION
# ==============================

results = []

for affected_road in affected_roads:

    road_data = df[
        df["location"] == affected_road
    ]

    if len(road_data) == 0:
        continue

    latest = road_data.iloc[-1]

    normal_vehicles = int(
        latest["vehicle_count"]
    )

    capacity = int(
        latest["road_capacity"]
    )

    # Traffic redirected because of road closure
    redirected_traffic = int(
        current_vehicles * 0.20
    )

    simulated_vehicles = (
        normal_vehicles + redirected_traffic
    )

    increase_percent = (
        (simulated_vehicles - normal_vehicles)
        / normal_vehicles
    ) * 100

    # Congestion calculation
    ratio = simulated_vehicles / capacity

    if ratio >= 0.80:
        status = "HIGH"

    elif ratio >= 0.50:
        status = "MEDIUM"

    else:
        status = "LOW"

    # Estimated delay
    delay = round(
        increase_percent * 0.30,
        1
    )

    results.append({
        "blocked_road": road,
        "affected_road": affected_road,
        "normal_vehicles": normal_vehicles,
        "simulated_vehicles": simulated_vehicles,
        "traffic_increase_percent": round(
            increase_percent, 2
        ),
        "congestion_level": status,
        "estimated_delay_minutes": delay,
        "block_duration_minutes": block_duration
    })

# ==============================
# DISPLAY
# ==============================

if not results:

    print("\nNo affected road data available.")

else:

    result_df = pd.DataFrame(results)

    print("\nSimulation Results:\n")

    for _, row in result_df.iterrows():

        print(
            f"{row['affected_road']} → "
            f"{row['congestion_level']} | "
            f"Vehicles: {row['simulated_vehicles']} | "
            f"Increase: {row['traffic_increase_percent']}% | "
            f"Delay: {row['estimated_delay_minutes']} min"
        )

    # ==============================
    # FIND BEST ALTERNATIVE
    # ==============================

    low_roads = result_df[
        result_df["congestion_level"] == "LOW"
    ]

    if len(low_roads) > 0:

        best_route = low_roads.sort_values(
            by="simulated_vehicles"
        ).iloc[0]

    else:

        best_route = result_df.sort_values(
            by="simulated_vehicles"
        ).iloc[0]

    print("\n================================")
    print("       BEST ALTERNATIVE")
    print("================================")

    print(
        "Recommended Road :",
        best_route["affected_road"]
    )

    print(
        "Traffic Level     :",
        best_route["congestion_level"]
    )

    print(
        "Simulated Vehicles:",
        best_route["simulated_vehicles"]
    )

    # ==============================
    # SAVE
    # ==============================

    result_df.to_csv(
        "what_if_result.csv",
        index=False
    )

    print("\nSaved: what_if_result.csv")

print("\nWhat-If simulation completed successfully!")