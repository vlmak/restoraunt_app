"""
Сервис для работы с заказами (чеками)
Здесь вся логика проверки и списания ингредиентов
"""
from typing import List, Optional
from decimal import Decimal
from src.database.connection import DatabaseConnection
from src.models.schemas import Check, CheckItem, KitchenOrder


class OrderService:
    def __init__(self):
        self.db = DatabaseConnection()
    #чеки

    def get_open_check_by_table(self, table_id: int):
        """Получить открытый чек для столика"""
        result = self.db.execute_query(
            """
            SELECT check_id, table_id, waiter_id, opened_at, status, total_amount
            FROM checks
            WHERE table_id = %s AND status = 'open'
            LIMIT 1;
            """,
            (table_id,),
            fetch=True,
            dict_cursor=True
        )
        return Check(**result[0]) if result else None

    def get_check_total(self, check_id: int):
        """Получить общую сумму из таблицы checks"""
        result = self.db.execute_query(
            "SELECT total_amount FROM checks WHERE check_id = %s;",
            (check_id,),
            fetch=True
        )
        return float(result[0][0]) if result else 0.0

    #позиции в чеке

    def add_dish_to_check(self, check_id: int, dish_id: int):
        """
        Добавляет блюдо в чек.
        Возвращает ID новой записи или None при ошибке
        """
        try:
            # Проверяем, что чек существует и открыт
            check_exists = self.db.execute_query(
                "SELECT check_id FROM checks WHERE check_id = %s AND status = 'open';",
                (check_id,),
                fetch=True
            )
            if not check_exists:
                print("Чек не найден или не открыт")
                return None

            # Получаем цену блюда
            price_result = self.db.execute_query(
                "SELECT price FROM dishes WHERE dish_id = %s;",
                (dish_id,),
                fetch=True
            )
            if not price_result:
                print(f"Блюдо с ID {dish_id} не найдено")
                return None

            price = float(price_result[0][0])

            # Вставляем новую запись
            result = self.db.execute_query(
                """
                INSERT INTO check_items (check_id, dish_id, price_at_moment, status)
                VALUES (%s, %s, %s, 'pending')
                RETURNING check_item_id;
                """,
                (check_id, dish_id, price),
                fetch=True
            )

            if result and len(result) > 0:
                new_id = result[0][0]
                print(f"Блюдо добавлено с ID: {new_id}")
                return new_id
            else:
                print("Не удалось получить ID новой записи")
                return None

        except Exception as e:
            print(f"Ошибка в add_dish_to_check: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_check_items(self, check_id: int):
        """Получить все позиции в чеке с названиями блюд"""
        result = self.db.execute_query(
            """
            SELECT
                ci.check_item_id,
                ci.check_id,
                ci.dish_id,
                ci.price_at_moment,
                ci.status,
                d.name AS dish_name
            FROM check_items ci
            JOIN dishes d ON ci.dish_id = d.dish_id
            WHERE ci.check_id = %s
            ORDER BY ci.check_item_id;
            """,
            (check_id,),
            fetch=True,
            dict_cursor=True
        )
        return [CheckItem(**row) for row in result]

    def remove_check_item(self, check_item_id: int):
        """Удалить позицию из чека"""
        try:
            self.db.execute_query(
                "DELETE FROM check_items WHERE check_item_id = %s;",
                (check_item_id,)
            )
            return True
        except Exception:
            return False

    #кухня

    def get_pending_orders(self):
        """Получить все блюда со статусом pending для кухни"""
        try:
            result = self.db.execute_query(
                """
                SELECT
                    ci.check_item_id,
                    ci.check_id,
                    d.name AS dish_name,
                    t.table_id,
                    t.table_id AS table_number,
                    ci.status,
                    ci.price_at_moment AS price
                FROM check_items ci
                JOIN dishes d ON ci.dish_id = d.dish_id
                JOIN checks c ON ci.check_id = c.check_id
                JOIN tables t ON c.table_id = t.table_id
                WHERE ci.status = 'pending'
                  AND c.status = 'open'
                ORDER BY ci.check_item_id DESC;
                """,
                fetch=True,
                dict_cursor=True
            )
            return [KitchenOrder(**row) for row in result]
        except Exception as e:
            print(f"❌ Ошибка get_pending_orders: {e}")
            return []

    #провенрка и списание ингредиентов

    def check_ingredients_sufficient(self, dish_id: int):
        """
        Проверяет, хватает ли ингредиентов на складе для блюда.
        Возвращает True если хватает, False если нет.
        """
        try:
            # Получаем все ингредиенты для блюда
            recipes = self.db.execute_query(
                """
                SELECT ingredient_id, quantity_portion
                FROM recipes
                WHERE dish_id = %s;
                """,
                (dish_id,),
                fetch=True,
                dict_cursor=True
            )

            if not recipes:
                print(f"Рецепт для блюда {dish_id} не найден")
                return True

            for recipe in recipes:
                ingredient_id = recipe['ingredient_id']
                needed = recipe['quantity_portion']

                # Проверяем остаток на складе
                stock = self.db.execute_query(
                    "SELECT current_stock FROM ingredients WHERE ingredient_id = %s;",
                    (ingredient_id,),
                    fetch=True
                )

                if not stock:
                    print(f"Ингредиент {ingredient_id} не найден на складе")
                    return False

                available = stock[0][0]
                if available < needed:
                    print(f"Не хватает ингредиента {ingredient_id}: нужно {needed}, есть {available}")
                    return False

            print(f"Все ингредиенты в наличии для блюда {dish_id}")
            return True

        except Exception as e:
            print(f"Ошибка проверки ингредиентов: {e}")
            return False

    def write_off_ingredients(self, dish_id: int, check_id: int):
        """
        Списывает ингредиенты со склада для приготовленного блюда.
        Логирует движения.
        """
        try:
            # Получаем все ингредиенты для блюда
            recipes = self.db.execute_query(
                """
                SELECT ingredient_id, quantity_portion
                FROM recipes
                WHERE dish_id = %s;
                """,
                (dish_id,),
                fetch=True,
                dict_cursor=True
            )

            if not recipes:
                print(f"Рецепт для блюда {dish_id} не найден")
                return False

            for recipe in recipes:
                ingredient_id = recipe['ingredient_id']
                quantity = recipe['quantity_portion']

                # Списываем со склада
                self.db.execute_query(
                    """
                    UPDATE ingredients
                    SET current_stock = current_stock - %s
                    WHERE ingredient_id = %s;
                    """,
                    (quantity, ingredient_id)
                )

                # Логируем движение
                self.db.execute_query(
                    """
                    INSERT INTO ingredient_movements (ingredient_id, quantity, type, movement_datetime)
                    VALUES (%s, %s, 'out', NOW());
                    """,
                    (ingredient_id, -quantity)
                )

            print(f"Ингредиенты для блюда {dish_id} списаны успешно")
            return True

        except Exception as e:
            print(f"Ошибка списания ингредиентов: {e}")
            return False

    #кнопки для повара

    def start_cooking(self, check_item_id: int) -> str:
        """
        Повар нажал 'Начать готовить'.
        """
        try:
            # 1. Получаем информацию о позиции
            item = self.db.execute_query(
                """
                SELECT 
                    ci.check_id, 
                    ci.dish_id, 
                    ci.status, 
                    d.name AS dish_name
                FROM check_items ci
                JOIN dishes d ON ci.dish_id = d.dish_id
                WHERE ci.check_item_id = %s;
                """,
                (check_item_id,),
                fetch=True,
                dict_cursor=True
            )

            if not item:
                return f"Позиция с ID {check_item_id} не найдена"

            item = item[0]
            check_id = item['check_id']
            dish_id = item['dish_id']
            dish_name = item['dish_name']
            current_status = item['status']

            print(f"Блюдо: {dish_name}, статус: {current_status}")

            # 2. Проверяем статус
            if current_status == 'ready':
                return f"Блюдо '{dish_name}' уже готово"
            if current_status == 'cancelled':
                return f"Блюдо '{dish_name}' уже отменено"
            if current_status != 'pending':
                return f"Блюдо нельзя приготовить (статус: {current_status})"

            # 3. Проверяем ингредиенты
            if not self.check_ingredients_sufficient(dish_id):
                return f"Недостаточно ингредиентов для блюда '{dish_name}'"

            # 4. Списываем ингредиенты
            if not self.write_off_ingredients(dish_id, check_id):
                return f"Не удалось списать ингредиенты для блюда '{dish_name}'"

            # 5. Обновляем статус блюда на 'ready'
            self.db.execute_query(
                """
                UPDATE check_items
                SET status = 'ready'
                WHERE check_item_id = %s;
                """,
                (check_item_id,)
            )

            # 6. Проверяем, что статус изменился
            check_status = self.db.execute_query(
                "SELECT status FROM check_items WHERE check_item_id = %s;",
                (check_item_id,),
                fetch=True
            )

            if check_status and check_status[0][0] == 'ready':
                print(f"Блюдо '{dish_name}' готово!")
                return f"Блюдо '{dish_name}' готово к подаче!"
            else:
                return f"Статус блюда '{dish_name}' не обновился"

        except Exception as e:
            print(f"Критическая ошибка в start_cooking: {e}")
            import traceback
            traceback.print_exc()
            return f"Ошибка: {str(e)}"

    def cancel_cooking(self, check_item_id: int):
        """
        Повар нажал 'Отмена'
        """
        try:
            # 1. Получаем информацию о позиции
            item = self.db.execute_query(
                """
                SELECT 
                    ci.check_id, 
                    ci.dish_id, 
                    ci.status, 
                    d.name AS dish_name
                FROM check_items ci
                JOIN dishes d ON ci.dish_id = d.dish_id
                WHERE ci.check_item_id = %s;
                """,
                (check_item_id,),
                fetch=True,
                dict_cursor=True
            )

            if not item:
                return f"Позиция с ID {check_item_id} не найдена"

            item = item[0]
            dish_name = item['dish_name']
            current_status = item['status']

            # 2. Проверяем статус
            if current_status == 'ready':
                return f"Нельзя отменить готовое блюдо '{dish_name}'"
            if current_status == 'cancelled':
                return f"Блюдо '{dish_name}' уже отменено"

            # 3. Меняем статус на 'cancelled'
            self.db.execute_query(
                """
                UPDATE check_items
                SET status = 'cancelled'
                WHERE check_item_id = %s;
                """,
                (check_item_id,)
            )

            print(f"Блюдо '{dish_name}' отменено")
            return f"Блюдо '{dish_name}' отменено"

        except Exception as e:
            print(f"Ошибка в cancel_cooking: {e}")
            import traceback
            traceback.print_exc()
            return f"Ошибка: {str(e)}"