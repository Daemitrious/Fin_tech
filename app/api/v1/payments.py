from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_api_key
from app.schemas.payment import PaymentCreateRequest, PaymentCreateResponse, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.post("", response_model=PaymentCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
    payload: PaymentCreateRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_db_session),
) -> PaymentCreateResponse:
    service = PaymentService(session)
    return await service.create_payment(payload=payload, idempotency_key=idempotency_key)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> PaymentResponse:
    service = PaymentService(session)
    payment = await service.get_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment
