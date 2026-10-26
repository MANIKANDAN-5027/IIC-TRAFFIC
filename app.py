from flask import Flask, jsonify, send_from_directory, request
import pandas as pd
import os
import requests

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

HEADERS = {
    "User-Agent": "IIC-Traffic-AI/1.0"
}

ROUTE_NAMES = [
    "Route A", "Route B", "Route C", "Route D",
    "Route E", "Route F", "Route G", "Route H"
]

ROUTE_COLOURS = [
    "#2563eb",
    "#16a34a",
    "#f59e0b",
    "#dc2626",
    "#7c3aed",
    "#0891b2",
    "#db2777",
    "#65a30d"
]


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return send_from_directory(
        os.path.join(BASE_DIR, "templates"),
        "index.html"
    )


# =========================================================
# GEOCODING
# =========================================================

@app.route("/api/geocode")
def geocode():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "error": "Location is empty"
        }), 400

    try:

        params = {
            "q": query + ", Tamil Nadu, India",
            "format": "json",
            "limit": 5,
            "countrycodes": "in",
            "addressdetails": 1
        }

        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        results = []

        for item in response.json():

            results.append({
                "display_name": item.get(
                    "display_name",
                    ""
                ),
                "lat": float(item["lat"]),
                "lon": float(item["lon"])
            })

        return jsonify(results)

    except Exception as e:

        return jsonify({
            "error": "Geocoding failed",
            "message": str(e)
        }), 500


def geocode_place(place):

    params = {
        "q": place + ", Tamil Nadu, India",
        "format": "json",
        "limit": 1,
        "countrycodes": "in"
    }

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    return {
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
        "display_name": data[0].get(
            "display_name",
            place
        )
    }


# =========================================================
# LOCATION SEARCH
# =========================================================

@app.route("/api/search-locations")
def search_locations():
    """Search every location CSV under the project, including village data."""
    q = request.args.get("q", "").strip().lower()
    if not q:
        return jsonify([])

    results = []
    seen = set()

    # Search the known files first, then recursively search additional CSVs
    # such as district_data/*.csv when they exist in the user's project.
    candidate_files = [
        ("district", os.path.join(BASE_DIR, "district_routes.csv")),
        ("taluk", os.path.join(BASE_DIR, "taluk_routes.csv")),
        ("village", os.path.join(BASE_DIR, "village_routes.csv"))
    ]

    for root, _, filenames in os.walk(BASE_DIR):
        for filename in filenames:
            if not filename.lower().endswith(".csv"):
                continue
            full = os.path.join(root, filename)
            if full not in [item[1] for item in candidate_files]:
                level = "village" if "village" in filename.lower() or "district_data" in root.lower() else "location"
                candidate_files.append((level, full))

    for level, file in candidate_files:
        if not os.path.exists(file):
            continue

        try:
            df = pd.read_csv(file)
            if df.empty:
                continue

            for col in ["district", "taluk", "village", "location", "lat", "lon"]:
                if col not in df.columns:
                    df[col] = ""

            text_columns = ["district", "taluk", "village", "location"]
            mask = pd.Series(False, index=df.index)
            for col in text_columns:
                mask = mask | df[col].fillna("").astype(str).str.lower().str.contains(q, regex=False)

            for _, row in df[mask].head(50).iterrows():
                location = str(row.get("location", "")).strip()
                village = str(row.get("village", "")).strip()
                taluk = str(row.get("taluk", "")).strip()
                district = str(row.get("district", "")).strip()

                name = location or village or taluk or district
                if not name or name.lower() in {"nan", "none"}:
                    continue

                try:
                    lat = float(row["lat"]) if pd.notna(row.get("lat")) and str(row.get("lat")).strip() else None
                except Exception:
                    lat = None
                try:
                    lon = float(row["lon"]) if pd.notna(row.get("lon")) and str(row.get("lon")).strip() else None
                except Exception:
                    lon = None

                key = (name.lower(), lat, lon)
                if key in seen:
                    continue
                seen.add(key)

                results.append({
                    "level": level,
                    "location": name,
                    "district": district,
                    "taluk": taluk,
                    "village": village,
                    "lat": lat,
                    "lon": lon,
                    "source_file": os.path.relpath(file, BASE_DIR)
                })

                if len(results) >= 100:
                    return jsonify(results)

        except Exception:
            continue

    return jsonify(results)


