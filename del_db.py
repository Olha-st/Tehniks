import sqlite3

# def clear_orders_and_payments(db_name="appliance_store.db"):
#     conn = sqlite3.connect(db_name)
#     cur = conn.cursor()

#     try:
#         # Видалити записи з таблиці order_items (спочатку залежну таблицю)
#         cur.execute("DELETE FROM order_items")
        
#         # Потім видалити з payments
#         cur.execute("DELETE FROM payments")
        
#         # Потім видалити з orders
#         cur.execute("DELETE FROM orders")

#         conn.commit()
#         print("Таблиці 'orders', 'order_items' та 'payments' очищено успішно.")
#     except Exception as e:
#         print("Помилка під час очищення:", e)
#         conn.rollback()
#     finally:
#         conn.close()

# # Виклик функції
# clear_orders_and_payments()


# import sqlite3

# def reset_orders_related_tables(db_path='appliance_store.db'):
#     try:
#         conn = sqlite3.connect(db_path)
#         cur = conn.cursor()

#         # Очистка таблиць
#         cur.execute("DELETE FROM order_items;")
#         cur.execute("DELETE FROM payments;")
#         cur.execute("DELETE FROM orders;")

#         # Скидання автоінкременту
#         cur.execute("DELETE FROM sqlite_sequence WHERE name='order_items';")
#         cur.execute("DELETE FROM sqlite_sequence WHERE name='payments';")
#         cur.execute("DELETE FROM sqlite_sequence WHERE name='orders';")

#         conn.commit()
#         print("Таблиці успішно очищено, і автоінкременти скинуто.")
#     except Exception as e:
#         print("Помилка:", e)
#     finally:
#         conn.close()

# # Виклик функції
# reset_orders_related_tables('your_database.db')  # Замінити на свій шлях до БД



# import sqlite3

# def clear_orders_and_payments(db_name="appliance_store.db"):
#     conn = sqlite3.connect(db_name)
#     cur = conn.cursor()
    
#     # Виведення усіх таблиць у базі
#     cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cur.fetchall()
#     print("Таблиці у базі:", [t[0] for t in tables])
    
#     conn.close()

# clear_orders_and_payments()


import sqlite3
import os

def reset_orders_related_tables(db_name="appliance_store.db"):
    db_path = os.path.abspath(db_name)
    print("Підключення до бази:", db_path)

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # Перевіряємо, чи існують необхідні таблиці
    required_tables = ['orders', 'order_items', 'payments']
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [row[0] for row in cur.fetchall()]

    for table in required_tables:
        if table not in existing_tables:
            print(f"⚠ Таблиця '{table}' не знайдена. Очищення не виконано.")
            conn.close()
            return

    # Очищення таблиць
    cur.execute("DELETE FROM order_items;")
    cur.execute("DELETE FROM payments;")
    cur.execute("DELETE FROM orders;")

    # Скидання AUTOINCREMENT
    cur.execute("DELETE FROM sqlite_sequence WHERE name='orders';")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='order_items';")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='payments';")

    conn.commit()
    conn.close()

    print("✅ Таблиці 'orders', 'order_items', 'payments' очищено та скинуто ID.")

# Запуск
reset_orders_related_tables()
