import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

client = MongoClient(MONGODB_URL)

db = client["complaint_system"]

users_collection = db["users"]
complaints_collection = db["complaints"]
complaint_history_collection = db["complaint_history"]