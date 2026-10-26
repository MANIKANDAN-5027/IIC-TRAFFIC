import traci
import statistics
import csv
from sklearn.cluster import DBSCAN

SUMO_CONFIG = "sumo/simulation.sumocfg"

# Start SUMO
traci.start(["sumo", "-c", SUMO_CONFIG])

# Create CSV file automatically
csv_file = open(
    "traffic_data.csv",
    "w",
    newline=""
)

csv_writer = csv.writer(csv_file)

# CSV column headings
csv_writer.writerow([
    "simulation_time",
    "vehicle_count",
    "average_speed",
    "dbscan_clusters",
    "traffic_status"
])

print("=" * 55)
print("       AI TRAFFIC MONITORING SYSTEM")
print("=" * 55)

try:

    while traci.simulation.getMinExpectedNumber() > 0:

        traci.simulationStep()

        # Get vehicles
        vehicle_ids = traci.vehicle.getIDList()

        speeds = []
        positions = []

        # Get speed and position of every vehicle
        for vehicle_id in vehicle_ids:

            speed = traci.vehicle.getSpeed(vehicle_id)
            position = traci.vehicle.getPosition(vehicle_id)

            speeds.append(speed)
            positions.append(position)

        # Vehicle count
        vehicle_count = len(vehicle_ids)

        # Average speed
        if speeds:
            average_speed = statistics.mean(speeds)
        else:
            average_speed = 0

        # -----------------------------
        # DBSCAN
        # -----------------------------

        if len(positions) >= 2:

            clustering = DBSCAN(
                eps=100,
                min_samples=2
            ).fit(positions)

            labels = clustering.labels_

            dbscan_clusters = len(
                set(labels)
            ) - (1 if -1 in labels else 0)

        else:
            dbscan_clusters = 0

        # -----------------------------
        # TRAFFIC CLASSIFICATION
        # -----------------------------

        if vehicle_count >= 10 and average_speed < 8:

            traffic_status = "HIGH CONGESTION"

        elif vehicle_count >= 5 and average_speed < 11:

            traffic_status = "MEDIUM TRAFFIC"

        else:

            traffic_status = "LOW TRAFFIC"

        # Simulation time
        simulation_time = traci.simulation.getTime()

        # -----------------------------
        # SAVE DATA TO CSV
        # -----------------------------

        csv_writer.writerow([
            simulation_time,
            vehicle_count,
            round(average_speed, 2),
            dbscan_clusters,
            traffic_status
        ])

        # Make sure data is written immediately
        csv_file.flush()

        # -----------------------------
        # DISPLAY
        # -----------------------------

        print("\n" + "-" * 55)

        print(
            f"Simulation Time : "
            f"{simulation_time:.1f} s"
        )

        print(
            f"Vehicles        : "
            f"{vehicle_count}"
        )

        print(
            f"Average Speed   : "
            f"{average_speed:.2f} m/s"
        )

        print(
            f"DBSCAN Clusters : "
            f"{dbscan_clusters}"
        )

        print(
            f"Traffic Status  : "
            f"{traffic_status}"
        )

        print("-" * 55)

finally:

    traci.close()
    csv_file.close()

    print("\nSimulation completed.")
    print("traffic_data.csv created successfully.")