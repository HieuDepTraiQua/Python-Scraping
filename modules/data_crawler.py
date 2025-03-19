from playwright.sync_api import sync_playwright
import json
from bs4 import BeautifulSoup
import json
import openai
from playwright.async_api import async_playwright
import re
import asyncio
import os
from flask import jsonify
from models.detail_content_craw import DetailContentCraw
from models.history_craw_class import HistoryCraw
from models.screnario_craw_class import *
from database import *
from bson import ObjectId
from datetime import datetime
import pytz

def crawl_data_by_html(url, content):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Truy cập trang
        page.goto(url)
        page.wait_for_timeout(3000)
        # Đọc dữ liệu JSON từ extract_with_gptkey()
        json_rs = json.loads(extract_with_gptkey(content))

        # Lấy tất cả các field động từ JSON
        # data_fields = json_rs["data"].keys()
        data_fields = [key for key, value in json_rs["data"].items() if isinstance(value, dict) and ("value" in value or "selector" in value)]

        list_json = []

        # Duyệt qua từng field động
        elements_dict = {}
        for field in data_fields:
            selector = json_rs["data"][field]["selector"]  # Lấy selector từ JSON
            elements = page.locator(selector).all()  # Lấy danh sách phần tử
            elements_dict[field] = elements

        # Ghép các dữ liệu thành từng bản ghi
        max_length = max(len(elements) for elements in elements_dict.values())  # Tìm số lượng lớn nhất
        
        for i in range(max_length):  
            json_data = {}
            for field in data_fields:
                elements = elements_dict[field]
                if i < len(elements):  # Kiểm tra xem có dữ liệu hay không
                    if field == "link":  # Nếu là link thì lấy thuộc tính href,...
                        json_data[field] = elements[i].get_attribute("href") or \
                                           elements[i].get_attribute("data-href") or \
                                           elements[i].get_attribute("data-url")
                    elif field == "image":  # Nếu là image thì lấy src,...
                        json_data[field] = elements[i].get_attribute("src") or \
                                           elements[i].get_attribute("href") or \
                                           elements[i].get_attribute("srcset") or \
                                           elements[i].get_attribute("data-src") or \
                                           elements[i].get_attribute("data-url") or \
                                           elements[i].get_attribute("style")
                    else:  # Mặc định lấy nội dung text
                        json_data[field] = elements[i].text_content().strip()
                else:
                    json_data[field] = None  # Nếu không có dữ liệu, gán None
            list_json.append(json_data)

        browser.close()
        result_json = {
            "column": list(data_fields),
            "data": list_json
        }

        # Ghi vào file JSON
        output_filename = "output_with_playwright.json"
        with open(output_filename, "w", encoding="utf-8") as json_file:
            json.dump(list_json, json_file, ensure_ascii=False, indent=4)

        print(f"Dữ liệu đã được ghi vào {output_filename}")
        
        return result_json

def read_file_content(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()
    
def read_json_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


    
def extract_with_gptkey(content):
    # html = read_file_content("div_content.txt")
    soup = BeautifulSoup(content, "html.parser")
    cleaned_html = soup.prettify()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    chat_completion = openai.chat.completions.create(
        messages=[
            {"role": "user", "content": f"Bạn là một AI giúp phân tích HTML và trích xuất dữ liệu quan trọng.\
                Đây là nội dung HTML:\n{cleaned_html}\nHãy trả về Json gồm các nội dung quan trọng trong đoạn HTML trên,\
                    tôi chỉ cần kết quả json, không cần giải thích và cấu trúc của những giá trị trả về luôn cố định và được định nghĩa như sau:\
                        value là giá trị của nội dung tìm được và selector là className dẫn tới thẻ đó\
                            hoặc một giá trị CSS selector nào đó dùng để định nghĩa thẻ, càng chính xác càng tốt,\
                                bọc selector và value là tên của thuộc tính quan trọng đó và đặt tên cho thuộc tính đó sao cho có ý nghĩa\
                                    (Ngoại trừ các trường hợp sau với thuộc tính là ảnh thì mang tên image, link thì có tên là link), \
                                        và cuối cùng tất cả các thuộc tính tìm được thì sẽ được bọc vào 1 object là data"}
        ],
        model="gpt-4o-mini",
        temperature=0.7
    )    
    extracted_data = chat_completion.model_dump()["choices"][0]["message"]["content"]
    cleaned_json = re.sub(r"^```json\n|\n```$", "", extracted_data)

    # Chuyển thành JSON object
    data = json.loads(cleaned_json)
    
    # # Xuất JSON
    output_filename = "output_with_gpt.json"
    # with open(output_filename, "w", encoding="utf-8") as json_file:
    #     json.dump(data, json_file, ensure_ascii=False, indent=4)
        
    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)    
    print("Đã lưu kết quả vào file output_with_gpt.json")
    return json.dumps(data, indent=2, ensure_ascii=False)
    # # Kết quả JSON
    # extracted_data = chat_completion["choices"][0]["message"]["content"]
    # print(extracted_data)
        

    
    
