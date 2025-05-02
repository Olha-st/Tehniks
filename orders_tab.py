from PyQt5.QtWidgets import QWidget,QDoubleSpinBox, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QComboBox, QLabel, QLineEdit, QSpinBox, QTableWidgetItem, QMessageBox, QDialog, QFormLayout
from database import get_all_orders, add_order, get_customers, get_products, add_order_item, get_order_items_by_order_id, update_product_quantity
from database import get_connection, get_all_orders_with_total_and_paid
from functools import partial



class OrdersTab(QWidget):
    def __init__(self, payments_tab=None, customers_tab=None):
        super().__init__()
        self.payments_tab = payments_tab
        self.customers_tab = customers_tab
        self.layout = QVBoxLayout()

        # Кнопки
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Створити замовлення")
        self.create_button.clicked.connect(self.open_order_form)
        button_layout.addWidget(self.create_button)

        self.delete_button = QPushButton("Видалити замовлення")
        self.delete_button.clicked.connect(self.delete_order)
        button_layout.addWidget(self.delete_button)


        self.layout.addLayout(button_layout)

        # Таблиця замовлень
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Клієнт", "Дата", "Статус", ""])
        self.table.cellDoubleClicked.connect(self.show_order_details_dialog)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.load_data()

    def load_data(self):
        conn = get_connection()
        cur = conn.cursor()

        # Отримуємо дані з бази даних
        cur.execute("""
            SELECT o.id, c.name, o.order_date, o.status
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
        """)
        orders = cur.fetchall()
        conn.close()

        # Оновлюємо таблицю з замовленнями
        self.table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            order_id, client_name, order_date, status = order
            self.table.setItem(row, 0, QTableWidgetItem(str(order_id)))
            self.table.setItem(row, 1, QTableWidgetItem(client_name))
            self.table.setItem(row, 2, QTableWidgetItem(order_date))
            self.table.setItem(row, 3, QTableWidgetItem(status))
            details_btn = QPushButton("Деталі")
            details_btn.clicked.connect(lambda _, oid=order_id: self.show_order_details_dialog(oid))
            self.table.setCellWidget(row, 4, details_btn)



    def open_order_form(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Нове замовлення")
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
        add_button.clicked.connect(self.add_product_to_order)


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


        self.dialog.setLayout(form_layout)
        self.dialog.exec_()

    def add_product_to_order(self):
        product_id = self.product_select.currentData()
        product = next(p for p in self.filtered_products if p[0] == product_id)
        name, price, quantity_available = product[1], product[2], product[3]
        quantity = self.quantity_input.value()

        if quantity > quantity_available:
            QMessageBox.warning(self, "Помилка", "Недостатня кількість товару на складі.")
            return

        self.product_list.append((product_id, quantity, price))

        row = self.products_table.rowCount()
        self.products_table.insertRow(row)
        self.products_table.setItem(row, 0, QTableWidgetItem(name))
        self.products_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        self.products_table.setItem(row, 2, QTableWidgetItem(f"₴{price}"))

        total = sum(q * p for _, q, p in self.product_list)
        self.total_label.setText(f"Загальна сума: ₴{total}")


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
        discount_value = int(discount_str.replace('%', ''))

        # Обчислюємо суму замовлення зі знижкою
        total_amount = base_amount * (1 - discount_value / 100)

        # Передаємо загальну суму в функцію add_order
        order_id = add_order(customer_id, order_date, base_amount)

        for product_id, quantity, unit_price in self.product_list:
            add_order_item(order_id, product_id, quantity, unit_price)
            update_product_quantity(product_id, -quantity)

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

        # Отримати товари замовлення
        cur.execute("""
            SELECT p.name, oi.quantity, oi.unit_price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (order_id,))
        products = cur.fetchall()

        conn.close()

        # Створити діалогове вікно
        dialog = QDialog()
        dialog.setWindowTitle(f"Деталі замовлення №{order_id}")

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Клієнт: {customer_name}"))
        layout.addWidget(QLabel(f"Сума без знижки: ₴{base_amount:.2f}"))
        layout.addWidget(QLabel(f"Знижка: {discount_value}%"))
        layout.addWidget(QLabel(f"До оплати: ₴{total_amount:.2f}"))

        # Таблиця товарів
        product_table = QTableWidget()
        product_table.setColumnCount(3)
        product_table.setHorizontalHeaderLabels(["Назва товару", "Кількість", "Ціна"])
        product_table.setRowCount(len(products))

        for row, (name, qty, price) in enumerate(products):
            product_table.setItem(row, 0, QTableWidgetItem(name))
            product_table.setItem(row, 1, QTableWidgetItem(str(qty)))
            product_table.setItem(row, 2, QTableWidgetItem(f"₴{price:.2f}"))

        layout.addWidget(QLabel("Список товарів:"))
        layout.addWidget(product_table)

        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec_()


    


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

