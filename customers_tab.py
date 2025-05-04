# customers_tab.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QLabel, QFormLayout
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from database import update_customer_discount,get_all_clients_with_stats, add_client_to_db, update_client_in_db, delete_client_from_db  # Приклад імпорту функцій з бази даних
from styles import style_table

class ClientsTab(QWidget):
    def __init__(self):
        super().__init__()

        # Основний layout
        self.layout = QVBoxLayout()

        button_style = """
            QPushButton {
                background-color: #B57EDC;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 14px;
                border: none;
                border-radius: 8px;
                min-width: 100px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #A070C4;
            }
            QPushButton:pressed {
                background-color: #8E5CB5;
            }
        """

        # Верхні кнопки
        # Розміщення кнопок
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(38, 38, 0, 38)  # Відступи: ліво 2см, верх/низ 1см, право 0
        button_layout.setSpacing(76)  # Відстань між кнопками: 2 см

        self.add_button = QPushButton("Новий клієнт")
        self.add_button.setFixedSize(200, 40)
        self.add_button.setStyleSheet(button_style)
        button_layout.addWidget(self.add_button, alignment=Qt.AlignLeft)

        self.edit_button = QPushButton("Оновити інформацію")
        self.edit_button.setFixedSize(200, 40)
        self.edit_button.setStyleSheet(button_style)
        button_layout.addWidget(self.edit_button, alignment=Qt.AlignLeft)
        # button_layout.addWidget(self.edit_button_button, alignment=Qt.AlignLeft)

        self.delete_button = QPushButton("Видалити")
        self.delete_button.setFixedSize(200, 40)
        self.delete_button.setStyleSheet(button_style)
        button_layout.addWidget(self.delete_button, alignment=Qt.AlignLeft)
        # button_layout.addWidget(self.delete_button_button, alignment=Qt.AlignLeft)

        self.layout.addLayout(button_layout)

        # Таблиця для відображення клієнтів
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
        "ID", "Прізвище та ім'я", "Номер телефону", "Email", "Адреса",
        "Кількість", "Накопичено", "Знижка", "VIP клієнт"
        ]) 
        style_table(self.table) 
        self.table.setColumnHidden(0, True)
        self.table.setColumnWidth(0, 50) #id
        self.table.setColumnWidth(1, 180) 
        self.table.setColumnWidth(2, 180)  
        self.table.setColumnWidth(3, 150) 
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 130)
        self.table.setColumnWidth(7, 90)
        self.table.setColumnWidth(5, 150)


        self.layout.addWidget(self.table)

        # Кнопки і таблиця додані до основного layout
        self.setLayout(self.layout)

        # Підключення подій до кнопок
        self.add_button.clicked.connect(self.add_client)
        self.edit_button.clicked.connect(self.edit_client)
        self.delete_button.clicked.connect(self.delete_client)

        # Маска для введення номера телефону
        self.phone_mask = QLineEdit()
        self.phone_mask.setPlaceholderText("+38 (___) ___-__-__")
        self.phone_mask.setInputMask("+38 (000) 000-00-00")  # Маска для номера телефону

        # Завантаження клієнтів при ініціалізації вкладки
        self.load_data()

    def load_data(self):
        """ Завантаження даних клієнтів з бази в таблицю """
        self.table.setRowCount(0)  # Очищення таблиці
        clients = get_all_clients_with_stats()  # Отримання клієнтів із бази

        self.table.setRowCount(len(clients))

        for row, client in enumerate(clients):
            for col in range(9):
                if col == 7:
                    # Знижка
                    value = f"{client[col]:.1f}%" if client[col] is not None else "0%"
                    item = QTableWidgetItem(value)
                elif col == 8:
                    # Постійний клієнт: Так / Ні
                    value = "Так" if client[col] else "Ні"
                    item = QTableWidgetItem(value)
                else:
                    # Інші поля
                    item = QTableWidgetItem(str(client[col]) if client[col] is not None else "")
                self.table.setItem(row, col, item)

    
    

    
    def add_client(self):
        """ Додати нового клієнта """
        self.client_form = QWidget()
        self.client_form.setWindowTitle("Додати користувача")
        
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.phone_input.setInputMask("+38 (000) 000-00-00")
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()

        form_layout.addRow("Прізвище та ім'я:", self.name_input)
        form_layout.addRow("Номер телефону:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Адреса:", self.address_input)

        # Стиль кнопок
        button_style = """
            QPushButton {
                background-color: #B57EDC;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 14px;
                border: none;
                border-radius: 8px;
                min-width: 100px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #A070C4;
            }
            QPushButton:pressed {
                background-color: #8E5CB5;
            }
        """

        # Кнопки
        save_button = QPushButton("Зберегти")
        save_button.setFixedSize(110, 30)
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(self.save_new_client)

        cancel_button = QPushButton("Скасувати")
        cancel_button.setFixedSize(110, 30)
        cancel_button.setStyleSheet(button_style)
        cancel_button.clicked.connect(self.client_form.close)

        # Горизонтальне розміщення кнопок
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(76, 38, 0, 38)  # ліво 2см, верх/низ 1см, право 0
        button_layout.setSpacing(76)  # відстань між кнопками — 2см
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        form_layout.addRow(button_layout)

        self.client_form.setLayout(form_layout)
        self.client_form.show()

    # def save_new_client(self):
    #     """ Зберегти нового клієнта в БД """
    #     name = self.name_input.text()
    #     phone = self.phone_input.text()
    #     email = self.email_input.text()
    #     address = self.address_input.text()

    #     # Функція для додавання нового клієнта до бази
    #     add_client_to_db(name, phone, email, address)

    #     self.client_form.close()
    #     self.load_data()

    from PyQt5.QtWidgets import QMessageBox

    def save_new_client(self):
        """ Зберегти нового клієнта з перевіркою введених даних """
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()

        if not name or not phone or not email or not address:
            QMessageBox.warning(
                self.client_form,
                "Помилка вводу",
                "Будь ласка, заповніть усі поля перед збереженням.",
            )
            return

        # Тут вставляєш логіку збереження до БД або списку
        print("Клієнт збережений:", name, phone, email, address)

        self.client_form.close()


    def edit_client(self):
        """ Редагувати клієнта """
        row = self.table.currentRow()
        if row == -1:
            return  # Якщо не вибраний рядок, нічого не робити

        client_id = self.table.item(row, 0).text()

        self.client_form = QWidget()
        self.client_form.setWindowTitle("Редагування користувача")

        form_layout = QFormLayout()

        # Перевірка на наявність елементів перед тим, як отримати текст
        name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        phone = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
        email = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        address = self.table.item(row, 4).text() if self.table.item(row, 4) else ""

        self.name_input = QLineEdit(name)
        self.phone_input = QLineEdit(phone)
        self.phone_input.setInputMask("+38 (000) 000-00-00")
        self.email_input = QLineEdit(email)
        self.address_input = QLineEdit(address)

        form_layout.addRow("Прізвище та ім'я:", self.name_input)
        form_layout.addRow("Номер телефону:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Адреса:", self.address_input)

        # Стиль кнопок

        button_style = """
            QPushButton {
                background-color: #B57EDC;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 14px;
                border: none;
                border-radius: 8px;
                min-width: 100px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #A070C4;
            }
            QPushButton:pressed {
                background-color: #8E5CB5;
            }
        """

        # Кнопки
        save_button = QPushButton("Зберегти зміни")
        save_button.setFixedSize(140, 30)
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(lambda: self.save_edited_client(client_id))

        cancel_button = QPushButton("Скасувати")
        cancel_button.setFixedSize(110, 30)
        cancel_button.setStyleSheet(button_style)
        cancel_button.clicked.connect(self.client_form.close)

        # Горизонтальне розміщення кнопок
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(76, 38, 0, 38)  # 2см зліва, 1см зверху/знизу
        button_layout.setSpacing(76)  # 2см між кнопками
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        form_layout.addRow(button_layout)

        self.client_form.setLayout(form_layout)
        self.client_form.show()


    def save_edited_client(self, client_id):
        """ Зберегти зміни в клієнта в БД """
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        address = self.address_input.text()

        # Функція для оновлення клієнта в базі
        update_client_in_db(client_id, name, phone, email, address)

        self.client_form.close()
        self.load_data()

    def delete_client(self):
        """ Видалити клієнта """
        row = self.table.currentRow()
        if row == -1:
            return  # Якщо не вибраний рядок, нічого не робити

        client_id = self.table.item(row, 0).text()
        delete_client_from_db(client_id)
        self.load_data()
