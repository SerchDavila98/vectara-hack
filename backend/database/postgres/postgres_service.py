import os
import psycopg2
from contextlib import closing

class DatabaseConfig:
    """
    Configuration for the database connection.
    """
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_SSLMODE = os.getenv('DB_SSLMODE')

    @classmethod
    def get_db_config(cls):
        """
        Returns a dictionary of database configuration parameters.
        """
        return {
            "host": cls.DB_HOST,
            "port": cls.DB_PORT,
            "dbname": cls.DB_NAME,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "sslmode": cls.DB_SSLMODE
        }

class PostgresService:
    def __init__(self, db_config):
        """
        Initialize the PostgresService with database configuration.
        """
        self.db_config = db_config

    def get_db_connection(self):
        """
        Creates and returns a new database connection using the instance's configuration.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"Unable to connect to the database: {e}")
            return None

    def insert_chat_history(self, username, message, response):
        """
        Inserts a new chat record into the chat_history table.
        """
        query = """
        INSERT INTO chat_history (timestamp, username, message, response)
        VALUES (NOW(), %s, %s, %s);
        """
        with closing(self.get_db_connection()) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username, message, response))
                conn.commit()

    def get_chat_history(self, username):
        """
        Retrieves chat history for a specific user.
        """
        query = "SELECT * FROM chat_history WHERE username = %s;"
        with closing(self.get_db_connection()) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                return cursor.fetchall()  # Returns a list of tuples

    def execute_generic_query(self, query, params=None):
        """
        Executes a generic SQL query.
        """
        with closing(self.get_db_connection()) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()  # For SELECT queries
                else:
                    conn.commit()  # For INSERT, UPDATE, DELETE queries
                    return cursor.rowcount  # Returns the number of rows affected

