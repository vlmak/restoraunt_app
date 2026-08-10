"""
Сервис для работы с поставщиками и заказами
"""
from typing import List, Optional
from decimal import Decimal
from src.database.connection import DatabaseConnection
from src.models.schemas import Supplier, SupplierOrder, SupplierOrderItem, Ingredient


class SupplierService:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_suppliers(self):
        result = self.db.execute_query(
            "SELECT supplier_id, name, contacts FROM suppliers ORDER BY name;",
            fetch=True,
            dict_cursor=True
        )
        return [Supplier(**row) for row in result]

    def get_low_stock_ingredients(self):
        try:
            result = self.db.execute_query(
                """
                SELECT ingredient_id, name, unit, min_stock, current_stock, price
                FROM ingredients
                WHERE current_stock < min_stock
                ORDER BY (min_stock - current_stock) DESC;
                """,
                fetch=True,
                dict_cursor=True
            )
            print(f"get_low_stock_ingredients: найдено {len(result)} записей")
            return [Ingredient(**row) for row in result]
        except Exception as e:
            print(f"Ошибка get_low_stock_ingredients: {e}")
            return []

    def create_supplier_order(self, supplier_id: int):
        result = self.db.execute_query(
            """
            INSERT INTO supplier_orders (supplier_id, order_date, status, total_amount)
            VALUES (%s, NOW(), 'draft', 0)
            RETURNING order_id;
            """,
            (supplier_id,),
            fetch=True
        )
        return result[0][0] if result else None

    def add_item_to_order(self, order_id: int, ingredient_id: int, quantity: float):
        try:
            self.db.execute_query(
                """
                INSERT INTO supplier_order_items (order_id, ingredient_id, quantity, unit_price)
                SELECT %s, %s, %s, price
                FROM ingredients
                WHERE ingredient_id = %s;
                """,
                (order_id, ingredient_id, quantity, ingredient_id)
            )
            self.db.execute_query("SELECT recalc_supplier_order_total(%s);", (order_id,))
            return True
        except Exception as e:
            print(f"Ошибка добавления позиции: {e}")
            return False

    def get_all_orders(self):
        """Получить все заказы поставщикам (как словари)"""
        result = self.db.execute_query(
            """
            SELECT 
                so.order_id,
                so.supplier_id,
                so.order_date,
                so.total_amount,
                so.status,
                s.name AS supplier_name
            FROM supplier_orders so
            JOIN suppliers s ON so.supplier_id = s.supplier_id
            ORDER BY so.order_id DESC;
            """,
            fetch=True,
            dict_cursor=True
        )
        return result

    def get_order_items(self, order_id: int):
        result = self.db.execute_query(
            """
            SELECT 
                soi.order_item_id,
                soi.order_id,
                soi.ingredient_id,
                i.name AS ingredient_name,
                soi.quantity,
                soi.unit_price,
                soi.quantity * soi.unit_price AS line_total
            FROM supplier_order_items soi
            JOIN ingredients i ON soi.ingredient_id = i.ingredient_id
            WHERE soi.order_id = %s
            ORDER BY soi.order_item_id;
            """,
            (order_id,),
            fetch=True,
            dict_cursor=True
        )
        return result

    def send_order(self, order_id: int) -> bool:
        try:
            self.db.execute_query(
                "UPDATE supplier_orders SET status = 'sent' WHERE order_id = %s;",
                (order_id,)
            )
            return True
        except Exception:
            return False

    def receive_order(self, order_id: int):
        """Принять заказ"""
        try:
            # 1. Получаем позиции заказа
            items = self.db.execute_query(
                """
                SELECT ingredient_id, quantity
                FROM supplier_order_items
                WHERE order_id = %s;
                """,
                (order_id,),
                fetch=True
            )

            if not items:
                print(f"❌ Заказ {order_id} пуст")
                return False

            # 2. Обновляем остатки на складе
            for item in items:
                ing_id, qty = item
                
                # Обновляем current_stock в ingredients
                self.db.execute_query(
                    """
                    UPDATE ingredients
                    SET current_stock = current_stock + %s
                    WHERE ingredient_id = %s;
                    """,
                    (qty, ing_id)
                )
                
                # Записываем движение в ingredient_movements
                self.db.execute_query(
                    """
                    INSERT INTO ingredient_movements (ingredient_id, quantity, type, movement_datetime)
                    VALUES (%s, %s, 'in', NOW());
                    """,
                    (ing_id, qty)
                )

            # 3. Меняем статус заказа
            self.db.execute_query(
                "UPDATE supplier_orders SET status = 'received' WHERE order_id = %s;",
                (order_id,)
            )
            
            print(f"Заказ {order_id} принят, остатки обновлены")
            return True
            
        except Exception as e:
            print(f"Ошибка приёма заказа: {e}")
            return False

    def cancel_order(self, order_id: int):
        """Отменить заказ"""
        try:
            # Проверяем, можно ли отменить
            status_check = self.db.execute_query(
                "SELECT status FROM supplier_orders WHERE order_id = %s;",
                (order_id,),
                fetch=True
            )
            
            if not status_check:
                print(f"Заказ {order_id} не найден")
                return False
            
            current_status = status_check[0][0]
            
            if current_status == 'received':
                print(f"Заказ {order_id} уже получен, нельзя отменить")
                return False
            
            if current_status == 'cancelled':
                print(f"Заказ {order_id} уже отменён")
                return False
            
            # Меняем статус
            self.db.execute_query(
                "UPDATE supplier_orders SET status = 'cancelled' WHERE order_id = %s;",
                (order_id,)
            )
            
            print(f"Заказ {order_id} отменён")
            return True
            
        except Exception as e:
            print(f"Ошибка отмены заказа: {e}")
            return False