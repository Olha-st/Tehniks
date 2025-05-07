import sqlite3
# функції для роботи з БД (SQLite)
DB_NAME = "appliance_store.db"

def get_connection(db_name="appliance_store.db"):
    return sqlite3.connect(db_name)

def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM categories")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_product(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (name, description, price, quantity, category_id, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

def update_product(product_id, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE products
        SET name=?, description=?, price=?, quantity=?, category_id=?, image_path=?
        WHERE id=?
    """, (*data, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

# користувачі
def get_category_names():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return {cat[0]: cat[1] for cat in categories}

def get_all_clients():
    """ Отримати всіх клієнтів з бази даних """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")  # Ваш запит для отримання всіх клієнтів
    clients = cursor.fetchall()
    conn.close()
    return clients

def add_client_to_db(name, phone, email, address):
    """ Додати нового клієнта в базу даних """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, phone, email, address)
        VALUES (?,?, ?, ?)
    """, (name, phone, email, address))
    conn.commit()
    conn.close()

def update_client_in_db(client_id, name, phone, email, address):
    """ Оновити дані клієнта в базі даних """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET name = ?, phone = ?, email = ?, address = ?
        WHERE id = ?
    """, (name, phone, email, address, client_id))
    conn.commit()
    conn.close()

def delete_client_from_db(client_id):
    """ Видалити клієнта з бази даних """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()

def get_customer_info(customer_id):
    conn = get_connection()
    cur = conn.cursor()

    # Загальна сума покупок і кількість замовлень
    cur.execute("""
        SELECT 
            COUNT(DISTINCT orders.id) AS order_count,
            IFNULL(SUM(order_items.quantity * order_items.unit_price), 0) AS total_spent
        FROM orders
        LEFT JOIN order_items ON orders.id = order_items.order_id
        WHERE orders.customer_id = ?
    """, (customer_id,))
    order_count, total_spent = cur.fetchone()

    # Отримуємо знижку та статус клієнта з таблиці customers
    cur.execute("""
        SELECT discount_level, is_regular
        FROM customers
        WHERE id = ?
    """, (customer_id,))
    discount, is_regular = cur.fetchone()

    # Отримуємо список замовлень клієнта
    cur.execute("""
        SELECT orders.id, orders.order_date, orders.status,
               IFNULL(SUM(order_items.quantity * order_items.unit_price), 0) AS total
        FROM orders
        LEFT JOIN order_items ON orders.id = order_items.order_id
        WHERE orders.customer_id = ?
        GROUP BY orders.id
        ORDER BY orders.order_date DESC
    """, (customer_id,))
    orders = cur.fetchall()

    conn.close()

    return {
        "order_count": order_count,
        "total_spent": total_spent,
        "discount": discount,
        "is_regular": is_regular,
        "orders": orders
    }



def update_customer_discount(customer_id):
    conn = get_connection()
    cur = conn.cursor()

    # Підрахунок загальної суми покупок і кількості замовлень
    cur.execute("""
        SELECT 
            COUNT(DISTINCT orders.id) AS order_count,
            IFNULL(SUM(order_items.quantity * order_items.unit_price), 0) AS total_spent
        FROM orders
        LEFT JOIN order_items ON orders.id = order_items.order_id
        WHERE orders.customer_id = ?
    """, (customer_id,))
    order_count, total_spent = cur.fetchone()

    # Визначення знижки
    if total_spent >= 50000:
        discount = "10%"
    elif total_spent >= 25000:
        discount = "5%"
    elif total_spent >= 12000:
        discount = "3%"
    else:
        discount = "0%"

    # Визначення постійного клієнта
    is_regular = 1 if order_count >= 3 else 0

    # Оновлення даних клієнта
    cur.execute("""
        UPDATE customers
        SET discount_level = ?, is_regular = ?
        WHERE id = ?
    """, (discount, is_regular, customer_id))

    conn.commit()
    conn.close()




def get_all_clients_with_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.id,
            c.name,
            c.phone,
            c.email,
            c.address,
            COUNT(o.id) AS order_count,
            COALESCE(SUM(o.total_amount), 0) AS total_spent,
            -- беремо останню знижку або середню, залежно від потреби
            COALESCE((SELECT discount_value FROM orders WHERE customer_id = c.id ORDER BY id DESC LIMIT 1), 0) AS last_discount,
            c.is_regular
        FROM 
            customers c
        LEFT JOIN 
            orders o ON c.id = o.customer_id
        GROUP BY 
            c.id

    """)
    clients = cur.fetchall()
    conn.close()
    return clients


# для постачальників

def get_all_suppliers():
    """ Отримати всіх постачальників з бази даних """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    conn.close()
    return suppliers

