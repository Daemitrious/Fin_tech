from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import OutboxEvent


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, event: OutboxEvent) -> None:
        self.session.add(event)

    async def get_unpublished(self, limit: int = 100) -> list[OutboxEvent]:
        result = await self.session.execute(
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_published(self, event: OutboxEvent, published_at: datetime) -> None:
        event.published_at = published_at
