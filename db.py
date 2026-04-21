from psycopg import connect
import bcrypt
from config import DB_CONFIG


def get_connection():
    return connect(**DB_CONFIG)


# =========================
# SECURITY
# =========================
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


# =========================
# USERS
# =========================
def get_user_by_username(username: str):
    query = """
    SELECT id, username, password_hash, role
    FROM users
    WHERE username = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            return cur.fetchone()


def get_user_by_telegram_id(telegram_id: int):
    query = """
    SELECT id, telegram_id, role, full_name
    FROM users
    WHERE telegram_id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (telegram_id,))
            return cur.fetchone()


def create_visitor(telegram_id: int, full_name: str = None):
    query = """
    INSERT INTO users (telegram_id, role, full_name)
    VALUES (%s, 'visitor', %s)
    RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (telegram_id, full_name))
            visitor_id = cur.fetchone()[0]
        conn.commit()
        return visitor_id


def get_visitor_db_id_by_telegram_id(telegram_id: int):
    query = """
    SELECT id
    FROM users
    WHERE telegram_id = %s AND role = 'visitor'
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (telegram_id,))
            row = cur.fetchone()
            return row[0] if row else None


def save_staff_telegram_id(username: str, telegram_id: int):
    query = """
    UPDATE users
    SET telegram_id = %s
    WHERE username = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (telegram_id, username))
        conn.commit()


def get_all_employee_telegram_ids():
    query = """
    SELECT telegram_id
    FROM users
    WHERE role = 'employee' AND telegram_id IS NOT NULL
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [row[0] for row in rows]


def get_full_name_by_visitor_id(visitor_id: int):
    query = """
    SELECT full_name
    FROM users
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (visitor_id,))
            row = cur.fetchone()
            return row[0] if row else None


def create_employee(username: str, password: str):
    password_hash = hash_password(password)

    query = """
    INSERT INTO users (username, password_hash, role)
    VALUES (%s, %s, 'employee')
    RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username, password_hash))
            employee_id = cur.fetchone()[0]
        conn.commit()
        return employee_id


# =========================
# CATEGORIES
# =========================
def get_all_categories():
    query = """
    SELECT id, name
    FROM categories
    ORDER BY id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


def get_category_by_id(category_id: int):
    query = """
    SELECT id, name
    FROM categories
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (category_id,))
            return cur.fetchone()


def create_category(name: str):
    query = """
    INSERT INTO categories (name)
    VALUES (%s)
    RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name,))
            category_id = cur.fetchone()[0]
        conn.commit()
        return category_id


def update_category(category_id: int, new_name: str):
    query = """
    UPDATE categories
    SET name = %s
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (new_name, category_id))
        conn.commit()


def delete_category(category_id: int):
    query = """
    DELETE FROM categories
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (category_id,))
        conn.commit()

# =========================
# PRODUCTS
# =========================
def get_products_by_category(category_id: int):
    query = """
    SELECT id, name, price
    FROM products
    WHERE category_id = %s
    ORDER BY id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (category_id,))
            return cur.fetchall()


def get_product_by_id(product_id: int):
    query = """
    SELECT id, category_id, name, description, price, image_file_id
    FROM products
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (product_id,))
            return cur.fetchone()


def get_all_products():
    query = """
    SELECT id, name, price
    FROM products
    ORDER BY id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


def create_product(category_id: int, name: str, description: str, price, image_file_id: str | None):
    query = """
    INSERT INTO products (category_id, name, description, price, image_file_id)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (category_id, name, description, price, image_file_id))
            product_id = cur.fetchone()[0]
        conn.commit()
        return product_id


def update_product(product_id: int, category_id: int, name: str, description: str, price, image_file_id: str | None):
    query = """
    UPDATE products
    SET category_id = %s,
        name = %s,
        description = %s,
        price = %s,
        image_file_id = %s
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (category_id, name, description, price, image_file_id, product_id))
        conn.commit()


def delete_product(product_id: int):
    query = """
    DELETE FROM products
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (product_id,))
        conn.commit()


# =========================
# CARTS
# =========================
def get_or_create_cart(user_id: int):
    select_query = """
    SELECT id
    FROM carts
    WHERE user_id = %s
    """
    insert_query = """
    INSERT INTO carts (user_id)
    VALUES (%s)
    RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(select_query, (user_id,))
            row = cur.fetchone()

            if row:
                return row[0]

            cur.execute(insert_query, (user_id,))
            cart_id = cur.fetchone()[0]
        conn.commit()
        return cart_id


def add_product_to_cart(user_id: int, product_id: int):
    cart_id = get_or_create_cart(user_id)

    select_query = """
    SELECT id, quantity
    FROM cart_items
    WHERE cart_id = %s AND product_id = %s
    """
    update_query = """
    UPDATE cart_items
    SET quantity = quantity + 1
    WHERE cart_id = %s AND product_id = %s
    """
    insert_query = """
    INSERT INTO cart_items (cart_id, product_id, quantity)
    VALUES (%s, %s, 1)
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(select_query, (cart_id, product_id))
            row = cur.fetchone()

            if row:
                cur.execute(update_query, (cart_id, product_id))
            else:
                cur.execute(insert_query, (cart_id, product_id))
        conn.commit()


def get_cart_items(user_id: int):
    query = """
    SELECT
        ci.product_id,
        p.name,
        p.price,
        ci.quantity,
        (p.price * ci.quantity) AS total_price
    FROM carts c
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.user_id = %s
    ORDER BY ci.id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            return cur.fetchall()


