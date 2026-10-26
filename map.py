import folium
import webbrowser
import os

# ==========================================
# REAL TRAFFIC MAP
# ==========================================

# Map center - change these coordinates
LATITUDE = 11.9401
LONGITUDE = 79.4861

# Create real OpenStreetMap
traffic_map = folium.Map(
    location=[LATITUDE, LONGITUDE],
    zoom_start=13,
    tiles="OpenStreetMap"
)

# ==========================================
# TRAFFIC LOCATIONS
# ==========================================

traffic_points = [
    {
        "name": "Traffic Point 1",
        "lat": LATITUDE + 0.005,
        "lon": LONGITUDE + 0.005,
        "vehicles": 7,
        "speed": 12.5
    },
    {
        "name": "Traffic Point 2",
        "lat": LATITUDE - 0.004,
        "lon": LONGITUDE + 0.008,
        "vehicles": 5,
        "speed": 10.2
    },
    {
        "name": "Traffic Point 3",
        "lat": LATITUDE + 0.008,
        "lon": LONGITUDE - 0.005,
        "vehicles": 3,
        "speed": 14.8
    }
]

# ==========================================
# ADD TRAFFIC MARKERS
# ==========================================

for point in traffic_points:

    vehicles = point["vehicles"]

    if vehicles >= 7:
        status = "HIGH TRAFFIC"
        icon_color = "red"

    elif vehicles >= 4:
        status = "MEDIUM TRAFFIC"
        icon_color = "orange"

    else:
        status = "LOW TRAFFIC"
        icon_color = "green"

    popup_text = f"""
    <b>{point['name']}</b><br>
    Vehicles: {vehicles}<br>
    Average Speed: {point['speed']} m/s<br>
    Status: {status}
    """

    folium.Marker(
        location=[point["lat"], point["lon"]],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=status,
        icon=folium.Icon(
            color=icon_color,
            icon="car",
            prefix="fa"
        )
    ).add_to(traffic_map)


# ==========================================
# SAVE MAP
# ==========================================

map_file = "traffic_map.html"

traffic_map.save(map_file)

print("=" * 40)
print("       REAL TRAFFIC MAP")
print("=" * 40)
print()
print("Map created successfully!")
print("Map file:", os.path.abspath(map_file))
print()
print("Opening map in browser...")
print("=" * 40)

webbrowser.open(
    "file://" + os.path.abspath(map_file)
)