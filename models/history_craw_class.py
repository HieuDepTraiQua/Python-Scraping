from typing import Optional
from pydantic import BaseModel, Field

class HistoryCraw(BaseModel):
    scenarioId: Optional[str] = Field(None, description="Id kịch bản")
    timeCraw: Optional[str] = Field(None, description="Lịch sử thời gian thu thập dữ liệu")
    
    
    def to_dict(self):
        return self.model_dump(exclude_unset=True)
    
    
    