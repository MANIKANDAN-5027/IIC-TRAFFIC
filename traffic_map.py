import folium
import pandas as pd

# ==============================
# LOAD TRAFFIC DATA
# ==============================

df = pd.read_csv("traffic_data.csv")

# ==============================
# MAP LOCATION
# ==============================

# Villupuram center
latitude = 11.9401
longitude = 79.4861

traffic_map = folium.Map(
    location=[latitude, longitude],
    zoom_start=13,
    tiles="OpenStreetMap"
)

# ==============================
# TRAFFIC STATUS COLORS
# ==============================

def get_color(status):
    status = str(status).upper()

    if "HIGH" in status:
        return "red"
    elif "MEDIUM" in status:
        return "orange"
    else:
        return "green"


# ==============================
# TRAFFIC MARKER
# ==============================

# Example real traffic points
traffic_points = [
    {
        "name": "Villupuram Bus Stand",
        "lat": 11.9398,
        "lon": 79.4872
    },
    {
        "name": "Villupuram Railway Station",
        "lat": 11.9365,
        "lon": 79.4950
    },
    {
        "name": "Four Roads Junction",
        "lat": 11.9435,
        "lon": 79.4835
    },
    {
        "name": "Gingee Road Junction",
        "lat": 11.9450,
        "lon": 79.4780
    }
]

# Use latest traffic data
latest = df.iloc[-1]

vehicle_count = int(latest["vehicle_count"])
average_speed = float(latest["average_speed"])
traffic_status = str(latest["traffic_status"])

color = get_color(traffic_status)

for point in traffic_points:

    popup_text = f"""
    <b>{point['name']}</b><br>
    Vehicles: {vehicle_count}<br>
    Average Speed: {average_speed:.2f} m/s<br>
    Status: {traffic_status}
    """

    folium.Marker(
        location=[point["lat"], point["lon"]],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=point["name"],
        icon=folium.Icon(
            color=color,
            icon="car",
            prefix="fa"
        )
    ).add_to(traffic_map)


# ==============================
# TITLE
# ==============================

title_html = """
<h3 align="center"
style="font-size:20px">
<b>IIC Traffic AI - Real-Time Traffic Map</b>
</h3>
"""

traffic_map.get_root().html.add_child(
    folium.Element(title_html)
)


# ==============================
# SAVE MAP
# ==============================

traffic_map.save("traffic_map.html")

print("=" * 50)
print("REAL TRAFFIC MAP")
print("=" * 50)
print(f"Vehicles       : {vehicle_count}")
print(f"Average Speed  : {average_speed:.2f} m/s")
print(f"Traffic Status : {traffic_status}")
print()
print("Map saved to: traffic_map.html")
print("=" * 50)