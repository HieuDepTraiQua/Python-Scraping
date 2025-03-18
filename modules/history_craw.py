from database import *

def get_history_craw(str_page, str_size):
    page = int(str_page.strip())
    size = int(str_size.strip())
    skip = (page - 1) * size

    # Lấy dữ liệu từ MongoDB
    histories = list(history_craw.find().skip(skip).limit(size))

    # Chuyển đổi ObjectId thành string để tránh lỗi
    for history in histories:
        history["_id"] = str(history["_id"])

    total_records = history_craw.count_documents({})
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
    
