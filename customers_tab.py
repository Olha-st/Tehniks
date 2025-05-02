# customers_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QFormLayout
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from database import get_all_clients,get_all_clients_with_stats, add_client_to_db, update_client_in_db, delete_client_from_db  # Приклад імпорту функцій з бази даних

class ClientsTab(QWidget):
    def __init__(self):
        super().__init__()

        # Основний layout
        self.layout = QVBoxLayout()

        # Верхні кнопки
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Додати")
        self.edit_button = QPushButton("Редагувати")
        self.delete_button = QPushButton("Видалити")
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        self.layout.addLayout(button_layout)

        # Таблиця для відображення клієнтів
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
        "ID", "Прізвище та ім'я", "Номер телефону", "Email", "Адреса",
        "К-сть замовлень", "Загальна сума", "Знижка", "Постійний клієнт"
        ])  
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
        
        save_button = QPushButton("Зберегти")
        save_button.clicked.connect(self.save_new_client)
        form_layout.addRow(save_button)

        self.client_form.setLayout(form_layout)
        self.client_form.show()

    def save_new_client(self):
        """ Зберегти нового клієнта в БД """
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        address = self.address_input.text()

        # Функція для додавання нового клієнта до бази
        add_client_to_db(name, phone, email, address)

        self.client_form.close()
        self.load_data()

    def edit_client(self):
        """ Редагувати клієнта """
        row = self.table.currentRow()
        if row == -1:
            return  # Якщо не вибраний рядок, нічого не робити

        client_id = self.table.item(row, 0).text()

        self.client_form = QWidget()
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


        save_button = QPushButton("Зберегти зміни")
        save_button.clicked.connect(lambda: self.save_edited_client(client_id))
        form_layout.addRow(save_button)

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
