"""
Сервис для авторизации пользователей
"""
from typing import Optional
from src.database.connection import DatabaseConnection
from src.models.schemas import Employee


class AuthService:
    def __init__(self):
        self.db = DatabaseConnection()

    def login(self, login: str, password: str):
        """
        Проверяет логин и пароль, возвращает сотрудника или None.
        логин = first_name + '.' + last_name
        Пароль = phone
        """
        result = self.db.execute_query(
            """
            SELECT 
                employee_id, 
                last_name, 
                first_name, 
                role, 
                phone
            FROM employees
            WHERE LOWER(first_name || '.' || last_name) = %s
              AND phone = %s;
            """,
            (login.lower(), password),
            fetch=True,
            dict_cursor=True
        )
        
        if result:
            return Employee(**result[0])
        return None

    def get_employee_by_id(self, employee_id: int):
        """Получить сотрудника по ID"""
        result = self.db.execute_query(
            """
            SELECT employee_id, last_name, first_name, role, phone
            FROM employees
            WHERE employee_id = %s;
            """,
            (employee_id,),
            fetch=True,
            dict_cursor=True
        )
        if result:
            return Employee(**result[0])
        return None
    def get_all_employees(self):
        """Получить всех сотрудников"""
        try:
            result = self.db.execute_query(
                """
                SELECT employee_id, first_name, last_name, role, phone
                FROM employees
                ORDER BY last_name, first_name;
                """,
                fetch=True,
                dict_cursor=True
            )
            return [Employee(**row) for row in result]
        except Exception as e:
            print(f"Ошибка получения сотрудников: {e}")
            return []