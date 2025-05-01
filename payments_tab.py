import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QFormLayout, QComboBox,
    QDateEdit, QDoubleSpinBox, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import QDate
from database import (
    get_all_orders_with_total_and_paid, get_connection,
    add_payment
)
from functools import partial


DB_NAME = "appliance_store.db"
class PaymentsTab(QWidget):
    def __init__(self, orders_tab, customers_tab=None):
        super().__init__()
        self.orders_tab = orders_tab
        self.customers_tab = customers_tab
        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Назва замовлення", "Клієнт", "Дата", "Статус",
            "Сума замовлення", "Сплачено", "Дія"
        ])
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        orders = get_all_orders_with_total_and_paid()
        self.table.setRowCount(len(orders))

        for row, order in enumerate(orders):
            order_id, title, client_name, date, status, total, paid = order
            self.table.setItem(row, 0, QTableWidgetItem(title))
            self.table.setItem(row, 1, QTableWidgetItem(client_name))
            self.table.setItem(row, 2, QTableWidgetItem(date))
            self.table.setItem(row, 3, QTableWidgetItem(status))
            self.table.setItem(row, 4, QTableWidgetItem(f"₴{total:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"₴{paid:.2f}"))

            pay_button = QPushButton("Оплатити")
            pay_button.clicked.connect(partial(self.open_payment_dialog, order_id, total - paid, self.orders_tab))
            self.table.setCellWidget(row, 6, pay_button)

    def open_payment_dialog(self, order_id, max_amount, orders_tab):
        dialog = QDialog()
        dialog.setWindowTitle("Внесення оплати")
        layout = QFormLayout()

        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        date_input.setDate(QDate.currentDate())

        amount_input = QDoubleSpinBox()
        amount_input.setMaximum(max_amount)
        amount_input.setValue(max_amount)
        amount_input.setDecimals(2)

        method_box = QComboBox()
        method_box.addItems(["Готівка", "Картка", "Банківський переказ"])

        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(lambda: self.save_payment(
            dialog, order_id, date_input.date().toString("yyyy-MM-dd"),
            amount_input.value(), method_box.currentText(), orders_tab
        ))

        layout.addRow("Дата:", date_input)
        layout.addRow("Сума:", amount_input)
        layout.addRow("Метод:", method_box)
        layout.addRow(save_btn)

        if self.customers_tab:
            self.customers_tab.load_data()

        dialog.setLayout(layout)
        dialog.exec_()

    def save_payment(self, dialog, order_id, date, amount, method, orders_tab):
        conn = get_connection("appliance_store.db")
        cur = conn.cursor()
        if amount <= 0:
            QMessageBox.warning(self, "Помилка", "Сума має бути більшою за 0.")
            return
        add_payment(order_id, date, amount, method)

        # Перевірка суми після оплати
        cur.execute("""
            SELECT 
                IFNULL(SUM(order_items.quantity * order_items.unit_price), 0) AS total,
                IFNULL((SELECT SUM(amount) FROM payments WHERE order_id = ?), 0) AS paid
            FROM order_items
            WHERE order_items.order_id = ?
        """, (order_id, order_id))
        total, paid = cur.fetchone()

        if paid >= total:
            cur.execute("UPDATE orders SET status = 'Оплачено' WHERE id = ?", (order_id,))
            conn.commit()

        orders_tab.load_data()
        dialog.accept()
        self.load_data()


