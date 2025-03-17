from flask import Flask, jsonify, request
from flask_cors import CORS
from modules.data_crawler import *
from modules.craw_schedule import *
import asyncio
import schedule
import time
import threading


app = Flask(__name__)
CORS(app)

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
    
@app.route("/scenario", methods=["POST"])
def create_scenario():
    try:
        data = request.get_json()
        # Chuyển đổi data thành Pydantic model
        scenaio = ScenarioCraw(**data)  
        result  = create_scenario_craw(scenaio)
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route("/scenario", methods=["PUT"])
def update_scenario():
    try:
        id = request.args.get("id")
        data = request.get_json()
        # Chuyển đổi data thành Pydantic model
        scenaio = ScenarioCraw(**data)  
        response, status_code = update_scenario_craw(id, scenaio)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500    
    
    
@app.route("/scenario", methods=["DELETE"])
def delete_scenario():
    try:
        id = request.args.get("id")
        response, status_code = delete_scenario_craw(id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route("/scenario", methods=["GET"])
def get_scenario():
    try:
        size = request.args.get("size")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
        page = request.args.get("page")
        result = filter_Scenario(page, size)
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
def run_scheduler():
    schedule.every(1).minutes.do(check_and_run_crawdata)
    while True:
        schedule.run_pending()
        time.sleep(1)


# Chạy scheduler khi app khởi động
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)