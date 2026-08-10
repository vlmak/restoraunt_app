"""
Сервис для работы с меню
"""
from typing import List, Optional
from src.database.connection import DatabaseConnection
from src.models.schemas import Dish


class MenuService:
    def __init__(self):
        self.db = DatabaseConnection()

    """
    Сервис для работы с меню
    """
from typing import List
from src.database.connection import DatabaseConnection
from src.models.schemas import Dish


class MenuService:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_dishes(self):
        """Получить все блюда из меню"""
        result = self.db.execute_query(
            """
            SELECT dish_id, name, price, category
            FROM dishes
            ORDER BY category, name;
            """,
            fetch=True,
            dict_cursor=True
        )
        return [Dish(**row) for row in result]

    def get_dishes_by_category(self, category: str):
        """Получить блюда по категории"""
        result = self.db.execute_query(
            """
            SELECT dish_id, name, price, category
            FROM dishes
            WHERE category = %s
            ORDER BY name;
            """,
            (category,),
            fetch=True,
            dict_cursor=True
        )
        return [Dish(**row) for row in result]

    def get_categories(self):
        """Получить все категории блюд"""
        result = self.db.execute_query(
            """
            SELECT DISTINCT category
            FROM dishes
            ORDER BY category;
            """,
            fetch=True
        )
        return [row[0] for row in result]

    def get_dish_by_id(self, dish_id: int):
        """Получить блюдо по ID"""
        result = self.db.execute_query(
            """
            SELECT dish_id, name, price, category
            FROM dishes
            WHERE dish_id = %s;
            """,
            (dish_id,),
            fetch=True,
            dict_cursor=True
        )
        if result:
            return Dish(**result[0])
        return None