# =========================================================
# ROUTING + VEHICLE-SPECIFIC TRAFFIC ANALYSIS
# =========================================================

@app.route("/api/route")
def calculate_route():
    """Return multiple real road-network route candidates.

    OSRM's public alternatives option often returns only one or two routes.
    To make the dashboard useful for route comparison, we also request
    several real road paths through different geographic corridor points.
    These are still OSRM road routes; no artificial straight-line route is
    drawn. The returned candidates are de-duplicated before AI ranking.
    """

    from_lat = request.args.get("from_lat")
    from_lon = request.args.get("from_lon")
    to_lat = request.args.get("to_lat")
    to_lon = request.args.get("to_lon")
    from_name = request.args.get("from", "").strip()
    to_name = request.args.get("to", "").strip()
    vehicle_type = request.args.get("vehicle", "car").strip().lower()

    if vehicle_type not in {"bike", "car", "heavy"}:
        vehicle_type = "car"

    if not all([from_lat, from_lon, to_lat, to_lon]):
        if not from_name or not to_name:
            return jsonify({"error": "From and To locations are required"}), 400
        try:
            from_result = geocode_place(from_name)
            to_result = geocode_place(to_name)
            if not from_result:
                return jsonify({"error": "From location not found"}), 404
            if not to_result:
                return jsonify({"error": "To location not found"}), 404
            from_lat, from_lon = from_result["lat"], from_result["lon"]
            to_lat, to_lon = to_result["lat"], to_result["lon"]
        except Exception as e:
            return jsonify({"error": "Location search failed", "message": str(e)}), 500

    try:
        from_lat, from_lon = float(from_lat), float(from_lon)
        to_lat, to_lon = float(to_lat), float(to_lon)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid coordinates"}), 400

    try:
        route_objects = get_route_candidates(
            from_lat, from_lon, to_lat, to_lon
        )
        if not route_objects:
            return jsonify({"error": "No route found"}), 404

        traffic_df = load_traffic_dataframe()
        results = []
        seen = set()

        for raw_index, route in enumerate(route_objects):
            geometry = route.get("geometry") or {}
            coords = geometry.get("coordinates") or []
            if len(coords) < 2:
                continue

            # Geometry fingerprint removes duplicate OSRM alternatives.
            fingerprint = geometry_fingerprint(coords)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)

            distance_km = float(route.get("distance", 0)) / 1000.0
            duration_min = float(route.get("duration", 0)) / 60.0
            road_name = get_main_road_name(route)
            traffic = get_road_traffic_context(
                traffic_df, road_name, raw_index
            )

            score = calculate_vehicle_route_score(
                duration_min=duration_min,
                traffic_score=traffic["traffic_score"],
                vehicle_type=vehicle_type,
                vehicle_count=traffic["vehicle_count"],
                road_capacity=traffic["road_capacity"],
                accident=traffic["accident"],
                road_work=traffic["road_work"],
                event=traffic["event"]
            )

            results.append({
                "route": f"Route {len(results) + 1}",
                "route_index": len(results),
                "road": road_name,
                "distance": round(distance_km, 2),
                "duration": round(duration_min, 2),
                "traffic_score": round(score, 2),
                "traffic_status": get_traffic_status(score),
                "colour": get_route_colour(get_traffic_status(score)),
                "geometry": geometry,
                "vehicle_type": vehicle_type,
                "vehicle_count": traffic["vehicle_count"],
                "average_speed": traffic["average_speed"],
                "road_capacity": traffic["road_capacity"],
                "congestion_score": traffic["traffic_score"],
                "accident": traffic["accident"],
                "road_work": traffic["road_work"],
                "event": traffic["event"],
                "traffic_source": traffic["source"]
            })

        if not results:
            return jsonify({"error": "No usable routes returned by routing engine"}), 404

        ranked_routes = sorted(results, key=lambda item: item["traffic_score"])
        for rank, item in enumerate(ranked_routes, start=1):
            item["rank"] = rank
            item["recommended"] = rank == 1

        return jsonify({
            "success": True,
            "vehicle_type": vehicle_type,
            "vehicle_label": vehicle_label(vehicle_type),
            "from": {"name": from_name, "lat": from_lat, "lon": from_lon},
            "to": {"name": to_name, "lat": to_lat, "lon": to_lon},
            "routes": ranked_routes,
            "best_route": ranked_routes[0],
            "route_count": len(ranked_routes),
            "route_note": (
                "Routes are real road-network paths returned by OSRM. "
                "Additional corridor routes are requested to expose more alternatives; "
                "the public routing service cannot guarantee every possible road path."
            )
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Routing server connection failed",
            "message": str(e)
        }), 502
    except Exception as e:
        return jsonify({
            "error": "Route calculation failed",
            "message": str(e)
        }), 500



