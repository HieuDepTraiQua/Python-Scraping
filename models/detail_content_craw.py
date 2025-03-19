from typing import Optional
from pydantic import BaseModel, Field

class DetailContentCraw(BaseModel):
    historyScrapedId: Optional[str] = Field(None, description="Id kịch bản lịch sử")
    data: Optional[str] = Field(None, description="Nội dung dữ liệu") # List các object không cố định
    
    
    def to_dict(self):
        return self.model_dump(exclude_unset=True)
    
    
    