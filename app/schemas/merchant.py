from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class MerchantCreate(BaseModel):
    business_name: str = Field(..., min_length=1)

class MerchantOut(BaseModel):
    id: UUID
    business_name: str
    api_key: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class MerchantCreateOut(MerchantOut):
    api_secret: str  # Only returned once on creation
