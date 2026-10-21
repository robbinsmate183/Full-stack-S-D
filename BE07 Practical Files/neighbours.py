from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017")
businesses = client.bizDB.biz

selected = list(businesses.aggregate([
    {"$match": {"location": {"$exists": True}}},
    {"$sample": {"size": 1}}
]))

if not selected:
    print("No businesses with locations found")
    raise SystemExit

business = selected[0]

print("Random business:", business["name"], "from", business["town"])

pipeline = [
    {"$geoNear": {
        "near": business["location"],
        "distanceField": "distance",
        "spherical": True,
        "minDistance": 1,
        "maxDistance": 50000
    }},
    {"$match": {"_id": {"$ne": business["_id"]}}},
    {"$project": {
        "name": 1,
        "town": 1,
        "distance": 1
    }},
    {"$limit": 10}
]

print("\n10 NEAREST BUSINESSES")

for neighbour in businesses.aggregate(pipeline):
    print(
        neighbour["name"],
        neighbour["town"],
        round(neighbour["distance"] / 1000, 2),
        "km"
    )

print("\nCLOSEST BUSINESS IN A DIFFERENT TOWN")

different_town_pipeline = [
    {"$geoNear": {
        "near": business["location"],
        "distanceField": "distance",
        "spherical": True
    }},
    {"$match": {"town": {"$ne": business["town"]}}},
    {"$limit": 1},
    {"$project": {
        "name": 1,
        "town": 1,
        "distance": 1
    }}
]

for neighbour in businesses.aggregate(different_town_pipeline):
    print(
        neighbour["name"],
        "from",
        neighbour["town"],
        "-",
        round(neighbour["distance"] / 1000, 2),
        "km away"
    )