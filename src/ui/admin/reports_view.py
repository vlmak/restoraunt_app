"""
Виджет отчётов
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QDateEdit, QPushButton, QHeaderView,
    QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from src.services.report_service import ReportService


class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        self.report_service = ReportService()
        self.init_ui()

    def init_ui(self):
        """Создаёт интерфейс"""
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Заголовок
        title = QLabel("📊 Отчёты")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #5D4037;")
        layout.addWidget(title)

        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("📅 Период:"))
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setCalendarPopup(True)
        period_layout.addWidget(self.date_from)

        period_layout.addWidget(QLabel("—"))
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        period_layout.addWidget(self.date_to)

        update_btn = QPushButton("🔄 Обновить")
        update_btn.clicked.connect(self.load_reports)
        period_layout.addWidget(update_btn)

        period_layout.addStretch()
        layout.addLayout(period_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.tabs)

        self.revenue_tab = self.create_revenue_tab()
        self.tabs.addTab(self.revenue_tab, "💰 Выручка")

        self.dishes_tab = self.create_dishes_tab()
        self.tabs.addTab(self.dishes_tab, "🍽️ Популярные блюда")

        self.tables_tab = self.create_tables_tab()
        self.tabs.addTab(self.tables_tab, "🪑 Загрузка залов")

        self.ingredients_tab = self.create_ingredients_tab()
        self.tabs.addTab(self.ingredients_tab, "📦 Расход ингредиентов")

        self.load_reports()

    def create_revenue_tab(self):
        """Создаёт вкладку с выручкой"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Суммарная выручка
        self.total_revenue_label = QLabel("💰 Общая выручка: 0 ₽")
        self.total_revenue_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.total_revenue_label.setStyleSheet("color: #2E7D32; padding: 10px; background-color: #E8F5E9; border-radius: 8px;")
        layout.addWidget(self.total_revenue_label)

        # Количество заказов
        self.total_orders_label = QLabel("📋 Всего заказов: 0")
        self.total_orders_label.setFont(QFont("Segoe UI", 14))
        self.total_orders_label.setStyleSheet("color: #5D4037; padding: 5px;")
        layout.addWidget(self.total_orders_label)

        # Таблица по дням
        self.revenue_table = QTableWidget()
        self.revenue_table.setColumnCount(3)
        self.revenue_table.setHorizontalHeaderLabels(["Дата", "Кол-во заказов", "Выручка"])
        self.revenue_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.revenue_table.setAlternatingRowColors(True)
        layout.addWidget(self.revenue_table)

        return widget

    def create_dishes_tab(self):
        """Создаёт вкладку с популярными блюдами"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.dishes_table = QTableWidget()
        self.dishes_table.setColumnCount(4)
        self.dishes_table.setHorizontalHeaderLabels(["Блюдо", "Категория", "Кол-во заказов", "Выручка"])
        self.dishes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dishes_table.setAlternatingRowColors(True)
        layout.addWidget(self.dishes_table)

        return widget

    def create_tables_tab(self):
        """Создаёт вкладку с загрузкой залов"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.tables_table = QTableWidget()
        self.tables_table.setColumnCount(3)
        self.tables_table.setHorizontalHeaderLabels(["Столик", "Кол-во заказов", "Среднее время (мин)"])
        self.tables_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tables_table.setAlternatingRowColors(True)
        layout.addWidget(self.tables_table)

        return widget

    def create_ingredients_tab(self):
        """Создаёт вкладку с расходом ингредиентов"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(4)
        self.ingredients_table.setHorizontalHeaderLabels(["Ингредиент", "Расход", "Остаток", "Статус"])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ingredients_table.setAlternatingRowColors(True)
        layout.addWidget(self.ingredients_table)

        return widget

    def load_reports(self):
        """Загружает все отчёты"""
        try:
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")

            # Выручка
            revenue_data = self.report_service.get_revenue(date_from, date_to)
            self.load_revenue(revenue_data)

            # Блюда
            dishes_data = self.report_service.get_popular_dishes(date_from, date_to)
            self.load_dishes(dishes_data)

            # Загрузка залов
            tables_data = self.report_service.get_table_load(date_from, date_to)
            self.load_tables(tables_data)

            # Ингредиенты
            ingredients_data = self.report_service.get_ingredient_usage(date_from, date_to)
            self.load_ingredients(ingredients_data)

        except Exception as e:
            print(f"Ошибка загрузки отчётов: {e}")

    def load_revenue(self, data):
        """Загружает данные о выручке"""
        if not data:
            return

        total = sum(row.get('revenue', 0) for row in data)
        orders = sum(row.get('orders_count', 0) for row in data)

        self.total_revenue_label.setText(f"💰 Общая выручка: {total:.2f} ₽")
        self.total_orders_label.setText(f"📋 Всего заказов: {orders}")

        self.revenue_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.revenue_table.setItem(i, 0, QTableWidgetItem(str(row.get('date', ''))))
            self.revenue_table.setItem(i, 1, QTableWidgetItem(str(row.get('orders_count', 0))))
            self.revenue_table.setItem(i, 2, QTableWidgetItem(f"{row.get('revenue', 0):.2f} ₽"))

    def load_dishes(self, data):
        """Загружает данные о популярных блюдах"""
        self.dishes_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.dishes_table.setItem(i, 0, QTableWidgetItem(row.get('name', '')))
            self.dishes_table.setItem(i, 1, QTableWidgetItem(row.get('category', '')))
            self.dishes_table.setItem(i, 2, QTableWidgetItem(str(row.get('count', 0))))
            self.dishes_table.setItem(i, 3, QTableWidgetItem(f"{row.get('revenue', 0):.2f} ₽"))

    def load_tables(self, data):
        """Загружает данные о загрузке залов"""
        self.tables_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.tables_table.setItem(i, 0, QTableWidgetItem(f"Стол #{row.get('table_id', '')}"))
            self.tables_table.setItem(i, 1, QTableWidgetItem(str(row.get('orders_count', 0))))
            self.tables_table.setItem(i, 2, QTableWidgetItem(f"{row.get('avg_time', 0):.1f}"))

    def load_ingredients(self, data):
        """Загружает данные о расходе ингредиентов"""
        self.ingredients_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.ingredients_table.setItem(i, 0, QTableWidgetItem(row.get('name', '')))
            self.ingredients_table.setItem(i, 1, QTableWidgetItem(f"{row.get('used', 0):.2f} {row.get('unit', '')}"))
            self.ingredients_table.setItem(i, 2, QTableWidgetItem(f"{row.get('current_stock', 0):.2f} {row.get('unit', '')}"))
            
            status = "Норма" if row.get('current_stock', 0) > row.get('min_stock', 0) else "МАЛО"
            self.ingredients_table.setItem(i, 3, QTableWidgetItem(status))