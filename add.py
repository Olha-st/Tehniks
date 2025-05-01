import sqlite3

def alter_customers_table():
    conn = sqlite3.connect("appliance_store.db")  # заміни на своє ім'я бази
    cur = conn.cursor()

    # Додаємо колонку discount_level, якщо її ще немає
    try:
        cur.execute("ALTER TABLE customers ADD COLUMN discount_level TEXT DEFAULT '0%'")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise

    # Додаємо колонку is_regular, якщо її ще немає
    try:
        cur.execute("ALTER TABLE customers ADD COLUMN is_regular INTEGER DEFAULT 0")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise

    conn.commit()
    conn.close()



def add_total_amount_column():
    conn = sqlite3.connect("appliance_store.db")  # заміни на ім’я твоєї бази
    cur = conn.cursor()

    # Перевіряємо, чи поле total_amount уже існує
    cur.execute("PRAGMA table_info(orders)")
    columns = [column[1] for column in cur.fetchall()]
    
    if "total_amount" not in columns:
        cur.execute("ALTER TABLE orders ADD COLUMN total_amount REAL DEFAULT 0")
        conn.commit()
        print("Стовпець 'total_amount' успішно додано до таблиці 'orders'.")
    else:
        print("Стовпець 'total_amount' вже існує.")
    
    conn.close()

# Виклик функції
add_total_amount_column()



# Виклик функції
alter_customers_table()
