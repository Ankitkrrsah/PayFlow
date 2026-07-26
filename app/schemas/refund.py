from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class RefundCreate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    reason: Optional[str] = None

class RefundOut(BaseModel):
    id: UUID
    transaction_id: UUID
    amount: Decimal
    status: str
    reason: Optional[str] = None
    created_at: datetime
