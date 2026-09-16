## afisha-service

FastAPI-приложение для управления мероприятиями и бронирования билетов.

Проект также включает отдельный сервис мониторинга покупок билетов, который получает события через Kafka, агрегирует статистику и передаёт обновления клиентам через WebSocket.

## Стек

- Python 3.13
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic
- Redis
- Kafka
- Dishka
- Taskiq
- WebSocket
- Docker Compose
- Pytest

## Установка и запуск

Скопируйте файл конфигурации:

```bash
cp .env.dev.example .env.dev
```

Через Docker Compose можно поднять PostgreSQL, Redis, Kafka и вспомогательные сервисы:

```bash
docker compose up -d db payment-api protection-api redis kafka kafka-init kafka-ui
```

Сервисы будут доступны:
- PostgreSQL: localhost:7432
- Redis: localhost:7379
- Kafka: localhost:9092 
- Kafka UI: http://localhost:8080
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

## Monitoring Service

Сервис apps/monitoring предназначен для мониторинга покупок билетов в реальном времени.

Основной сервис генерирует тестовые события покупки билетов для имитации
потока реальных покупок и публикует их в Kafka-топик `tickets.purchased`.
Monitoring Service получает эти события, агрегирует данные по мероприятиям
и сохраняет результаты в PostgreSQL.

После успешного сохранения и подтверждения Kafka-сообщений агрегированные данные передаются через внутреннюю asyncio.Queue фоновому WebSocket-воркеру и рассылаются подключённым клиентам.

Для каждого WebSocket-клиента используется отдельная очередь отправки, поэтому медленный клиент не блокирует отправку сообщений остальным клиентам.

### Запуск Monitoring Service

Установить зависимости:

```bash
cd apps/monitoring
uv sync
```

Применить миграции:

```bash
ENV_FILE=.env.dev uv run alembic upgrade head
```

Запустить сервис:

```bash
ENV_FILE=.env.dev uv run uvicorn src.monitoring.main:app --reload --port 8001
```

Monitoring Service будет доступен по адресу:
http://localhost:8001

WebSocket:
```
ws://localhost:8001/ws/purchase_events
```

Для проверки WebSocket-рассылки можно запустить тестовый клиент:

```bash
uv run python websocket_client.py
```

## Тесты

### Основной сервис

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

### Monitoring Service

Тесты Monitoring Service запускаются из директории сервиса:

```bash
cd apps/monitoring
uv run pytest
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

## Kafka

Для демонстрации событийного взаимодействия между сервисами основной сервис
в фоновом режиме генерирует тестовые события покупки билетов, имитирующие
реальные события оплаты, и публикует их в Kafka-топик `tickets.purchased`.

События содержат идентификатор платежа и мероприятия, количество приобретённых билетов, сумму покупки и время оплаты.

Monitoring Service выступает consumer'ом этих событий. Сообщения обрабатываются батчами до 10 сообщений с максимальным ожиданием батча 500 мс. Подтверждение Kafka-сообщений выполняется только после успешной агрегации и сохранения данных в PostgreSQL.

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
- Асинхронная публикация событий покупки билетов в Kafka. 
- Batch-обработка Kafka-сообщений с ручным подтверждением после успешной записи в PostgreSQL. 
- Агрегация статистики покупок по мероприятиям в отдельном Monitoring Service. 
- Real-time рассылка агрегированной статистики через WebSocket. 
- Независимая отправка сообщений WebSocket-клиентам через отдельные очереди.