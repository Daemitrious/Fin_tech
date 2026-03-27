from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


Currency = Literal["RUB", "USD", "EUR"]
PaymentStatus = Literal["pending", "succeeded", "failed"]


class PaymentCreateRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=12)
    currency: Currency
    description: str = Field(..., min_length=1, max_length=255)
    metadata: dict[str, Any] = Field(default_factory=dict)
    webhook_url: HttpUrl


class PaymentCreateResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any] = Field(alias="metadata_json")
    status: PaymentStatus
    idempotency_key: str
    webhook_url: HttpUrl
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime
