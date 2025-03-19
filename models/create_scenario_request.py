from typing import Optional
from pydantic import BaseModel, Field

class CreateScenarioRequest(BaseModel):
    url: Optional[str] = Field(None, description="URL cụ thể của kịch bản")
    name: Optional[str] = Field(None, description="Tên của kịch bản")
    content: Optional[str] = Field(None, description="Nội dung cần thu thập dữ liệu")
    time: Optional[str] = Field(None, description="Thời gian chạy thu thập dữ liệu")
    type: Optional[str] = Field(None, description="Loại của kịch bản thu thập dữ liệu")
    scrapedData: Optional[str] = Field(None, description="Dữ liệu thu thập được")
    
    
    def to_dict(self):
        return self.model_dump(exclude_unset=True)
    
    
    