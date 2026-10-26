import requests
import folium
import webbrowser
import os

# ============================================================
# IIC TRAFFIC AI - ALTERNATIVE ROUTE
# ============================================================

# Example: Villupuram
START = (11.9401, 79.4861)
DESTINATION = (11.9475, 79.4930)

print("=" * 60)
print("       IIC TRAFFIC AI - ROUTE SYSTEM")
print("=" * 60)

# OSRM uses longitude,latitude
start_lon, start_lat = START[1], START[0]
dest_lon, dest_lat = DESTINATION[1], DESTINATION[0]

url = (
    "https://router.project-osrm.org/route/v1/driving/"
    f"{start_lon},{start_lat};"
    f"{dest_lon},{dest_lat}"
)

params = {
    "alternatives": "true",
    "overview": "full",
    "geometries": "geojson"
}

try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

except Exception as e:
    print("\nERROR connecting to routing service:")
    print(e)
    exit()


# ============================================================
# CHECK ROUTE
# ============================================================

if data.get("code") != "Ok" or not data.get("routes"):
    print("\nNo route was found.")
    exit()

routes = data["routes"]

print("\nRoutes found:", len(routes))


# ============================================================
# CREATE MAP
# ============================================================

traffic_map = folium.Map(
    location=START,
    zoom_start=14,
    tiles="OpenStreetMap"
)


# ============================================================
# START MARKER
# ============================================================

folium.Marker(
    START,
    popup="Starting Point",
    tooltip="START",
    icon=folium.Icon(
        color="blue",
        icon="play"
    )
).add_to(traffic_map)


# ============================================================
# DESTINATION MARKER
# ============================================================

folium.Marker(
    DESTINATION,
    popup="Destination",
    tooltip="DESTINATION",
    icon=folium.Icon(
        color="black",
        icon="flag"
    )
).add_to(traffic_map)


# ============================================================
# DRAW ROUTES
# ============================================================

for index, route in enumerate(routes):

    coordinates = route["geometry"]["coordinates"]

    # GeoJSON = longitude, latitude
    points = [
        [coord[1], coord[0]]
        for coord in coordinates
    ]

    distance_km = route["distance"] / 1000
    duration_min = route["duration"] / 60

    if index == 0:

        route_name = "Recommended Route"
        route_color = "blue"

    else:

        route_name = "Alternative Route"
        route_color = "green"

    popup = f"""
    <b>{route_name}</b><br>
    Distance: {distance_km:.2f} km<br>
    Estimated Time: {duration_min:.1f} minutes
    """

    folium.PolyLine(
        points,
        color=route_color,
        weight=6,
        opacity=0.8,
        popup=popup,
        tooltip=route_name
    ).add_to(traffic_map)

    print(
        f"{route_name}: "
        f"{distance_km:.2f} km, "
        f"{duration_min:.1f} minutes"
    )


# ============================================================
# SAVE MAP
# ============================================================

map_file = "alternative_route_map.html"

traffic_map.save(map_file)

print("\nMap saved to:")
print(os.path.abspath(map_file))

print("\nOpening map...")

webbrowser.open(
    "file://" + os.path.abspath(map_file)
)

print("\nRoute system completed successfully.")