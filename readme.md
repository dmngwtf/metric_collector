# Metric Collector
<p align="center">
  <h2 align="center">Асинхронный TCP-сервер для сбора метрик</h2>
  <p align="center">
    <b>Бинарный протокол • asyncio • TimescaleDB</b><br>
    <b>Пакетная запись • Graceful shutdown • JSON-логи</b>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.11-blue" />
    <img src="https://img.shields.io/badge/asyncio-%F0%9F%92%A8-green" />
    <img src="https://img.shields.io/badge/TimescaleDB-%E2%8F%B1-orange" />
    <img src="https://img.shields.io/badge/structlog-%F0%9F%93%9D-brightgreen" />
    <img src="https://img.shields.io/badge/pytest-%E2%9C%85-blue" />
    <img src="https://img.shields.io/badge/Docker-%F0%9F%90%B3-lightgrey" />
  </p>
</p>

---

## Возможности
| Функция | Описание |
| --------------------------------- | ----------------------------------------- |
| **Бинарный TCP-протокол** | Приём метрик в компактном формате (timestamp + name + float64) |
| **Асинхронная обработка** | Множественные клиенты через `asyncio` без блокировок |
| **Пакетная запись** | Буферизация в памяти → запись в БД каждые 5 сек |
| **TimescaleDB hypertables** | Авто-конвертация таблицы в hypertable для временных рядов |
| **Graceful shutdown** | Корректное завершение: запись буфера, закрытие соединений |
| **JSON-логирование** | Структурированные логи через `structlog` |
| **Авто-миграции** | Инициализация БД и hypertable при старте |
| **Юнит-тесты** | Покрытие парсера, хранилища, записи |

---

## Стек
```yaml
Language: Python 3.11
Runtime: asyncio
Database: PostgreSQL 15 + TimescaleDB
ORM: SQLAlchemy 2.0 (async)
Logging: structlog + json
Testing: pytest + asyncio
```
---

## Быстрый старт
```bash
git clone <repository_url>
cd metric_collector
cp .env.example .env
```
---

## Настройка ENV
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=metrics_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
TCP_HOST=0.0.0.0
TCP_PORT=9999
BATCH_INTERVAL=5
```
---

## Запуск через Docker
```bash
docker-compose up -d
```
Сервер доступен на `TCP_PORT`, БД — на `5432`.

Логи:
```bash
docker-compose logs -f collector
```

---

## Структура проекта
Коротко по каждому файлу.

---

### **📁 metric_collector/**
* **app.py** — точка входа: запуск сервера, миграции, graceful shutdown.
* **config.py** — загрузка `.env`, валидация, настройки.
* **server.py** — асинхронный TCP-сервер (`asyncio.start_server`).
* **parser.py** — разбор бинарного пакета (структура: `!Q B {name_len}s d`).
* **store.py** — in-memory буфер метрик (список/очередь).
* **db_writer.py** — фоновая задача: пакетная вставка в TimescaleDB.
* **models.py** — SQLAlchemy модель `metrics` (time, name, value).
* **migrate.py** — создание БД, таблицы, hypertable (`create_hypertable`).

---

### **📁 tests/**
* **test_parser.py** — проверка парсинга валидных/некорректных пакетов.
* **test_store.py** — поведение буфера при переполнении.
* **test_integration.py** — сквозной тест: TCP → парсер → БД.

---

### **Корневые файлы**
* **docker-compose.yml** — PostgreSQL + TimescaleDB + collector.
* **Dockerfile** — образ Python с зависимостями.
* **requirements.txt** — `asyncio`, `asyncpg`, `sqlalchemy[asyncio]`, `structlog`, `pytest`, ...
* **.env.example** — шаблон переменных.

---

## Протокол (бинарный)
```
┌─────────────────┬──────────────────────┬──────────────────────┬─────────────────┐
│ timestamp (8B)  │ name_len (1B)        │ metric_name (N B)    │ value (8B)      │
│ uint64 BE       │ uint8                │ UTF-8                │ float64 BE      │
└─────────────────┴──────────────────────┴──────────────────────┴─────────────────┘
```

**Пример (Python):**
```python
import struct
import time

timestamp = int(time.time() * 1_000_000)  # мкс
name = "cpu.usage"
value = 73.5

packet = struct.pack(
    "!Q B {}s d".format(len(name)),
    timestamp, len(name), name.encode(), value
)
```

---

## Тестирование
### Отправка метрики
```bash
echo -ne '\x00\x00\x01\x88\xD2\xE9\xA0\x00\x06metric\x40\x49\x0F\xDB\x00\x00\x00\x00' | nc 127.0.0.1 9999
```

### Проверка в БД
```sql
SELECT time, metric_name, value FROM metrics ORDER BY time DESC LIMIT 5;
```

### Юнит-тесты
```bash
pytest -v
```

---

## Пример лога
```json
{
  "event": "metric_received",
  "timestamp": "2025-11-16T19:06:42.123456",
  "client": "127.0.0.1:54321",
  "metric": "cpu.temp",
  "value": 68.4
}
```

---

## Docker-команды
```bash
# Пересобрать и запустить
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f collector

# Остановка
docker-compose down
```

---