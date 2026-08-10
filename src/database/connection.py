"""
Модуль управления подключением к PostgreSQL
Использует паттерн Singleton для управления соединением
"""

import os
import psycopg2
from psycopg2 import OperationalError, DatabaseError
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

class DatabaseConnection:
    """
    Класс-синглтон для управления подключением к базе данных.
    Обеспечивает единое соединение на всё приложение.
    """
    _instanse = None
    
    def __new__(cls):
        if cls._instanse is None:
            cls._instanse = super().__new__(cls)
        return cls._instanse
    def __init__(self):
        self._connection = None
        self._cursor = None
    def _connect(self):
        if self._connection is not None and self._connection.closed:
            return self._connection
        try:
            self._connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "restoraunt"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "")
            )
            print("Подключение к PostgreSQL установлено")
        except:
            print("Ошибка подключения")
    def get_cursor(self, dict_cursor=False):
        if self._connection is None or self._connection.closed:
            self._connect()
        
        if dict_cursor:
            return self._connection.cursor(cursor_factory=RealDictCursor)
        return self._connection.cursor()
    def execute_query(self, query, params=None, fetch=False, dict_cursor=False):
        cursor = None
        try:
            if self._connection is None or self._connection.closed:
                self._connect()
            
            if dict_cursor:
                cursor = self._connection.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = self._connection.cursor()
            
            cursor.execute(query, params or ())
            
            # 👇 ВСЕГДА ДЕЛАЕМ COMMIT, ДАЖЕ ЕСЛИ FETCH=True
            self._connection.commit()
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                return cursor.rowcount
                
        except Exception as e:
            if self._connection:
                self._connection.rollback()
            print(f"❌ Ошибка execute_query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    def close(self):
        """Закрывает соединение с базой данных"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            print("Соединение с БД закрыто")
            self._connection = None
    @property
    def is_connected(self):
        """Проверяет, активно ли соединение"""
        return self._connection is not None and not self._connection.closed