def get_route_candidates(from_lat, from_lon, to_lat, to_lon):
    """Generate a larger set of DISTINCT real road-network candidates.

    OSRM's public alternatives flag does not mean "return every possible
    route". It normally returns only a small number of alternatives.

    To expose more useful alternatives, we make several routing requests
    through different geographic corridor points. OSRM snaps those points to
    its road network, so every returned path is still a real routed road path
    rather than a straight line drawn by the application.

    The function returns up to MAX_ROUTE_CANDIDATES distinct paths. The exact
    number depends on the road network and what the public OSRM service can
    return for the requested origin/destination.
    """
    MAX_ROUTE_CANDIDATES = 20

    # Direct route + OSRM-native alternatives.
    requests_to_make = [[]]

    # Build many diverse corridor waypoint sets. We intentionally keep this
    # finite: "all mathematical paths" in a road graph can be enormous.
    requests_to_make.extend(
        build_corridor_waypoints(from_lat, from_lon, to_lat, to_lon)
    )

    candidates = []

    for waypoints in requests_to_make:
        try:
            routes = request_osrm_route(
                from_lat, from_lon, to_lat, to_lon, waypoints
            )
            candidates.extend(routes)
        except requests.exceptions.RequestException:
            # A failed candidate must not stop the remaining route search.
            continue
        except Exception:
            continue

        # Stop making more public-service requests once enough unique routes
        # have been collected.
        unique_now = unique_routes(candidates)
        if len(unique_now) >= MAX_ROUTE_CANDIDATES:
            return unique_now[:MAX_ROUTE_CANDIDATES]

    return unique_routes(candidates)[:MAX_ROUTE_CANDIDATES]


def request_osrm_route(from_lat, from_lon, to_lat, to_lon, waypoints):
    points = [(from_lon, from_lat)]
    points.extend(waypoints)
    points.append((to_lon, to_lat))

    coordinates = ";".join(
        f"{lon:.6f},{lat:.6f}" for lon, lat in points
    )

    url = f"{OSRM_URL}/{coordinates}"

    params = {
        # OSRM's native alternatives are useful in addition to our corridor
        # requests. It still does NOT promise every possible route.
        "alternatives": "true",
        "steps": "true",
        "overview": "full",
        "geometries": "geojson",
        "continue_straight": "false"
    }

    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=25
    )
    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        return []

    return data.get("routes", [])


