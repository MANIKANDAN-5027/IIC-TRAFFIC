import os
import pandas as pd
import random

random.seed(42)

OUTPUT_FOLDER = "district_data"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


districts = [
    "Ariyalur",
    "Chengalpattu",
    "Chennai",
    "Coimbatore",
    "Cuddalore",
    "Dharmapuri",
    "Dindigul",
    "Erode",
    "Kallakurichi",
    "Kancheepuram",
    "Karur",
    "Krishnagiri",
    "Madurai",
    "Mayiladuthurai",
    "Nagapattinam",
    "Namakkal",
    "Nilgiris",
    "Perambalur",
    "Pudukkottai",
    "Ramanathapuram",
    "Ranipet",
    "Salem",
    "Sivaganga",
    "Tenkasi",
    "Thanjavur",
    "Theni",
    "Thoothukudi",
    "Tiruchirappalli",
    "Tirunelveli",
    "Tirupathur",
    "Tiruppur",
    "Tiruvallur",
    "Tiruvarur",
    "Vellore",
    "Viluppuram",
    "Virudhunagar",
    "Kanyakumari"
]


road_names = [
    "Main Road",
    "NH Road",
    "Bus Stand Road",
    "Market Road",
    "Bypass Road",
    "Ring Road",
    "Town Road",
    "Highway Road"
]


weather_list = [
    "Clear",
    "Cloudy",
    "Rain",
    "Normal"
]


def traffic_level(score):

    if score < 35:
        return "LOW"

    elif score < 70:
        return "MEDIUM"

    else:
        return "HIGH"


for district in districts:

    records = []

    for i in range(100):

        vehicle_count = random.randint(100, 1000)

        avg_speed = random.randint(15, 70)

        accident = random.choice([0, 0, 0, 1])

        road_work = random.choice([0, 0, 0, 1])

        event = random.choice([0, 0, 0, 1])

        score = round(
            (
                vehicle_count / 1000 * 45
                +
                (70 - avg_speed) / 70 * 30
                +
                accident * 10
                +
                road_work * 5
                +
                event * 10
            ),
            2
        )

        score = min(score, 100)

        records.append({

            "district": district,

            "location":
                f"{district} {random.choice(road_names)}",

            "road":
                random.choice(road_names),

            "vehicle_count":
                vehicle_count,

            "avg_speed":
                avg_speed,

            "weather":
                random.choice(weather_list),

            "accident":
                accident,

            "road_work":
                road_work,

            "event":
                event,

            "congestion_score":
                score,

            "congestion_level":
                traffic_level(score)

        })

    df = pd.DataFrame(records)

    filename = os.path.join(
        OUTPUT_FOLDER,
        district + ".csv"
    )

    df.to_csv(
        filename,
        index=False
    )

    print(
        f"Created: {filename}"
    )


print()
print("======================================")
print("38 DISTRICT CSV FILES CREATED")
print("======================================")