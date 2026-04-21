import telebot
from telebot import types
from telebot.types import BotCommand

from config import TOKEN
from db import (
    get_user_by_username,
    verify_password,
    get_user_by_telegram_id,
    create_visitor,
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
    get_products_by_category,
    get_product_by_id,
    get_all_products,
    create_product,
    update_product,
    delete_product,
    get_visitor_db_id_by_telegram_id,
    add_product_to_cart,
    get_cart_items,
    remove_product_from_cart,
    clear_cart,
    get_cart_total,
    create_order_from_cart,
    get_order_items,
    get_order_by_id,
    get_orders_by_visitor,
    get_all_orders,
    update_order_status,
    save_staff_telegram_id,
    get_all_employee_telegram_ids,
    get_full_name_by_visitor_id,
    create_employee,
    get_all_promotions,
    create_promotion,
    delete_promotion,
    get_about_text,
    update_about_text,
    get_connection,
    reset_business_data,
)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

auth_data = {}
user_sessions = {}
owner_state = {}


bot.set_my_commands([
    BotCommand("start", "Запустить бота"),
    BotCommand("menu", "Открыть меню"),
    BotCommand("profile", "Открыть профиль"),
    BotCommand("cart", "Открыть корзину"),
    BotCommand("orders", "Открыть заказы"),
    BotCommand("help", "Помощь")
])


# =========================
# КЛАВИАТУРЫ
# =========================
def get_role_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("👑 Владелец", "👨‍💼 Сотрудник", "🙋 Посетитель")
    return keyboard


def get_visitor_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("👤 Профиль", "📂 Каталог")
    keyboard.row("🛒 Корзина", "📦 Мои заказы")
    keyboard.row("🎁 Акции", "ℹ️ О нас")
    return keyboard


def get_employee_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("👤 Профиль", "📋 Заказы")
    keyboard.row("🔄 Сменить роль")
    return keyboard


def get_owner_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("👤 Профиль", "📋 Заказы")
    keyboard.row("🛠 Каталог", "👥 Сотрудники")
    keyboard.row("📰 Контент", "🧹 Сброс данных")
    keyboard.row("🔄 Сменить роль")
    return keyboard


def get_owner_catalog_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("➕ Добавить категорию", "✏️ Изменить категорию")
    keyboard.row("🗑 Удалить категорию", "➕ Добавить товар")
    keyboard.row("✏️ Изменить товар", "🗑 Удалить товар")
    keyboard.row("⬅️ Назад")
    return keyboard


def get_owner_staff_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("➕ Создать сотрудника")
    keyboard.row("⬅️ Назад")
    return keyboard


def get_owner_content_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("➕ Добавить акцию", "🗑 Удалить акцию")
    keyboard.row("✏️ Изменить О нас")
    keyboard.row("⬅️ Назад")
    return keyboard


def get_reset_confirm_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("✅ Подтвердить сброс", "❌ Отмена")
    return keyboard


def get_categories_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    categories = get_all_categories()

    for category_id, category_name in categories:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"📂 {category_name}",
                callback_data=f"category_{category_id}"
            )
        )

    return keyboard


def get_products_inline_keyboard(category_id: int):
    keyboard = types.InlineKeyboardMarkup()
    products = get_products_by_category(category_id)

    for product_id, product_name, price in products:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{product_name} — {price} ₽",
                callback_data=f"product_{product_id}"
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            text="⬅️ Назад к категориям",
            callback_data="back_to_categories"
        )
    )

    return keyboard


def get_product_card_keyboard(product_id: int, category_id: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="🛒 Добавить в корзину",
            callback_data=f"add_to_cart_{product_id}"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            text="⬅️ Назад к товарам",
            callback_data=f"back_to_products_{category_id}"
        )
    )
    return keyboard


def get_cart_inline_keyboard(items):
    keyboard = types.InlineKeyboardMarkup()

    for product_id, name, price, quantity, total_price in items:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"❌ Удалить: {name}",
                callback_data=f"remove_from_cart_{product_id}"
            )
        )

    if items:
        keyboard.add(
            types.InlineKeyboardButton(
                text="🗑 Очистить корзину",
                callback_data="clear_cart"
            )
        )
        keyboard.add(
            types.InlineKeyboardButton(
                text="📦 Оформить заказ",
                callback_data="checkout_order"
            )
        )

    return keyboard


def get_employee_orders_keyboard(orders):
    keyboard = types.InlineKeyboardMarkup()

    for order_id, visitor_id, status, created_at in orders:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"📦 Заказ #{order_id} — {status}",
                callback_data=f"employee_order_{order_id}"
            )
        )

    return keyboard


def get_order_status_keyboard(order_id: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="✅ Принят",
            callback_data=f"set_status_{order_id}_Принят"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            text="🛠 В работе",
            callback_data=f"set_status_{order_id}_В_работе"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            text="🎉 Готов",
            callback_data=f"set_status_{order_id}_Готов"
        )
    )
    return keyboard


