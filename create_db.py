import sqlite3

# Створення/підключення до бази даних
conn = sqlite3.connect("appliance_store.db")
cursor = conn.cursor()

# 1. Таблиця категорій товарів
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
)
""")

# 2. Таблиця товарів
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    category_id INTEGER,
    image_path TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
""")

# 3. Таблиця клієнтів
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT
)
""")

# 4. Таблиця замовлень
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
""")

# 5. Таблиця товарів у замовленнях
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
""")

# 6. Таблиця оплат
cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    payment_date TEXT NOT NULL,
    amount REAL NOT NULL,
    method TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
)
""")

# 7. Таблиця постачальників
cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_info TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price_per_unit REAL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
""")


# Збереження змін і закриття з'єднання
conn.commit()
conn.close()

print("Базу даних успішно створено.")
