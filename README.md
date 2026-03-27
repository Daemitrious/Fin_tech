Payment Service

Команды:
Основные команды запуска:

bash:

- cp .env.example .env
- docker compose up --build


Отдельные команды:

bash:

- alembic upgrade head
- uvicorn app.main:app --host 0.0.0.0 --port 8000
- python -m app.workers.outbox_publisher
- python -m app.workers.payment_consumer


Как запустить:

Вариант 1. Через Docker Compose

bash:

- cp .env.example .env
- docker compose up --build


После запуска будут доступны:

- API: 'http://localhost:8000'
- Swagger: 'http://localhost:8000/docs'
- RabbitMQ UI: 'http://localhost:15672' ('guest/guest')

Вариант 2. Локально без Docker

Нужны отдельно поднятые PostgreSQL и RabbitMQ.

bash:
- cp .env.example .env
- poetry install
- alembic upgrade head
- uvicorn app.main:app --reload
- python -m app.workers.outbox_publisher
- python -m app.workers.payment_consumer


