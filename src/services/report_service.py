"""
Сервис для отчётов
"""
from src.database.connection import DatabaseConnection


class ReportService:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_revenue(self, date_from: str, date_to: str):
        """Получить выручку за период"""
        result = self.db.execute_query(
            """
            SELECT 
                DATE(closed_at) AS date,
                COUNT(*) AS orders_count,
                SUM(total_amount) AS revenue
            FROM checks
            WHERE status = 'closed'
              AND closed_at BETWEEN %s AND %s
            GROUP BY DATE(closed_at)
            ORDER BY date DESC;
            """,
            (date_from, date_to),
            fetch=True,
            dict_cursor=True
        )
        return result

    def get_popular_dishes(self, date_from: str, date_to: str):
        """Получить популярные блюда за период"""
        result = self.db.execute_query(
            """
            SELECT 
                d.name,
                d.category,
                COUNT(*) AS count,
                SUM(ci.price_at_moment) AS revenue
            FROM check_items ci
            JOIN dishes d ON ci.dish_id = d.dish_id
            JOIN checks c ON ci.check_id = c.check_id
            WHERE c.status = 'closed'
              AND c.closed_at BETWEEN %s AND %s
              AND ci.status = 'ready'
            GROUP BY d.dish_id, d.name, d.category
            ORDER BY count DESC
            LIMIT 20;
            """,
            (date_from, date_to),
            fetch=True,
            dict_cursor=True
        )
        return result

    def get_table_load(self, date_from: str, date_to: str):
        """Получить загрузку столиков за период"""
        result = self.db.execute_query(
            """
            SELECT 
                t.table_id,
                COUNT(*) AS orders_count,
                COALESCE(
                    AVG(EXTRACT(EPOCH FROM (c.closed_at - c.opened_at)) / 60),
                    0
                ) AS avg_time
            FROM tables t
            LEFT JOIN checks c ON t.table_id = c.table_id
                AND c.status = 'closed'
                AND c.closed_at BETWEEN %s AND %s
            GROUP BY t.table_id
            ORDER BY orders_count DESC;
            """,
            (date_from, date_to),
            fetch=True,
            dict_cursor=True
        )
        return result

    def get_ingredient_usage(self, date_from: str, date_to: str):
        """Получить расход ингредиентов за период"""
        result = self.db.execute_query(
            """
            SELECT 
                i.name,
                i.unit,
                i.current_stock,
                i.min_stock,
                COALESCE(SUM(im.quantity), 0) * -1 AS used
            FROM ingredients i
            LEFT JOIN ingredient_movements im ON i.ingredient_id = im.ingredient_id
                AND im.type = 'out'
                AND im.movement_datetime BETWEEN %s AND %s
            GROUP BY i.ingredient_id, i.name, i.unit, i.current_stock, i.min_stock
            ORDER BY used DESC;
            """,
            (date_from, date_to),
            fetch=True,
            dict_cursor=True
        )
        return result