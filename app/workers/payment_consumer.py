from __future__ import annotations

import asyncio
import logging

from faststream import Context
from faststream.exceptions import AckMessage
from faststream.rabbit import RabbitMessage

from app.db.session import async_session_factory
from app.services.message_bus import broker, payments_dlq, payments_exchange, payments_queue
from app.services.payment_processor import PaymentProcessor

logger = logging.getLogger(__name__)


@broker.subscriber(payments_queue, exchange=payments_exchange, retry=False)
async def handle_payment(payload: dict, message: RabbitMessage, ctx: Context) -> None:
    retry_count = int(message.headers.get("x-retry-count", 0)) if message.headers else 0
    try:
        async with async_session_factory() as session:
            processor = PaymentProcessor(session)
            await processor.process(payload)
    except Exception as exc:  # noqa: BLE001
        logger.exception("payment_processing_failed", extra={"payload": payload, "retry": retry_count})
        if retry_count >= 2:
            await broker.publish(payload, exchange=payments_exchange, routing_key=payments_dlq.name, queue=payments_dlq)
            raise AckMessage() from exc

        delay = 2 ** retry_count
        await asyncio.sleep(delay)
        headers = dict(message.headers or {})
        headers["x-retry-count"] = retry_count + 1
        await broker.publish(
            payload,
            exchange=payments_exchange,
            routing_key=payments_queue.name,
            queue=payments_queue,
            headers=headers,
        )
        raise AckMessage() from exc


async def wait_for_broker() -> None:
    while True:
        try:
            await broker.connect()
            logger.info("rabbitmq_connected")
            return
        except Exception:  # noqa: BLE001
            logger.exception("rabbitmq_connect_failed")
            await asyncio.sleep(2)


async def main() -> None:
    await wait_for_broker()
    await broker.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
