# вікно додавання/редагування товару
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QLabel, QFileDialog
from database import get_categories

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("Товар")

        self.categories = get_categories()
        self.selected_category_id = None

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Назва товару")
        layout.addWidget(QLabel("Назва:"))
        layout.addWidget(self.name_input)

        self.description_input = QTextEdit()
        layout.addWidget(QLabel("Опис:"))
        layout.addWidget(self.description_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1_000_000)
        self.price_input.setPrefix("₴")
        layout.addWidget(QLabel("Ціна:"))
        layout.addWidget(self.price_input)

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 10000)
        layout.addWidget(QLabel("Кількість:"))
        layout.addWidget(self.quantity_input)

        self.category_box = QComboBox()
        for cat_id, cat_name in self.categories:
            self.category_box.addItem(cat_name, cat_id)
        layout.addWidget(QLabel("Категорія:"))
        layout.addWidget(self.category_box)

        self.image_input = QLineEdit()
        browse_btn = QPushButton("Огляд...")
        browse_btn.clicked.connect(self.browse_image)
        layout.addWidget(QLabel("Шлях до фото:"))
        layout.addWidget(self.image_input)
        layout.addWidget(browse_btn)

        self.save_button = QPushButton("Зберегти")
        self.save_button.clicked.connect(self.accept)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        if product:
            self.name_input.setText(product[1])
            self.description_input.setPlainText(product[2])
            self.price_input.setValue(product[3])
            self.quantity_input.setValue(product[4])
            self.category_box.setCurrentIndex(self.category_box.findData(product[5]))
            self.image_input.setText(product[6])

    def get_data(self):
        return (
            self.name_input.text(),
            self.description_input.toPlainText(),
            self.price_input.value(),
            self.quantity_input.value(),
            self.category_box.currentData(),
            self.image_input.text()
        )

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Оберіть зображення", "", "Image Files (*.png *.jpg *.jpeg)")
        if path:
            self.image_input.setText(path)
