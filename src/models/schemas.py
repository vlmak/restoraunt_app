"""
Модели данных для ресторанного приложения
Основаны на структуре базы данных
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class Table:
    """Столик в ресторане"""
    table_id: int
    capacity: int
    status: str
    cleaning_started_at: Optional[datetime] = None


@dataclass
class Employee:
    """Сотрудник ресторана"""
    employee_id: int
    last_name: str
    first_name: str
    role: str 
    phone: str


@dataclass
class Reservation:
    """Бронирование столика"""
    reservation_id: int
    table_id: int
    guest_name: str
    phone: str
    reservation_time: datetime
    persons: int
    status: str 


@dataclass
class Check:
    """Чек/заказ"""
    check_id: int
    table_id: int
    waiter_id: int
    opened_at: datetime
    status: str 
    total_amount: Decimal = Decimal('0')
    closed_at: Optional[datetime] = None


@dataclass
class CheckItem:
    check_item_id: int
    check_id: int
    dish_id: int
    price_at_moment: Decimal
    status: str
    dish_name: Optional[str] = None

@dataclass
class Dish:
    """Блюдо из меню"""
    dish_id: int
    name: str
    price: Decimal
    category: str


@dataclass
class Ingredient:
    ingredient_id: int
    name: str
    unit: str
    min_stock: float
    current_stock: float
    price: float = 0.0


@dataclass
class Recipe:
    """Рецепт (связь блюда и ингредиентов)"""
    dish_id: int
    ingredient_id: int
    quantity_portion: Decimal


@dataclass
class Supplier:
    """Поставщик"""
    supplier_id: int
    name: str
    contacts: Optional[str] = None


@dataclass
class SupplierOrder:
    """Заказ поставщику"""
    order_id: int
    supplier_id: int
    order_date: datetime
    status: str  
    total_amount: Decimal = Decimal('0')


@dataclass
class SupplierOrderItem:
    """Позиция в заказе поставщику"""
    order_item_id: int
    order_id: int
    ingredient_id: int
    quantity: Decimal
    unit_price: Decimal


@dataclass
class IngredientMovement:
    """Движение ингредиента"""
    movement_id: int
    ingredient_id: int
    quantity: Decimal
    type: str  
    movement_datetime: datetime

@dataclass
class TableWithOrder:
    """Столик с информацией о текущем заказе (для схемы зала)"""
    table_id: int
    capacity: int
    status: str
    check_id: Optional[int] = None
    total_amount: Optional[Decimal] = None
    waiter_name: Optional[str] = None


@dataclass
class KitchenOrder:
    """Заказ для кухонного экрана (повар)"""
    check_item_id: int
    check_id: int
    dish_name: str
    table_id: int
    table_number: int
    status: str
    price: float


@dataclass
class StockAlert:
    """Уведомление о низком запасе"""
    ingredient_id: int
    name: str
    current_stock: Decimal
    min_stock: Decimal
    unit: str
    shortage: Decimal