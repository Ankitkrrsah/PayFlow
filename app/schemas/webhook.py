from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class WebhookCreate(BaseModel):
    url: str
    events: List[str]

class WebhookOut(BaseModel):
    id: UUID
    url: str
    events: List[str]
    is_active: bool
    created_at: datetime
    secret: Optional[str] = None
