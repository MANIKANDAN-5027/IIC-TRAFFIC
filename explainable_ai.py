import pandas as pd

# Load route results
df = pd.read_csv("route_optimization.csv")

# Best route
best = df.sort_values(
    by="traffic_score"
).iloc[0]

print("\n================================")
print("        EXPLAINABLE AI")
print("================================")

print("\n🏆 Recommended Route")
print("------------------------------")

print("Route          :", best["route"])
print("Road           :", best["road"])
print("Traffic Score  :", best["traffic_score"])
print("Traffic Status :", best["traffic_status"])
print("Estimated Delay:", best["estimated_delay"], "minutes")

print("\nWhy was this route selected?")
print("------------------------------")

if best["traffic_status"] == "LOW":
    print("✓ Low traffic congestion")

if best["traffic_score"] < 40:
    print("✓ Low traffic score")

if best["estimated_delay"] < 15:
    print("✓ Lower estimated travel delay")

# Compare with other routes
other_routes = df[
    df["route"] != best["route"]
]

if len(other_routes) > 0:

    average_other_score = (
        other_routes["traffic_score"].mean()
    )

    if best["traffic_score"] < average_other_score:
        print("✓ Lower traffic score than other routes")

    best_delay = best["estimated_delay"]
    average_other_delay = (
        other_routes["estimated_delay"].mean()
    )

    if best_delay < average_other_delay:
        print("✓ Lower estimated delay than other routes")

print("\n================================")
print("        AI DECISION")
print("================================")

print(
    f"AI recommends {best['road']} "
    f"because it has the lowest traffic score "
    f"among the available routes."
)

print("\nExplainable AI completed successfully!")