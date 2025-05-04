from PyQt5.QtWidgets import QWidget,QDoubleSpinBox, QVBoxLayout, QTableWidget,QHeaderView, QPushButton, QHBoxLayout, QComboBox, QLabel, QLineEdit,QInputDialog, QSpinBox, QTableWidgetItem, QMessageBox, QDialog, QFormLayout
from database import get_all_orders, add_order, get_customers, get_products, add_order_item, get_order_items_by_order_id, update_product_quantity
from database import get_connection, get_all_orders_with_total_and_paid, update_customer_discount
from functools import partial
import sqlite3
from PyQt5.QtCore import Qt
from styles import style_table, style_controls



class OrdersTab(QWidget):
    def __init__(self, parent=None, payments_tab=None, customers_tab=None):
        super().__init__(parent)
        self.payments_tab = payments_tab
        self.customers_tab = customers_tab
        self.layout = QVBoxLayout()

        # Кнопки
        button_layout = QHBoxLayout()


        # Горизонтальний layout для кнопок
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(24, 24, 0, 24)  # Зліва 2 см, зверху/знизу по 1 см
        button_layout.setSpacing(0)  # Відстань між кнопками = 2 см

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

        self.create_button = QPushButton("Створити замовлення")
        self.create_button.setFixedSize(200, 40)
        self.create_button.setStyleSheet(button_style)
        self.create_button.clicked.connect(self.open_order_form)
        button_layout.addWidget(self.create_button, alignment=Qt.AlignLeft)

        self.delete_button = QPushButton("Видалити замовлення")
        self.delete_button.setFixedSize(200, 40)
        self.delete_button.setStyleSheet(button_style)
        self.delete_button.clicked.connect(self.delete_order)
        button_layout.addWidget(self.delete_button, alignment=Qt.AlignLeft)



        self.layout.addLayout(button_layout)

        # Таблиця замовлень
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID","Номер", "Клієнт", "Дата", "Статус", "Інформація"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        style_table(self.table)
        self.table.setColumnHidden(0, True)
        # Зміна ширини колонок таблиці

        self.table.setColumnWidth(0, 50) #id
        self.table.setColumnWidth(1, 300) 
        self.table.setColumnWidth(2, 150)  
        self.table.setColumnWidth(3, 150) 
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 150)
        self.table.cellDoubleClicked.connect(self.show_order_details_dialog)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.load_data()

    def load_data(self):
        conn = get_connection()
        cur = conn.cursor()

        # Отримуємо дані з бази даних
        cur.execute("""
            SELECT o.id, o.title, c.name, o.order_date, o.status
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
        """)
        orders = cur.fetchall()
        conn.close()

        # Оновлюємо таблицю з замовленнями
        self.table.setRowCount(len(orders))
        # self.table.setColumnCount(6)

        button_style = """
                QPushButton {
                    background-color: #B57EDC;
                    color: white;
                    padding: 5px 10px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #A070C4;  
                }
                QPushButton:pressed {
                    background-color: #8E5CB5;  
                }
            """

            # Додавання рядків у таблицю
        for row, order in enumerate(orders):
            order_id, order_title, client_name, order_date, status = order
            self.table.setItem(row, 0, QTableWidgetItem(str(order_id)))
            self.table.setItem(row, 1, QTableWidgetItem(order_title))  # показує номер
            self.table.setItem(row, 2, QTableWidgetItem(client_name))
            self.table.setItem(row, 3, QTableWidgetItem(order_date))
            self.table.setItem(row, 4, QTableWidgetItem(status))

            # Кнопка "Деталі" з бузковим стилем
            details_btn = QPushButton("Деталі")
            details_btn.setFixedSize(130, 40)
            details_btn.setStyleSheet(button_style)
            details_btn.clicked.connect(lambda _, oid=order_id: self.show_order_details_dialog(oid))


            # Центрування кнопки у комірці
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.addWidget(details_btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setContentsMargins(0, 0, 0, 0)  # без відступів

            self.table.setCellWidget(row, 5, btn_container)
            self.table.verticalHeader().setDefaultSectionSize(60)  # висота рядка




    def add_product_to_new_order(self):
        selected_index = self.product_select.currentIndex()
        if selected_index == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть товар.")
            return

        product_id = self.product_select.currentData()
        quantity = self.quantity_input.value()

        product = next((p for p in self.filtered_products if p[0] == product_id), None)
        if not product or product[3] < quantity:
            QMessageBox.warning(self, "Помилка", "Недостатня кількість товару.")
            return

        name, price = product[1], product[2]
        self.product_list.append((product_id, quantity, price))

        row = self.products_table.rowCount()
        self.products_table.insertRow(row)
        self.products_table.setItem(row, 0, QTableWidgetItem(name))
        self.products_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        self.products_table.setItem(row, 2, QTableWidgetItem(str(price)))

        self.update_new_order_total()

    def update_new_order_total(self):
        total = sum(q * p for _, q, p in self.product_list)
        self.total_label.setText(f"Загальна сума: ₴{total}")


    def open_order_form(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Нове замовлення")
        self.dialog.setFixedSize(600, 500)
        form_layout = QFormLayout()

        self.customer_box = QComboBox()
        for id_, name in get_customers():
            self.customer_box.addItem(name, id_)

        self.products = get_products()  # products: list of tuples (id, name, price, quantity)
        self.product_select = QComboBox()
        self.filtered_products = [p for p in self.products if p[3] > 0]
        for p in self.filtered_products:
            self.product_select.addItem(f"{p[1]} (₴{p[2]}) - {p[3]}шт", p[0])

        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)

        self.product_list = []


        self.total_label = QLabel("Загальна сума: ₴0")

        add_button = QPushButton("Додати товар")
        add_button.clicked.connect(self.add_product_to_new_order)


        self.products_table = QTableWidget()
        self.products_table.setColumnCount(3)
        self.products_table.setHorizontalHeaderLabels(["Назва", "Кількість", "Ціна"])

        form_layout.addRow(self.total_label)
        save_button = QPushButton("Зберегти замовлення")
        save_button.clicked.connect(self.save_order)

        form_layout.addRow("Клієнт:", self.customer_box)
        form_layout.addRow("Товар:", self.product_select)
        form_layout.addRow("Кількість:", self.quantity_input)
        form_layout.addRow(add_button)
        form_layout.addRow(self.products_table)

        form_layout.addRow(save_button)

        self.total_label = QLabel("Загальна сума: ₴0")
        form_layout.addRow(self.total_label)

        # Стилі для елементів
        self.dialog.setStyleSheet("""
            QDialog {
                background-color: #E6E6FA;  /* світло-бузковий */
            }

            QLabel {
                font-size: 14px;
                color: #4B0082;
            }

            QComboBox, QSpinBox, QLineEdit, QTextEdit {
                background-color: white;
                border: 1px solid #9370DB;
                padding: 5px;
                font-size: 14px;
                border-radius: 6px;
            }

            QPushButton {
                background-color: #9370DB;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #7B68EE;
            }

            QPushButton:pressed {
                background-color: #6A5ACD;
            }
        """)


        self.dialog.setLayout(form_layout)
        self.dialog.exec_()

    def add_product_to_order(self, order_id, product_table, total_label, discount_value):
        # Діалог вибору товару
        products = self.get_all_products()
        product_names = [p[1] for p in products]  # список назв товарів

        product_name, ok = QInputDialog.getItem(self, "Додати товар", "Оберіть товар:", product_names, editable=False)
        if not ok or not product_name:
            return

        quantity, ok = QInputDialog.getInt(self, "Кількість", "Введіть кількість:", 1, 1)
        if not ok:
            return

        product = next((p for p in products if p[1] == product_name), None)
        if not product:
            QMessageBox.warning(self, "Помилка", "Товар не знайдено.")
            return

        product_id = product[0]
        price = product[2]

        conn = get_connection()
        cur = conn.cursor()

        # Перевірка на дублікати
        cur.execute("SELECT id FROM order_items WHERE order_id = ? AND product_id = ?", (order_id, product_id))
        if cur.fetchone():
            QMessageBox.warning(self, "Увага", "Товар вже додано до замовлення.")
            conn.close()
            return

        # Додавання товару в базу даних
        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
        """, (order_id, product_id, quantity, price))
        conn.commit()
        conn.close()

        # Додати рядок до таблиці
        row = product_table.rowCount()
        product_table.insertRow(row)
        product_table.setItem(row, 0, QTableWidgetItem(product_name))
        product_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        product_table.setItem(row, 2, QTableWidgetItem(str(price)))  # Без ₴ для обчислень

        # Кнопка видалення товару з замовлення
        delete_btn = QPushButton("Видалити")
        delete_btn.clicked.connect(lambda _, r=row, oid=order_id: self.delete_product_from_order(r, oid, product_table, total_label, discount_value))
        product_table.setCellWidget(row, 3, delete_btn)

        # Оновлення суми замовлення з урахуванням знижки
        self.update_order_total(product_table, total_label, discount_value)

        QMessageBox.information(self, "Успіх", "Товар додано до замовлення.")






    def save_order(self):
        if not self.product_list:
            QMessageBox.warning(self, "Помилка", "Додайте хоча б один товар.")
            return

        customer_id = self.customer_box.currentData()
        from datetime import datetime
        order_date = datetime.now().strftime("%Y-%m-%d")

        # Обчислюємо загальну суму замовлення (без знижки)
        base_amount = sum(quantity * unit_price for _, quantity, unit_price in self.product_list)

        # Отримуємо поточну знижку для клієнта
        cur = get_connection().cursor()
        cur.execute("SELECT discount_level FROM customers WHERE id = ?", (customer_id,))
        discount_str = cur.fetchone()[0]
        discount_value = int(discount_str.replace('%', '')) if discount_str else 0

        # Обчислюємо суму замовлення зі знижкою (якщо потрібно для відображення)
        total_amount = base_amount * (1 - discount_value / 100)

        # Додаємо замовлення (можеш передати total_amount, якщо хочеш враховувати знижку у БД)
        order_id = add_order(customer_id, order_date, base_amount)

        for product_id, quantity, unit_price in self.product_list:
            add_order_item(order_id, product_id, quantity, unit_price)
            self.update_product_quantity(product_id, -quantity)  # віднімаємо кількість зі складу

        # Оновлюємо знижку клієнта (окремо)
        update_customer_discount(customer_id)

        # Оновлюємо таблиці з клієнтами та оплатами
        if self.payments_tab:
            self.payments_tab.load_data()

        if self.customers_tab:
            self.customers_tab.load_data()

        self.dialog.accept()
        self.load_data()



    def show_order_details_dialog(self, order_id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT o.base_amount, o.discount_value, o.total_amount, c.name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.id = ?
        """, (order_id,))
        result = cur.fetchone()

        if not result:
            QMessageBox.warning(self, "Помилка", "Замовлення не знайдено.")
            return

        base_amount, discount_value, total_amount, customer_name = result

        cur.execute("""
            SELECT p.name, oi.quantity, oi.unit_price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (order_id,))
        products = cur.fetchall()

        conn.close()

        dialog = QDialog()
        dialog.setWindowTitle(f"Редагування замовлення №{order_id}")
        dialog.setMinimumSize(800, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f2f2ff;
                font-size: 14pt;
                font-family: Segoe UI;
            }
            QLabel {
                font-weight: bold;
                margin-bottom: 5px;
                font-size: 10pt;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bbb;
                font-size: 13pt;
            }
            QHeaderView::section {
                background-color: #b3aaff;
                font-weight: bold;
                font-size: 12pt;
                margin-bottom: 5px;
                padding: 5px;
                border: 1px solid #aaa;
            }
            QPushButton {
                background-color: #a68cff;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #9370db;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        layout.addWidget(QLabel(f"Клієнт: {customer_name}"))
        layout.addWidget(QLabel(f"Знижка: {discount_value}%"))

        total_label = QLabel()
        layout.addWidget(total_label)

        product_table = QTableWidget()
        product_table.setColumnCount(4)
        product_table.setHorizontalHeaderLabels(["Назва товару", "Кількість", "Ціна", "Операції"])
        # Встановлення ширини колонок
        product_table.setColumnWidth(0, 400)  # Назва товару
        product_table.setColumnWidth(1, 100)   # Кількість
        product_table.setColumnWidth(2, 100)   # Ціна
        product_table.setColumnWidth(3, 110)  # Операції
        product_table.setRowCount(len(products))

        product_table.verticalHeader().setDefaultSectionSize(40)

        for row, (name, qty, price) in enumerate(products):
            product_table.setItem(row, 0, QTableWidgetItem(name))

            qty_item = QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(Qt.AlignCenter)
            qty_item.setFlags(qty_item.flags() | Qt.ItemIsEditable)
            product_table.setItem(row, 1, qty_item)

            price_item = QTableWidgetItem(str(price))
            price_item.setTextAlignment(Qt.AlignCenter)
            price_item.setFlags(price_item.flags() | Qt.ItemIsEditable)
            product_table.setItem(row, 2, price_item)

            delete_btn = QPushButton("Видалити")
            delete_btn.setStyleSheet("QPushButton { background-color: #ff6666; color: white; border-radius: 6px; padding: 6px 12px; }"
                                    "QPushButton:hover { background-color: #e64545; }")
            delete_btn.clicked.connect(lambda _, r=row: self.delete_product_from_order(r, order_id, product_table, total_label, discount_value))
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.addWidget(delete_btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            product_table.setCellWidget(row, 3, btn_container)

        layout.addWidget(QLabel("Список товарів:"))
        layout.addWidget(product_table)

        product_table.cellChanged.connect(lambda *_: self.update_order_total(product_table, total_label, discount_value))
        self.update_order_total(product_table, total_label, discount_value)

        # Buttons area
        button_layout = QHBoxLayout()

        add_product_btn = QPushButton("Додати товар")
        add_product_btn.clicked.connect(lambda: self.add_product_to_order(order_id, product_table, total_label, discount_value))
        button_layout.addWidget(add_product_btn)

        save_btn = QPushButton("Зберегти зміни")
        save_btn.clicked.connect(lambda: self.save_order_changes(order_id, product_table, dialog, total_label, discount_value))
        button_layout.addWidget(save_btn)

        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()






    def get_all_products(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, price FROM products")  # Отримуємо id, назву та ціну товарів
        products = cur.fetchall()  # Отримуємо всі товари
        conn.close()
        return products


    def update_order_total(self, product_table, total_label, discount_value):
        total = 0
        
        for row in range(product_table.rowCount()):
            try:
                quantity = int(product_table.item(row, 1).text())
                price = float(product_table.item(row, 2).text())
                total += quantity * price
            except (ValueError, AttributeError):
                continue

        discounted = total * (1 - discount_value / 100)
        total_label.setText(f"Сума без знижки: ₴{total:.2f} | Із знижкою {discount_value}%: ₴{discounted:.2f}")





    # def delete_product_from_order(self, row, order_id, product_table, total_label, discount_value):
    #     product_name_item = product_table.item(row, 0)
    #     if product_name_item is None:
    #         QMessageBox.warning(self, "Помилка", "Не вдалося отримати назву товару.")
    #         return

    #     product_name = product_name_item.text()

    #     # Видалення з бази
    #     conn = get_connection()
    #     cur = conn.cursor()
    #     cur.execute("SELECT id FROM products WHERE name = ?", (product_name,))
    #     result = cur.fetchone()
    #     if not result:
    #         QMessageBox.warning(self, "Помилка", f"Товар '{product_name}' не знайдено в базі даних.")
    #         conn.close()
    #         return

    #     product_id = result[0]
    #     cur.execute("DELETE FROM order_items WHERE order_id = ? AND product_id = ?", (order_id, product_id))
    #     conn.commit()
    #     conn.close()

    def delete_product_from_order(self, row, order_id, product_table, total_label, discount_value):
        # Отримуємо назву товару
        product_name_item = product_table.item(row, 0)
        if product_name_item is None:
            QMessageBox.warning(self, "Помилка", "Не вдалося отримати назву товару.")
            return

        product_name = product_name_item.text()

        # Підключення до бази даних
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Пошук товару за назвою
            cur.execute("SELECT id FROM products WHERE name = ?", (product_name,))
            result = cur.fetchone()
            if not result:
                QMessageBox.warning(self, "Помилка", f"Товар '{product_name}' не знайдено в базі даних.")
                return

            product_id = result[0]
            
            # Видалення товару з таблиці order_items
            cur.execute("DELETE FROM order_items WHERE order_id = ? AND product_id = ?", (order_id, product_id))
            conn.commit()

            # Оновлення таблиці після видалення
            product_table.removeRow(row)

            # Оновлюємо загальну суму
            self.update_order_total(product_table, total_label, discount_value)
            
            # Повідомлення про успішне видалення
            QMessageBox.information(self, "Успіх", f"Товар '{product_name}' успішно видалено з замовлення.")

        except Exception as e:
            # Обробка помилок під час роботи з базою даних
            QMessageBox.critical(self, "Помилка", f"Сталася помилка при роботі з базою даних: {str(e)}")
        
        finally:
            # Закриття з'єднання з базою даних
            if conn:
                conn.close()




    def save_order_changes(self, order_id, product_table, dialog, total_label, discount_value):
        base_amount = 0

        # Проходимо по всіх рядках таблиці товарів
        for row in range(product_table.rowCount()):
            product_name_item = product_table.item(row, 0)
            quantity_item = product_table.item(row, 1)
            price_item = product_table.item(row, 2)

            if not product_name_item or not quantity_item or not price_item:
                continue  # Пропустити порожні рядки

            product_name = product_name_item.text()
            try:
                # Спробуємо отримати кількість та ціну
                quantity = int(quantity_item.text())
                price = float(price_item.text().replace("₴", "").strip())  # Видаляємо ₴ та пробіли
            except ValueError:
                continue  # Пропустити некоректні значення

            product_id = self.get_product_id_by_name(product_name)
            if product_id is not None:
                # Оновлюємо дані в таблиці order_items
                self.update_order_item(order_id, product_id, quantity, price)
                # Оновлюємо кількість товару на складі
                self.update_product_quantity(product_id, quantity)

                base_amount += quantity * price  # Обчислюємо базову суму

        # Обчислюємо загальну суму після знижки
        total_amount = base_amount * (1 - discount_value / 100)

        # Оновлюємо інформацію в таблиці orders
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE orders
            SET base_amount = ?, total_amount = ?
            WHERE id = ?
        """, (base_amount, total_amount, order_id))

        conn.commit()
        conn.close()

        # Оновлення вкладки Оплати
        if self.payments_tab:
            self.payments_tab.load_data()

        # Оновлення вкладки Клієнти
        if self.customers_tab:
            self.customers_tab.load_data()

        # Інформуємо користувача
        QMessageBox.information(self, "Збережено", "Зміни збережено успішно.")

        # Закриваємо діалогове вікно
        # dialog.accept()

        # Оновлюємо дані
        self.load_data()


    def get_database_connection(self):
        # Replace with your actual database file path
        return sqlite3.connect("appliance_store.db")

    def update_product_quantity(self, product_id, quantity):
        # Option 1: If you need to establish a connection using a method
        connection = self.get_database_connection()

        # Option 2: If the connection is already stored in a variable
        # connection = self.connection  # Use this if you have a connection object already
        
        cursor = connection.cursor()
        
        # Update the product quantity in the database
        cursor.execute("""
            UPDATE products
            SET quantity = quantity - ?
            WHERE id = ?
        """, (quantity, product_id))
        
        # Commit changes and close the cursor
        connection.commit()
        cursor.close()


    def get_product_id_by_name(self, product_name):
        conn = get_connection()
        cur = conn.cursor()
        
        # Get the product ID based on the product name
        cur.execute("SELECT id FROM products WHERE name = ?", (product_name,))
        result = cur.fetchone()
        conn.close()
        
        if result:
            return result[0]  # Return the product ID
        else:
            QMessageBox.warning(self, "Помилка", f"Товар '{product_name}' не знайдений.")
            return None
        
    def update_order_item(self, order_id, product_id, quantity, unit_price):
        conn = get_connection()
        cur = conn.cursor()
        
        # Update the order item in the database
        cur.execute("""
            UPDATE order_items
            SET quantity = ?, unit_price = ?
            WHERE order_id = ? AND product_id = ?
        """, (quantity, unit_price, order_id, product_id))
        
        conn.commit()
        conn.close()



    def open_payment_dialog(self, order_id, max_amount, orders_tab):
        dialog = QDialog()
        dialog.setWindowTitle("Внесення оплати")
        layout = QFormLayout()

        # Додаємо поля для відображення базової суми та знижки
        conn = get_connection("appliance_store.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT base_amount, discount_value, total_amount
            FROM orders
            WHERE id = ?
        """, (order_id,))
        base_amount, discount_value, total_amount = cur.fetchone()
        conn.close()

        # Відображення базової суми та знижки
        self.base_amount_label = QLabel(f"Сума без знижки: ₴{base_amount:.2f}")
        self.discount_label = QLabel(f"Знижка: {discount_value}%")
        self.total_amount_label = QLabel(f"До оплати: ₴{total_amount:.2f}")

        layout.addRow(self.base_amount_label)
        layout.addRow(self.discount_label)
        layout.addRow(self.total_amount_label)

        # Введення суми та методу оплати
        amount_input = QDoubleSpinBox()
        amount_input.setMaximum(max_amount)
        amount_input.setValue(max_amount)
        amount_input.setDecimals(2)

        method_box = QComboBox()
        method_box.addItems(["Готівка", "Картка", "Банківський переказ"])

        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(lambda: self.save_payment(
            dialog, order_id, amount_input.value(), method_box.currentText(), orders_tab
        ))

        layout.addRow("Сума:", amount_input)
        layout.addRow("Метод:", method_box)
        layout.addRow(save_btn)


        dialog.setLayout(layout)
        dialog.exec_()


    def get_selected_order_id(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть замовлення зі списку.")
            return None
        return int(self.table.item(selected_row, 0).text())


    def delete_order(self):
        order_id = self.get_selected_order_id()
        if order_id is None:
            return

        confirm = QMessageBox.question(
            self, "Підтвердження", f"Ви впевнені, що хочете видалити замовлення №{order_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()

            # Видалити товари замовлення
            cur.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            # Видалити саме замовлення
            cur.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успіх", "Замовлення видалено.")
            self.load_data()

            if self.payments_tab:
                self.payments_tab.load_data()

