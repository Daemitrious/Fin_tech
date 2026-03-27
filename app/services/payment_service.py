from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import OutboxEvent
from app.models.payment import Payment
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.events import PaymentCreatedEvent
from app.schemas.payment import PaymentCreateRequest, PaymentCreateResponse, PaymentResponse


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.payment_repository = PaymentRepository(session)
        self.outbox_repository = OutboxRepository(session)

    async def create_payment(self, payload: PaymentCreateRequest, idempotency_key: str) -> PaymentCreateResponse:
        existing = await self.payment_repository.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            return PaymentCreateResponse(payment_id=existing.id, status=existing.status.value, created_at=existing.created_at)

        payment = Payment(
            amount=payload.amount,
            currency=payload.currency,
            description=payload.description,
            metadata_json=payload.metadata,
            idempotency_key=idempotency_key,
            webhook_url=str(payload.webhook_url),
        )
        self.payment_repository.add(payment)
        await self.session.flush()

        event = PaymentCreatedEvent(
            payment_id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            metadata=payment.metadata_json,
            webhook_url=payment.webhook_url,
            created_at=payment.created_at,
        )
        self.outbox_repository.add(
            OutboxEvent(
                aggregate_type="payment",
                aggregate_id=payment.id,
                routing_key="payments.new",
                payload=event.model_dump(mode="json"),
                headers={"event_type": "payment.created"},
            )
        )
        await self.session.commit()
        return PaymentCreateResponse(payment_id=payment.id, status=payment.status.value, created_at=payment.created_at)

    async def get_payment(self, payment_id: str) -> PaymentResponse | None:
        payment = await self.payment_repository.get_by_id(UUID(payment_id))
        if payment is None:
            return None
        return PaymentResponse.model_validate(payment)
