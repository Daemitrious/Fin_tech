from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timezone
from uuid import UUID

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.payment import PaymentStatus
from app.repositories.payment_repository import PaymentRepository

logger = logging.getLogger(__name__)


class PaymentProcessor:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.payment_repository = PaymentRepository(session)

    async def process(self, payload: dict) -> None:
        payment_id = UUID(str(payload["payment_id"]))
        payment = await self.payment_repository.get_by_id(payment_id)
        if payment is None:
            raise ValueError(f"Payment {payment_id} not found")
        if payment.status != PaymentStatus.pending:
            logger.info("payment_already_processed", extra={"payment_id": str(payment.id), "status": payment.status.value})
            return

        await asyncio.sleep(random.randint(settings.payment_processing_min_delay_sec, settings.payment_processing_max_delay_sec))
        is_success = random.random() < 0.9
        payment.status = PaymentStatus.succeeded if is_success else PaymentStatus.failed
        payment.processed_at = datetime.now(timezone.utc)
        await self.session.commit()

        await self._send_webhook(payment_id=str(payment.id), status=payment.status.value, webhook_url=payment.webhook_url)

    async def _send_webhook(self, payment_id: str, status: str, webhook_url: str) -> None:
        body = {"payment_id": payment_id, "status": status}
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(settings.max_webhook_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            retry=retry_if_exception_type((httpx.HTTPError, RuntimeError)),
            reraise=True,
        ):
            with attempt:
                async with httpx.AsyncClient(timeout=settings.webhook_timeout_sec) as client:
                    response = await client.post(webhook_url, json=body)
                    if response.status_code >= 500:
                        raise RuntimeError(f"Webhook temporary failure with status {response.status_code}")
                    response.raise_for_status()
