import config
from pymongo import MongoClient

client = MongoClient(config.MONGO_URI)
db = client[config.DATABASE_NAME]

print(f"✅ Kết nối đến MongoDB: {config.DATABASE_NAME}")

scenario_scraping = db["scenario_scraping"]
history_scraped = db["history_scraped"]
detail_data_scraped = db["detail_data_scraped"]