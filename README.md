## afisha-service

FastAPI-приложение для управления мероприятиями и бронирования билетов.

## Стек

- Python 3.13
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic
- Redis
- Dishka
- Taskiq
- Docker Compose
- Pytest

## Установка и запуск

Скопируйте файл конфигурации:

```bash
cp .env.dev.example .env.dev
```

Через Docker Compose можно поднять PostgreSQL, Redis, API платежей и API страховки:

```bash
docker compose up -d db payment-api protection-api redis
```

Сервисы будут доступны:
- PostgreSQL: localhost:7432
- Redis: localhost:7379
- Taskiq Admin: http://localhost:3000
- Payment API: http://localhost:9001
- Protection API: http://localhost:9002

Установить зависимости:

```bash
uv sync
```

Применить миграции:

```bash
ENV_FILE=.env.dev uv run alembic upgrade head
```

Запустить приложение:

```bash
ENV_FILE=.env.dev uv run uvicorn src.afisha.main:app --reload
```

Запустить Taskiq workers и scheduler через Docker Compose:

```bash
docker compose up -d afisha-taskiq-admin afisha-taskiq-cpu-worker afisha-taskiq-io-worker afisha-taskiq-scheduler
```

Приложение будет доступно по адресу:
http://localhost:8000

## Тесты

Тестовая PostgreSQL-база создаётся автоматически при первом запуске PostgreSQL-контейнера.
Тестовый Redis необходимо поднять отдельно:

```bash
docker compose up -d redis-test
```

Применить миграции к тестовой базе:

```bash
ENV_FILE=.env.test uv run alembic upgrade head
```

Запустить тесты:

```bash
ENV_FILE=.env.test uv run pytest
```

## Эндпоинты

```http
POST /events/{event_id}/checkout
```
Создает предварительное бронирование выбранных мест на заданное в конфигурации время (по умолчанию 15 мин) и возвращает данные для оплаты и страховки (дополнительно).

```http
GET /organizer/events/{event_id}/dashboard
```
Возвращает организатору основную статистику по мероприятию: (продажи, заполняемость, средний чек и тд).

```http
GET /events/{event_id}
```

Возвращает описание мероприятия.

## Фоновые задачи

Фоновые задачи выполняются через Taskiq и разделены на CPU- и I/O-очереди.

### Генерация PDF-отчётов

Генерация PDF-отчётов выполняется в отдельной фоновой задаче. Для зависших отчётов реализован recovery-механизм, который повторно публикует необработанные задачи.

### Очистка просроченных бронирований

Периодическая задача освобождает места и удаляет неоплаченные бронирования с истёкшим временем резерва.

### Повторный запрос Protection API

Если Protection API не отвечает за 3 секунды или возвращает ошибку, бронирование создаётся без страховки, а повторный запрос выполняется в фоне с ограниченным числом повторных попыток.

## Особенности реализации

- Асинхронное взаимодействие с внешними Payment и Protection API.
- Конкурентное выполнение независимых аналитических запросов к базе данных.
- Транзакционное резервирование мест с защитой от конфликтного бронирования.
- Компенсирующие действия при ошибках внешних сервисов.
- Фоновые и периодические задачи на Taskiq с разделением CPU- и I/O-нагрузки.
- Интеграционные тесты с отдельным тестовым окружением.
- Кеширование мероприятий с TTL и jitter.
- Distributed singleflight при cache miss.
- Асинхронная консолидация просмотров в БД батчами.
- Graceful shutdown с flush оставшихся событий.