def build_corridor_waypoints(from_lat, from_lon, to_lat, to_lon):
    """Create diverse intermediate points for real road-network detours.

    The points are only routing constraints. They are NOT drawn directly on
    the map. OSRM snaps/routs through them and returns the actual road geometry.

    More corridor patterns means more chances of finding genuinely different
    roads around Chennai/Tamil Nadu's dense network.
    """
    import math

    mid_lat = math.radians((from_lat + to_lat) / 2.0)

    lon_scale = 111.32 * max(math.cos(mid_lat), 0.2)
    lat_scale = 110.57

    dx_km = (to_lon - from_lon) * lon_scale
    dy_km = (to_lat - from_lat) * lat_scale
    length = math.hypot(dx_km, dy_km)

    if length < 1.0:
        return []

    ux = dx_km / length
    uy = dy_km / length

    # Perpendicular vector to the direct origin->destination direction.
    px = -uy
    py = ux

    def point_at(fraction, offset_km):
        x = dx_km * fraction + px * offset_km
        y = dy_km * fraction + py * offset_km

        lat = from_lat + y / lat_scale
        lon = from_lon + x / lon_scale

        return (lon, lat)

    # For short trips, large offsets can force very odd routes. Scale the
    # maximum detour with trip length.
    max_offset = max(1.5, min(14.0, length * 0.45))

    offsets = [
        1.5,
        -1.5,
        3.0,
        -3.0,
        5.0,
        -5.0,
        7.0,
        -7.0,
        10.0,
        -10.0,
    ]

    offsets = [
        max(-max_offset, min(max_offset, value))
        for value in offsets
    ]

    waypoint_sets = []

    # One-point corridors.
    for offset in offsets:
        waypoint_sets.append([
            point_at(0.50, offset)
        ])

    # Two-point same-side corridors.
    for offset in [3.0, -3.0, 6.0, -6.0, 9.0, -9.0]:
        offset = max(-max_offset, min(max_offset, offset))
        waypoint_sets.append([
            point_at(0.28, offset),
            point_at(0.72, offset)
        ])

    # Two-point cross-over corridors. These often produce different urban
    # road choices than a single symmetric detour.
    cross = [
        (4.0, -4.0),
        (-4.0, 4.0),
        (7.0, -5.0),
        (-7.0, 5.0),
    ]

    for first, second in cross:
        first = max(-max_offset, min(max_offset, first))
        second = max(-max_offset, min(max_offset, second))

        waypoint_sets.append([
            point_at(0.30, first),
            point_at(0.70, second)
        ])

    # Three-point broad corridors for longer trips. These are especially useful
    # when a direct line crosses a lake, airport, restricted area, etc.
    if length >= 8:
        for offset in [5.0, -5.0, 9.0, -9.0]:
            offset = max(-max_offset, min(max_offset, offset))
            waypoint_sets.append([
                point_at(0.22, offset),
                point_at(0.50, offset * 1.15),
                point_at(0.78, offset * 0.75)
            ])

    # Remove duplicate waypoint sets.
    unique = []
    seen = set()

    for waypoints in waypoint_sets:
        key = tuple(
            (round(lon, 4), round(lat, 4))
            for lon, lat in waypoints
        )

        if key not in seen:
            seen.add(key)
            unique.append(waypoints)

    return unique


def unique_routes(routes):
    """Return distinct route geometries while preserving first-seen order."""
    unique = []
    seen = set()

    for route in routes:
        coords = (route.get("geometry") or {}).get("coordinates") or []
        fingerprint = geometry_fingerprint(coords)

        if not fingerprint:
            continue

        if fingerprint in seen:
            continue

        seen.add(fingerprint)
        unique.append(route)

    return unique


