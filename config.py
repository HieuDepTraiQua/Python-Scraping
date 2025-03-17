import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Đọc các biến
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


os.environ["ALL_PROXY"] = "socks5://1202c69h2a:1202c69h2a@157.66.98.63:43596"