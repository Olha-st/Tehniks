from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QComboBox, QLabel, QLineEdit, QSpinBox, QTableWidgetItem, QMessageBox, QDialog, QFormLayout
from database import get_all_orders, add_order, get_customers, get_products, add_order_item, get_order_items_by_order_id, update_product_quantity

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

        self.view_button = QPushButton("Переглянути деталі")
        self.view_button.clicked.connect(self.handle_view_order)
        button_layout.addWidget(self.view_button)

        self.layout.addLayout(button_layout)

        # Таблиця замовлень
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Клієнт", "Дата", "Статус"])
        self.table.cellDoubleClicked.connect(self.show_order_details)
        self.layout.addWidget(self.table)



        self.setLayout(self.layout)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        orders = get_all_orders()
        self.table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.table.setItem(row, 0, QTableWidgetItem(str(order[0])))
            self.table.setItem(row, 1, QTableWidgetItem(order[1]))
            self.table.setItem(row, 2, QTableWidgetItem(order[2]))
            self.table.setItem(row, 3, QTableWidgetItem(order[3]))

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



    # def show_order_details(self, row, column):
    #     order_id = int(self.table.item(row, 0).text())
    #     items = get_order_items_by_order_id(order_id)

    #     msg = "Склад замовлення:\n"
    #     total = 0
    #     for item in items:
    #         name, quantity, unit_price = item
    #         total += quantity * unit_price
    #         msg += f"{name} — {quantity} × ₴{unit_price} = ₴{quantity * unit_price}\n"

    #     msg += f"\nЗагальна сума: ₴{total}"
    #     QMessageBox.information(self, "Деталі замовлення", msg)



    def show_order_details(self, order_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT o.base_amount, o.discount_value, o.total_amount
            FROM orders o
            WHERE o.id = ?
        """, (order_id,))
        result = cur.fetchone()
        if result:
            base_amount, discount_value, total_amount = result
            discount_str = f"{discount_value}%"
            self.base_amount_label.setText(f"Сума без знижки: {base_amount} грн")
            self.discount_label.setText(f"Знижка: {discount_str}")
            self.total_amount_label.setText(f"До оплати: {total_amount} грн")
        conn.close()


    def handle_view_order(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Увага", "Будь ласка, виберіть замовлення.")
            return
        row = self.table.currentRow()
        self.show_order_details(row, 0)

    def open_payment_dialog(self, order_id, max_amount):
        # Передаємо current `OrdersTab` як аргумент
        self.payments_tab.open_payment_dialog(order_id, max_amount, self)


