from scheduler.poller import start_polling
import asyncio
import psycopg2
import os
from utils.logger import setup_logger

logger = setup_logger(__name__)

if __name__ == "__main__":
    
    # Entry point of application
    # Calls functions to connect to Petkit
    # Log onto DB
    logger.info("Starting Petkit data polling application...")
    logger.info("Connecting to database...")

    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_polling(conn))
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")


    