async def fetch_with_playwright(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Chặn quảng cáo, tracking
        async def block_ads(route):
            blocked_domains = ["ads", "analytics", "doubleclick", "googlesyndication"]
            if any(domain in route.request.url for domain in blocked_domains):
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", block_ads)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)  # Giảm timeout 20s
            # Tải ảnh khi load trang web 
            await page.evaluate('''() => {
                document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                    if (img.dataset.src) img.src = img.dataset.src;
                    else if (img.dataset.srcset) img.src = img.dataset.srcset;
                    img.loading = "eager";  // Đổi sang chế độ tải ngay lập tức
                });
            }''')
            await page.evaluate('''() => {
                document.querySelectorAll('img').forEach(img => {
                    if (img.dataset.src) {
                        img.src = img.dataset.src;    
                    } else if (img.dataset.srcset) {
                        img.src = img.dataset.srcset;
                    } 
                });
                document.querySelectorAll('video').forEach(video => {
                    video.querySelectorAll('source').forEach(source => {
                        if (source.dataset.srcVideo) {
                            source.src = source.dataset.srcVideo;
                        }
                    });
                    video.load();  // Load lại video sau khi thay src
                });
            }''')
            # page.on("requestfinished", lambda req: print(f"📥 Loaded: {req.url}"))
            # page.on("requestfailed", lambda req: print(f"❌ Failed: {req.url}"))
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Lỗi khi tải trang: {e}")
            await browser.close()
            return None        
        # Cuộn xuống để tải thêm nội dung
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.evaluate('''() => {
            document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                if (img.dataset.src) img.src = img.dataset.src;
                else if (img.dataset.srcset) img.src = img.dataset.srcset;
                img.loading = "eager";  // Đổi sang chế độ tải ngay lập tức
            });
        }''')
        await page.evaluate('''() => {
            document.querySelectorAll('img').forEach(img => {
                if (img.dataset.src) {
                    img.src = img.dataset.src;    
                } else if (img.dataset.srcset) {
                    img.src = img.dataset.srcset;
                } 
            });
            document.querySelectorAll('video').forEach(video => {
                //if (video.dataset.srcImage) {
                //    video.poster = video.dataset.srcImage;
                //}
                video.querySelectorAll('source').forEach(source => {
                    if (source.dataset.srcVideo) {
                        source.src = source.dataset.srcVideo;
                    }
                });
                video.load();  // Load lại video sau khi thay src
            });
        }''')
        
        # page.on("requestfinished", lambda req: print(f"📥 Loaded: {req.url}"))
        # page.on("requestfailed", lambda req: print(f"❌ Failed: {req.url}"))
        await asyncio.sleep(1)  # Đợi trang tải

        # Lấy nội dung HTML
        html_content = await page.content()
        await browser.close()

        return html_content
    
    
def create_scenario_craw(scenaio):
    print(scenaio)
    
    scenaio_create =  ScenarioCraw()
    scenaio_create.__dict__ = scenaio.__dict__.copy()
    
    scrapedData = scenaio.scrapedData   
    new_scenaio = scenario_scraping.insert_one(scenaio_create.model_dump())
    if scrapedData is not None: 
        history = HistoryCraw(
            scenarioId=str(new_scenaio.inserted_id),
            timeScraped=datetime.now()
        )
        new_history_scenario = history_scraped.insert_one(history.model_dump())
        data_craw = DetailContentCraw(
            historyScrapedId=str(new_history_scenario.inserted_id),
            data=scrapedData
        )
        detail_data_scraped.insert_one(data_craw.model_dump())
    return {"id": str(new_scenaio.inserted_id)}

def update_scenario_craw(id, scenaio: ScenarioCraw):
    # Kiểm tra ID có hợp lệ không
    if not ObjectId.is_valid(id):
        return {"status": "error", "message": "Invalid ID format"}, 400

    # Chuyển đổi ID sang ObjectId
    obj_id = ObjectId(id)
    updated_record = scenario_scraping.find_one_and_update(
        {"_id": obj_id}, 
        {"$set": scenaio.to_dict()}, 
        return_document=True  # Trả về bản ghi sau khi cập nhật
    )
    
    updated_record["_id"] = str(updated_record["_id"])
    

    if updated_record:
        return {"status": "success", "message": "Record updated successfully", "data": updated_record}, 200
    else:
        return {"status": "error", "message": "Record not found"}, 404


def delete_scenario_craw(id):
    # Kiểm tra ID có hợp lệ không
    if not ObjectId.is_valid(id):
        return {"status": "error", "message": "Invalid ID format"}, 400

    # Chuyển đổi ID sang ObjectId
    obj_id = ObjectId(id)
    
    existing_record = scenario_scraping.find_one({"_id": obj_id})
    if not existing_record:
        return {"status": "error", "message": "Record not found"}, 404

    # Thực hiện xóa trong MongoDB
    scenario_scraping.delete_one({"_id": obj_id})
    return {"status": "success", "message": "Record deleted successfully"}, 200
    
def filter_Scenario(page, size):
    skip = (page - 1) * size

    # Lấy dữ liệu từ MongoDB
    scenarios = list(scenario_scraping.find().skip(skip).limit(size))

    # Chuyển đổi ObjectId thành string để tránh lỗi
    for scenario in scenarios:
        scenario["_id"] = str(scenario["_id"])

    total_records = scenario_scraping.count_documents({})
    total_pages = (total_records + size - 1) // size

    return {
        "data": scenarios,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_records": total_records,
            "page": page
        }
    }