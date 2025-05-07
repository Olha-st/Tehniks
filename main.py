from products_tab import ProductsTab
from customers_tab import ClientsTab
from suppliers_tab import SuppliersTab
from orders_tab import OrdersTab
from payments_tab import PaymentsTab
from styles import style_table
import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QSpacerItem,
    QMessageBox, QApplication, QTabWidget, QMainWindow, QHBoxLayout, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sqlite3
import sys

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вхід")
        self.setFixedSize(400, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: #F4E8FF;
            }
            QLabel {
                font-weight: bold;
            }
            QLineEdit, QPushButton {
                padding: 6px;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #B57EDC;
                color: white;
                font-weight: bold;
            }
        """)

        main_layout = QVBoxLayout()

        # Додаємо зображення
        image_label = QLabel()
        pixmap = QPixmap("logo.jpg")
        image_label.setPixmap(pixmap.scaledToWidth(150))  # масштабування
        if not pixmap.isNull():
            image_label.setPixmap(pixmap.scaledToWidth(200))
        else:
            image_label.setText("Зображення не знайдено")
        image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(image_label)

        # Привітальний текст
        welcome_label = QLabel("🌟 Авторизуйся\nта користуйся перевагами магазину!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #5A2A83;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(welcome_label)


        # Форма
        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Логін:", self.username_input)
        form_layout.addRow("Пароль:", self.password_input)

        # Додаємо відступ 1 см після поля пароля
        form_layout.addItem(QSpacerItem(0, 18, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Кнопки
        self.login_btn = QPushButton("Увійти")
        self.register_btn = QPushButton("Реєстрація")
        self.login_btn.setFixedSize(120, 40)
        self.register_btn.setFixedSize(120, 40)

        self.login_btn.clicked.connect(self.try_login)
        self.register_btn.clicked.connect(self.register_user)

        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.register_btn)
        buttons_layout.addSpacing(10)

        form_layout.addRow("", buttons_layout)

        main_layout.addLayout(form_layout)
        self.setLayout(main_layout)
        self.user_role = None


    def try_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        conn = sqlite3.connect("appliance_store.db")
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = cur.fetchone()
        conn.close()

        if result:
            self.user_role = result[0]
            self.accept()
        else:
            QMessageBox.warning(self, "Помилка", "Невірний логін або пароль")

    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть логін і пароль")
            return

        conn = sqlite3.connect("appliance_store.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        if cur.fetchone():
            QMessageBox.warning(self, "Помилка", "Користувач з таким логіном вже існує")
        else:
            cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, "user"))
            conn.commit()
            QMessageBox.information(self, "Успіх", "Користувача зареєстровано успішно!")
        conn.close()


class MainWindow(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.setWindowTitle("Магазин побутової техніки")
        self.setGeometry(100, 100, 1300, 600)
        self.user_role = role

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                background: #D8BFD8;              /* світло-бузковий */
                color: black;
                border: 1px solid #A9A9A9;
                padding: 5px 5px;
                font-size: 12px;
                font-weight: bold;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                min-width: 10px;
                height: 100px;
            }

            QTabBar::tab:selected {
                background: #9370DB;              /* активна вкладка - темніший бузковий */
                color: white;
            }

            QTabBar::tab:hover {
                background: #BA55D3;
                color: white;
            }

            QTabWidget::pane {
                border: 2px solid #9370DB;
                border-radius: 5px;
                padding: 5px;
            }
            """)
        



        # Спочатку створюємо ClientsTab
        self.clients_tab = ClientsTab()

        # Створюємо ProductsTab і зберігаємо посилання
        self.products_tab = ProductsTab()

        # Тимчасово створюємо orders_tab без посилань
        self.orders_tab = OrdersTab()

        # Створюємо PaymentsTab і передаємо посилання на інші вкладки
        self.payments_tab = PaymentsTab(self.orders_tab, self.clients_tab)

        # Тепер можна встановити посилання у OrdersTab
        self.orders_tab.payments_tab = self.payments_tab
        self.orders_tab.customers_tab = self.clients_tab
        self.orders_tab.products_tab = self.products_tab 

        # Викликаємо метод для ініціалізації UI
        self.init_ui()

    def init_ui(self):
        if self.user_role == "admin":
            # Адміністратор бачить усі вкладки
            self.tab_widget.addTab(self.products_tab, "Товари")
            self.tab_widget.addTab(self.orders_tab, "Замовлення")
            self.tab_widget.addTab(self.clients_tab, "Клієнти")
            self.tab_widget.addTab(self.payments_tab, "Оплати")
            # self.tab_widget.addTab(self.suppliers_tab, "Постачальники")
        elif self.user_role == "user":
            # Обмеження функціоналу для звичайного користувача
            self.products_tab.disable_editing()
            self.orders_tab.restrict_user_mode()

            self.tab_widget.addTab(self.products_tab, "Товари")
            self.tab_widget.addTab(self.orders_tab, "Замовлення")


        self.setCentralWidget(self.tab_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        window = MainWindow(login.user_role)
        window.show()
        sys.exit(app.exec_())

