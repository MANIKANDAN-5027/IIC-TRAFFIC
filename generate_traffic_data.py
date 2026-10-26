import pandas as pd
import random
from datetime import datetime, timedelta

roads = [
    "GST Road",
    "OMR Road",
    "Anna Salai",
    "Poonamallee High Road",
    "Mount Road",
    "ECR Road",
    "Velachery Main Road"
]

weather_conditions = ["Clear", "Cloudy", "Rain"]

data = []

start_date = datetime(2026, 1, 1)

for i in range(10000):

    dt = start_date + timedelta(
        minutes=random.randint(0, 365 * 24 * 60)
    )

    hour = dt.hour

    # Peak-hour vehicle generation
    if 7 <= hour <= 9:
        vehicle_count = random.randint(700, 1200)
    elif 17 <= hour <= 20:
        vehicle_count = random.randint(750, 1300)
    else:
        vehicle_count = random.randint(150, 700)

    avg_speed = random.randint(15, 60)
    road_capacity = random.randint(900, 1200)

    weather = random.choice(weather_conditions)

    accident = random.choices([0, 1], weights=[95, 5])[0]
    road_work = random.choices([0, 1], weights=[90, 10])[0]
    event = random.choices([0, 1], weights=[92, 8])[0]

    # Congestion score
    score = (
        (vehicle_count / road_capacity) * 60
        + ((60 - avg_speed) / 60) * 25
        + accident * 10
        + road_work * 5
        + event * 5
    )

    if weather == "Rain":
        score += 5

    score = min(round(score), 100)

    if score < 40:
        congestion_level = "Low"
    elif score < 70:
        congestion_level = "Medium"
    else:
        congestion_level = "High"

    data.append([
        dt.strftime("%Y-%m-%d"),
        dt.strftime("%H:%M"),
        dt.strftime("%A"),
        random.choice(roads),
        vehicle_count,
        avg_speed,
        road_capacity,
        weather,
        accident,
        road_work,
        event,
        congestion_level,
        score
    ])

columns = [
    "date",
    "time",
    "day_of_week",
    "location",
    "vehicle_count",
    "avg_speed",
    "road_capacity",
    "weather",
    "accident",
    "road_work",
    "event",
    "congestion_level",
    "congestion_score"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv("traffic_data.csv", index=False)

print("traffic_data.csv created successfully!")
print("Total records:", len(df))