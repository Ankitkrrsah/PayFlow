from typing import Optional, Literal
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class PaymentLinkCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: Literal["USD", "EUR", "GBP", "INR"]
    description: Optional[str] = None
    expires_in_minutes: Optional[int] = Field(None, gt=0)

class PaymentLinkOut(BaseModel):
    id: UUID
    amount: Decimal
    currency: str
    description: Optional[str] = None
    status: str
    expires_at: Optional[datetime] = None
    created_at: datetime
    pay_url: str
