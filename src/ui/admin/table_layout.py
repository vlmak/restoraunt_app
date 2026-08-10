"""
Виджет схемы зала для администратора
"""
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QVBoxLayout, 
    QLabel, QMessageBox, QDialog, QLineEdit, 
    QDateTimeEdit, QSpinBox, QHBoxLayout, QFormLayout
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont

from src.services.table_service import TableService


class TableLayoutWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.table_service = TableService()
        self.table_buttons = {}
        self.init_ui()
        self.load_tables()

    def init_ui(self):
        """Создаёт интерфейс"""
        self.setStyleSheet("""
            QWidget {
                background-color: #F5EDE3;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        self.setLayout(layout)

        # Заголовок
        title = QLabel("🪑 Схема зала")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #5D4037; padding: 10px;")
        layout.addWidget(title)

        # Подзаголовок
        subtitle = QLabel("Кликните по столику для управления")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #8D6E63; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # Сетка для столиков
        self.tables_grid = QGridLayout()
        self.tables_grid.setSpacing(25)
        self.tables_grid.setContentsMargins(40, 20, 40, 20)
        layout.addLayout(self.tables_grid)

        # Кнопка обновления
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Обновить")
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
            QPushButton:hover {
                background-color: #6D4C41;
            }
        """)
        refresh_btn.clicked.connect(self.load_tables)
        bottom_layout.addWidget(refresh_btn)
        
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

    def load_tables(self):
        """Загружает столики из БД и отображает их"""
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

    def create_table_button(self, table) -> QPushButton:
        """Создаёт круглую кнопку для одного столика"""
        btn = QPushButton()
        btn.setFixedSize(140, 140)
        
        colors = {
            'free': '#4CAF50',
            'occupied': '#E53935',
            'reserved': '#FF8F00',
            'needs_cleaning': '#78909C'
        }
        color = colors.get(table.status, '#BDBDBD')
        
        status_text = {
            'free': '🟢 Свободен',
            'occupied': '🔴 Занят',
            'reserved': '🟡 Зарезервирован',
            'needs_cleaning': '⚪ Требует уборки'
        }.get(table.status, table.status)
        
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
        
        btn.setText(f"Стол #{table.table_id}\n{status_text}")
        btn.clicked.connect(lambda checked, t=table: self.on_table_clicked(t))
        
        return btn

    def on_table_clicked(self, table):
        """Обработка клика по столику"""
        if table.status == 'free':
            self.open_reservation_dialog(table)
        elif table.status == 'reserved':
            self.show_reservation_info(table)
        elif table.status == 'occupied':
            self.show_occupied_info(table)
        elif table.status == 'needs_cleaning':
            self.show_cleaning_info(table)
    def show_cleaning_info(self, table):
        """Показывает информацию о столике, который требует уборки"""
        try:
            # Получаем время начала уборки
            result = self.table_service.get_cleaning_info(table.table_id)
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Столик #{table.table_id} — Требует уборки")
            msg.setIcon(QMessageBox.Information)
            
            info_text = (
                f"🪑 Столик #{table.table_id}\n"
                f"👥 Вместимость: {table.capacity} чел.\n"
                f"⚪ Статус: Требует уборки\n\n"
                f"🧹 Столик ожидает уборки.\n"
                f"🕐 С момента закрытия чека прошло: {result.get('time_since', 'неизвестно')}\n\n"
                f"ℹ️ Статус изменится автоматически через 5 минут\n"
                f"   после закрытия чека (по триггеру)."
            )
            
            msg.setText(info_text)
            msg.setStyleSheet("QLabel{min-width: 350px;}")
            
            # Только кнопка OK
            msg.addButton(QMessageBox.Ok)
            msg.exec_()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить информацию о столике:\n{str(e)}"
            )

    def show_occupied_info(self, table):
        """Показывает информацию о занятом столике"""
        try:
            order_info = self.table_service.get_current_order_by_table(table.table_id)
            
            if not order_info:
                QMessageBox.information(
                    self,
                    f"Столик #{table.table_id}",
                    f"🪑 Столик #{table.table_id}\n"
                    f"🔴 Статус: Занят\n"
                    f"ℹ️ Информация о заказе не найдена"
                )
                return
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Столик #{table.table_id} — Занят")
            msg.setIcon(QMessageBox.Information)
            
            info_text = (
                f"🪑 Столик #{table.table_id}\n"
                f"👥 Вместимость: {table.capacity} чел.\n"
                f"🔴 Статус: Занят\n\n"
                f"📋 Информация о заказе:\n"
                f"   Чек №{order_info.get('check_id', 'не указан')}\n"
                f"   💰 Сумма: {order_info.get('total_amount', 0)} ₽\n"
                f"   🕐 Открыт: {order_info.get('opened_at', 'не указано')}\n"
                f"   👤 Официант: {order_info.get('waiter_name', 'не указан')}\n"
            )
            
            try:
                items = self.table_service.get_check_items(order_info['check_id'])
                if items:
                    info_text += "\n📌 Заказ:\n"
                    for item in items:
                        info_text += f"   • {item.get('dish_name', 'блюдо')} × {item.get('quantity', 1)} — {item.get('price_at_moment', 0)} ₽\n"
            except Exception as e:
                info_text += f"\n📌 Заказ: (ошибка загрузки: {str(e)})"
            
            msg.setText(info_text)
            msg.setStyleSheet("QLabel{min-width: 400px;}")
            
            msg.addButton(QMessageBox.Ok)
            msg.exec_()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить информацию о столике:\n{str(e)}"
            )

    def show_reservation_info(self, table):
        """Показывает информацию о брони и кнопку отмены"""
        try:
            reservation = self.table_service.get_active_reservation(table.table_id)
            
            if not reservation:
                QMessageBox.information(
                    self,
                    f"Столик #{table.table_id}",
                    f"🪑 Столик #{table.table_id}\n"
                    f"🟡 Статус: Зарезервирован\n"
                    f"ℹ️ Информация о брони не найдена.\n\n"
                    f"Возможно, бронь уже была отменена или завершена.\n"
                    f"Обновите схему зала."
                )
                return
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Столик #{table.table_id} — Зарезервирован")
            msg.setIcon(QMessageBox.Information)
            
            info_text = (
                f"🪑 Столик #{table.table_id}\n"
                f"👥 Вместимость: {table.capacity} чел.\n"
                f"🟡 Статус: Зарезервирован\n\n"
                f"📋 Информация о брони:\n"
                f"   👤 Гость: {reservation.get('guest_name', 'не указан')}\n"
                f"   📞 Телефон: {reservation.get('phone', 'не указан')}\n"
                f"   👥 Гостей: {reservation.get('persons', 0)} чел.\n"
                f"   🕐 Время: {reservation.get('reservation_time', 'не указано')}\n"
                f"   📌 Статус: {reservation.get('status', 'неизвестен')}"
            )
            
            msg.setText(info_text)
            msg.setStyleSheet("QLabel{min-width: 350px;}")
            
            cancel_btn = msg.addButton(" Отменить бронь", QMessageBox.ActionRole)
            msg.addButton(QMessageBox.Ok)
            
            msg.exec_()
            
            if msg.clickedButton() == cancel_btn:
                self.cancel_reservation_dialog(table)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить информацию о брони:\n{str(e)}"
            )

    def open_reservation_dialog(self, table):
        """Открывает диалог резервации столика"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Резервация столика #{table.table_id}")
        dialog.setFixedSize(400, 420)
        dialog.setModal(True)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # Информация о столике
        info = QLabel(f"Резервация столика #{table.table_id} (вместимость: {table.capacity} чел.)")
        info.setFont(QFont("Segoe UI", 12, QFont.Bold))
        info.setStyleSheet("color: #5D4037;")
        layout.addWidget(info)

        # Имя гостя
        layout.addWidget(QLabel("👤 Имя гостя:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("Введите имя гостя")
        name_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 6px;")
        layout.addWidget(name_input)

        # Телефон
        layout.addWidget(QLabel("📞 Телефон:"))
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("+7-XXX-XXX-XX-XX")
        phone_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 6px;")
        layout.addWidget(phone_input)

        # Дата и время
        layout.addWidget(QLabel("📅 Дата и время:"))
        datetime_input = QDateTimeEdit()
        datetime_input.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        datetime_input.setCalendarPopup(True)
        datetime_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 6px;")
        layout.addWidget(datetime_input)

        # Количество гостей
        layout.addWidget(QLabel("👥 Количество гостей:"))
        persons_input = QSpinBox()
        persons_input.setRange(1, table.capacity)
        persons_input.setValue(1)
        persons_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 6px;")
        layout.addWidget(persons_input)

        layout.addSpacing(15)

        # Кнопки
        btn_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Зарезервировать")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        ok_btn.clicked.connect(lambda: self.save_reservation(
            dialog, table, name_input, phone_input, datetime_input, persons_input
        ))
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        dialog.exec_()

    def save_reservation(self, dialog, table, name_input, phone_input, datetime_input, persons_input):
        """Сохраняет бронь в БД"""
        name = name_input.text().strip()
        phone = phone_input.text().strip()
        reservation_time = datetime_input.dateTime().toPyDateTime()
        persons = persons_input.value()

        if not name or not phone:
            QMessageBox.warning(dialog, "Ошибка", "Введите имя и телефон гостя")
            return

        try:
            success = self.table_service.create_reservation(
                table_id=table.table_id,
                guest_name=name,
                phone=phone,
                reservation_time=reservation_time,
                persons=persons
            )
            
            if success:
                QMessageBox.information(
                    dialog, 
                    "Успех", 
                    f"Столик #{table.table_id} зарезервирован!\n\n"
                    f"Гость: {name}\n"
                    f"Телефон: {phone}\n"
                    f"Время: {reservation_time.strftime('%d.%m.%Y %H:%M')}\n"
                    f"Гостей: {persons} чел."
                )
                dialog.accept()
                self.load_tables()
            else:
                QMessageBox.critical(dialog, "Ошибка", "Не удалось зарезервировать столик.\n\n"
                                      "Возможно, столик уже занят или забронирован.")
        except Exception as e:
            error_msg = str(e)
            if "already reserved" in error_msg.lower() or "не хватает" in error_msg.lower():
                QMessageBox.critical(dialog, "Ошибка", f"{error_msg}")
            else:
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка при резервации:\n{error_msg}")

    def cancel_reservation_dialog(self, table):
        """Подтверждение отмены брони"""
        try:
            reservation = self.table_service.get_active_reservation(table.table_id)
            
            if not reservation:
                QMessageBox.information(
                    self,
                    "Информация",
                    f"У столика #{table.table_id} нет активной брони.\n"
                    "Возможно, она уже была отменена."
                )
                self.load_tables()
                return
            
            reply = QMessageBox.question(
                self,
                "Отмена брони",
                f"❓ Отменить бронь столика #{table.table_id}?\n\n"
                f"👤 Гость: {reservation.get('guest_name', 'не указан')}\n"
                f"🕐 Время: {reservation.get('reservation_time', 'не указано')}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.table_service.cancel_reservation(table.table_id)
                
                if success:
                    # Принудительно обновляем статус столика на 'free'
                    self.table_service.update_table_status(table.table_id, 'free')
                    QMessageBox.information(self, "Успех", f" Бронь столика #{table.table_id} отменена")
                else:
                    QMessageBox.critical(self, "Ошибка", " Не удалось отменить бронь.\n\n"
                                        "Возможно, бронь уже была отменена.")
                
                self.load_tables()
                    
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось отменить бронь:\n{str(e)}"
            )

    def clean_table_dialog(self, table):
        """Отметить столик как убранный"""
        reply = QMessageBox.question(
            self,
            "Уборка столика",
            f" Отметить столик #{table.table_id} как убранный?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.table_service.clean_table(table.table_id):
                QMessageBox.information(self, "Успех", f"Столик #{table.table_id} убран")
                self.load_tables()
            else:
                QMessageBox.critical(self, "Ошибка", " Не удалось отметить столик как убранный")
