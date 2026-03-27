from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.idempotency_key == idempotency_key))
        return result.scalar_one_or_none()

    def add(self, payment: Payment) -> None:
        self.session.add(payment)
