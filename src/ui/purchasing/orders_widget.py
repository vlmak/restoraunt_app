"""
Вкладка заказов для менеджера по закупкам
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QMessageBox,
    QHeaderView, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.services.supplier_service import SupplierService


class OrdersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()
        self.init_ui()
        self.load_orders()

    def init_ui(self):
        self.setStyleSheet("background-color: #F5EDE3;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        title = QLabel("Заказы поставщикам")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #5D4037; padding: 10px;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Поставщик", "Дата", "Сумма", "Статус"
        ])
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
        self.table.itemDoubleClicked.connect(self.show_order_details)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #8D6E63;
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #6D4C41; }
        """)
        refresh_btn.clicked.connect(self.load_orders)
        btn_layout.addWidget(refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def load_orders(self):
        try:
            orders = self.supplier_service.get_all_orders()

            self.table.setRowCount(len(orders))

            for i, order in enumerate(orders):
                self.table.setItem(i, 0, QTableWidgetItem(str(order.get('order_id', ''))))
                self.table.setItem(i, 1, QTableWidgetItem(order.get('supplier_name', 'Неизвестно')))
                self.table.setItem(i, 2, QTableWidgetItem(str(order.get('order_date', ''))[:16]))
                self.table.setItem(i, 3, QTableWidgetItem(f"{order.get('total_amount', 0):.2f} ₽"))
                self.table.setItem(i, 4, QTableWidgetItem(order.get('status', 'unknown')))

        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")
            import traceback
            traceback.print_exc()

    def show_order_details(self, item):
        row = item.row()
        order_id = int(self.table.item(row, 0).text())
        order_status = self.table.item(row, 4).text()

        items = self.supplier_service.get_order_items(order_id)

        if not items:
            QMessageBox.information(self, "Информация", "Заказ пуст")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Детали заказа №{order_id}")
        dialog.setFixedSize(700, 500)
        dialog.setModal(True)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        info = QLabel(f"Заказ №{order_id} — {self.table.item(row, 1).text()}")
        info.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(info)

        status_label = QLabel(f"Статус: {order_status}")
        status_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(status_label)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Ингредиент", "Кол-во", "Цена", "Сумма"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        table.setRowCount(len(items))
        total = 0
        for i, item in enumerate(items):
            table.setItem(i, 0, QTableWidgetItem(item.get('ingredient_name', 'Неизвестно')))
            table.setItem(i, 1, QTableWidgetItem(str(item.get('quantity', 0))))
            table.setItem(i, 2, QTableWidgetItem(f"{item.get('unit_price', 0):.2f} ₽"))
            table.setItem(i, 3, QTableWidgetItem(f"{item.get('line_total', 0):.2f} ₽"))
            total += item.get('line_total', 0)

        total_label = QLabel(f"ИТОГО: {total:.2f} ₽")
        total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        total_label.setStyleSheet("color: #2E7D32; padding: 10px; background-color: #E8F5E9; border-radius: 8px;")

        layout.addWidget(table)
        layout.addWidget(total_label)

        btn_layout = QHBoxLayout()

        if order_status not in ['received', 'cancelled']:
            receive_btn = QPushButton("Заказ приехал")
            receive_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 25px;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #388E3C; }
            """)
            receive_btn.clicked.connect(lambda: self.receive_order(order_id, dialog))
            btn_layout.addWidget(receive_btn)

            cancel_btn = QPushButton("Заказ не приехал")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    padding: 10px 25px;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #D32F2F; }
            """)
            cancel_btn.clicked.connect(lambda: self.cancel_order(order_id, dialog))
            btn_layout.addWidget(cancel_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                padding: 10px 25px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #616161; }
        """)
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        dialog.exec_()

    def receive_order(self, order_id, dialog):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Подтвердить получение заказа №{order_id}?\n\n"
            "Ингредиенты будут добавлены на склад.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        success = self.supplier_service.receive_order(order_id)
        if success:
            QMessageBox.information(self, "Успех", f"Заказ №{order_id} принят!\nИнгредиенты добавлены на склад.")
            dialog.accept()
            self.load_orders()
        else:
            QMessageBox.critical(self, "Ошибка", " Не удалось принять заказ")

    def cancel_order(self, order_id, dialog):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Отменить заказ №{order_id}?\n\n"
            "Ингредиенты НЕ будут добавлены на склад.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        success = self.supplier_service.cancel_order(order_id)
        if success:
            QMessageBox.information(self, "Успех", f"Заказ №{order_id} отменён.")
            dialog.accept()
            self.load_orders()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось отменить заказ")