import mysql.connector
import os
from typing import Optional
from mysql.connector import pooling
from dotenv import load_dotenv
# Singleton pattern para el pool de conexiones
class MySQLConnectionPool:
    _instance: Optional[pooling.MySQLConnectionPool] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            # Usar variables de entorno o valores predeterminados
            host = os.getenv("MYSQL_HOST", "localhost")
            user = os.getenv("MYSQL_USER", "root")
            password = os.getenv("MYSQL_PASSWORD", "")
            database = os.getenv("MYSQL_DATABASE", "kpib")
            port = int(os.getenv("DB_PORT", "3306"))

            cls._instance = pooling.MySQLConnectionPool(
                pool_name="kpib_pool",
                pool_size=5,
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
            )
            print(f"MySQL pool created: connected to {database} on {host}:{port}")
        return cls._instance

def get_db_connection():
    """Obtiene una conexión del pool"""
    try:
        pool = MySQLConnectionPool.get_instance()
        return pool.get_connection()
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        raise