from PyQt5.QtWidgets import (QWidget,QDoubleSpinBox, QVBoxLayout, QTableWidget,QHeaderView, QTabWidget,
                             QPushButton, QHBoxLayout, QComboBox, QLabel, QLineEdit,QInputDialog, 
                             QSpinBox, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QFileDialog)
from database import get_all_orders, add_order, get_customers, get_products, add_order_item
from database import get_connection, update_customer_discount
from functools import partial
import sqlite3
from PyQt5.QtCore import Qt
from styles import style_table
from reportlab.lib.pagesizes import A4
from PyQt5.QtWidgets import QPushButton
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure



class OrdersTab(QWidget):
    def __init__(self, parent=None, payments_tab=None, customers_tab=None, products_tab=None):
        super().__init__(parent)
        self.payments_tab = payments_tab
        self.customers_tab = customers_tab
        self.products_tab = products_tab  # Додаємо посилання на вкладку з товарами
        self.layout = QVBoxLayout()
        self.conn = get_connection()



        # Горизонтальний layout для кнопок
        button_layout = QHBoxLayout()
        button_layout.setSpacing(76)  # Відстань між кнопками = 2 см
        button_layout.setAlignment(Qt.AlignLeft)

        button_style = """
            QPushButton {
                background-color: #B57EDC;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 14px;
                border: none;
                border-radius: 8px;

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
        button_layout.addWidget(self.create_button)

        self.delete_button = QPushButton("Видалити замовлення")
        self.delete_button.setFixedSize(200, 40)
        self.delete_button.setStyleSheet(button_style)
        self.delete_button.clicked.connect(self.delete_order)
        button_layout.addWidget(self.delete_button)

        self.print_invoice_btn = QPushButton("          Друк чеку      ")
        self.print_invoice_btn.setFixedSize(200, 40)
        self.print_invoice_btn.setStyleSheet(button_style)
        self.print_invoice_btn.clicked.connect(self.print_invoice)
        button_layout.addWidget(self.print_invoice_btn)

        self.stats_button = QPushButton("Статистика")
        self.stats_button.setFixedSize(200, 40)
        self.stats_button.setStyleSheet(button_style)
        self.stats_button.clicked.connect(self.show_statistics)
        button_layout.addWidget(self.stats_button)


        # Відступ перед кнопками (1 см)
        self.layout.addSpacing(20)

        # Додаємо layout з кнопками
        self.layout.addLayout(button_layout)

        # Відступ після кнопок (1 см)
        self.layout.addSpacing(20)

        self.setLayout(self.layout)



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
        
        if self.products_tab:
            self.products_tab.load_data()




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
        style_table(self.products_table)
        self.table.setColumnWidth(0, 150) 
        self.table.setColumnWidth(1, 200) 
        self.table.setColumnWidth(2, 100)  

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
        product_names = [p[1] for p in products]  

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

        # Отримання кількості до зміни
        cur.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
        before_quantity = cur.fetchone()
        if before_quantity is None:
            QMessageBox.warning(self, "Помилка", "Не знайдено товару на складі.")
            conn.close()
            return

        print(f"[LOG] Кількість товару до зміни (ID={product_id}): {before_quantity[0]}")

        # Додавання товару до order_items
        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
        """, (order_id, product_id, quantity, price))

        # Зменшення кількості товару на складі
        cur.execute("""
            UPDATE products SET quantity = quantity - ?
            WHERE id = ? AND quantity >= ?
        """, (quantity, product_id, quantity))

        if cur.rowcount == 0:
            QMessageBox.warning(self, "Помилка", "Недостатня кількість товару на складі.")
            conn.rollback()
            conn.close()
            return

        # Отримання кількості після зміни
        cur.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
        after_quantity = cur.fetchone()
        print(f"[LOG] Кількість товару після зміни (ID={product_id}): {after_quantity[0]}")

        conn.commit()
        conn.close()

        # Додати рядок до таблиці
        row = product_table.rowCount()
        product_table.insertRow(row)
        product_table.setItem(row, 0, QTableWidgetItem(product_name))
        product_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        product_table.setItem(row, 2, QTableWidgetItem(str(price)))

        # Стилізована червона кнопка видалення
        delete_btn = QPushButton("Видалити")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6666;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e64545;
            }
        """)
        delete_btn.clicked.connect(lambda _, r=row: self.delete_product_from_order(r, order_id, product_table, total_label, discount_value))

        # Центрування кнопки в комірці
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addWidget(delete_btn)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        product_table.setCellWidget(row, 3, btn_container)

        # Оновлення суми
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
            self.update_product_quantity(product_id, quantity)  # віднімаємо кількість зі складу

        # Оновлюємо знижку клієнта (окремо)
        update_customer_discount(customer_id)

        # Оновлюємо таблиці з клієнтами та оплатами
        if self.payments_tab:
            self.payments_tab.load_data()

            # Оновлюємо таблицю товарів
        if self.products_tab:
            self.products_tab.load_data()

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

        delete_button_style = """
            QPushButton {
                background-color: #ff6666;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e64545;
            }
        """

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
            delete_btn.setStyleSheet(delete_button_style)
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




    # def save_order_changes(self, order_id, product_table, dialog, total_label, discount_value):
    #     base_amount = 0

    #     # Проходимо по всіх рядках таблиці товарів
    #     for row in range(product_table.rowCount()):
    #         product_name_item = product_table.item(row, 0)
    #         quantity_item = product_table.item(row, 1)
    #         price_item = product_table.item(row, 2)

    #         if not product_name_item or not quantity_item or not price_item:
    #             continue  # Пропустити порожні рядки

    #         product_name = product_name_item.text()
    #         try:
    #             # Спробуємо отримати кількість та ціну
    #             quantity = int(quantity_item.text())
    #             price = float(price_item.text().replace("₴", "").strip())  # Видаляємо ₴ та пробіли
    #         except ValueError:
    #             continue  # Пропустити некоректні значення

    #         product_id = self.get_product_id_by_name(product_name)
    #         if product_id is not None:
    #             # Оновлюємо дані в таблиці order_items
    #             self.update_order_item(order_id, product_id, quantity, price)
    #             # Оновлюємо кількість товару на складі
    #             self.update_product_quantity(product_id, quantity)

    #             base_amount += quantity * price  # Обчислюємо базову суму

    #     # Обчислюємо загальну суму після знижки
    #     total_amount = base_amount * (1 - discount_value / 100)

    #     # Оновлюємо інформацію в таблиці orders
    #     conn = get_connection()
    #     cur = conn.cursor()
    #     cur.execute("""
    #         UPDATE orders
    #         SET base_amount = ?, total_amount = ?
    #         WHERE id = ?
    #     """, (base_amount, total_amount, order_id))

    #     conn.commit()
    #     conn.close()

    #     # Оновлення вкладки Оплати
    #     if self.payments_tab:
    #         self.payments_tab.load_data()

    #     # Оновлення вкладки Клієнти
    #     if self.customers_tab:
    #         self.customers_tab.load_data()

    #     # Інформуємо користувача
    #     QMessageBox.information(self, "Збережено", "Зміни збережено успішно.")

    #     # Закриваємо діалогове вікно
    #     # dialog.accept()

    #     # Оновлюємо дані
    #     self.load_data()

    def save_order_changes(self, order_id, product_table, dialog, total_label, discount_value):
        base_amount = 0
        conn = get_connection()
        cur = conn.cursor()

        try:
            for row in range(product_table.rowCount()):
                product_name_item = product_table.item(row, 0)
                quantity_item = product_table.item(row, 1)
                price_item = product_table.item(row, 2)

                if not product_name_item or not quantity_item or not price_item:
                    continue  # Пропустити порожні рядки

                product_name = product_name_item.text()
                try:
                    quantity = int(quantity_item.text())
                    price = float(price_item.text().replace("₴", "").strip())
                except ValueError:
                    continue  # Пропустити некоректні значення

                # Отримуємо product_id і поточну кількість на складі
                cur.execute("SELECT id, quantity FROM products WHERE name = ?", (product_name,))
                product_data = cur.fetchone()
                if not product_data:
                    continue

                product_id, stock_quantity = product_data

                # Отримуємо стару кількість у замовленні
                cur.execute("""
                    SELECT quantity FROM order_items
                    WHERE order_id = ? AND product_id = ?
                """, (order_id, product_id))
                old_data = cur.fetchone()
                old_quantity = old_data[0] if old_data else 0

                # Обчислюємо зміну (дельту)
                delta = quantity - old_quantity

                # Перевірка на наявність достатньої кількості товару
                if delta > 0 and stock_quantity < delta:
                    raise Exception(f"Недостатньо товару '{product_name}' на складі. Доступно: {stock_quantity}, потрібно: {delta}.")

                # Оновлюємо order_items
                if old_data:
                    cur.execute("""
                        UPDATE order_items
                        SET quantity = ?, unit_price = ?
                        WHERE order_id = ? AND product_id = ?
                    """, (quantity, price, order_id, product_id))
                else:
                    cur.execute("""
                        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                        VALUES (?, ?, ?, ?)
                    """, (order_id, product_id, quantity, price))

                # Оновлюємо склад на основі різниці
                cur.execute("""
                    UPDATE products
                    SET quantity = quantity - ?
                    WHERE id = ?
                """, (delta, product_id))

                base_amount += quantity * price

            # Обчислення суми зі знижкою
            total_amount = base_amount * (1 - discount_value / 100)

            cur.execute("""
                UPDATE orders
                SET base_amount = ?, total_amount = ?
                WHERE id = ?
            """, (base_amount, total_amount, order_id))

            conn.commit()

            QMessageBox.information(self, "Збережено", "Зміни збережено успішно.")
            dialog.accept()

            if self.payments_tab:
                self.payments_tab.load_data()

            if self.customers_tab:
                self.customers_tab.load_data()

            self.load_data()

        except Exception as e:
            conn.rollback()
            QMessageBox.warning(self, "Помилка", f"Не вдалося зберегти зміни:\n{str(e)}")

        finally:
            conn.close()



    def get_database_connection(self):
        # Replace with your actual database file path
        return sqlite3.connect("appliance_store.db")

    def update_product_quantity(self, product_id, quantity):
        try:
            # Отримуємо з'єднання з базою даних
            connection = self.get_database_connection()
            
            # Створюємо курсор
            cursor = connection.cursor()

            # Перевіряємо поточну кількість товару перед зменшенням
            cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
            current_quantity = cursor.fetchone()[0]

            if current_quantity is None or current_quantity < quantity:
                # Якщо кількість товару недостатня, можна вивести попередження або вжити інших дій
                QMessageBox.warning(self, "Помилка", "Недостатньо товару на складі.")
                return

            # Оновлюємо кількість товару
            cursor.execute("""
                UPDATE products
                SET quantity = quantity - ?
                WHERE id = ?
            """, (quantity, product_id))

            # Підтверджуємо зміни в базі даних
            connection.commit()

            # Оновлюємо таблицю товарів, щоб відобразити нові дані
            if self.products_tab:
                self.products_tab.load_data()

        except Exception as e:
            # Логування або виведення помилки
            print(f"Помилка оновлення кількості товару: {e}")
            QMessageBox.warning(self, "Помилка", f"Сталася помилка при оновленні кількості товару: {e}")
        
        finally:
            # Закриваємо курсор і з'єднання в будь-якому випадку
            cursor.close()
            connection.close()



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


    # def delete_order(self):
    #     order_id = self.get_selected_order_id()
    #     if order_id is None:
    #         return

    #     confirm = QMessageBox.question(
    #         self, "Підтвердження", f"Ви впевнені, що хочете видалити замовлення №{order_id}?",
    #         QMessageBox.Yes | QMessageBox.No
    #     )

    #     if confirm == QMessageBox.Yes:
    #         conn = get_connection()
    #         cur = conn.cursor()

    #         # Видалити товари замовлення
    #         cur.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
    #         # Видалити саме замовлення
    #         cur.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    #         conn.commit()
    #         conn.close()

    #         QMessageBox.information(self, "Успіх", "Замовлення видалено.")
    #         self.load_data()

    #         if self.payments_tab:
    #             self.payments_tab.load_data()

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

            # 1. Отримати список товарів і кількостей у замовленні
            cur.execute("""
                SELECT product_id, quantity FROM order_items WHERE order_id = ?
            """, (order_id,))
            items = cur.fetchall()

            # 2. Повернути кожен товар на склад
            for product_id, quantity in items:
                cur.execute("""
                    UPDATE products
                    SET quantity = quantity + ?
                    WHERE id = ?
                """, (quantity, product_id))

            # 3. Видалити записи з order_items
            cur.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            # 4. Видалити саме замовлення
            cur.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успіх", "Замовлення видалено і товари повернуто на склад.")
            self.load_data()

            if self.payments_tab:
                self.payments_tab.load_data()


    def restrict_user_mode(self):
        # Доступна лише кнопка "Створити замовлення"
        self.create_button.setEnabled(True)

        # Забороняємо/вимикаємо інші кнопки та таблицю
        self.delete_button.setEnabled(False)
        self.table.setDisabled(True)


    def print_invoice(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Помилка", "Будь ласка, виберіть замовлення для друку.")
            return

        try:
            order_id = int(self.table.item(selected_items[0].row(), 0).text())
        except ValueError:
            QMessageBox.warning(self, "Помилка", "Неможливо отримати ID замовлення.")
            return

        from database import get_connection
        conn = get_connection()
        cur = conn.cursor()

        # Отримати основну інформацію про замовлення
        cur.execute("SELECT title, base_amount, total_amount FROM orders WHERE id = ?", (order_id,))
        order_info = cur.fetchone()
        if not order_info:
            QMessageBox.warning(self, "Помилка", "Замовлення не знайдено.")
            return

        title, base_amount, total_amount = order_info

        # Отримати товари замовлення
        cur.execute("""
            SELECT p.name, oi.quantity, p.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (order_id,))

        items = cur.fetchall()
        conn.close()

        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.units import cm

        # Підключити шрифт Arial
        pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))

        file_path = f"check_{title.replace(':', '-')}.pdf"
        c = canvas.Canvas(file_path, pagesize=A4)
        c.setFont("Arial", 12)

        width, height = A4
        y = height - 2 * cm

        # Заголовок
        c.setFont("Arial", 14)
        c.drawCentredString(width / 2, y, f"Чек до замовлення № {title}")
        y -= 1.2 * cm

        # Банківські реквізити
        c.setFont("Arial", 10)
        details = [
            "IBAN: UA393287040000026002054312944 в АТ КБ \"ПРИВАТБАНК\" (МФО 328704)",
            "ЄДРПОУ: 38935167",
            "ІПН: 389351615535",
            "Св-во ПДВ: 200149913",
            "Директор, діючий на підставі Статуту: Авраменко Віталій Валерійович",
            "Контактний телефон: (048) 736-04-94"
        ]
        for line in details:
            c.drawString(2 * cm, y, line)
            y -= 0.6 * cm

        y -= 0.8 * cm
        c.setFont("Arial", 11)
        c.drawString(2 * cm, y, "Товари:")
        y -= 0.5 * cm

        # Таблиця товарів
        c.setFont("Arial", 10)
        c.drawString(2 * cm, y, "Назва")
        c.drawString(8 * cm, y, "Кількість")
        c.drawString(12 * cm, y, "Ціна")
        y -= 0.4 * cm

        for name, quantity, price in items:
            c.drawString(2 * cm, y, str(name))
            c.drawString(10 * cm, y, str(quantity))
            c.drawString(12 * cm, y, f"{price:.2f} грн")
            y -= 0.4 * cm

        y -= 0.8 * cm
        c.setFont("Arial", 11)
        c.drawString(2 * cm, y, f"До оплати (без знижки): {base_amount:.2f} грн")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Знижка: {base_amount - total_amount:.2f} грн")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Сума до оплати: {total_amount:.2f} грн")

        c.save()

        QMessageBox.information(self, "Готово", f"Чек збережено як {file_path}")




    def show_statistics(self):
        conn = sqlite3.connect("appliance_store.db")
        cursor = conn.cursor()

        # --- Дані для продажів у грн ---
        cursor.execute("""
            SELECT 
                categories.name AS category_name,
                SUM(order_items.quantity * order_items.unit_price) AS total_sales
            FROM order_items
            JOIN products ON order_items.product_id = products.id
            JOIN categories ON products.category_id = categories.id
            GROUP BY categories.id
            ORDER BY total_sales DESC
        """)
        sales_results = cursor.fetchall()
        sales_dict = {row[0]: row[1] for row in sales_results}

        # --- Дані для кількості продажів ---
        cursor.execute("""
            SELECT 
                categories.name AS category_name,
                SUM(order_items.quantity) AS total_quantity
            FROM order_items
            JOIN products ON order_items.product_id = products.id
            JOIN categories ON products.category_id = categories.id
            GROUP BY categories.id
            ORDER BY total_quantity DESC
        """)
        quantity_results = cursor.fetchall()
        quantity_dict = {row[0]: row[1] for row in quantity_results}

        conn.close()

        categories = list(sales_dict.keys())

        # --- Створення діалогу ---
        dialog = QDialog(self)
        dialog.setWindowTitle("Статистика продажів")
        layout = QVBoxLayout()
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.West)

        # --- Вкладка 1: Таблиця ---
        table_tab = QWidget()
        table_layout = QVBoxLayout()

        # Основна таблиця
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Категорія", "Сума продажів (грн)", "Кількість (шт)"])
        style_table(table)
        table.setColumnWidth(0, 300) 
        table.setColumnWidth(1, 200) 
        table.setColumnWidth(2, 180)  
        table.setRowCount(len(categories))

        for row_idx, category in enumerate(categories):
            total_sales = sales_dict.get(category, 0)
            total_quantity = quantity_dict.get(category, 0)
            table.setItem(row_idx, 0, QTableWidgetItem(category))
            table.setItem(row_idx, 1, QTableWidgetItem(f"{total_sales:.2f}"))
            table.setItem(row_idx, 2, QTableWidgetItem(str(total_quantity)))

        # ТОП-3 за сумою
        top_3_sales = sorted(sales_results, key=lambda x: x[1], reverse=True)[:3]
        top_sales_text = "ТОП-3 за сумою:\n" + "\n".join(
            [f"{i+1}. {cat} – {amt:.2f} грн" for i, (cat, amt) in enumerate(top_3_sales)]
        )
        top_sales_label = QLabel(top_sales_text)
        top_sales_label.setStyleSheet("font-weight: bold; margin-top: 10px;")

        # ТОП-3 за кількістю
        top_3_quantity = sorted(quantity_results, key=lambda x: x[1], reverse=True)[:3]
        top_qty_text = "ТОП-3 за кількістю:\n" + "\n".join(
            [f"{i+1}. {cat} – {qty} шт" for i, (cat, qty) in enumerate(top_3_quantity)]
        )
        top_qty_label = QLabel(top_qty_text)
        top_qty_label.setStyleSheet("font-weight: bold; margin-top: 10px;")

        # Додати до layout
        table_layout.addWidget(table)
        table_layout.addWidget(top_sales_label)
        table_layout.addWidget(top_qty_label)
        table_tab.setLayout(table_layout)
        tabs.addTab(table_tab, "Таблиця")

        # --- Вкладка 2: Графік суми продажів ---
        chart_tab = QWidget()
        chart_layout = QVBoxLayout()

        fig1 = Figure(figsize=(6, 4))
        canvas1 = FigureCanvas(fig1)
        ax1 = fig1.add_subplot(111)

        ax1.bar(categories, [sales_dict[c] for c in categories], color='skyblue')
        ax1.set_title("Продажі за категоріями")
        ax1.set_ylabel("Сума продажів (грн)")
        ax1.set_xticks(range(len(categories)))
        ax1.set_xticklabels(categories, rotation=60, ha='right')

        fig1.tight_layout()
        chart_layout.addWidget(canvas1)
        chart_tab.setLayout(chart_layout)
        tabs.addTab(chart_tab, "Діаграма (грн)")

        # --- Вкладка 3: Графік кількості продажів ---
        quantity_tab = QWidget()
        quantity_layout = QVBoxLayout()

        fig2 = Figure(figsize=(6, 4))
        canvas2 = FigureCanvas(fig2)
        ax2 = fig2.add_subplot(111)

        ax2.bar(categories, [quantity_dict[c] for c in categories], color='lightgreen')
        ax2.set_title("Кількість проданих товарів за категоріями")
        ax2.set_ylabel("Кількість товарів")
        ax2.set_xticks(range(len(categories)))
        ax2.set_xticklabels(categories, rotation=60, ha='right')

        fig2.tight_layout()
        quantity_layout.addWidget(canvas2)
        quantity_tab.setLayout(quantity_layout)
        tabs.addTab(quantity_tab, "Діаграма (шт)")

        # --- Завершення ---
        layout.addWidget(tabs)
        dialog.setLayout(layout)
        dialog.resize(800, 550)
        dialog.exec_()




