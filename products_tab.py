# вкладка "Товари"
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QComboBox,
    QTableWidgetItem, QMessageBox, QAbstractItemView, QLineEdit, QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QDialog
from product_dialog import ProductDialog
from database import get_all_products, add_product, update_product, delete_product, get_category_names
import sqlite3
from styles import style_table, style_controls


class ProductsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Верхні кнопки
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Додати товар")
        self.add_button.setFixedSize(160, 60)
        self.edit_button = QPushButton("Редагувати товар")
        self.edit_button.setFixedSize(160, 60)
        self.delete_button = QPushButton("Видалити")
        self.delete_button.setFixedSize(160, 60)
        self.details_button = QPushButton("Деталі")
        self.details_button.setFixedSize(160, 60)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.details_button)
        self.layout.addLayout(button_layout)

        self.filter_layout = QHBoxLayout()
        self.filter_category_label = QLabel("Обери категорію:")
        self.filter_category_combo = QComboBox()
        self.filter_category_combo.addItem("Усі")  # перший пункт
        for name in get_category_names().values():
            self.filter_category_combo.addItem(name)

        self.filter_price_from_label = QLabel("Ціна від:")
        self.filter_price_from = QLineEdit()
        self.filter_price_from.setPlaceholderText("0")

        self.filter_price_to_label = QLabel("до:")
        self.filter_price_to = QLineEdit()
        self.filter_price_to.setPlaceholderText("10000")

        self.filter_button = QPushButton("Фільтрувати")
        self.filter_button.clicked.connect(self.filter_products)

        self.filter_layout.addWidget(self.filter_category_label)
        self.filter_layout.addWidget(self.filter_category_combo)
        self.filter_layout.addWidget(self.filter_price_from_label)
        self.filter_layout.addWidget(self.filter_price_from)
        self.filter_layout.addWidget(self.filter_price_to_label)
        self.filter_layout.addWidget(self.filter_price_to)
        self.filter_layout.addWidget(self.filter_button)

        style_controls(
            self.add_button,
            self.edit_button,
            self.delete_button,
            self.details_button,
            self.filter_button,
            labels=[
                self.filter_category_label,
                self.filter_price_from_label,
                self.filter_price_to_label
            ],
            line_edits=[
                self.filter_price_from,
                self.filter_price_to
            ],
            combo_box=self.filter_category_combo
)


        self.layout.addLayout(self.filter_layout) 

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Назва", "Ціна", "Кількість", "Категорія","Фото"
        ])

        style_table(self.table)

        # Встановлення стилю для таблиці
        self.table.setStyleSheet("QTableWidget {font-size: 16px;}")
        self.table.setColumnHidden(0, True)
        


        # Зміна ширини колонок таблиці
        self.table.verticalHeader().setDefaultSectionSize(50)  # Наприклад, 50 пікселів

        self.table.setColumnWidth(0, 50) #id
        self.table.setColumnWidth(1, 300)  # назва
        self.table.setColumnWidth(2, 80)  
        self.table.setColumnWidth(3, 100) 
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 250)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        # Підключення кнопок
        self.add_button.clicked.connect(self.add_product)
        self.edit_button.clicked.connect(self.edit_product)
        self.delete_button.clicked.connect(self.delete_product)
        self.details_button.clicked.connect(self.show_details)

        self.load_data()



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
            if selected_category != "Усі":
                cat_name = category_names.get(prod[5], "Невідомо")
                if cat_name != selected_category:
                    continue

            if min_price and float(prod[3]) < float(min_price):
                continue

            if max_price and float(prod[3]) > float(max_price):
                continue

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

            quantity_item = QTableWidgetItem(str(prod[4]))              # Кількість
            quantity_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, quantity_item)
           

            category_name = category_names.get(prod[5], "Невідомо")
            self.table.setItem(row, 4, QTableWidgetItem(category_name))

            # Кнопки: одна "Додати фото" + одна "Переглянути фото"
            image_buttons_layout = QHBoxLayout()

            button_style = """
                QPushButton {
                    background-color: #B57EDC;         /* Medium Purple */
                    color: white;
                    padding: 5px 10px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #A070C4;         /* Darker purple on hover */
                }
                QPushButton:pressed {
                    background-color: #8E5CB5;         /* Another tone when pressed */
                }
            """

            # Кнопка додавання фото
            add_photo_button = QPushButton("Додати фото")
            add_photo_button.setStyleSheet(button_style)
            add_photo_button.clicked.connect(lambda _, product_id=prod[0]: self.add_product_image(product_id))
            image_buttons_layout.addWidget(add_photo_button)

            # Кнопка перегляду фото
            view_photos_button = QPushButton("Переглянути")
            view_photos_button.setStyleSheet(button_style)
            view_photos_button.clicked.connect(lambda _, product_id=prod[0]: self.view_images_slider(product_id))
            image_buttons_layout.addWidget(view_photos_button)
            add_photo_button.setFixedSize(110, 30)
            view_photos_button.setFixedSize(110,30)



            image_widget = QWidget()
            image_widget.setLayout(image_buttons_layout)
            self.table.setCellWidget(row, 5, image_widget)

    def view_images_slider(self, product_id):
        images = self.get_product_images(product_id)
        if not images:
            QMessageBox.information(self, "Фото", "Для цього товару немає фото.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Перегляд фото")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        index_label = QLabel()
        index_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(index_label)

        current_index = [0]  # Змінна в списку, щоб передавати по посиланню

        def update_image():
            pixmap = QPixmap(images[current_index[0]])
            if pixmap.isNull():
                image_label.setText("Не вдалося завантажити зображення")
            else:
                image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
            index_label.setText(f"Фото {current_index[0]+1} з {len(images)}")

        def show_next():
            current_index[0] = (current_index[0] + 1) % len(images)
            update_image()

        def show_previous():
            current_index[0] = (current_index[0] - 1) % len(images)
            update_image()

        buttons_layout = QHBoxLayout()
        prev_button = QPushButton("← Назад")
        prev_button.clicked.connect(show_previous)
        buttons_layout.addWidget(prev_button)

        next_button = QPushButton("Вперед →")
        next_button.clicked.connect(show_next)
        buttons_layout.addWidget(next_button)

        layout.addLayout(buttons_layout)

        update_image()  # Показати перше фото

        dialog.exec()




    def add_product_image(self, product_id):
        # Відкриваємо діалогове вікно для вибору файлу
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()  # Отримуємо вибрані файли
            if file_paths:
                image_path = file_paths[0]  # Беремо перше фото (якщо їх кілька, можна додати логіку для кількох)
                self.save_image_to_database(product_id, image_path)  # Викликаємо метод для збереження фото в базу даних
                
                # Повідомлення про успішне додавання
                QMessageBox.information(self, "Успіх", "Фото додано успішно!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Помилка", "Не вибрано жодного файлу.")


    def get_product_images(self, product_id):
        # Підключення до бази даних з використанням контекстного менеджера для автоматичного закриття з'єднання
        with sqlite3.connect('appliance_store.db') as conn:
            cursor = conn.cursor()
            
            # Виконання запиту для отримання всіх фото для конкретного товару
            cursor.execute("SELECT image_path FROM product_photos WHERE product_id = ?", (product_id,))
            
            # Отримуємо всі результати запиту
            images = cursor.fetchall()

        # Повертаємо список шляхів до фото
        return [image[0] for image in images]

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

    def save_image_to_database(self, product_id, image_path):
        # Підключення до бази даних
        with sqlite3.connect('appliance_store.db') as conn:
            cursor = conn.cursor()

            # Виконання SQL-запиту для вставки нового фото для товару
            cursor.execute("""
                INSERT INTO product_photos (product_id, image_path) 
                VALUES (?, ?)
            """, (product_id, image_path))

            # Збереження змін
            conn.commit()



    



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
