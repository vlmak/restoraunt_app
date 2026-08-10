"""
Главное окно приложения
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.models.schemas import Employee


class MainWindow(QMainWindow):
    def __init__(self, employee: Employee):
        super().__init__()
        self.employee = employee
        self.setWindowTitle(f"Ресторан — {employee.role}")
        self.resize(1200, 800)

        self.init_ui()

    def init_ui(self):
        """Создаёт интерфейс главного окна"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        top_panel = self.create_top_panel()
        layout.addWidget(top_panel)

        self.tabs = QTabWidget()
        self.add_tabs_by_role()
        layout.addWidget(self.tabs)

    def create_top_panel(self):
        """Создаёт верхнюю панель с информацией о пользователе"""
        from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox

        widget = QWidget()
        widget.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-bottom: 1px solid #ddd;")
        layout = QHBoxLayout()
        widget.setLayout(layout)

        # Информация о пользователе
        info = QLabel(
            f"👤 {self.employee.first_name} {self.employee.last_name}  |  "
            f"Роль: {self.employee.role}"
        )
        info.setFont(QFont("Arial", 14))
        layout.addWidget(info)
        layout.addStretch()

        btn_logout = QPushButton("🚪 Выйти")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 25px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        btn_logout.clicked.connect(self.logout)
        layout.addWidget(btn_logout)

        return widget

    def add_tabs_by_role(self):
        """Добавляет вкладки в зависимости от роли"""
        role = self.employee.role

        if role == 'admin':
            self.add_admin_tabs()
        elif role == 'waiter':
            self.add_waiter_tabs()
        elif role == 'cook':
            self.add_cook_tabs()
        elif role == 'purchasing_manager':
            self.add_purchasing_tabs()
        else:
            self.tabs.addTab(self.create_placeholder("Неизвестная роль"), "Ошибка")

    def add_admin_tabs(self):
        """Вкладки для администратора"""
        try:
            from src.ui.admin.table_layout import TableLayoutWidget
            self.tabs.addTab(TableLayoutWidget(), "🪑 Зал")
        except Exception as e:
            print(f"Ошибка загрузки схемы зала: {e}")
            self.tabs.addTab(self.create_placeholder(" Ошибка загрузки зала"), "Зал")
        
        try:
            from src.ui.admin.reports_view import ReportsView
            self.tabs.addTab(ReportsView(), "📊 Отчёты")
        except Exception as e:
            print(f"Ошибка загрузки отчётов: {e}")
            self.tabs.addTab(self.create_placeholder("Ошибка загрузки отчётов"), "Отчёты")

    def add_waiter_tabs(self):
        """Вкладки для официанта"""
        try:
            from src.ui.waiter.table_layout import WaiterTableLayout
            self.tabs.addTab(WaiterTableLayout(self.employee.employee_id), "🪑 Зал")
        except Exception as e:
            print(f"Ошибка загрузки зала для официанта: {e}")
            self.tabs.addTab(self.create_placeholder("Ошибка загрузки зала"), "Зал")

    def add_cook_tabs(self):
        """Вкладки для повара"""
        try:
            from src.ui.cook.kitchen_widget import KitchenWidget
            self.tabs.addTab(KitchenWidget(self.employee.employee_id), "🔥 Кухня")
        except Exception as e:
            print(f"Ошибка загрузки кухонного экрана: {e}")
            self.tabs.addTab(self.create_placeholder("Ошибка загрузки кухни"), "Кухня")

    def add_purchasing_tabs(self):
        """Вкладки для менеджера по закупкам"""
        try:
            from src.ui.purchasing.notifications_widget import NotificationsWidget
            self.tabs.addTab(NotificationsWidget(), "🔔 Уведомления")
        except Exception as e:
            print(f"Ошибка загрузки уведомлений: {e}")
            self.tabs.addTab(self.create_placeholder("Ошибка загрузки"), "Уведомления")
        
        try:
            from src.ui.purchasing.orders_widget import OrdersWidget
            self.tabs.addTab(OrdersWidget(), "📦 Заказы")
        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")
            self.tabs.addTab(self.create_placeholder("❌ Ошибка загрузки"), "Заказы")

    def create_placeholder(self, text: str):
        """Создаёт временный виджет-заглушку"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 24))
        label.setStyleSheet("color: #aaa; padding: 80px;")
        layout.addWidget(label)

        return widget

    def logout(self):
        """Выход из системы"""
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Выход",
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()
            from src.ui.auth_window import AuthWindow
            self.auth_window = AuthWindow()
            self.auth_window.show()