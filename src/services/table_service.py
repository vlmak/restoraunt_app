"""
Сервис для работы со столиками
"""
from typing import List, Optional
from src.database.connection import DatabaseConnection
from src.models.schemas import Table, TableWithOrder


class TableService:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_tables(self):
        """Получить все столики"""
        result = self.db.execute_query(
            """
            SELECT table_id, capacity, status, cleaning_started_at
            FROM tables
            ORDER BY table_id;
            """,
            fetch=True,
            dict_cursor=True
        )
        return [Table(**row) for row in result]

    def get_table_by_id(self, table_id: int):
        """Получить столик по ID"""
        result = self.db.execute_query(
            """
            SELECT table_id, capacity, status, cleaning_started_at
            FROM tables
            WHERE table_id = %s;
            """,
            (table_id,),
            fetch=True,
            dict_cursor=True
        )
        if result:
            return Table(**result[0])
        return None

    def update_table_status(self, table_id: int, status: str):
        """Принудительно обновляет статус столика"""
        try:
            self.db.execute_query(
                "UPDATE tables SET status = %s WHERE table_id = %s;",
                (status, table_id)
            )
            return True
        except Exception as e:
            print(f"Ошибка обновления статуса столика: {e}")
            return False

    def get_free_tables(self):
        """Получить все свободные столики"""
        result = self.db.execute_query(
            """
            SELECT table_id, capacity, status, cleaning_started_at
            FROM tables
            WHERE status = 'free'
            ORDER BY table_id;
            """,
            fetch=True,
            dict_cursor=True
        )
        return [Table(**row) for row in result]

    def get_tables_with_orders(self):
        """Получить все столики с информацией о текущем заказе"""
        result = self.db.execute_query(
            """
            SELECT
                t.table_id,
                t.capacity,
                t.status,
                c.check_id,
                c.total_amount,
                e.first_name || ' ' || e.last_name AS waiter_name
            FROM tables t
            LEFT JOIN checks c ON t.table_id = c.table_id AND c.status = 'open'
            LEFT JOIN employees e ON c.waiter_id = e.employee_id
            ORDER BY t.table_id;
            """,
            fetch=True,
            dict_cursor=True
        )
        return [TableWithOrder(**row) for row in result]

    def create_reservation(self, table_id: int, guest_name: str, phone: str,
                           reservation_time, persons: int):
        """Создаёт бронь столика"""
        try:
            self.db.execute_query(
                """
                INSERT INTO reservations (table_id, guest_name, phone, reservation_time, persons, status)
                VALUES (%s, %s, %s, %s, %s, 'active');
                """,
                (table_id, guest_name, phone, reservation_time, persons)
            )
            return True
        except Exception as e:
            print(f"Ошибка создания брони: {e}")
            return False

    def cancel_reservation(self, table_id: int):
        """Отменяет активную бронь столика"""
        try:
            # Сначала проверяем, есть ли активная бронь
            check = self.db.execute_query(
                """
                SELECT reservation_id FROM reservations
                WHERE table_id = %s AND status = 'active'
                LIMIT 1;
                """,
                (table_id,),
                fetch=True
            )
            
            if not check:
                print(f"Нет активной брони для столика {table_id}")
                return False
            
            # Отменяем бронь
            self.db.execute_query(
                """
                UPDATE reservations
                SET status = 'cancelled'
                WHERE table_id = %s AND status = 'active';
                """,
                (table_id,)
            )
            return True
            
        except Exception as e:
            print(f"Ошибка отмены брони: {e}")
            return False
    def get_cleaning_info(self, table_id: int):
        """Получить информацию о столике, который требует уборки"""
        try:
            result = self.db.execute_query(
                """
                SELECT 
                    cleaning_started_at,
                    EXTRACT(EPOCH FROM (NOW() - cleaning_started_at)) / 60 AS minutes_since
                FROM tables
                WHERE table_id = %s AND status = 'needs_cleaning';
                """,
                (table_id,),
                fetch=True,
                dict_cursor=True
            )
            
            if result:
                minutes = result[0].get('minutes_since', 0)
                if minutes is not None:
                    minutes = round(minutes, 1)
                    result[0]['time_since'] = f"{minutes} мин."
                else:
                    result[0]['time_since'] = "неизвестно"
                return result[0]
            return {'time_since': 'неизвестно'}
        except Exception as e:
            print(f"Ошибка получения информации об уборке: {e}")
            return {'time_since': 'неизвестно'}

    def get_current_order_by_table(self, table_id: int):
        """Получить текущий заказ для столика"""
        try:
            result = self.db.execute_query(
                """
                SELECT 
                    c.check_id,
                    c.total_amount,
                    c.opened_at,
                    e.first_name || ' ' || e.last_name AS waiter_name
                FROM checks c
                LEFT JOIN employees e ON c.waiter_id = e.employee_id
                WHERE c.table_id = %s AND c.status = 'open'
                ORDER BY c.opened_at DESC
                LIMIT 1;
                """,
                (table_id,),
                fetch=True,
                dict_cursor=True
            )
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка в get_current_order_by_table: {e}")
            return None

    def get_check_items(self, check_id: int):
        """Получить позиции в чеке"""
        try:
            result = self.db.execute_query(
                """
                SELECT 
                    d.name AS dish_name,
                    ci.quantity,
                    ci.price_at_moment
                FROM check_items ci
                JOIN dishes d ON ci.dish_id = d.dish_id
                WHERE ci.check_id = %s;
                """,
                (check_id,),
                fetch=True,
                dict_cursor=True
            )
            return result
        except Exception as e:
            print(f"Ошибка в get_check_items: {e}")
            return []

    def get_active_reservation(self, table_id: int):
        """Получить активную бронь для столика"""
        result = self.db.execute_query(
            """
            SELECT 
                reservation_id,
                guest_name,
                phone,
                reservation_time,
                persons,
                status
            FROM reservations
            WHERE table_id = %s AND status = 'active'
            ORDER BY reservation_time
            LIMIT 1;
            """,
            (table_id,),
            fetch=True,
            dict_cursor=True
        )
        return result[0] if result else None