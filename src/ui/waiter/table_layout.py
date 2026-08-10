"""
Виджет схемы зала для официанта
"""
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QVBoxLayout,
    QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.services.table_service import TableService
from src.services.order_service import OrderService


class WaiterTableLayout(QWidget):
    def __init__(self, employee_id: int):
        super().__init__()
        self.employee_id = employee_id
        self.table_service = TableService()
        self.order_service = OrderService()
        self.table_buttons = {}
        self.init_ui()
        self.load_tables()

    def init_ui(self):
        self.setStyleSheet("QWidget { background-color: #F5EDE3; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        self.setLayout(layout)

        title = QLabel("🪑 Занятые столики")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #5D4037; padding: 10px;")
        layout.addWidget(title)

        subtitle = QLabel("Кликните по занятому столику для работы с заказом")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #8D6E63; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        self.tables_grid = QGridLayout()
        self.tables_grid.setSpacing(25)
        self.tables_grid.setContentsMargins(40, 20, 40, 20)
        layout.addLayout(self.tables_grid)

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
        refresh_btn.clicked.connect(self.load_tables)
        layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)

    def load_tables(self):
        tables = self.table_service.get_all_tables()

        for i in reversed(range(self.tables_grid.count())):
            widget = self.tables_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.table_buttons.clear()

        for table in tables:
            btn = self.create_table_button(table)
            row = (table.table_id - 1) // 4
            col = (table.table_id - 1) % 4
            self.tables_grid.addWidget(btn, row, col)
            self.table_buttons[table.table_id] = btn

    def create_table_button(self, table):
        btn = QPushButton()
        btn.setFixedSize(140, 140)

        colors = {
            'free': '#A5D6A7',
            'occupied': '#E53935',
            'reserved': '#FFE0B2',
            'needs_cleaning': '#BDBDBD'
        }
        color = colors.get(table.status, '#BDBDBD')
        is_active = table.status == 'occupied'

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 4px solid #3E2723;
                border-radius: 70px;
                font-size: 15px;
                font-weight: bold;
                color: white;
                padding: 15px;
            }}
            QPushButton:hover {{
                border-color: #1B0000;
                border-width: 5px;
            }}
        """)

        status_text = {
            'free': '🟢 Свободен',
            'occupied': '🔴 Занят',
            'reserved': '🟡 Зарезервирован',
            'needs_cleaning': '⚪ Требует уборки'
        }.get(table.status, table.status)

        btn.setText(f"Стол #{table.table_id}\n{status_text}")

        if is_active:
            btn.clicked.connect(lambda checked, t=table: self.on_table_clicked(t))
        else:
            btn.setEnabled(False)
            btn.setStyleSheet(btn.styleSheet() + "\nQPushButton { opacity: 0.5; }")

        return btn

    def on_table_clicked(self, table):
        from src.ui.waiter.order_widget import OrderWidget

        check = self.order_service.get_open_check_by_table(table.table_id)

        if not check:
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Для столика #{table.table_id} нет открытого чека."
            )
            return

        self.order_widget = OrderWidget(check.check_id, table.table_id, self.employee_id)
        self.order_widget.exec_()
        self.load_tables()