def geometry_fingerprint(coords):
    if not coords:
        return ""
    # Sampling makes the fingerprint stable without storing the entire path.
    sample = coords[::max(1, len(coords) // 20)]
    if coords[-1] not in sample:
        sample.append(coords[-1])
    return "|".join(
        f"{round(float(p[0]), 4)},{round(float(p[1]), 4)}"
        for p in sample
        if len(p) >= 2
    )


def load_traffic_dataframe():
    """Load the CSV traffic dataset safely."""
    file = os.path.join(BASE_DIR, "traffic_data.csv")
    if not os.path.exists(file):
        return pd.DataFrame()

    try:
        return pd.read_csv(file)
    except Exception as e:
        print("traffic_data.csv:", e)
        return pd.DataFrame()


def get_road_traffic_context(df, road_name, route_index=0):
    """Find the closest CSV traffic record for the route's main road.

    If a road is not present in the CSV, a neutral fallback is returned.
    This keeps routing functional for village roads that are only present
    in the map network.
    """
    defaults = {
        "vehicle_count": 0,
        "average_speed": 40.0,
        "road_capacity": 1000.0,
        "traffic_score": 30.0,
        "accident": 0,
        "road_work": 0,
        "event": 0,
        "source": "default routing context"
    }

    if df.empty or not road_name:
        return defaults

    work = df.copy()
    for col in [
        "location", "vehicle_count", "avg_speed", "road_capacity",
        "congestion_score", "accident", "road_work", "event"
    ]:
        if col not in work.columns:
            if col == "location":
                work[col] = ""
            else:
                work[col] = 0

    locations = work["location"].fillna("").astype(str)
    road = str(road_name).strip().lower()

    # Exact road match first.
    mask = locations.str.strip().str.lower() == road
    matches = work[mask]

    # Then partial match, e.g. "GST Road" inside a longer road label.
    if matches.empty:
        mask = locations.str.lower().str.contains(road, regex=False)
        matches = work[mask]

    if matches.empty:
        # Try road tokens to handle labels such as "GST Road, Chennai".
        tokens = [token for token in road.split() if len(token) > 2]
        if tokens:
            token_mask = locations.str.lower().apply(
                lambda value: sum(token in value for token in tokens) >= max(1, len(tokens) // 2)
            )
            matches = work[token_mask]

    if matches.empty:
        return defaults

    # Latest row is the best available CSV snapshot for that road.
    row = matches.iloc[-1]

    return {
        "vehicle_count": safe_int(row.get("vehicle_count")),
        "average_speed": safe_float(row.get("avg_speed")) or 40.0,
        "road_capacity": safe_float(row.get("road_capacity")) or 1000.0,
        "traffic_score": safe_float(row.get("congestion_score")) or 0.0,
        "accident": safe_int(row.get("accident")),
        "road_work": safe_int(row.get("road_work")),
        "event": safe_int(row.get("event")),
        "source": "traffic_data.csv"
    }


def vehicle_label(vehicle_type):
    return {
        "bike": "Bike",
        "car": "Car",
        "heavy": "Heavy Vehicle"
    }.get(vehicle_type, "Car")


def get_vehicle_factor(vehicle_type):
    # Higher factor means that congestion/road conditions affect that
    # vehicle category more strongly in the AI ranking.
    return {
        "bike": 0.85,
        "car": 1.00,
        "heavy": 1.25
    }.get(vehicle_type, 1.00)


def calculate_vehicle_route_score(
    duration_min,
    traffic_score,
    vehicle_type,
    vehicle_count,
    road_capacity,
    accident,
    road_work,
    event
):
    """Transparent route score from 0-100.

    The score is based on route travel time plus the CSV's traffic score,
    capacity utilization, incident flags and vehicle category impact.
    """
    factor = get_vehicle_factor(vehicle_type)

    duration_component = min(duration_min * 1.15, 45.0)
    csv_component = min(max(traffic_score, 0) * 0.45, 35.0)

    capacity = max(road_capacity, 1.0)
    utilization = max(vehicle_count, 0) / capacity
    density_component = min(utilization * 18.0, 18.0)

    incident_component = (
        accident * 14.0 +
        road_work * 8.0 +
        event * 5.0
    )

    score = (
        duration_component +
        csv_component * factor +
        density_component * factor +
        incident_component * factor
    )

    return min(max(score, 0.0), 100.0)


def get_traffic_status(score):
    if score <= 30:
        return "LOW"
    if score <= 60:
        return "MEDIUM"
    return "HIGH"


def get_route_colour(status):
    return {
        "LOW": "#16a34a",
        "MEDIUM": "#f59e0b",
        "HIGH": "#dc2626"
    }.get(str(status).upper(), "#6b7280")


def get_main_road_name(route):
    try:
        roads = []
        for leg in route.get("legs", []):
            for step in leg.get("steps", []):
                name = step.get("name", "")
                if name:
                    roads.append(name)

        if roads:
            # Prefer the first named road; OSRM may contain several steps.
            return roads[0]
    except Exception:
        pass

    return "Alternative Road"


# =========================================================
# VEHICLE CATEGORY MONITORING
# =========================================================

@app.route("/api/vehicle-monitor")
def vehicle_monitor():
    """Return vehicle category estimates from the existing CSV.

    If bike/car/heavy columns exist in a future CSV, they are used directly.
    Otherwise the existing vehicle_count is split into transparent estimated
    categories. This does not claim to be live GPS data.
    """
    df = load_traffic_dataframe()

    if df.empty:
        return jsonify({
            "error": "traffic_data.csv not found or empty"
        }), 404

    row = df.iloc[-1]
    total = safe_int(row.get("vehicle_count"))

    has_categories = all(
        column in df.columns
        for column in ["bike_count", "car_count", "heavy_vehicle_count"]
    )

    if has_categories:
        bike = safe_int(row.get("bike_count"))
        car = safe_int(row.get("car_count"))
        heavy = safe_int(row.get("heavy_vehicle_count"))
        source = "CSV vehicle category columns"
    else:
        # Transparent fallback because the current CSV has only vehicle_count.
        bike = round(total * 0.35)
        car = round(total * 0.50)
        heavy = max(total - bike - car, 0)
        source = "Estimated from vehicle_count; add category columns for measured counts"

    total_categories = bike + car + heavy
    if total_categories > 0:
        density = min((total_categories / max(safe_float(row.get("road_capacity")) or 1000, 1)) * 100, 100)
    else:
        density = 0

    congestion_score = safe_float(row.get("congestion_score")) or 0

    return jsonify({
        "location": str(row.get("location", "")),
        "date": str(row.get("date", "")),
        "time": str(row.get("time", "")),
        "vehicle_type_options": ["bike", "car", "heavy"],
        "bike_count": bike,
        "car_count": car,
        "heavy_vehicle_count": heavy,
        "total_vehicle_count": total_categories,
        "road_capacity": safe_int(row.get("road_capacity")),
        "traffic_density": round(density, 2),
        "congestion_score": round(congestion_score, 2),
        "congestion_level": str(row.get("congestion_level", get_traffic_status(congestion_score))),
        "source": source,
        "live": False,
        "note": "CSV-based monitoring; not live GPS telemetry."
    })


# =========================================================
# CURRENT TRAFFIC
# =========================================================


# =========================================================

@app.route("/api/current")
def current_traffic():

    file = os.path.join(
        BASE_DIR,
        "traffic_data.csv"
    )

    if not os.path.exists(file):

        return jsonify({
            "error":
                "traffic_data.csv not found"
        }), 404

    try:

        df = pd.read_csv(file)

        row = df.iloc[-1]

        return jsonify({

            "location":
                str(
                    row.get(
                        "location",
                        "Traffic Area"
                    )
                ),

            "vehicle_count":
                safe_int(
                    row.get(
                        "vehicle_count"
                    )
                ),

            "speed":
                safe_float(
                    row.get(
                        "avg_speed"
                    )
                ) or 0,

            "weather":
                str(
                    row.get(
                        "weather",
                        "Unknown"
                    )
                ),

            "accident":
                safe_int(
                    row.get(
                        "accident"
                    )
                ),

            "road_work":
                safe_int(
                    row.get(
                        "road_work"
                    )
                ),

            "event":
                safe_int(
                    row.get(
                        "event"
                    )
                ),

            "traffic_level":
                str(
                    row.get(
                        "congestion_level",
                        "Unknown"
                    )
                ),

            "score":
                safe_float(
                    row.get(
                        "congestion_score"
                    )
                ) or 0,

            "lat":
                safe_float(
                    row.get("lat")
                ),

            "lon":
                safe_float(
                    row.get("lon")
                )
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# TRAFFIC ALERTS
# =========================================================

@app.route("/api/alerts")
def traffic_alerts():

    file = os.path.join(
        BASE_DIR,
        "traffic_data.csv"
    )

    if not os.path.exists(file):

        return jsonify({

            "location":
                "Traffic Area",

            "alert_count":
                0,

            "alerts": [{

                "type":
                    "INFO",

                "severity":
                    "warning",

                "title":
                    "Traffic data unavailable",

                "message":
                    "traffic_data.csv was not found.",

                "lat":
                    None,

                "lon":
                    None
            }]
        })

    try:

        df = pd.read_csv(file)

        row = df.iloc[-1]

        location = str(
            row.get(
                "location",
                "Traffic Area"
            )
        )

        accident = safe_int(
            row.get(
                "accident"
            )
        )

        road_work = safe_int(
            row.get(
                "road_work"
            )
        )

        event = safe_int(
            row.get(
                "event"
            )
        )

        score = (
            safe_float(
                row.get(
                    "congestion_score"
                )
            )
            or 0
        )

        level = str(
            row.get(
                "congestion_level",
                ""
            )
        ).upper()

        lat = safe_float(
            row.get("lat")
        )

        lon = safe_float(
            row.get("lon")
        )

        alerts = []

        if accident > 0:

            alerts.append({

                "type":
                    "ACCIDENT",

                "severity":
                    "danger",

                "title":
                    "Accident reported",

                "message":
                    f"Possible accident reported near {location}. Drive carefully.",

                "lat":
                    lat,

                "lon":
                    lon
            })

        if road_work > 0:

            alerts.append({

                "type":
                    "ROAD_WORK",

                "severity":
                    "warning",

                "title":
                    "Road work detected",

                "message":
                    f"Road work may cause delay near {location}.",

                "lat":
                    lat,

                "lon":
                    lon
            })

        if event > 0:

            alerts.append({

                "type":
                    "EVENT",

                "severity":
                    "warning",

                "title":
                    "Event-related traffic",

                "message":
                    f"An event may increase traffic near {location}.",

                "lat":
                    lat,

                "lon":
                    lon
            })

        if (
            level == "HIGH"
            or score >= 60
        ):

            alerts.append({

                "type":
                    "HEAVY_TRAFFIC",

                "severity":
                    "danger",

                "title":
                    "Heavy traffic ahead",

                "message":
                    f"High congestion detected near {location}. Consider an alternative route.",

                "lat":
                    lat,

                "lon":
                    lon
            })

        elif (
            level == "MEDIUM"
            or score >= 30
        ):

            alerts.append({

                "type":
                    "MODERATE_TRAFFIC",

                "severity":
                    "warning",

                "title":
                    "Moderate traffic",

                "message":
                    f"Moderate congestion detected near {location}.",

                "lat":
                    lat,

                "lon":
                    lon
            })

        if not alerts:

            alerts.append({

                "type":
                    "CLEAR",

                "severity":
                    "success",

                "title":
                    "No major traffic issues",

                "message":
                    f"No major traffic issue detected near {location}.",

                "lat":
                    lat,

                "lon":
                    lon
            })

        alert_count = len([
            x for x in alerts
            if x["type"] != "CLEAR"
        ])

        return jsonify({

            "location":
                location,

            "alert_count":
                alert_count,

            "alerts":
                alerts
        })

    except Exception as e:

        return jsonify({

            "error":
                "Alert generation failed",

            "message":
                str(e)

        }), 500


# =========================================================
# FUTURE PREDICTION
# =========================================================

@app.route("/api/future")
def future_prediction():

    file = os.path.join(
        BASE_DIR,
        "future_prediction.csv"
    )

    if not os.path.exists(file):

        return jsonify({
            "error":
                "future_prediction.csv not found"
        }), 404

    try:

        df = pd.read_csv(file)

        row = df.iloc[-1]

        return jsonify({

            "location":
                str(
                    row.get(
                        "location",
                        ""
                    )
                ),

            "current_time":
                str(
                    row.get(
                        "current_time",
                        ""
                    )
                ),

            "future_time":
                str(
                    row.get(
                        "future_time",
                        ""
                    )
                ),

            "current_vehicles":
                safe_int(
                    row.get(
                        "current_vehicle_count"
                    )
                ),

            "predicted_vehicles":
                safe_int(
                    row.get(
                        "predicted_vehicle_count"
                    )
                ),

            "traffic":
                str(
                    row.get(
                        "predicted_traffic",
                        "Unknown"
                    )
                ),

            "confidence":
                safe_float(
                    row.get(
                        "confidence"
                    )
                ) or 0
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# CSV APIs
# =========================================================

@app.route("/api/spread")
def congestion_spread():

    return read_csv_endpoint(
        "congestion_spread.csv"
    )


@app.route("/api/what-if")
def what_if():

    return read_csv_endpoint(
        "what_if_result.csv"
    )


@app.route("/api/routes")
def routes():

    return read_csv_endpoint(
        "route_optimization.csv"
    )


def read_csv_endpoint(filename):

    file = os.path.join(
        BASE_DIR,
        filename
    )

    if not os.path.exists(file):

        return jsonify({
            "error":
                f"{filename} not found"
        }), 404

    try:

        return jsonify(
            pd.read_csv(
                file
            ).to_dict(
                orient="records"
            )
        )

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# EXPLAINABLE AI
# =========================================================

@app.route("/api/explanation")
def explanation():

    file = os.path.join(
        BASE_DIR,
        "route_optimization.csv"
    )

    if not os.path.exists(file):

        return jsonify({
            "error":
                "route_optimization.csv not found"
        }), 404

    try:

        df = pd.read_csv(file)

        best = df.sort_values(
            by="traffic_score"
        ).iloc[0]

        return jsonify({

            "route":
                best["route"],

            "road":
                best["road"],

            "traffic_score":
                float(
                    best["traffic_score"]
                ),

            "traffic_status":
                best["traffic_status"],

            "estimated_delay":
                float(
                    best["estimated_delay"]
                ),

            "reasons": [

                "Low traffic congestion",

                "Low traffic score",

                "Lower estimated travel delay",

                "Better traffic condition than other routes"
            ]
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# DISTRICT / TALUK / VILLAGE
# =========================================================

@app.route("/api/districts")
def districts():

    return read_csv_endpoint(
        "district_routes.csv"
    )


@app.route("/api/taluks")
def taluks():

    return read_csv_endpoint(
        "taluk_routes.csv"
    )


@app.route("/api/villages")
def villages():

    return read_csv_endpoint(
        "village_routes.csv"
    )


@app.route("/api/location-data")
def location_data():

    output = {

        "districts": [],
        "taluks": [],
        "villages": []
    }

    files = {

        "districts":
            "district_routes.csv",

        "taluks":
            "taluk_routes.csv",

        "villages":
            "village_routes.csv"
    }

    for key, filename in files.items():

        file = os.path.join(
            BASE_DIR,
            filename
        )

        if os.path.exists(file):

            try:

                output[key] = (
                    pd.read_csv(
                        file
                    )
                    .to_dict(
                        orient="records"
                    )
                )

            except Exception:

                output[key] = []

    return jsonify(output)


# =========================================================
# SAFE DATA HELPERS
# =========================================================

def safe_float(value):

    try:

        if pd.isna(value):
            return None

        return float(value)

    except Exception:

        return None


def safe_int(value):

    try:

        if pd.isna(value):
            return 0

        return int(
            float(value)
        )

    except Exception:

        return 0


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print("=" * 55)
    print("IIC TRAFFIC AI")
    print("Google-style Map + Alternative Routes + Alerts")
    print("http://127.0.0.1:5000")
    print("=" * 55)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )