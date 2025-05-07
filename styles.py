# table_styles.py

from PyQt5.QtWidgets import QTableWidget

def style_table(table: QTableWidget):
    """Функція стилізації таблиці"""

    # Стиль заголовків
    table.horizontalHeader().setStyleSheet(
        "QHeaderView::section {"
        "background-color: #9370DB;"  # Темно-бузковий
        "color: white;"
        "font-size: 18px;"
        "font-weight: bold;"
        "padding: 10px;"
        "}"
    )

    # Стиль самої таблиці
    # table.setStyleSheet("""
    #     QTableWidget {
    #         background-color: #E6E6FA;           /* Бузковий (lavender) */
    #         font-size: 18px;
    #         gridline-color: #D8BFD8;            /* Блідо-бузковий */
    #         selection-background-color: #DDA0DD;/* Світло-бузковий для виділення */
    #         selection-color: black;
    #     }
    # """)

    # Автоматичне розтягування останньої колонки
    # table.horizontalHeader().setStretchLastSection(True)




def style_controls(
    add_button,
    edit_button,
    delete_button,
    details_button,
    filter_button,
    labels,
    line_edits,
    combo_box
):
    # Кнопки
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
    for btn in [add_button, edit_button, delete_button, details_button, filter_button]:
        btn.setStyleSheet(button_style)

    # Мітки
    label_style = """
        QLabel {
            font-size: 14px;
            color: #333;
            font-weight: bold;
        }
    """
    for lbl in labels:
        lbl.setStyleSheet(label_style)

    # Поля введення
    line_edit_style = """
        QLineEdit {
            font-size: 14px;
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 6px;
            min-width: 60px;
        }
    """
    for edit in line_edits:
        edit.setStyleSheet(line_edit_style)

    # Комбобокс
    combo_style = """
        QComboBox {
            font-size: 14px;
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        QComboBox QAbstractItemView {
            selection-background-color: #B57EDC;
        }
    """
    combo_box.setStyleSheet(combo_style)
