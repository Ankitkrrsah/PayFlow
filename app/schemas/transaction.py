from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class PaySimulationRequest(BaseModel):
    payment_method: str
    simulate_failure: bool = False

class TransactionOut(BaseModel):
    id: UUID
    payment_link_id: Optional[UUID]
    merchant_id: UUID
    amount: Decimal
    currency: str
    status: str
    payment_method: Optional[str] = None
    created_at: datetime

class TransactionListResponse(BaseModel):
    items: list[TransactionOut]
    total: int
    limit: int
    offset: int

class TransactionSummaryOut(BaseModel):
    status: str
    total_count: int
    total_amount: Decimal
