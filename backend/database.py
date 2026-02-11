import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                return True
        except Error as e:
            logger.error(f"Error while connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")
    
    def execute_query(self, query, params=None, commit=False):
        """Execute a query"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if commit:
                self.connection.commit()
                logger.info(f"Query executed and committed")
                return cursor.rowcount
            else:
                result = cursor.fetchall()
                cursor.close()
                return result
        except Error as e:
            logger.error(f"Query execution error: {e}")
            if commit:
                self.connection.rollback()
            return None
    
    def execute_insert(self, query, params=None):
        """Insert a record and return the last inserted ID"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            logger.info(f"Insert successful, last_id: {last_id}")
            return last_id if last_id > 0 else 1  # Return at least 1 if insert succeeded
        except Error as e:
            logger.error(f"Insert error: {e}")
            self.connection.rollback()
            return None
    
    def close(self):
        """Close the connection"""
        self.disconnect()

# Global database instance
db = Database()
