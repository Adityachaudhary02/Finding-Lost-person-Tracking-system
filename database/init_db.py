import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Adi@808389',
    'port': 3306
}

def create_database():
    """Create database and tables"""
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        logger.info("Reading schema file...")
        schema_path = 'database/schema.sql'
        with open(schema_path, 'r') as f:
            sql_content = f.read()
        
        # Split SQL statements and execute them
        statements = sql_content.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement:
                logger.info(f"Executing: {statement[:50]}...")
                cursor.execute(statement)
        
        connection.commit()
        logger.info("Database and tables created successfully!")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        logger.error(f"Error creating database: {e}")
        raise

if __name__ == "__main__":
    create_database()
