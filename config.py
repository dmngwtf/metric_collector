from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

class Config:
    HOST = os.getenv("SERVER_HOST", "127.0.0.1")
    PORT = int(os.getenv("SERVER_PORT", 9999))
    DB_FLUSH_INTERVAL = int(os.getenv("DB_FLUSH_INTERVAL", 5))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DB_CONNECTION = {
        "dbname": os.getenv("TARGET_DB_NAME", "metrics_db"),
        "user": os.getenv("TARGET_DB_USER", "postgres"),
        "password": os.getenv("TARGET_DB_PASSWORD", "password"),
        "host": os.getenv("TARGET_DB_HOST", "localhost"),
        "port": os.getenv("TARGET_DB_PORT", "5432")
    }