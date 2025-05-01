from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QFormLayout
from database import get_all_suppliers, add_supplier_to_db, update_supplier_in_db, delete_supplier_from_db  # Імпорт функцій для роботи з БД

class SuppliersTab(QWidget):
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

        # Таблиця для відображення постачальників
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Назва постачальника", "Контактна інформація"])
        self.layout.addWidget(self.table)

        # Кнопки і таблиця додані до основного layout
        self.setLayout(self.layout)

        # Підключення подій до кнопок
        self.add_button.clicked.connect(self.add_supplier)
        self.edit_button.clicked.connect(self.edit_supplier)
        self.delete_button.clicked.connect(self.delete_supplier)

        self.load_data()

    def load_data(self):
        """ Завантаження даних постачальників з бази в таблицю """
        self.table.setRowCount(0)  # Очищення таблиці
        suppliers = get_all_suppliers()  # Функція отримання всіх постачальників з БД

        self.table.setRowCount(len(suppliers))

        for row, supplier in enumerate(suppliers):
            self.table.setItem(row, 0, QTableWidgetItem(str(supplier[0])))  # ID
            self.table.setItem(row, 1, QTableWidgetItem(supplier[1]))       # Назва постачальника
            self.table.setItem(row, 2, QTableWidgetItem(supplier[2]))       # Контактна інформація

    def add_supplier(self):
        """ Додати нового постачальника """
        self.supplier_form = QWidget()
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.contact_info_input = QLineEdit()
        
        form_layout.addRow("Назва постачальника:", self.name_input)
        form_layout.addRow("Контактна інформація:", self.contact_info_input)
        
        save_button = QPushButton("Зберегти")
        save_button.clicked.connect(self.save_new_supplier)
        form_layout.addRow(save_button)

        self.supplier_form.setLayout(form_layout)
        self.supplier_form.show()

    def save_new_supplier(self):
        """ Зберегти нового постачальника в БД """
        name = self.name_input.text()
        contact_info = self.contact_info_input.text()

        # Функція для додавання нового постачальника до бази
        add_supplier_to_db(name, contact_info)

        self.supplier_form.close()
        self.load_data()

    def edit_supplier(self):
        """ Редагувати постачальника """
        row = self.table.currentRow()
        if row == -1:
            return  # Якщо не вибраний рядок, нічого не робити

        supplier_id = self.table.item(row, 0).text()

        self.supplier_form = QWidget()
        form_layout = QFormLayout()
        
        # Перевірка на наявність елементів перед тим, як отримати текст
        name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        contact_info = self.table.item(row, 2).text() if self.table.item(row, 2) else ""

        self.name_input = QLineEdit(name)
        self.contact_info_input = QLineEdit(contact_info)

        form_layout.addRow("Назва постачальника:", self.name_input)
        form_layout.addRow("Контактна інформація:", self.contact_info_input)

        save_button = QPushButton("Зберегти зміни")
        save_button.clicked.connect(lambda: self.save_edited_supplier(supplier_id))
        form_layout.addRow(save_button)

        self.supplier_form.setLayout(form_layout)
        self.supplier_form.show()

    def save_edited_supplier(self, supplier_id):
        """ Зберегти зміни в постачальника в БД """
        name = self.name_input.text()
        contact_info = self.contact_info_input.text()

        # Функція для оновлення постачальника в базі
        update_supplier_in_db(supplier_id, name, contact_info)

        self.supplier_form.close()
        self.load_data()

    def delete_supplier(self):
        """ Видалити постачальника """
        row = self.table.currentRow()
        if row == -1:
            return  # Якщо не вибраний рядок, нічого не робити

        supplier_id = self.table.item(row, 0).text()
        delete_supplier_from_db(supplier_id)
        self.load_data()
