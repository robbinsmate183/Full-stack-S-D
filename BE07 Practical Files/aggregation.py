from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017")
businesses = client.bizDB.biz

# Exercise 1: Banbridge businesses and 2024 profits
print("\nBANBRIDGE BUSINESSES - 2024 PROFITS")

pipeline = [
    {"$match": {"town": "Banbridge"}},
    {"$project": {"town": 1, "profit": 1}}
]

for business in businesses.aggregate(pipeline):
    print(business["town"], business["profit"][2]["gross"])


# Exercise 2: Belfast businesses and employee numbers
print("\nBELFAST BUSINESSES - EMPLOYEES")

pipeline = [
    {"$match": {"town": "Belfast"}},
    {"$project": {"name": 1, "num_employees": 1, "_id": 0}}
]

for business in businesses.aggregate(pipeline):
    print(business["name"], business["num_employees"])


# Exercise 3: Unwind, filter, sort, skip and limit
print("\nPROFITABLE BUSINESSES")

pipeline = [
    {"$match": {"town": "Banbridge"}},
    {"$project": {
        "town": 1,
        "profit": 1,
        "num_employees": 1
    }},
    {"$unwind": "$profit"},
    {"$match": {
        "num_employees": {"$gte": 50},
        "profit.gross": {"$gte": 0}
    }},
    {"$sort": {"profit.gross": -1}},
    {"$skip": 0},
    {"$limit": 10}
]

for business in businesses.aggregate(pipeline):
    print(business)


# Exercise 4: Save aggregation results to a collection
print("\nCREATING profitable_big_biz COLLECTION")

pipeline = [
    {"$match": {"town": "Banbridge"}},
    {"$project": {
        "town": 1,
        "profit": 1,
        "num_employees": 1,
        "_id": 0
    }},
    {"$unwind": "$profit"},
    {"$match": {
        "num_employees": {"$gte": 50},
        "profit.gross": {"$gte": 0}
    }},
    {"$out": "profitable_big_biz"}
]

list(businesses.aggregate(pipeline))

print("Collection created")


# Exercise 5: Summary statistics
print("\nPROFIT SUMMARY")

summary_pipeline = [
    {"$group": {
        "_id": None,
        "count": {"$sum": 1},
        "total": {"$sum": "$profit.gross"},
        "average": {"$avg": "$profit.gross"},
        "max": {"$max": "$profit.gross"},
        "min": {"$min": "$profit.gross"}
    }}
]

for result in client.bizDB.profitable_big_biz.aggregate(summary_pipeline):
    print(result)


# Exercise 6: Count businesses in each town
print("\nBUSINESSES BY TOWN")

pipeline = [
    {"$group": {
        "_id": "$town",
        "count": {"$sum": 1}
    }},
    {"$sort": {"_id": 1}}
]

for result in businesses.aggregate(pipeline):
    print(result["_id"], result["count"])