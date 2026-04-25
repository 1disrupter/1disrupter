import json
from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client.get_default_database()
venues = db["venues"]

with open("benalmadena.seed.json", "r") as f:
    data = json.load(f)

venues.insert_many(data)

print("Benalmádena venues inserted successfully!")
