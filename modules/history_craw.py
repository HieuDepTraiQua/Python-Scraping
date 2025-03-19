from database import *
from bson import ObjectId

def get_history_craw(page, size):
    skip = (page - 1) * size

    # Lấy dữ liệu từ MongoDB
    histories = list(history_scraped.find().skip(skip).limit(size))

    # Chuyển đổi ObjectId thành string để tránh lỗi
    for history in histories:
        history["_id"] = str(history["_id"])

    total_records = history_scraped.count_documents({})
    total_pages = (total_records + size - 1) // size

    return {
        "data": histories,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_records": total_records,
            "page": page
        }
    }
    
def get_detail_content_scraped(history_scraped_id, page, size):
    obj_id = ObjectId(history_scraped_id)
    
    skip = (page - 1) * size

    # Lấy dữ liệu từ MongoDB
    scraped_records = list(detail_data_scraped.find({"historyScrapedId": obj_id}).skip(skip).limit(size))

    # Chuyển đổi ObjectId thành string để tránh lỗi
    for record in scraped_records:
        record["_id"] = str(record["_id"])

    total_records = history_scraped.count_documents({})
    total_pages = (total_records + size - 1) // size

    return {
        "data": scraped_records,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_records": total_records,
            "page": page
        }
    }
    
