from datetime import datetime
from database import *
from .data_crawler import *


def call_service(scenario):
    print(f"Running service for scenario: {scenario['_id']}, Time: {scenario['time']}")
    existing_record = scenario_scraping.find_one({"_id": scenario['_id']})
    if not existing_record:
        return {"status": "error", "message": "Record not found"}, 404
    crawl_data_by_html(existing_record['url'], existing_record['content'])
    

# Hàm kiểm tra và gọi service
def check_and_run_crawdata():
    current_time = datetime.now().strftime("%H:%M")  # Lấy giờ hiện tại dạng "HH:MM"
    scenarios = scenario_scraping.find({"time": current_time})
    
    for scenario in scenarios:
        call_service(scenario)  # Gọi service