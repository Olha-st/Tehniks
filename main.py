import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget
from PyQt5.QtCore import Qt
from products_tab import ProductsTab
from customers_tab import ClientsTab
from suppliers_tab import SuppliersTab
from orders_tab import OrdersTab
from payments_tab import PaymentsTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Магазин побутової техніки")
        self.setGeometry(100, 100, 1000, 600)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)

        # Створення вкладок
        self.clients_tab = ClientsTab()
        self.orders_tab = OrdersTab()  # Спочатку створюємо orders_tab
        self.payments_tab = PaymentsTab(self.orders_tab, self.clients_tab)

        # Передаємо посилання на вкладки, які мають бути оновлені
        self.orders_tab.payments_tab = self.payments_tab
        self.orders_tab.customers_tab = self.clients_tab

        # Додавання вкладок у правильному порядку
        self.tab_widget.addTab(ProductsTab(), "Товари")
        self.tab_widget.addTab(self.orders_tab, "Замовлення")
        self.tab_widget.addTab(self.payments_tab, "Оплати")
        self.tab_widget.addTab(self.clients_tab, "Клієнти")
        self.tab_widget.addTab(SuppliersTab(), "Постачальники")





        self.setCentralWidget(self.tab_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
