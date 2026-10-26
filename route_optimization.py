import pandas as pd

# ==============================
# LOAD DATA
# ==============================

df = pd.read_csv("traffic_data.csv")

print("\n================================")
print("       AI ROUTE OPTIMIZATION")
print("================================")

# ==============================
# ROUTE OPTIONS
# ==============================

routes = {
    "Route A": ["GST Road"],
    "Route B": ["Mount Road"],
    "Route C": ["Velachery Main Road"],
    "Route D": ["OMR Road"]
}

results = []

# ==============================
# CALCULATE ROUTE SCORE
# ==============================

for route_name, roads in routes.items():

    total_score = 0
    total_vehicles = 0
    total_speed = 0
    count = 0

    for road in roads:

        road_data = df[
            df["location"] == road
        ]

        if len(road_data) == 0:
            continue

        latest = road_data.iloc[-1]

        vehicles = float(
            latest["vehicle_count"]
        )

        speed = float(
            latest["avg_speed"]
        )

        capacity = float(
            latest["road_capacity"]
        )

        # Traffic ratio
        traffic_ratio = (
            vehicles / capacity
        )

        # Traffic score: 0 = best, 100 = worst
        traffic_score = (
            traffic_ratio * 70
            + ((60 - speed) / 60) * 30
        )

        traffic_score = min(
            round(traffic_score, 2),
            100
        )

        total_score += traffic_score
        total_vehicles += vehicles
        total_speed += speed
        count += 1

    if count == 0:
        continue

    average_score = total_score / count
    average_speed = total_speed / count

    # Estimated delay
    delay = round(
        average_score * 0.35,
        2
    )

    # Route status
    if average_score >= 70:
        status = "HIGH"

    elif average_score >= 40:
        status = "MEDIUM"

    else:
        status = "LOW"

    results.append({

        "route": route_name,

        "road": ", ".join(roads),

        "traffic_score":
            round(average_score, 2),

        "vehicle_count":
            int(total_vehicles),

        "average_speed":
            round(average_speed, 2),

        "estimated_delay":
            delay,

        "traffic_status":
            status
    })

# ==============================
# CREATE RESULT
# ==============================

result_df = pd.DataFrame(results)

# Best route = lowest traffic score
best_route = result_df.sort_values(
    by="traffic_score"
).iloc[0]

# ==============================
# DISPLAY
# ==============================

print("\nRoute Analysis:\n")

for _, row in result_df.iterrows():

    print(
        f"{row['route']} | "
        f"{row['road']} | "
        f"Score: {row['traffic_score']} | "
        f"Traffic: {row['traffic_status']} | "
        f"Delay: {row['estimated_delay']} min"
    )

print("\n================================")
print("         BEST ROUTE")
print("================================")

print(
    "Recommended Route :",
    best_route["route"]
)

print(
    "Road               :",
    best_route["road"]
)

print(
    "Traffic Score      :",
    best_route["traffic_score"]
)

print(
    "Traffic Status     :",
    best_route["traffic_status"]
)

print(
    "Estimated Delay    :",
    best_route["estimated_delay"],
    "minutes"
)

# ==============================
# SAVE RESULT
# ==============================

result_df.to_csv(
    "route_optimization.csv",
    index=False
)

print("\nSaved: route_optimization.csv")
print("\nAI route optimization completed successfully!")