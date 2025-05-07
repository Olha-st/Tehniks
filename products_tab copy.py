# вкладка "Товари"
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QComboBox,
    QTableWidgetItem, QMessageBox, QAbstractItemView, QLineEdit, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QDialog
from PyQt5.QtCore import Qt
from product_dialog import ProductDialog
from database import get_all_products, add_product, update_product, delete_product, get_category_names
import sqlite3


class ProductsTab(QWidget):
    def __init__(self):
        super().__init__()
        # Головний вертикальний layout
        self.layout = QVBoxLayout()

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

        # === КНОПКИ ===
        buttons_with_spacing = QVBoxLayout()
        buttons_with_spacing.addSpacing(24)

        for text in ["Додати товар", "Редагувати товар", "Видалити", "Деталі"]:
            btn = QPushButton(text)
            btn.setFixedSize(200, 40)
            btn.setStyleSheet(button_style)

            wrapper = QWidget()
            wrapper_layout = QHBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(0, 0, 0, 0)
            wrapper_layout.setAlignment(Qt.AlignLeft)
            wrapper_layout.addWidget(btn)

            buttons_with_spacing.addWidget(wrapper)

        buttons_with_spacing.addSpacing(24)
        self.layout.addLayout(buttons_with_spacing)

        # === ФІЛЬТР ===
        # self.filter_layout = QHBoxLayout()
        # self.filter_layout.setSpacing(38)
        # self.filter_layout.setAlignment(Qt.AlignLeft)

        # self.filter_category_label = QLabel("Обери категорію:")
        # self.filter_category_combo = QComboBox()
        # self.filter_category_combo.addItem("Усі")
        # for name in get_category_names().values():
        #     self.filter_category_combo.addItem(name)

        # self.filter_price_from_label = QLabel("Ціна від:")
        # self.filter_price_from = QLineEdit()
        # self.filter_price_from.setFixedSize(100, 30)
        # self.filter_price_from.setPlaceholderText("0")

        # Створення layout для фільтра
        self.filter_layout = QHBoxLayout()
        self.filter_layout.setSpacing(20)  # Відстань між елементами
        self.filter_layout.setAlignment(Qt.AlignLeft)  # Вирівнювання по лівому краю

        # Створення віджетів фільтра
        self.filter_category_label = QLabel("Обери категорію:")
        self.filter_category_combo = QComboBox()
        self.filter_category_combo.setFixedSize(150, 30)
        self.filter_category_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.filter_category_combo.addItem("Усі")
        for name in get_category_names().values():
            self.filter_category_combo.addItem(name)

        self.filter_price_from_label = QLabel("Ціна від:")
        self.filter_price_from = QLineEdit()
        self.filter_price_from.setPlaceholderText("0")
        self.filter_price_from.setFixedSize(100, 30)
        self.filter_price_from.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.filter_price_to_label = QLabel("до:")
        self.filter_price_to = QLineEdit()
        self.filter_price_to.setPlaceholderText("10000")
        self.filter_price_to.setFixedSize(100, 30)
        self.filter_price_to.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.filter_button = QPushButton("Фільтрувати")
        self.filter_button.setFixedSize(150, 40)
        self.filter_button.setStyleSheet(button_style)
        self.filter_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.filter_button.clicked.connect(self.filter_products)

        # Додавання елементів у layout
        self.filter_layout.addWidget(self.filter_category_label)
        self.filter_layout.addWidget(self.filter_category_combo)
        self.filter_layout.addWidget(self.filter_price_from_label)
        self.filter_layout.addWidget(self.filter_price_from)
        self.filter_layout.addWidget(self.filter_price_to_label)
        self.filter_layout.addWidget(self.filter_price_to)
        self.filter_layout.addWidget(self.filter_button)

        # Додавання фільтра до головного layout
        self.layout.addLayout(self.filter_layout)

        filter_with_spacing = QVBoxLayout()
        filter_with_spacing.addSpacing(24)
        filter_with_spacing.addLayout(self.filter_layout)
        filter_with_spacing.addSpacing(24)

        self.layout.addLayout(filter_with_spacing)
        self.setLayout(self.layout)

    
    
    def filter_products(self):
        print("Фільтрування товарів")
        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Назва", "Ціна", "Кількість", "Категорія ID", "Фото"
        ])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        # Підключення кнопок
        self.add_button.clicked.connect(self.add_product)
        self.edit_button.clicked.connect(self.edit_product)
        self.delete_button.clicked.connect(self.delete_product)
        self.details_button.clicked.connect(self.show_details)

        self.load_data()

    from database import get_all_products, add_product, update_product, delete_product, get_category_names

    def load_data(self):
        self.table.setRowCount(0)
        products = get_all_products()
        category_names = get_category_names()

        # Отримання значень фільтрів
        selected_category = self.filter_category_combo.currentText()
        min_price = self.filter_price_from.text()
        max_price = self.filter_price_to.text()

        # Фільтрація
        filtered_products = []
        for prod in products:
            # prod[3] — ціна, prod[4] — кількість, prod[5] — id категорії

            # Фільтр за категорією
            if selected_category != "Усі":
                cat_name = category_names.get(prod[5], "Невідомо")
                if cat_name != selected_category:
                    continue

            # Фільтр за мінімальною ціною
            if min_price:
                try:
                    if float(prod[3]) < float(min_price):
                        continue
                except ValueError:
                    pass

            # Фільтр за максимальною ціною
            if max_price:
                try:
                    if float(prod[3]) > float(max_price):
                        continue
                except ValueError:
                    pass

            filtered_products.append(prod)

        # Розміщення товарів без залишку в кінці
        available = [p for p in filtered_products if p[4] > 0]
        out_of_stock = [p for p in filtered_products if p[4] == 0]
        sorted_products = available + out_of_stock

        self.table.setRowCount(len(sorted_products))

        for row, prod in enumerate(sorted_products):
            self.table.setItem(row, 0, QTableWidgetItem(str(prod[0])))  # ID
            self.table.setItem(row, 1, QTableWidgetItem(prod[1]))       # Назва
            self.table.setItem(row, 2, QTableWidgetItem(str(prod[3])))  # Ціна
            self.table.setItem(row, 3, QTableWidgetItem(str(prod[4])))  # Кількість

            # Назва категорії
            category_name = category_names.get(prod[5], "Невідомо")
            self.table.setItem(row, 4, QTableWidgetItem(category_name))

            # Кнопка "Показати" фото
            show_button = QPushButton("Показати")
            show_button.clicked.connect(lambda _, path=prod[6]: self.show_image(path))
            self.table.setCellWidget(row, 5, show_button)


    def get_selected_product(self):
        row = self.table.currentRow()
        if row == -1:
            return None
        product_id = int(self.table.item(row, 0).text())
        for product in get_all_products():
            if product[0] == product_id:
                return product
        return None

    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            add_product(data)
            self.load_data()

    def edit_product(self):
        selected = self.get_selected_product()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Оберіть товар для редагування.")
            return
        dialog = ProductDialog(self, selected)
        if dialog.exec_():
            new_data = dialog.get_data()
            update_product(int(selected[0]), new_data)
            self.load_data()

    def delete_product(self):
        selected = self.get_selected_product()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Оберіть товар для видалення.")
            return
        confirm = QMessageBox.question(self, "Підтвердження", f"Видалити товар '{selected[1]}'?")
        if confirm == QMessageBox.Yes:
            delete_product(int(selected[0]))
            self.load_data()

    def show_details(self):
        selected = self.get_selected_product()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Оберіть товар.")
            return
        QMessageBox.information(self, f"Опис товару: {selected[1]}", selected[2])

    def show_image(self, image_path):
        if not image_path:
            QMessageBox.warning(self, "Фото", "Фото не вказано.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Фото товару")
        layout = QVBoxLayout()
        label = QLabel()

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            label.setText("Не вдалося завантажити зображення.")
        else:
            label.setPixmap(pixmap.scaled(400, 400, aspectRatioMode=1))

        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec_()

    def filter_products(self):
        selected_category = self.filter_category_combo.currentText()
        price_from = self.filter_price_from.text()
        price_to = self.filter_price_to.text()

        query = '''
            SELECT id, name, category_id, price, quantity FROM products
        '''
        filters = []
        params = []

        if selected_category != "Усі":
            category_id = self.get_category_id_by_name(selected_category)
            filters.append("category_id = ?")
            params.append(category_id)

        if price_from:
            filters.append("price >= ?")
            params.append(float(price_from))

        if price_to:
            filters.append("price <= ?")
            params.append(float(price_to))

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY quantity = 0, id ASC"

        conn = sqlite3.connect("appliance_store.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        products = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        category_names = get_category_names()
        for row_num, product in enumerate(products):
            self.table.insertRow(row_num)
            prod_id, name, category_id, price, quantity = product
            self.table.setItem(row_num, 0, QTableWidgetItem(str(prod_id)))
            self.table.setItem(row_num, 1, QTableWidgetItem(name))
            self.table.setItem(row_num, 2, QTableWidgetItem(category_names.get(category_id, "Невідомо")))
            self.table.setItem(row_num, 3, QTableWidgetItem(f"{price:.2f}"))
            self.table.setItem(row_num, 4, QTableWidgetItem(str(quantity)))

            details_button = QPushButton("Деталі")
            details_button.clicked.connect(lambda _, pid=prod_id: self.show_description(pid))
            self.table.setCellWidget(row_num, 5, details_button)

            photo_button = QPushButton("Показати")
            photo_button.clicked.connect(lambda _, pid=prod_id: self.show_photo(pid))
            self.table.setCellWidget(row_num, 6, photo_button)

    def get_category_id_by_name(self, name):
        categories = get_category_names()
        for cat_id, cat_name in categories.items():
            if cat_name == name:
                return cat_id
        return None