def get_owner_categories_inline_keyboard(prefix: str):
    keyboard = types.InlineKeyboardMarkup()
    categories = get_all_categories()

    for category_id, category_name in categories:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"📂 {category_name}",
                callback_data=f"{prefix}_{category_id}"
            )
        )

    return keyboard


def get_owner_products_inline_keyboard(prefix: str):
    keyboard = types.InlineKeyboardMarkup()
    products = get_all_products()

    for product_id, name, price in products:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{name} — {price} ₽",
                callback_data=f"{prefix}_{product_id}"
            )
        )

    return keyboard


# =========================
# ФУНКЦИИ
# =========================
def is_visitor(user_id: int) -> bool:
    session = user_sessions.get(user_id)
    return bool(session and session.get("role") == "visitor")


def is_owner(user_id: int) -> bool:
    session = user_sessions.get(user_id)
    return bool(session and session.get("role") == "owner")


def is_staff(user_id: int) -> bool:
    session = user_sessions.get(user_id)
    return bool(session and session.get("role") in ["employee", "owner"])


def get_current_visitor_db_id(telegram_id: int):
    return get_visitor_db_id_by_telegram_id(telegram_id)


def render_cart_text(items, total_sum):
    if not items:
        return "🛒 <b>Ваша корзина пуста</b>"

    lines = ["<b>🛒 Ваша корзина</b>\n"]

    for index, (product_id, name, price, quantity, total_price) in enumerate(items, start=1):
        lines.append(
            f"<b>{index}. {name}</b>\n"
            f"💰 Цена: {price} ₽\n"
            f"🔢 Количество: {quantity}\n"
            f"🧾 Сумма: {total_price} ₽\n"
        )

    lines.append(f"<b>Итого: {total_sum} ₽</b>")
    return "\n".join(lines)


def show_cart(chat_id: int, telegram_id: int):
    visitor_db_id = get_current_visitor_db_id(telegram_id)

    if not visitor_db_id:
        bot.send_message(chat_id, "⚠️ Профиль посетителя не найден. Нажмите /start")
        return

    items = get_cart_items(visitor_db_id)
    total_sum = get_cart_total(visitor_db_id)

    bot.send_message(
        chat_id,
        render_cart_text(items, total_sum),
        reply_markup=get_cart_inline_keyboard(items)
    )


def render_order_text(order_id: int):
    order = get_order_by_id(order_id)

    if not order:
        return "⚠️ Заказ не найден."

    db_order_id, visitor_id, status, created_at = order
    visitor_name = get_full_name_by_visitor_id(visitor_id) or "Посетитель"
    items = get_order_items(order_id)

    lines = [
        f"<b>📦 Заказ #{db_order_id}</b>",
        f"👤 Посетитель: {visitor_name}",
        f"📌 Статус: <b>{status}</b>",
        "",
        "<b>Состав заказа:</b>"
    ]

    total_sum = 0

    for name, price, quantity in items:
        item_sum = price * quantity
        total_sum += item_sum
        lines.append(f"• {name} | {price} ₽ × {quantity} = {item_sum} ₽")

    lines.append("")
    lines.append(f"<b>Итого: {total_sum} ₽</b>")

    return "\n".join(lines)


def notify_employees_about_new_order(order_id: int):
    employee_ids = get_all_employee_telegram_ids()
    text = render_order_text(order_id)

    for employee_telegram_id in employee_ids:
        try:
            bot.send_message(
                employee_telegram_id,
                f"🔔 <b>Поступил новый заказ</b>\n\n{text}",
                reply_markup=get_order_status_keyboard(order_id)
            )
        except Exception:
            pass


