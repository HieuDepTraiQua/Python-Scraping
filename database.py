import config
from pymongo import MongoClient

client = MongoClient(config.MONGO_URI)
db = client[config.DATABASE_NAME]

print(f"✅ Kết nối đến MongoDB: {config.DATABASE_NAME}")

scenario_craw = db["scenario_craw"]