def remove_product_from_cart(user_id: int, product_id: int):
    query = """
    DELETE FROM cart_items
    WHERE cart_id = (
        SELECT id FROM carts WHERE user_id = %s
    )
    AND product_id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id, product_id))
        conn.commit()


def clear_cart(user_id: int):
    query = """
    DELETE FROM cart_items
    WHERE cart_id = (
        SELECT id FROM carts WHERE user_id = %s
    )
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
        conn.commit()


def get_cart_total(user_id: int):
    query = """
    SELECT COALESCE(SUM(p.price * ci.quantity), 0)
    FROM carts c
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.user_id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            row = cur.fetchone()
            return row[0] if row else 0


# =========================
# ORDERS
# =========================
def create_order_from_cart(visitor_id: int):
    cart_items_query = """
    SELECT
        p.id,
        p.name,
        p.price,
        ci.quantity
    FROM carts c
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    WHERE c.user_id = %s
    ORDER BY ci.id
    """

    create_order_query = """
    INSERT INTO orders (visitor_id, status)
    VALUES (%s, 'Принят')
    RETURNING id
    """

    create_order_item_query = """
    INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity)
    VALUES (%s, %s, %s, %s, %s)
    """

    clear_cart_query = """
    DELETE FROM cart_items
    WHERE cart_id = (
        SELECT id FROM carts WHERE user_id = %s
    )
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(cart_items_query, (visitor_id,))
            items = cur.fetchall()

            if not items:
                return None

            cur.execute(create_order_query, (visitor_id,))
            order_id = cur.fetchone()[0]

            for product_id, product_name, product_price, quantity in items:
                cur.execute(
                    create_order_item_query,
                    (order_id, product_id, product_name, product_price, quantity)
                )

            cur.execute(clear_cart_query, (visitor_id,))
        conn.commit()

    return order_id


def get_order_items(order_id: int):
    query = """
    SELECT product_name, product_price, quantity
    FROM order_items
    WHERE order_id = %s
    ORDER BY id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (order_id,))
            return cur.fetchall()


def get_order_by_id(order_id: int):
    query = """
    SELECT id, visitor_id, status, created_at
    FROM orders
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (order_id,))
            return cur.fetchone()


def get_orders_by_visitor(visitor_id: int):
    query = """
    SELECT id, status, created_at
    FROM orders
    WHERE visitor_id = %s
    ORDER BY id DESC
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (visitor_id,))
            return cur.fetchall()


def get_all_orders():
    query = """
    SELECT id, visitor_id, status, created_at
    FROM orders
    ORDER BY id DESC
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


def update_order_status(order_id: int, new_status: str):
    query = """
    UPDATE orders
    SET status = %s
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (new_status, order_id))
        conn.commit()


# =========================
# PROMOTIONS
# =========================
def get_all_promotions():
    query = """
    SELECT id, title, description
    FROM promotions
    ORDER BY id DESC
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


def create_promotion(title: str, description: str):
    query = """
    INSERT INTO promotions (title, description)
    VALUES (%s, %s)
    RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (title, description))
            promotion_id = cur.fetchone()[0]
        conn.commit()
        return promotion_id


def delete_promotion(promotion_id: int):
    query = """
    DELETE FROM promotions
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (promotion_id,))
        conn.commit()


# =========================
# ABOUT
# =========================
def get_about_text():
    query = """
    SELECT content
    FROM about_info
    ORDER BY id ASC
    LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
            return row[0] if row else "Информация пока не заполнена."


def update_about_text(new_text: str):
    select_query = """
    SELECT id
    FROM about_info
    ORDER BY id ASC
    LIMIT 1
    """

    update_query = """
    UPDATE about_info
    SET content = %s
    WHERE id = %s
    """

    insert_query = """
    INSERT INTO about_info (content)
    VALUES (%s)
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(select_query)
            row = cur.fetchone()

            if row:
                about_id = row[0]
                cur.execute(update_query, (new_text, about_id))
            else:
                cur.execute(insert_query, (new_text,))
        conn.commit()


#СБРОС ВСЕГО И ВСЯ(DANGER)

def reset_business_data():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Очищаем всех посетителей и сотрудников, оставляем только владельца
            cur.execute("DELETE FROM users WHERE role IN ('employee', 'visitor')")

            # Очищаем каталог
            cur.execute("DELETE FROM categories")

            # Очищаем акции
            cur.execute("DELETE FROM promotions")

            # Очищаем заказы и корзины
            cur.execute("DELETE FROM orders")
            cur.execute("DELETE FROM carts")

            # Сброс текста "О нас" к стандартному
            cur.execute("SELECT id FROM about_info ORDER BY id ASC LIMIT 1")
            row = cur.fetchone()

            if row:
                cur.execute(
                    "UPDATE about_info SET content = %s WHERE id = %s",
                    ("Информация пока не заполнена.", row[0])
                )
            else:
                cur.execute(
                    "INSERT INTO about_info (content) VALUES (%s)",
                    ("Информация пока не заполнена.",)
                )

        conn.commit()