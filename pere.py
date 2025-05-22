import sqlite3

def migrate_customers_table(db_path="applianse_store.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # КРОК 1: Перейменувати стару таблицю
        # cursor.execute("ALTER TABLE customers RENAME TO customers_old;")

        # # КРОК 2: Створити нову таблицю з user_id
        # cursor.execute("""
        # CREATE TABLE customers (
        #     id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     user_id INTEGER UNIQUE NOT NULL,
        #     name TEXT NOT NULL,
        #     phone TEXT NOT NULL,
        #     email TEXT,
        #     address TEXT,
        #     FOREIGN KEY (user_id) REFERENCES users(id)
        # );
        # """)

        # КРОК 3: Вставити дані зі старої таблиці
        # ⚠️ Замінити user_id=1 на правильне значення у твоєму випадку
        cursor.execute("""
        INSERT INTO customers (name, phone, email, address, user_id)
        SELECT name, phone, email, address, 1 FROM customers1;
        """)

        conn.commit()
        print("[INFO] Таблицю оновлено та дані перенесено успішно.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"[ERROR] Сталася помилка: {e}")
    finally:
        conn.close()