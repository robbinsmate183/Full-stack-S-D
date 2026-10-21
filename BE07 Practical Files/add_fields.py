from pymongo import MongoClient
import random

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.bizDB
businesses = db.biz

# Add employee numbers and profits
for business in businesses.find():
    businesses.update_one(
        {"_id": business["_id"]},
        {
            "$set": {
                "num_employees": random.randint(1, 100),
                "profit": [
                    {"year": "2022", "gross": random.randint(-500000, 500000)},
                    {"year": "2023", "gross": random.randint(-500000, 500000)},
                    {"year": "2024", "gross": random.randint(-500000, 500000)}
                ],
                "dummy": "Test"
            }
        }
    )

print("Added employee numbers, profits and dummy field")

# Remove temporary dummy field
for business in businesses.find():
    businesses.update_one(
        {"_id": business["_id"]},
        {"$unset": {"dummy": ""}}
    )

print("Removed dummy field")
print("Successfully updated businesses")