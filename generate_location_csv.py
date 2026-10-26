import os
import pandas as pd


# =========================================================
# FOLDERS
# =========================================================

os.makedirs("data", exist_ok=True)
os.makedirs("data/routes", exist_ok=True)


# =========================================================
# DISTRICTS
# =========================================================

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
    "Virudhunagar"
]


# =========================================================
# DISTRICT CSV
# =========================================================

district_rows = []

for i, district in enumerate(districts):

    district_rows.append({
        "district_id": i + 1,
        "district": district
    })


pd.DataFrame(
    district_rows
).to_csv(
    "data/districts.csv",
    index=False
)


# =========================================================
# SAMPLE TALUK DATA
# =========================================================
# More taluks can be added easily.

taluks = [

    ["Chennai", "Chennai North"],
    ["Chennai", "Chennai South"],

    ["Tiruvallur", "Tiruvallur"],
    ["Tiruvallur", "Ponneri"],
    ["Tiruvallur", "Gummidipoondi"],
    ["Tiruvallur", "Avadi"],

    ["Chengalpattu", "Chengalpattu"],
    ["Chengalpattu", "Tambaram"],
    ["Chengalpattu", "Thiruporur"],

    ["Kancheepuram", "Kancheepuram"],
    ["Kancheepuram", "Sriperumbudur"],

    ["Villupuram", "Villupuram"],
    ["Villupuram", "Tindivanam"],
    ["Villupuram", "Gingee"],

    ["Cuddalore", "Cuddalore"],
    ["Cuddalore", "Panruti"],
    ["Cuddalore", "Chidambaram"],

    ["Perambalur", "Perambalur"],
    ["Perambalur", "Kunnam"],
]


taluk_rows = []

for i, item in enumerate(taluks):

    taluk_rows.append({

        "taluk_id":
            i + 1,

        "district":
            item[0],

        "taluk":
            item[1]
    })


pd.DataFrame(
    taluk_rows
).to_csv(
    "data/taluks.csv",
    index=False
)


# =========================================================
# SAMPLE VILLAGE DATA
# =========================================================

villages = [

    ["Chennai", "Chennai North", "Manali"],
    ["Chennai", "Chennai North", "Madhavaram"],
    ["Chennai", "Chennai North", "Tiruvottiyur"],

    ["Tiruvallur", "Tiruvallur", "Tiruvallur"],
    ["Tiruvallur", "Ponneri", "Ponneri"],
    ["Tiruvallur", "Gummidipoondi", "Gummidipoondi"],
    ["Tiruvallur", "Avadi", "Avadi"],

    ["Chengalpattu", "Chengalpattu", "Chengalpattu"],
    ["Chengalpattu", "Tambaram", "Tambaram"],
    ["Chengalpattu", "Thiruporur", "Kelambakkam"],

    ["Kancheepuram", "Kancheepuram", "Kancheepuram"],
    ["Kancheepuram", "Sriperumbudur", "Sriperumbudur"],

    ["Villupuram", "Villupuram", "Villupuram"],
    ["Villupuram", "Tindivanam", "Tindivanam"],
    ["Villupuram", "Gingee", "Gingee"],

    ["Cuddalore", "Cuddalore", "Cuddalore"],
    ["Cuddalore", "Panruti", "Panruti"],
    ["Cuddalore", "Chidambaram", "Chidambaram"],

    ["Perambalur", "Perambalur", "Perambalur"],
    ["Perambalur", "Kunnam", "Kunnam"]
]


village_rows = []

for i, item in enumerate(villages):

    village_rows.append({

        "village_id":
            i + 1,

        "district":
            item[0],

        "taluk":
            item[1],

        "village":
            item[2]
    })


pd.DataFrame(
    village_rows
).to_csv(
    "data/villages.csv",
    index=False
)


# =========================================================
# ROUTE DATA
# =========================================================

route_rows = []


for item in villages:

    district = item[0]
    taluk = item[1]
    village = item[2]

    roads = [

        ("Route A", "Main Road", 22.5, "LOW", 8.2),

        ("Route B", "NH / Highway", 38.7, "MEDIUM", 11.5),

        ("Route C", "Alternative Road", 52.4, "MEDIUM", 15.8),

        ("Route D", "Village Link Road", 68.3, "HIGH", 20.4)
    ]

    for road in roads:

        route_rows.append({

            "district":
                district,

            "taluk":
                taluk,

            "village":
                village,

            "route":
                road[0],

            "road":
                road[1],

            "traffic_score":
                road[2],

            "traffic_status":
                road[3],

            "estimated_delay":
                road[4]
        })


route_df = pd.DataFrame(
    route_rows
)


# =========================================================
# SAVE ROUTE CSV FILES
# =========================================================

route_df.to_csv(
    "data/routes/village_routes.csv",
    index=False
)


# District routes

district_route_rows = []

for district in districts:

    roads = [
        ("Route A", "Main Road", 25.4, "LOW", 9.0),
        ("Route B", "Highway", 41.8, "MEDIUM", 12.5),
        ("Route C", "Alternative Road", 57.2, "MEDIUM", 16.2),
        ("Route D", "Bypass Road", 72.5, "HIGH", 21.8)
    ]

    for r in roads:

        district_route_rows.append({

            "district":
                district,

            "route":
                r[0],

            "road":
                r[1],

            "traffic_score":
                r[2],

            "traffic_status":
                r[3],

            "estimated_delay":
                r[4]
        })


pd.DataFrame(
    district_route_rows
).to_csv(
    "data/routes/district_routes.csv",
    index=False
)


# Taluk routes

taluk_route_rows = []

for item in taluks:

    for r in [
        ("Route A", "Main Road", 24.5, "LOW", 8.5),
        ("Route B", "Highway", 39.5, "MEDIUM", 11.4),
        ("Route C", "Alternative Road", 54.8, "MEDIUM", 15.2),
        ("Route D", "Bypass Road", 69.7, "HIGH", 20.1)
    ]:

        taluk_route_rows.append({

            "district":
                item[0],

            "taluk":
                item[1],

            "route":
                r[0],

            "road":
                r[1],

            "traffic_score":
                r[2],

            "traffic_status":
                r[3],

            "estimated_delay":
                r[4]
        })


pd.DataFrame(
    taluk_route_rows
).to_csv(
    "data/routes/taluk_routes.csv",
    index=False
)


print()
print("=" * 60)
print("LOCATION CSV GENERATION COMPLETED")
print("=" * 60)

print()
print("Created:")

print("data/districts.csv")
print("data/taluks.csv")
print("data/villages.csv")

print()
print("Routes:")

print("data/routes/district_routes.csv")
print("data/routes/taluk_routes.csv")
print("data/routes/village_routes.csv")

print()
print("Districts :", len(districts))
print("Taluks    :", len(taluks))
print("Villages  :", len(villages))

print()
print("Completed successfully!")