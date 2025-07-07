
---

# Metric Collector

Асинхронный TCP-сервер на Python для сбора, хранения и записи метрик в TimescaleDB.

---

##  Возможности

* **Бинарный прием метрик** по TCP:

  ```
  [timestamp: uint64_t BE, 8 байт]
  [metric_name_length: uint8_t, 1 байт]
  [metric_name: utf-8, N байт]
  [value: float64 BE, 8 байт]
  ```
* **Асинхронная обработка** клиентов через `asyncio`
* **Пакетная запись в БД** каждые 5 секунд
* **Graceful shutdown**
* **JSON-логирование** (`structlog`)
* **Авто-миграции** базы (PostgreSQL + TimescaleDB)
* **Юнит-тесты** с `pytest`

---

##  Структура проекта

```
metric_collector/
├── app.py             # Точка входа
├── config.py          # Конфигурации
├── server.py          # TCP-сервер
├── parser.py          # Парсинг бинарных метрик
├── store.py           # Хранилище метрик
├── db_writer.py       # Запись в TimescaleDB
├── models.py          # Модель метрики
├── migrate.py         # Создание базы и таблицы
├── tests/             # Тесты (parser, store)
└── requirements.txt   # Зависимости
```

---

##  Установка


```bash
cd /path/to/metric_collector
pip install -r requirements.txt
```

**TimescaleDB:**

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
```


---

##  Запуск

```bash
cd /path/to/metric_collector
python -m metric_collector.app
```

---

##  Тестирование

**Отправка метрики:**

```bash
echo -ne '\x00\x00\x01\x88\xD2\xE9\xA0\x00\x06metric\x40\x49\x0F\xDB\x00\x00\x00\x00' | nc 127.0.0.1 9999
```

**Проверка в БД:**

```sql
SELECT * FROM metrics;
```

**Юнит-тесты:**

```bash
pytest metric_collector/tests/
```


