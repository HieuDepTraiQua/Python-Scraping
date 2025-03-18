from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from modules.data_crawler import *
from modules.craw_schedule import *
import schedule
import time
import threading
from pydantic import BaseModel



app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Định nghĩa model đầu vào
class ScenarioCrawModel(BaseModel):
    url: str
    content: str
    time: str
    type: str | None = None  # Có thể None


# API: Cào dữ liệu từ URL
@app.post("/crawl")
async def crawl_api(data: ScenarioCrawModel):
    try:
        result = crawl_data_by_html(data.url, data.content)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API: Lấy HTML từ URL
@app.get("/get-html")
async def get_news(url: str = Query(..., description="URL để lấy nội dung HTML")):
    try:
        page_content = await fetch_with_playwright(url)
        return {"html": page_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API: Tạo scenario
@app.post("/scenario")
async def create_scenario(data: ScenarioCrawModel):
    try:
        scenario = ScenarioCraw(**data.model_dump())  # Chuyển sang model của bạn
        result = create_scenario_craw(scenario)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API: Cập nhật scenario
@app.put("/scenario")
async def update_scenario(id: str, data: ScenarioCrawModel):
    try:
        scenario = ScenarioCraw(**data.model_dump())
        response, status_code = update_scenario_craw(id, scenario)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API: Xóa scenario
@app.delete("/scenario")
async def delete_scenario(id: str):
    try:
        response, status_code = delete_scenario_craw(id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API: Lấy danh sách scenario
@app.get("/scenario")
async def get_scenario(page: int = 1, size: int = 10):
    try:
        result = filter_Scenario(page, size)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Chạy scheduler
def run_scheduler():
    schedule.every(1).minutes.do(check_and_run_crawdata)
    while True:
        schedule.run_pending()
        time.sleep(1)


# Chạy scheduler trong thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()


# Chạy chương trình: uvicorn app:app --host 0.0.0.0 --port 5000 --loop asyncio

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
    

