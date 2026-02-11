import psycopg2
import logging
import os
import time

# Configure module-level logger
logger = logging.getLogger(__name__)

class Database:
    """
    Handles PostgreSQL connections, schema initialization, and data ingestion.
    Implements Retry Pattern for fault tolerance.
    """
    def __init__(self):
        # Retrieve credentials from Docker environment variables
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "password")
        self.db_name = os.getenv("POSTGRES_DB", "cstm_db")
        self.conn = None

    def connect(self):
        """Establishes connection to the database with exponential backoff."""
        max_retries = 5
        for i in range(max_retries):
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    dbname=self.db_name
                )
                logger.info("Successfully established connection to PostgreSQL.")
                return True
            except Exception as e:
                logger.warning(f"Database connection attempt {i+1}/{max_retries} failed: {e}")
                time.sleep(5) # Wait before retrying
        return False

    def init_db(self):
        """Initializes database schema if not exists."""
        if not self.conn:
            return
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS metrics (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cpu_usage FLOAT,
            ram_usage FLOAT,
            gpu_temp INT,
            btc_price FLOAT,
            eth_price FLOAT
        );
        """
        try:
            cur = self.conn.cursor()
            cur.execute(create_table_query)
            self.conn.commit()
            logger.info("Database schema verified (Tables initialized).")
            cur.close()
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")

    def save_metrics(self, cpu, ram, gpu_temp, btc, eth):
        """Persists a new telemetry record."""
        if not self.conn:
            return

        insert_query = """
        INSERT INTO metrics (cpu_usage, ram_usage, gpu_temp, btc_price, eth_price)
        VALUES (%s, %s, %s, %s, %s);
        """
        try:
            cur = self.conn.cursor()
            cur.execute(insert_query, (cpu, ram, gpu_temp, btc, eth))
            self.conn.commit()
            logger.info("Telemetry data persisted to database.")
            cur.close()
        except Exception as e:
            logger.error(f"Failed to insert record: {e}")
            self.conn.rollback() # Rollback transaction to maintain integrity