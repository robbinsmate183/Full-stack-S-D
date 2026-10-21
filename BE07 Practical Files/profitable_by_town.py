from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017")
businesses = client.bizDB.biz

print("BUSINESS COUNTS BY TOWN")

for result in businesses.aggregate([
    {"$group": {"_id": "$town", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]):
    print(result["_id"], result["count"])

print("\nMOST PROFITABLE BUSINESS PER TOWN AND YEAR")

pipeline = [
    {"$unwind": "$profit"},
    {"$sort": {"profit.gross": -1}},
    {"$group": {
        "_id": {
            "town": "$town",
            "year": "$profit.year"
        },
        "business": {"$first": "$name"},
        "gross": {"$first": "$profit.gross"}
    }},
    {"$sort": {"_id.town": 1, "_id.year": 1}}
]

for result in businesses.aggregate(pipeline):
    print(
        result["_id"]["town"],
        result["_id"]["year"],
        result["business"],
        result["gross"]
    )