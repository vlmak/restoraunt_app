"""
Окно авторизации
"""
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.services.auth_service import AuthService
from src.ui.main_window import MainWindow


class AuthWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.init_ui()

    def init_ui(self):
        """Создаёт интерфейс окна авторизации"""
        self.setWindowTitle("Ресторан — Вход в систему")
        self.setFixedSize(1000, 900)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(50, 50, 50, 50)

        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Введите свои данные для входа")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        lbl_login = QLabel("👤 Логин:")
        lbl_login.setFont(QFont("Arial", 16))
        layout.addWidget(lbl_login)

        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("например: Иван.Иванов")
        self.input_login.setMinimumHeight(35)
        self.input_login.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: white;
            }
        """)
        layout.addWidget(self.input_login)

        lbl_password = QLabel("🔒 Пароль:")
        lbl_password.setFont(QFont("Arial", 16))
        layout.addWidget(lbl_password)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("телефон для теста")
        self.input_password.setMinimumHeight(35)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: white;
            }
        """)
        layout.addWidget(self.input_password)

        layout.addSpacing(25)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_login = QPushButton("ВОЙТИ")
        self.btn_login.setMinimumHeight(45)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.btn_login.clicked.connect(self.on_login)
        btn_layout.addWidget(self.btn_login)

        self.btn_cancel = QPushButton("ОТМЕНА")
        self.btn_cancel.setMinimumHeight(45)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)


        self.input_login.returnPressed.connect(self.on_login)
        self.input_password.returnPressed.connect(self.on_login)

        self.setLayout(layout)

    def on_login(self):
        """Обработка нажатия на кнопку Войти"""
        login = self.input_login.text().strip()
        password = self.input_password.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        employee = self.auth_service.login(login, password)

        if employee:
            self.accept()
            self.open_main_window(employee)
        else:
            QMessageBox.critical(
                self,
                "Ошибка авторизации",
                "Неверный логин или пароль!\n\n"
                "Логин: имя.фамилия (например: Иван.Иванов)\n"
                "Пароль: номер телефона (например: +7 (916) 444-55-66)"
            )

    def open_main_window(self, employee):
        """Открывает главное окно после успешного входа"""
        try:
            from src.ui.main_window import MainWindow
            self.main_window = MainWindow(employee)
            self.main_window.show()
            self.hide()                                        
        except Exception as e:
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось открыть главное окно:\n{str(e)}"
            )

    def closeEvent(self, event):
        """Закрытие окна"""
        QApplication.quit()