from typing import Optional
from pydantic import BaseModel, Field

class ScenarioCraw(BaseModel):
    id: Optional[str] = Field(None, description="Id của kịch bản")
    url: Optional[str] = Field(None, description="URL cụ thể của kịch bản")
    content: Optional[str] = Field(None, description="Nội dung cần thu thập dữ liệu")
    time: Optional[str] = Field(None, description="Thời gian chạy thu thập dữ liệu")
    type: Optional[str] = Field(1, description="Loại của kịch bản thu thập dữ liệu")