from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class PaymentCreatedEvent(BaseModel):
    payment_id: UUID
    amount: Decimal
    currency: Literal["RUB", "USD", "EUR"]
    description: str
    metadata: dict[str, Any]
    webhook_url: HttpUrl
    created_at: datetime
