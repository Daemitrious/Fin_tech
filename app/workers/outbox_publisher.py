from __future__ import annotations

import asyncio
import logging

from app.db.session import async_session_factory
from app.repositories.outbox_repository import OutboxRepository
from app.services.message_bus import broker, payments_dlq, payments_exchange, payments_queue
from app.utils.time import utcnow

logger = logging.getLogger(__name__)


async def publish_once() -> None:
    async with async_session_factory() as session:
        repository = OutboxRepository(session)
        events = await repository.get_unpublished()
        if not events:
            return
        for event in events:
            await broker.publish(
                event.payload,
                exchange=payments_exchange,
                routing_key=event.routing_key,
                queue=payments_queue,
                headers=event.headers,
            )
            await repository.mark_published(event, utcnow())
        await session.commit()
        logger.info("outbox_published", extra={"count": len(events)})


async def wait_for_broker() -> None:
    while True:
        try:
            await broker.connect()
            await broker.declare_queue(payments_queue)
            await broker.declare_queue(payments_dlq)
            logger.info("rabbitmq_connected")
            return
        except Exception:  # noqa: BLE001
            logger.exception("rabbitmq_connect_failed")
            await asyncio.sleep(2)


async def main() -> None:
    await wait_for_broker()
    try:
        while True:
            try:
                await publish_once()
            except Exception:  # noqa: BLE001
                logger.exception("outbox_publish_failed")
            await asyncio.sleep(1)
    finally:
        await broker.close()


if __name__ == "__main__":
    asyncio.run(main())
