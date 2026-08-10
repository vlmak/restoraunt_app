"""
Вкладка уведомлений для менеджера по закупкам
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QMessageBox,
    QHeaderView, QDialog, QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from src.services.supplier_service import SupplierService


class NotificationsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()
        self.init_ui()
        self.load_notifications()

    def init_ui(self):
        self.setStyleSheet("background-color: #F5EDE3;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        title = QLabel("Уведомления о низком запасе")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #5D4037; padding: 10px;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Ингредиент", "Остаток", "Мин. запас", "Действие"
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
        layout.addWidget(self.table)

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
        refresh_btn.clicked.connect(self.load_notifications)
        layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)

    def load_notifications(self):
        """Загружает ингредиенты с низким запасом"""
        try:
            items = self.supplier_service.get_low_stock_ingredients()
            print(f"Найдено уведомлений: {len(items)}")

            self.table.setRowCount(len(items))

            for i, item in enumerate(items):
                self.table.setItem(i, 0, QTableWidgetItem(str(item.ingredient_id)))
                self.table.setItem(i, 1, QTableWidgetItem(item.name))
                self.table.setItem(i, 2, QTableWidgetItem(f"{item.current_stock} {item.unit}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{item.min_stock} {item.unit}"))

                order_btn = QPushButton("Заказать")
                order_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 5px 15px;
                        border: none;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #388E3C; }
                """)
                order_btn.clicked.connect(lambda checked, ing=item: self.create_order(ing))
                self.table.setCellWidget(i, 4, order_btn)

        except Exception as e:
            print(f"Ошибка загрузки уведомлений: {e}")
            import traceback
            traceback.print_exc()
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Ошибка: {str(e)}"))

    def create_order(self, ingredient):
        """Создаёт заказ для выбранного ингредиента"""
        try:
            suppliers = self.supplier_service.get_all_suppliers()
            if not suppliers:
                QMessageBox.warning(self, "Ошибка", "Нет поставщиков в системе")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Создание заказа")
            dialog.setFixedSize(400, 300)
            dialog.setModal(True)

            layout = QVBoxLayout()
            dialog.setLayout(layout)

            layout.addWidget(QLabel("Выберите поставщика:"))

            combo = QComboBox()
            for sup in suppliers:
                combo.addItem(sup.name, sup.supplier_id)
            layout.addWidget(combo)

            layout.addWidget(QLabel(f"Ингредиент: {ingredient.name}"))
            layout.addWidget(QLabel(f"Текущий остаток: {ingredient.current_stock} {ingredient.unit}"))

            layout.addWidget(QLabel("Количество для заказа:"))
            qty_input = QSpinBox()
            qty_input.setRange(1, 1000)
            qty_input.setValue(max(int(ingredient.min_stock * 2), 10))
            layout.addWidget(qty_input)

            btn_layout = QHBoxLayout()
            ok_btn = QPushButton("Создать заказ")
            ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                }
            """)
            cancel_btn = QPushButton("Отмена")
            cancel_btn.clicked.connect(dialog.reject)

            def on_ok():
                supplier_id = combo.currentData()
                quantity = qty_input.value()

                if not supplier_id:
                    QMessageBox.warning(dialog, "Ошибка", "Выберите поставщика")
                    return

                order_id = self.supplier_service.create_supplier_order(supplier_id)
                if order_id:
                    self.supplier_service.add_item_to_order(order_id, ingredient.ingredient_id, quantity)
                    QMessageBox.information(dialog, "Успех", f"Заказ №{order_id} создан!")
                    dialog.accept()
                    self.load_notifications()
                else:
                    QMessageBox.critical(dialog, "Ошибка", "Не удалось создать заказ")

            ok_btn.clicked.connect(on_ok)
            btn_layout.addWidget(ok_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)

            dialog.exec_()
            
        except Exception as e:
            print(f"Ошибка создания заказа: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")