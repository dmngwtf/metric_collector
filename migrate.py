import psycopg2
from psycopg2 import sql
import structlog
from dotenv import load_dotenv
import os

load_dotenv()

logger = structlog.get_logger()

# Конфигурация подключения (административные параметры для создания базы)
ADMIN_DB_CONFIG = {
    "dbname": os.getenv("ADMIN_DB_NAME", "postgres"),
    "user": os.getenv("ADMIN_DB_USER", "postgres"),
    "password": os.getenv("ADMIN_DB_PASSWORD", "password"),
    "host": os.getenv("ADMIN_DB_HOST", "localhost"),
    "port": os.getenv("ADMIN_DB_PORT", "5432")
}

# Конфигурация целевой базы данных
TARGET_DB_CONFIG = {
    "dbname": os.getenv("TARGET_DB_NAME", "metrics_db"),
    "user": os.getenv("TARGET_DB_USER", "postgres"),
    "password": os.getenv("TARGET_DB_PASSWORD", "password"),
    "host": os.getenv("TARGET_DB_HOST", "localhost"),
    "port": os.getenv("TARGET_DB_PORT", "5432")
}

def create_database():
    """Создает базу данных metrics_db, если она не существует."""
    try:
        conn = psycopg2.connect(**ADMIN_DB_CONFIG)
        conn.set_session(autocommit=True)
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(TARGET_DB_CONFIG["dbname"]))
        )
        logger.info(f"Database {TARGET_DB_CONFIG['dbname']} created")
    except psycopg2.errors.DuplicateDatabase:
        logger.info(f"Database {TARGET_DB_CONFIG['dbname']} already exists")
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def create_metrics_table():
    """Создает таблицу metrics и преобразует её в гипертаблицу TimescaleDB, если ещё не преобразована."""
    try:
        conn = psycopg2.connect(**TARGET_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                timestamp TIMESTAMPTZ NOT NULL,
                metric_name TEXT NOT NULL,
                value DOUBLE PRECISION NOT NULL
            );
        """)
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM timescaledb_information.hypertables
                WHERE hypertable_name = 'metrics'
            );
        """)
        is_hypertable = cursor.fetchone()[0]
        if not is_hypertable:
            cursor.execute("SELECT create_hypertable('metrics', 'timestamp');")
            logger.info("Table metrics created and configured as hypertable")
        else:
            logger.info("Table metrics is already a hypertable")
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to create metrics table: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer()
        ]
    )
    try:
        create_database()
        create_metrics_table()
        logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    main()