"""
Окно заказа для официанта
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QMessageBox,
    QComboBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from src.services.order_service import OrderService
from src.services.menu_service import MenuService


class OrderWidget(QDialog):
    def __init__(self, check_id: int, table_id: int, employee_id: int):
        super().__init__()
        self.check_id = check_id
        self.table_id = table_id
        self.employee_id = employee_id
        self.order_service = OrderService()
        self.menu_service = MenuService()

        self.setWindowTitle(f"Заказ — Столик #{table_id}")
        self.setFixedSize(650, 550)
        self.setModal(True)

        self.init_ui()
        self.load_order()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        title = QLabel(f"🍽️ Заказ для столика #{self.table_id}")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #5D4037;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Блюдо", "Цена", "Статус"])
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

        self.total_label = QLabel("Итого: 0 ₽")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.total_label.setStyleSheet(
            "color: #2E7D32; padding: 10px; background-color: #E8F5E9; border-radius: 8px;"
        )
        layout.addWidget(self.total_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        add_btn = QPushButton(" Добавить блюдо")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #388E3C; }
        """)
        add_btn.clicked.connect(self.add_dish)
        btn_layout.addWidget(add_btn)

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)
        refresh_btn.clicked.connect(self.load_order)
        btn_layout.addWidget(refresh_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #616161; }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def load_order(self):
        """Загружает все блюда из check_items с цветовой индикацией"""
        try:
            items = self.order_service.get_check_items(self.check_id)
            total = self.order_service.get_check_total(self.check_id)

            self.table.setRowCount(len(items))

            status_colors = {
                'pending': QColor(255, 255, 255),
                'ready': QColor(200, 255, 200),
                'cancelled': QColor(255, 200, 200),
                'served': QColor(200, 200, 255)
            }

            status_display = {
                'pending': 'Ожидает',
                'ready': 'Готово',
                'cancelled': 'Отменено',
                'served': 'Подано'
            }

            for i, item in enumerate(items):
                self.table.setItem(i, 0, QTableWidgetItem(item.dish_name or 'Блюдо'))
                self.table.setItem(i, 1, QTableWidgetItem(f"{item.price_at_moment:.2f} ₽"))

                status_text = status_display.get(item.status, item.status)
                status_item = QTableWidgetItem(status_text)
                color = status_colors.get(item.status, QColor(255, 255, 255))
                status_item.setBackground(color)

                font = QFont()
                font.setBold(True)
                status_item.setFont(font)

                self.table.setItem(i, 2, status_item)

            self.total_label.setText(f"Итого: {total:.2f} ₽")
            
        except Exception as e:
            print(f"Ошибка загрузки заказа: {e}")
            import traceback
            traceback.print_exc()

    def add_dish(self):
        """Добавляет блюдо в заказ"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление блюда")
        dialog.setFixedSize(400, 200)
        dialog.setModal(True)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        layout.addWidget(QLabel("Выберите блюдо:"))

        try:
            dishes = self.menu_service.get_all_dishes()
            combo = QComboBox()
            for dish in dishes:
                combo.addItem(f"{dish.name} — {dish.price} ₽", dish.dish_id)
            layout.addWidget(combo)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить меню: {e}")
            dialog.reject()
            return

        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Добавить")
        add_btn.setStyleSheet("""
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
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)

        def on_add():
            try:
                dish_id = combo.currentData()
                if not dish_id:
                    QMessageBox.warning(self, "Ошибка", "Выберите блюдо")
                    return
                
                print(f"🔄 on_add: dish_id={dish_id}, check_id={self.check_id}")
                
                new_id = self.order_service.add_dish_to_check(self.check_id, dish_id)
                print(f"🔄 new_id: {new_id}")
                
                if new_id is not None:
                    QMessageBox.information(self, "Успех", f"Блюдо добавлено! (ID: {new_id})")
                    dialog.accept()
                    self.load_order()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось добавить блюдо")
                    
            except Exception as e:
                print(f"Ошибка в on_add: {e}")
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Ошибка", f"Ошибка:\n{str(e)}")

        add_btn.clicked.connect(on_add)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        dialog.exec_()