"""
Кухонный экран для повара
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QMessageBox,
    QHeaderView
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from src.services.order_service import OrderService


class KitchenWidget(QWidget):
    def __init__(self, employee_id: int):
        super().__init__()
        self.employee_id = employee_id
        self.order_service = OrderService()
        self.init_ui()
        self.load_orders()

        self.timer = QTimer()
        self.timer.timeout.connect(self.load_orders)
        self.timer.start(10000)

    def init_ui(self):
        self.setStyleSheet("background-color: #F5EDE3;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        title = QLabel("Кухонный экран")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #5D4037; padding: 10px;")
        layout.addWidget(title)

        subtitle = QLabel("Блюда, ожидающие приготовления (status: pending)")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #8D6E63; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Блюдо", "Стол", "Цена"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                gridline-color: #eee;
            }
            QTableWidget::item { padding: 8px; }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        self.cook_btn = QPushButton("Начать готовить")
        self.cook_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #388E3C; }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #666;
            }
        """)
        self.cook_btn.clicked.connect(self.start_cooking)
        btn_layout.addWidget(self.cook_btn)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #D32F2F; }
            QPushButton:disabled {
                background-color: #EF9A9A;
                color: #666;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_cooking)
        btn_layout.addWidget(self.cancel_btn)

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)
        refresh_btn.clicked.connect(self.load_orders)
        btn_layout.addWidget(refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.count_label = QLabel("📋 Всего заказов: 0")
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setFont(QFont("Segoe UI", 12))
        self.count_label.setStyleSheet("color: #5D4037; padding: 10px;")
        layout.addWidget(self.count_label)

    def load_orders(self):
        """Загружает блюда со статусом pending"""
        try:
            # 👇 ОЧИЩАЕМ ТАБЛИЦУ
            self.table.clearContents()
            self.table.setRowCount(0)

            orders = self.order_service.get_pending_orders()

            self.table.setRowCount(len(orders))

            for i, order in enumerate(orders):
                self.table.setItem(i, 0, QTableWidgetItem(str(order.check_item_id)))
                self.table.setItem(i, 1, QTableWidgetItem(order.dish_name or 'Блюдо'))
                self.table.setItem(i, 2, QTableWidgetItem(f"#{order.table_number}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{order.price:.2f} ₽"))

            self.count_label.setText(f"📋 Всего заказов: {len(orders)}")

            has_orders = len(orders) > 0
            self.cook_btn.setEnabled(has_orders)
            self.cancel_btn.setEnabled(has_orders)

            print(f"✅ Загружено заказов: {len(orders)}")

        except Exception as e:
            print(f" Ошибка загрузки заказов: {e}")
            self.count_label.setText(f" Ошибка загрузки: {str(e)[:50]}...")

    def get_selected_order(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите блюдо")
            return None

        item = self.table.item(current_row, 0)
        if not item:
            return None

        try:
            return int(item.text())
        except ValueError:
            return None

    def start_cooking(self):
        check_item_id = self.get_selected_order()
        if check_item_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Начать приготовление блюда?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        print(f" Начинаю готовить check_item_id={check_item_id}")

        result = self.order_service.start_cooking(check_item_id)
        print(f" Результат: {result}")

        if result.startswith('✅'):
            QMessageBox.information(self, "Успех", result)
        else:
            QMessageBox.warning(self, "Ошибка", result)

        self.load_orders()

    def cancel_cooking(self):
        check_item_id = self.get_selected_order()
        if check_item_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Отменить приготовление блюда?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        print(f"Отменяю check_item_id={check_item_id}")

        result = self.order_service.cancel_cooking(check_item_id)
        print(f"Результат: {result}")

        if result.startswith('✅'):
            QMessageBox.information(self, "Успех", result)
        else:
            QMessageBox.warning(self, "Ошибка", result)

        self.load_orders()