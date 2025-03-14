from flask import Flask, jsonify, request
from flask_cors import CORS
from modules.data_crawler import *
import asyncio
import config
from pymongo import MongoClient



app = Flask(__name__)
CORS(app)
client = MongoClient(config.MONGO_URI)
db = client[config.DATABASE_NAME]

print(f"✅ Kết nối đến MongoDB: {config.DATABASE_NAME}")

@app.route("/crawl", methods=["POST"])
def crawl_api():
    try:
        data = request.get_json()
        if not data or "url" not in data or "content" not in data:
            return jsonify({"status": "error", "message": "Missing 'url' or 'content' in request body"}), 400
        
        url = data["url"]
        content = data["content"]
        
        result  = crawl_data_by_html(url, content)
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route("/get-html", methods=["GET"])
def get_news():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        page_content = asyncio.run(fetch_with_playwright(url))  # Chạy async function trong Flask
        return jsonify({"html": page_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)