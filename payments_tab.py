import sqlite3
from PyQt5.QtCore import Qt
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
from styles import style_table, style_controls


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
            "Номер", "Клієнт", "Дата", "Статус",
            "До оплати", "Сплачено", "Дія"
        ])
        style_table(self.table)
        self.table.setColumnWidth(0, 150) 
        self.table.setColumnWidth(1, 200) 
        self.table.setColumnWidth(2, 100)  
        self.table.setColumnWidth(3, 100) 
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 110)
        self.table.setColumnWidth(6, 120)

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        orders = get_all_orders_with_total_and_paid()
        self.table.setRowCount(len(orders))

        for row, order in enumerate(orders):
            order_id, title, client_name, date, status, base, discount, total, paid = order
            self.table.setItem(row, 0, QTableWidgetItem(title))
            self.table.setItem(row, 1, QTableWidgetItem(client_name))
            self.table.setItem(row, 2, QTableWidgetItem(date))
            self.table.setItem(row, 3, QTableWidgetItem(status))
            self.table.setItem(row, 4, QTableWidgetItem(f"₴{total:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"₴{paid:.2f}"))
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
            pay_button = QPushButton("Оплатити")
            pay_button.setFixedSize(100, 40)
            pay_button.setStyleSheet(button_style)
            pay_button.clicked.connect(partial(self.open_payment_dialog, order_id, total - paid, self.orders_tab))
            # self.table.setCellWidget(row, 6, pay_button)

            # Центрування кнопки у комірці
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.addWidget(pay_button)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setContentsMargins(0, 0, 0, 0)  # без відступів

            self.table.setCellWidget(row, 6, btn_container)
            self.table.verticalHeader().setDefaultSectionSize(60)  # висота рядка


    def open_payment_dialog(self, order_id, max_amount, orders_tab):
        dialog = QDialog()
        dialog.setWindowTitle("Внесення оплати")
        layout = QFormLayout()

        # Стилізація діалогу
        dialog.setStyleSheet("""
            QDialog {
                background-color: #F4E8FF;
                font-family: Arial;
                font-size: 14px;
            }
            QFormLayout QLabel {
                font-weight: bold;
                margin-bottom: 6px;
            }
            QLineEdit, QDoubleSpinBox, QComboBox, QDateEdit {
                padding: 6px;
                border: 1px solid #B57EDC;
                border-radius: 6px;
                background-color: white;
            }
            QPushButton {
                background-color: #B57EDC;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #A070C4;
            }
            QPushButton:pressed {
                background-color: #8E5CB5;
            }
        """)

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
            dialog,
            order_id,
            date_input.date().toString("yyyy-MM-dd"),
            amount_input.value(),
            method_box.currentText(),
            orders_tab
        ))

        layout.addRow("Дата:", date_input)
        layout.addRow("Сума:", amount_input)
        layout.addRow("Метод:", method_box)
        layout.addRow("", save_btn)  # пусте ім'я поля, щоб кнопка була під елементами

        dialog.setLayout(layout)
        dialog.exec_()

    def save_payment(self, dialog, order_id, payment_date, amount, method, orders_tab):
        conn = get_connection("appliance_store.db")
        cur = conn.cursor()

        if amount <= 0:
            QMessageBox.warning(self, "Помилка", "Сума має бути більшою за 0.")
            return

        # Додаємо оплату в базу даних
        add_payment(order_id, payment_date, amount, method)

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



