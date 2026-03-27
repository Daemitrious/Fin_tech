from __future__ import annotations

from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

from app.core.config import settings

payments_exchange = RabbitExchange(settings.payments_exchange, durable=True)
payments_queue = RabbitQueue(
    name=settings.payments_new_queue,
    routing_key=settings.payments_new_queue,
    durable=True,
    arguments={
        "x-dead-letter-exchange": settings.payments_exchange,
        "x-dead-letter-routing-key": settings.payments_dlq,
    },
)
payments_dlq = RabbitQueue(name=settings.payments_dlq, routing_key=settings.payments_dlq, durable=True)

broker = RabbitBroker(settings.rabbitmq_url)
