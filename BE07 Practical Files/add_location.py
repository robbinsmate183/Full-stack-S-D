from pymongo import MongoClient
import random

client = MongoClient("mongodb://127.0.0.1:27017")
businesses = client.bizDB.biz

# Bounds are latitude minimum, longitude minimum,
# latitude maximum, longitude maximum.
locations = {
    "Coleraine": [55.10653864221481, -6.703013870894064,
                  55.16083114339611, -6.640640630380869],
    "Banbridge": [54.32805966474902, -6.29894073802459,
                   54.36914017698541, -6.238287009221747]
}

# Approximate town centres for remaining towns
centres = {
    "Belfast": (54.5973, -5.9301),
    "Lisburn": (54.5162, -6.0580),
    "Ballymena": (54.8653, -6.2804),
    "Derry": (54.9970, -7.3090),
    "Newry": (54.1751, -6.3402),
    "Enniskillen": (54.3448, -7.6384),
    "Omagh": (54.6000, -7.3000),
    "Ballymoney": (55.0700, -6.5100)
}

for town, (lat, lon) in centres.items():
    locations[town] = [
        lat - 0.02, lon - 0.02,
        lat + 0.02, lon + 0.02
    ]

updated = 0

for business in businesses.find():
    town = business["town"]

    if town not in locations:
        continue

    lat_min, lon_min, lat_max, lon_max = locations[town]

    latitude = random.uniform(lat_min, lat_max)
    longitude = random.uniform(lon_min, lon_max)

    businesses.update_one(
        {"_id": business["_id"]},
        {"$set": {
            "location": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }
        }}
    )

    updated += 1

print(f"Added locations to {updated} businesses")

businesses.create_index([("location", "2dsphere")])
print("Created 2dsphere index")