def notify_visitor_about_status_change(order_id: int, new_status: str):
    order = get_order_by_id(order_id)

    if not order:
        return

    _, visitor_id, _, _ = order

    query = """
    SELECT telegram_id
    FROM users
    WHERE id = %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (visitor_id,))
            row = cur.fetchone()

    if row and row[0]:
        try:
            bot.send_message(
                row[0],
                f"📦 Статус вашего заказа <b>#{order_id}</b> изменён: <b>{new_status}</b>"
            )
        except Exception:
            pass


def show_main_menu_by_session(chat_id: int, user_id: int):
    session = user_sessions.get(user_id)

    if not session:
        bot.send_message(chat_id, "Нажмите /start")
        return

    role = session.get("role")

    if role == "visitor":
        bot.send_message(
            chat_id,
            "🏠 <b>Главное меню посетителя</b>\nВыберите нужный раздел:",
            reply_markup=get_visitor_main_menu()
        )
    elif role == "employee":
        bot.send_message(
            chat_id,
            "👨‍💼 <b>Меню сотрудника</b>\nВыберите нужный раздел:",
            reply_markup=get_employee_menu()
        )
    elif role == "owner":
        bot.send_message(
            chat_id,
            "👑 <b>Меню владельца</b>\nВыберите нужный раздел:",
            reply_markup=get_owner_menu()
        )


# =========================
# СТАРТ И АВТОРИЗАЦИЯ
# =========================
@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = get_role_keyboard()

    with open("start.jpg", "rb") as photo:
        bot.send_photo(
            message.chat.id,
            photo,
            caption=(
                "<b>Добро пожаловать! 👋</b>\n\n"
                "Я — персональный бот этого заведения.\n"
                "Здесь вы можете посмотреть каталог, собрать корзину, оформить заказ "
                "и узнать актуальную информацию.\n\n"
                "<b>Выберите вашу роль:</b>"
            ),
            reply_markup=keyboard
        )


@bot.message_handler(func=lambda message: message.text in ["👑 Владелец", "👨‍💼 Сотрудник", "🙋 Посетитель"])
def role_handler(message):
    user_id = message.from_user.id
    role_text = message.text

    if role_text == "🙋 Посетитель":
        handle_visitor_login(message)
        return

    auth_data[user_id] = {}

    msg = bot.send_message(message.chat.id, "🔐 Введите логин:")
    bot.register_next_step_handler(msg, process_login_step)


def handle_visitor_login(message):
    telegram_id = message.from_user.id

    full_name_parts = [
        message.from_user.first_name or "",
        message.from_user.last_name or ""
    ]
    full_name = " ".join(part for part in full_name_parts if part).strip()

    user = get_user_by_telegram_id(telegram_id)

    if not user:
        create_visitor(telegram_id, full_name if full_name else None)

    user_sessions[telegram_id] = {
        "role": "visitor",
        "username": None,
        "full_name": full_name if full_name else "Посетитель"
    }

    bot.send_message(
        message.chat.id,
        "🙌 <b>Добро пожаловать в главное меню!</b>\nВыберите нужный раздел ниже:",
        reply_markup=get_visitor_main_menu()
    )


def process_login_step(message):
    user_id = message.from_user.id

    if user_id not in auth_data:
        bot.send_message(message.chat.id, "⚠️ Сессия входа сброшена. Нажмите /start")
        return

    auth_data[user_id]["username"] = message.text.strip()

    msg = bot.send_message(message.chat.id, "🔑 Введите пароль:")
    bot.register_next_step_handler(msg, process_password_step)


def process_password_step(message):
    user_id = message.from_user.id

    if user_id not in auth_data:
        bot.send_message(message.chat.id, "⚠️ Сессия входа сброшена. Нажмите /start")
        return

    username = auth_data[user_id]["username"]
    password = message.text.strip()

    user = get_user_by_username(username)

    if not user:
        bot.send_message(message.chat.id, "❌ Неверный логин или пароль.")
        auth_data.pop(user_id, None)
        return

    _, db_username, db_password_hash, db_role = user

    if not verify_password(password, db_password_hash):
        bot.send_message(message.chat.id, "❌ Неверный логин или пароль.")
        auth_data.pop(user_id, None)
        return

    if db_role == "employee":
        save_staff_telegram_id(db_username, user_id)

    user_sessions[user_id] = {
        "role": db_role,
        "username": db_username
    }

    if db_role == "owner":
        bot.send_message(
            message.chat.id,
            "👑 <b>Успешный вход</b>\nВы вошли как <b>Владелец</b>.",
            reply_markup=get_owner_menu()
        )
    elif db_role == "employee":
        bot.send_message(
            message.chat.id,
            "👨‍💼 <b>Успешный вход</b>\nВы вошли как <b>Сотрудник</b>.",
            reply_markup=get_employee_menu()
        )
    else:
        bot.send_message(message.chat.id, "⚠️ Ошибка роли.")

    auth_data.pop(user_id, None)


# =========================
# ПРОФИЛИ
# =========================
@bot.message_handler(func=lambda message: message.text == "👤 Профиль")
def universal_profile_handler(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        bot.send_message(message.chat.id, "⚠️ Сначала войдите. Нажмите /start")
        return

    role = session.get("role")

    if role == "visitor":
        full_name = session.get("full_name", "Посетитель")
        visitor_db_id = get_current_visitor_db_id(user_id)
        orders_count = len(get_orders_by_visitor(visitor_db_id)) if visitor_db_id else 0

        bot.send_message(
            message.chat.id,
            f"<b>👤 Ваш профиль</b>\n\n"
            f"🧾 Имя: {full_name}\n"
            f"🎭 Роль: Посетитель\n"
            f"🆔 Telegram ID: {user_id}\n"
            f"📦 Заказов: {orders_count}"
        )
        return

    username = session.get("username")
    role_name = "Владелец" if role == "owner" else "Сотрудник"

    if role == "owner":
        products_count = len(get_all_products())
        orders_count = len(get_all_orders())
        employees_count = len(get_all_employee_telegram_ids())
        bot.send_message(
            message.chat.id,
            f"<b>👑 Профиль владельца</b>\n\n"
            f"🔐 Логин: {username}\n"
            f"🎭 Роль: {role_name}\n"
            f"📦 Всего заказов: {orders_count}\n"
            f"🛍 Товаров в каталоге: {products_count}\n"
            f"👥 Активных сотрудников в Telegram: {employees_count}"
        )
    else:
        orders_count = len(get_all_orders())
        bot.send_message(
            message.chat.id,
            f"<b>👨‍💼 Профиль сотрудника</b>\n\n"
            f"🔐 Логин: {username}\n"
            f"🎭 Роль: {role_name}\n"
            f"📋 Доступных заказов: {orders_count}"
        )


# =========================
# МЕНЮ ПОСЕТИТЕЛЯ
# =========================
@bot.message_handler(func=lambda message: message.text == "📂 Каталог")
def catalog_handler(message):
    categories = get_all_categories()

    if not categories:
        bot.send_message(message.chat.id, "📂 Каталог пока пуст.")
        return

    bot.send_message(
        message.chat.id,
        "<b>📂 Каталог товаров</b>\n\nВыберите категорию:",
        reply_markup=get_categories_inline_keyboard()
    )


@bot.message_handler(func=lambda message: message.text == "🛒 Корзина")
def cart_handler(message):
    user_id = message.from_user.id
    show_cart(message.chat.id, user_id)


@bot.message_handler(func=lambda message: message.text == "📦 Мои заказы")
def my_orders_handler(message):
    user_id = message.from_user.id

    visitor_db_id = get_current_visitor_db_id(user_id)

    if not visitor_db_id:
        bot.send_message(message.chat.id, "⚠️ Профиль посетителя не найден.")
        return

    orders = get_orders_by_visitor(visitor_db_id)

    if not orders:
        bot.send_message(message.chat.id, "📦 У вас пока нет заказов.")
        return

    lines = ["<b>📦 Ваши заказы</b>\n"]

    for order_id, status, created_at in orders:
        lines.append(f"• Заказ <b>#{order_id}</b> — {status}")

    bot.send_message(message.chat.id, "\n".join(lines))


@bot.message_handler(func=lambda message: message.text == "🎁 Акции")
def offers_handler(message):
    promotions = get_all_promotions()

    if not promotions:
        bot.send_message(message.chat.id, "🎁 Сейчас активных акций нет.")
        return

    lines = ["<b>🎁 Наши акции</b>\n"]

    for _, title, description in promotions:
        lines.append(f"<b>{title}</b>\n{description}\n")

    bot.send_message(message.chat.id, "\n".join(lines))


@bot.message_handler(func=lambda message: message.text == "ℹ️ О нас")
def about_handler(message):
    about_text = get_about_text()
    bot.send_message(message.chat.id, f"<b>ℹ️ О нас</b>\n\n{about_text}")


# =========================
# МЕНЮ ВЛАДЕЛЬЦА
# =========================
@bot.message_handler(func=lambda message: message.text == "📋 Заказы")
def staff_orders_handler(message):
    orders = get_all_orders()

    if not orders:
        bot.send_message(message.chat.id, "📋 Заказов пока нет.")
        return

    bot.send_message(
        message.chat.id,
        "<b>📋 Список заказов</b>\nВыберите заказ:",
        reply_markup=get_employee_orders_keyboard(orders)
    )


@bot.message_handler(func=lambda message: message.text == "🛠 Каталог")
def owner_catalog_menu_handler(message):
    bot.send_message(
        message.chat.id,
        "<b>🛠 Управление каталогом</b>",
        reply_markup=get_owner_catalog_menu()
    )


@bot.message_handler(func=lambda message: message.text == "👥 Сотрудники")
def owner_staff_menu_handler(message):
    bot.send_message(
        message.chat.id,
        "<b>👥 Управление сотрудниками</b>",
        reply_markup=get_owner_staff_menu()
    )


@bot.message_handler(func=lambda message: message.text == "📰 Контент")
def owner_content_menu_handler(message):
    bot.send_message(
        message.chat.id,
        "<b>📰 Управление контентом</b>",
        reply_markup=get_owner_content_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🧹 Сброс данных")
def reset_data_handler(message):
    bot.send_message(
        message.chat.id,
        "<b>⚠️ Внимание!</b>\n\n"
        "Будут удалены:\n"
        "• все посетители\n"
        "• все сотрудники\n"
        "• весь каталог\n"
        "• все корзины\n"
        "• все заказы\n"
        "• все акции\n\n"
        "Владелец останется.\n"
        "Продолжить?",
        reply_markup=get_reset_confirm_keyboard()
    )


@bot.message_handler(func=lambda message: message.text == "✅ Подтвердить сброс")
def confirm_reset_handler(message):
    try:
        reset_business_data()
        auth_data.clear()
        owner_state.clear()

        
        current = user_sessions.get(message.from_user.id)
        user_sessions.clear()
        if current and current.get("role") == "owner":
            user_sessions[message.from_user.id] = current

        bot.send_message(
            message.chat.id,
            "✅ Данные успешно очищены.\n\nБот готов к новой работе.",
            reply_markup=get_owner_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка при сбросе данных:\n{e}",
            reply_markup=get_owner_menu()
        )


@bot.message_handler(func=lambda message: message.text == "❌ Отмена")
def cancel_reset_handler(message):
    bot.send_message(
        message.chat.id,
        "Сброс отменён.",
        reply_markup=get_owner_menu()
    )


@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def back_to_owner_menu_handler(message):
    owner_state.pop(message.from_user.id, None)

    bot.send_message(
        message.chat.id,
        "<b>👑 Главное меню владельца</b>",
        reply_markup=get_owner_menu()
    )


# =========================
# КАТЕГОРИИ
# =========================
@bot.message_handler(func=lambda message: message.text == "➕ Добавить категорию")
def add_category_handler(message):
    msg = bot.send_message(message.chat.id, "📂 Введите название новой категории:")
    bot.register_next_step_handler(msg, process_add_category)


def process_add_category(message):
    category_name = message.text.strip()

    try:
        create_category(category_name)
        bot.send_message(
            message.chat.id,
            f"✅ Категория <b>{category_name}</b> успешно добавлена.",
            reply_markup=get_owner_catalog_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Не удалось добавить категорию.\n\n{e}",
            reply_markup=get_owner_catalog_menu()
        )


@bot.message_handler(func=lambda message: message.text == "✏️ Изменить категорию")
def edit_category_handler(message):
    categories = get_all_categories()
    if not categories:
        bot.send_message(message.chat.id, "📂 Категорий пока нет.")
        return

    bot.send_message(
        message.chat.id,
        "<b>✏️ Выберите категорию для изменения</b>",
        reply_markup=get_owner_categories_inline_keyboard("owner_edit_category")
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("owner_edit_category_"))
def owner_edit_category_callback(call):
    category_id = int(call.data.split("_")[-1])

    owner_state[call.from_user.id] = {
        "category_id": category_id
    }

    bot.send_message(call.message.chat.id, "✏️ Введите новое название категории:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_edit_category_name)

    bot.answer_callback_query(call.id)


def process_edit_category_name(message):
    data = owner_state.get(message.from_user.id, {})
    category_id = data.get("category_id")
    new_name = message.text.strip()

    try:
        update_category(category_id, new_name)
        bot.send_message(
            message.chat.id,
            f"✅ Категория успешно изменена.\nНовое название: <b>{new_name}</b>",
            reply_markup=get_owner_catalog_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Не удалось изменить категорию.\n\n{e}",
            reply_markup=get_owner_catalog_menu()
        )

    owner_state.pop(message.from_user.id, None)


@bot.message_handler(func=lambda message: message.text == "🗑 Удалить категорию")
def delete_category_handler(message):
    categories = get_all_categories()

    if not categories:
        bot.send_message(message.chat.id, "📂 Категорий пока нет.")
        return

    bot.send_message(
        message.chat.id,
        "<b>🗑 Выберите категорию для удаления</b>",
        reply_markup=get_owner_categories_inline_keyboard("owner_delete_category")
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("owner_delete_category_"))
def owner_delete_category_callback(call):
    category_id = int(call.data.split("_")[-1])

    try:
        delete_category(category_id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✅ Категория удалена.\nВсе товары этой категории также удалены."
        )
        bot.send_message(
            call.message.chat.id,
            "<b>🛠 Меню управления каталогом</b>",
            reply_markup=get_owner_catalog_menu()
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка удаления:\n{e}")

    bot.answer_callback_query(call.id)


# =========================
# УПРАВЛЕНИЕ СОТРУДНИКАМИ
# =========================
@bot.message_handler(func=lambda message: message.text == "➕ Создать сотрудника")
def create_employee_handler(message):
    owner_state[message.from_user.id] = {}
    msg = bot.send_message(message.chat.id, "👤 Введите логин нового сотрудника:")
    bot.register_next_step_handler(msg, process_employee_username)


def process_employee_username(message):
    owner_state[message.from_user.id]["employee_username"] = message.text.strip()

    msg = bot.send_message(message.chat.id, "🔐 Введите пароль нового сотрудника:")
    bot.register_next_step_handler(msg, process_employee_password)


def process_employee_password(message):
    username = owner_state.get(message.from_user.id, {}).get("employee_username")
    password = message.text.strip()

    try:
        create_employee(username, password)
        bot.send_message(
            message.chat.id,
            f"✅ Сотрудник <b>{username}</b> успешно создан.",
            reply_markup=get_owner_staff_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Не удалось создать сотрудника.\n\n{e}",
            reply_markup=get_owner_staff_menu()
        )

    owner_state.pop(message.from_user.id, None)


# =========================
# ТОВАРЫ
# =========================
@bot.message_handler(func=lambda message: message.text == "➕ Добавить товар")
def add_product_handler(message):
    categories = get_all_categories()
    if not categories:
        bot.send_message(message.chat.id, "⚠️ Сначала добавьте хотя бы одну категорию.")
        return

    owner_state[message.from_user.id] = {}

    bot.send_message(
        message.chat.id,
        "<b>➕ Выберите категорию для нового товара</b>",
        reply_markup=get_owner_categories_inline_keyboard("owner_add_product_category")
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("owner_add_product_category_"))
def owner_add_product_category_callback(call):
    category_id = int(call.data.split("_")[-1])
    owner_state[call.from_user.id]["category_id"] = category_id

    bot.send_message(call.message.chat.id, "📝 Введите название товара:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_new_product_name)

    bot.answer_callback_query(call.id)


def process_new_product_name(message):
    owner_state[message.from_user.id]["name"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "📄 Введите описание товара:")
    bot.register_next_step_handler(msg, process_new_product_description)


def process_new_product_description(message):
    owner_state[message.from_user.id]["description"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "💰 Введите цену товара:")
    bot.register_next_step_handler(msg, process_new_product_price)


def process_new_product_price(message):
    try:
        owner_state[message.from_user.id]["price"] = float(message.text.strip().replace(",", "."))
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Цена должна быть числом.")
        return

    msg = bot.send_message(
        message.chat.id,
        "🖼 Теперь отправьте фото товара.\nЕсли фото не нужно — отправьте символ: -"
    )
    bot.register_next_step_handler(msg, process_new_product_image)


def process_new_product_image(message):
    data = owner_state.get(message.from_user.id, {})

    image_file_id = None

    if message.content_type == "photo":
        image_file_id = message.photo[-1].file_id
    elif message.text and message.text.strip() == "-":
        image_file_id = None
    else:
        bot.send_message(message.chat.id, "⚠️ Отправьте фото товара или символ '-'")
        return

    try:
        product_id = create_product(
            category_id=data["category_id"],
            name=data["name"],
            description=data["description"],
            price=data["price"],
            image_file_id=image_file_id
        )
        bot.send_message(
            message.chat.id,
            f"✅ Товар успешно добавлен.\nID товара: <b>{product_id}</b>",
            reply_markup=get_owner_catalog_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Не удалось добавить товар.\n\n{e}",
            reply_markup=get_owner_catalog_menu()
        )

    owner_state.pop(message.from_user.id, None)


@bot.message_handler(func=lambda message: message.text == "✏️ Изменить товар")
def edit_product_handler(message):
    products = get_all_products()
    if not products:
        bot.send_message(message.chat.id, "🛍 Товаров пока нет.")
        return

    bot.send_message(
        message.chat.id,
        "<b>✏️ Выберите товар для изменения</b>",
        reply_markup=get_owner_products_inline_keyboard("owner_edit_product")
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("owner_edit_product_"))
def owner_edit_product_callback(call):
    product_id = int(call.data.split("_")[-1])
    product = get_product_by_id(product_id)

    if not product:
        bot.answer_callback_query(call.id, "Товар не найден.")
        return

    owner_state[call.from_user.id] = {
        "product_id": product_id
    }

    bot.send_message(
        call.message.chat.id,
        "<b>📂 Выберите новую категорию товара</b>",
        reply_markup=get_owner_categories_inline_keyboard("owner_edit_product_category")
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("owner_edit_product_category_"))
def owner_edit_product_category_callback(call):
    category_id = int(call.data.split("_")[-1])
    owner_state[call.from_user.id]["category_id"] = category_id

    bot.send_message(call.message.chat.id, "📝 Введите новое название товара:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_edit_product_name)

    bot.answer_callback_query(call.id)


def process_edit_product_name(message):
    owner_state[message.from_user.id]["name"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "📄 Введите новое описание товара:")
    bot.register_next_step_handler(msg, process_edit_product_description)


def process_edit_product_description(message):
    owner_state[message.from_user.id]["description"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "💰 Введите новую цену товара:")
    bot.register_next_step_handler(msg, process_edit_product_price)


def process_edit_product_price(message):
    try:
        owner_state[message.from_user.id]["price"] = float(message.text.strip().replace(",", "."))
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Цена должна быть числом.")
        return

    msg = bot.send_message(
        message.chat.id,
        "🖼 Отправьте новое фото товара, новый image_file_id или '-' если без картинки:"
    )
    bot.register_next_step_handler(msg, process_edit_product_image)


def process_edit_product_image(message):
    data = owner_state.get(message.from_user.id, {})
    image_file_id = None

    if message.content_type == "photo":
        image_file_id = message.photo[-1].file_id
    elif message.text and message.text.strip() == "-":
        image_file_id = None
    else:
        image_file_id = message.text.strip()

    try:
        update_product(
            product_id=data["product_id"],
            category_id=data["category_id"],
            name=data["name"],
            description=data["description"],
            price=data["price"],
            image_file_id=image_file_id
        )
        bot.send_message(
            message.chat.id,
            "✅ Товар успешно изменён.",
            reply_markup=get_owner_catalog_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Не удалось изменить товар.\n\n{e}",
            reply_markup=get_owner_catalog_menu()
        )

    owner_state.pop(message.from_user.id, None)


@bot.message_handler(func=lambda message: message.text == "🗑 Удалить товар")
def delete_product_handler(message):
    products = get_all_products()
    if not products:
        bot.send_message(message.chat.id, "🛍 Товаров пока нет.")
        return

    bot.send_message(
        message.chat.id,
        "<b>🗑 Выберите товар для удаления</b>",
        reply_markup=get_owner_products_inline_keyboard("owner_delete_product")
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("owner_delete_product_"))
def owner_delete_product_callback(call):
    product_id = int(call.data.split("_")[-1])

    try:
        delete_product(product_id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✅ Товар успешно удалён."
        )
        bot.send_message(
            call.message.chat.id,
            "<b>🛠 Меню управления каталогом</b>",
            reply_markup=get_owner_catalog_menu()
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Не удалось удалить товар.\n\n{e}")

    bot.answer_callback_query(call.id)


# =========================
# УПРАВЛЕНИЕ КОНТЕНТОМ
# =========================
@bot.message_handler(func=lambda message: message.text == "➕ Добавить акцию")
def add_promotion_handler(message):
    owner_state[message.from_user.id] = {}
    msg = bot.send_message(message.chat.id, "🎁 Введите заголовок акции:")
    bot.register_next_step_handler(msg, process_promotion_title)


def process_promotion_title(message):
    owner_state[message.from_user.id]["promotion_title"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "📝 Введите описание акции:")
    bot.register_next_step_handler(msg, process_promotion_description)


def process_promotion_description(message):
    title = owner_state.get(message.from_user.id, {}).get("promotion_title")
    description = message.text.strip()

    try:
        create_promotion(title, description)
        bot.send_message(
            message.chat.id,
            "✅ Акция успешно добавлена.",
            reply_markup=get_owner_content_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Не удалось добавить акцию.\n\n{e}",
            reply_markup=get_owner_content_menu()
        )

    owner_state.pop(message.from_user.id, None)


@bot.message_handler(func=lambda message: message.text == "🗑 Удалить акцию")
def delete_promotion_handler(message):
    promotions = get_all_promotions()

    if not promotions:
        bot.send_message(message.chat.id, "🎁 Акций пока нет.")
        return

    lines = ["<b>Список акций</b>\n"]
    for promotion_id, title, description in promotions:
        lines.append(f"ID {promotion_id} — {title}")

    lines.append("\nВведите ID акции для удаления:")
    msg = bot.send_message(message.chat.id, "\n".join(lines))
    bot.register_next_step_handler(msg, process_delete_promotion_id)


def process_delete_promotion_id(message):
    try:
        promotion_id = int(message.text.strip())
        delete_promotion(promotion_id)
        bot.send_message(
            message.chat.id,
            "✅ Акция успешно удалена.",
            reply_markup=get_owner_content_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Не удалось удалить акцию.\n\n{e}",
            reply_markup=get_owner_content_menu()
        )


@bot.message_handler(func=lambda message: message.text == "✏️ Изменить О нас")
def edit_about_handler(message):
    current_text = get_about_text()
    msg = bot.send_message(
        message.chat.id,
        f"<b>Текущий текст:</b>\n\n{current_text}\n\nВведите новый текст:"
    )
    bot.register_next_step_handler(msg, process_about_text)


def process_about_text(message):
    try:
        update_about_text(message.text.strip())
        bot.send_message(
            message.chat.id,
            "✅ Раздел <b>О нас</b> успешно обновлён.",
            reply_markup=get_owner_content_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Не удалось обновить текст.\n\n{e}",
            reply_markup=get_owner_content_menu()
        )


# =========================
# КАТАЛОГ коллбеки
# =========================
@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def category_callback(call):
    category_id = int(call.data.split("_")[1])
    products = get_products_by_category(category_id)

    if not products:
        bot.answer_callback_query(call.id, "В этой категории пока нет товаров.")
        return

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>📂 Товары категории</b>\nВыберите товар:",
        reply_markup=get_products_inline_keyboard(category_id)
    )


@bot.callback_query_handler(func=lambda call: call.data == "back_to_categories")
def back_to_categories_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>📂 Выберите категорию</b>",
        reply_markup=get_categories_inline_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_products_"))
def back_to_products_callback(call):
    category_id = int(call.data.split("_")[3])

    bot.delete_message(call.message.chat.id, call.message.message_id)

    bot.send_message(
        call.message.chat.id,
        "<b>📂 Товары категории</b>\nВыберите товар:",
        reply_markup=get_products_inline_keyboard(category_id)
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def product_callback(call):
    product_id = int(call.data.split("_")[1])
    product = get_product_by_id(product_id)

    if not product:
        bot.answer_callback_query(call.id, "Товар не найден.")
        return

    _, category_id, name, description, price, image_file_id = product

    text = (
        f"<b>{name}</b>\n\n"
        f"{description or 'Описание отсутствует.'}\n\n"
        f"💰 Цена: <b>{price} ₽</b>"
    )

    bot.delete_message(call.message.chat.id, call.message.message_id)

    if image_file_id:
        bot.send_photo(
            call.message.chat.id,
            image_file_id,
            caption=text,
            reply_markup=get_product_card_keyboard(product_id, category_id)
        )
    else:
        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=get_product_card_keyboard(product_id, category_id)
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_to_cart_"))
def add_to_cart_callback(call):
    user_id = call.from_user.id
    visitor_db_id = get_current_visitor_db_id(user_id)

    if not visitor_db_id:
        bot.answer_callback_query(call.id, "Профиль посетителя не найден.")
        return

    product_id = int(call.data.split("_")[3])
    add_product_to_cart(visitor_db_id, product_id)

    bot.answer_callback_query(call.id, "Товар добавлен в корзину ✅")


# =========================
# КОРЗИНА
# =========================
@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_from_cart_"))
def remove_from_cart_callback(call):
    user_id = call.from_user.id
    visitor_db_id = get_current_visitor_db_id(user_id)

    if not visitor_db_id:
        bot.answer_callback_query(call.id, "Профиль посетителя не найден.")
        return

    product_id = int(call.data.split("_")[3])
    remove_product_from_cart(visitor_db_id, product_id)

    items = get_cart_items(visitor_db_id)
    total_sum = get_cart_total(visitor_db_id)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=render_cart_text(items, total_sum),
        reply_markup=get_cart_inline_keyboard(items)
    )


@bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
def clear_cart_callback(call):
    user_id = call.from_user.id
    visitor_db_id = get_current_visitor_db_id(user_id)

    if not visitor_db_id:
        bot.answer_callback_query(call.id, "Профиль посетителя не найден.")
        return

    clear_cart(visitor_db_id)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🛒 <b>Ваша корзина пуста</b>",
        reply_markup=None
    )


@bot.callback_query_handler(func=lambda call: call.data == "checkout_order")
def checkout_order_callback(call):
    user_id = call.from_user.id
    visitor_db_id = get_current_visitor_db_id(user_id)

    if not visitor_db_id:
        bot.answer_callback_query(call.id, "Профиль посетителя не найден.")
        return

    order_id = create_order_from_cart(visitor_db_id)

    if not order_id:
        bot.answer_callback_query(call.id, "Корзина пуста.")
        return

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Заказ <b>#{order_id}</b> успешно оформлен!"
    )

    notify_employees_about_new_order(order_id)


# =========================
# ЗАКАЗЫ СОТРУДНИКА
# =========================
@bot.callback_query_handler(func=lambda call: call.data.startswith("employee_order_"))
def employee_order_callback(call):
    order_id = int(call.data.split("_")[2])

    bot.send_message(
        call.message.chat.id,
        render_order_text(order_id),
        reply_markup=get_order_status_keyboard(order_id)
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("set_status_"))
def set_status_callback(call):
    parts = call.data.split("_")
    order_id = int(parts[2])
    raw_status = "_".join(parts[3:])
    new_status = raw_status.replace("_", " ")

    update_order_status(order_id, new_status)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=render_order_text(order_id),
        reply_markup=get_order_status_keyboard(order_id)
    )

    notify_visitor_about_status_change(order_id, new_status)
    bot.answer_callback_query(call.id, f"Статус изменён: {new_status}")


# =========================
# КОМАНДЫ И ОБЩИЕ ОБРАБОТЧИКИ
# =========================
@bot.message_handler(commands=['menu'])
def menu_command_handler(message):
    user_id = message.from_user.id
    show_main_menu_by_session(message.chat.id, user_id)


@bot.message_handler(commands=['profile'])
def profile_command_handler(message):
    universal_profile_handler(message)


@bot.message_handler(commands=['cart'])
def cart_command_handler(message):
    cart_handler(message)


@bot.message_handler(commands=['orders'])
def orders_command_handler(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        bot.send_message(message.chat.id, "⚠️ Сначала войдите через /start")
        return

    role = session.get("role")
    if role == "visitor":
        my_orders_handler(message)
    elif role in ["employee", "owner"]:
        staff_orders_handler(message)
    else:
        bot.send_message(message.chat.id, "⚠️ Команда недоступна.")


@bot.message_handler(commands=['help'])
def help_command_handler(message):
    bot.send_message(
        message.chat.id,
        "<b>📖 Доступные команды</b>\n\n"
        "/start — запустить бота\n"
        "/menu — открыть меню\n"
        "/profile — открыть профиль\n"
        "/cart — открыть корзину\n"
        "/orders — открыть заказы\n"
        "/help — помощь\n\n"
        "Используйте кнопки внизу экрана для быстрой навигации."
    )


@bot.message_handler(func=lambda message: message.text == "🔄 Сменить роль")
def change_role_handler(message):
    user_id = message.from_user.id

    auth_data.pop(user_id, None)
    user_sessions.pop(user_id, None)
    owner_state.pop(user_id, None)

    bot.send_message(
        message.chat.id,
        "🔄 <b>Выберите новую роль:</b>",
        reply_markup=get_role_keyboard()
    )


@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def fallback_handler(message):
    if message.content_type == "photo":
        bot.send_message(
            message.chat.id,
            "🖼 Фото получено, но сейчас для этого действия нет активного шага."
        )
        return

    bot.send_message(
        message.chat.id,
        "ℹ️ Используйте кнопки меню или команды: /start, /menu, /help"
    )


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)