def add_supplier_to_db(name, contact_info):
    """ Додати постачальника в базу даних """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO suppliers (name, contact_info) VALUES (?, ?)", (name, contact_info))
    conn.commit()
    conn.close()

def update_supplier_in_db(supplier_id, name, contact_info):
    """ Оновити дані постачальника в базі даних """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE suppliers SET name = ?, contact_info = ? WHERE id = ?", (name, contact_info, supplier_id))
    conn.commit()
    conn.close()

def delete_supplier_from_db(supplier_id):
    """ Видалити постачальника з бази даних """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
    conn.commit()
    conn.close()

# замовлення

def get_customers():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM customers")
    return cur.fetchall()

def get_products():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, quantity FROM products")
    return cur.fetchall()


def add_order(customer_id, order_date, base_amount):
    conn = get_connection()
    cur = conn.cursor()

    # Отримуємо загальну кількість замовлень і суму попередніх замовлень клієнта
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM orders WHERE customer_id = ?", (customer_id,))
    order_count, total_spent = cur.fetchone()

    # Знижка залежно від суми попередніх замовлень
    if total_spent >= 100000:
        discount_percent = 7
    elif total_spent >= 55000:
        discount_percent = 3
    elif total_spent >= 25000:
        discount_percent = 1
    else:
        discount_percent = 0

    # Постійний клієнт (від 3-х замовлень) — +1.5% до знижки
    is_regular = 1 if order_count >= 3 else 0
    if is_regular:
        discount_percent += 1.5

    # Розрахунок остаточної суми зі знижкою
    total_amount = round(base_amount * (1 - discount_percent / 100), 2)

    # Створення нового замовлення
    cur.execute("""
        INSERT INTO orders (customer_id, order_date, status, total_amount, base_amount, discount_value)
        VALUES (?, ?, 'Очікує підтвердження', ?, ?, ?)
    """, (customer_id, order_date, total_amount, base_amount, discount_percent))
    conn.commit()

    order_id = cur.lastrowid

    # Назва замовлення
    order_title = f"order_{order_date}_{order_id}"
    cur.execute("UPDATE orders SET title = ? WHERE id = ?", (order_title, order_id))

    # Оновлення статусу постійного клієнта
    cur.execute("UPDATE customers SET is_regular = ? WHERE id = ?", (is_regular, customer_id))

    conn.commit()
    conn.close()

    return order_id


def add_order_item(order_id, product_id, quantity, unit_price):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)", (order_id, product_id, quantity, unit_price))
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT orders.id, customers.name, orders.order_date, orders.status
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
    """)
    return cur.fetchall()

def get_order_items_by_order_id(order_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT products.name, order_items.quantity, order_items.unit_price
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
    """, (order_id,))
    return cur.fetchall()


def update_product_quantity(self, product_id, quantity):
    conn = get_connection()  # Replace with your actual database connection function
    cur = conn.cursor()
    
    # Assuming you want to subtract the ordered quantity from the stock_quantity
    cur.execute("""
        UPDATE products
        SET stock_quantity = stock_quantity - ?
        WHERE id = ?
    """, (quantity, product_id))
    
    conn.commit()
    conn.close()



# оплати
def get_all_payments():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    SELECT payments.id, orders.id, payments.payment_date, payments.amount, payments.method
    FROM payments
    JOIN orders ON payments.order_id = orders.id
    """)
    return cur.fetchall()



def add_payment(order_id, payment_date, amount, method):
    conn = get_connection()
    cur = conn.cursor()

    # Додати платіж
    cur.execute("""
        INSERT INTO payments (order_id, payment_date, amount, method)
        VALUES (?, ?, ?, ?)
    """, (order_id, payment_date, amount, method))

    # Отримати загальну суму оплати за замовлення
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE order_id = ?", (order_id,))
    total_paid = cur.fetchone()[0]

    # Отримати повну суму до оплати за замовлення
    cur.execute("SELECT total_amount FROM orders WHERE id = ?", (order_id,))
    total_amount = cur.fetchone()[0]

    # Якщо сплачено повністю або більше — оновити статус
    if total_paid >= total_amount:
        cur.execute("UPDATE orders SET status = 'Оплачено' WHERE id = ?", (order_id,))

    conn.commit()
    conn.close()


def get_orders_for_payment():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id FROM orders")
    return cur.fetchall()

def get_all_orders_with_total_and_paid():
    conn = get_connection("appliance_store.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            o.id AS order_id,
            o.title,
            c.name AS client_name,
            o.order_date AS date,
            o.status,
            o.base_amount,
            o.discount_value,
            o.total_amount,
            IFNULL(SUM(p.amount), 0) AS paid
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        LEFT JOIN payments p ON o.id = p.order_id
        GROUP BY o.id
    """)
    orders = cur.fetchall()
    conn.close()
    return orders





