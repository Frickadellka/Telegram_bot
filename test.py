import telebot
from telebot import types

from config import TOKEN
from db import get_user_by_username, verify_password

bot = telebot.TeleBot(TOKEN)

auth_data = {}
user_sessions = {}


def get_role_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Владелец", "Сотрудник", "Посетитель")
    return keyboard


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = get_role_keyboard()

    with open("start.jpg", "rb") as photo:
        bot.send_photo(
            message.chat.id,
            photo,
            caption="Приветствую! Я - персональный бот этого заведения. "
                "Я помогу тебе сориентироваться и найти нужную информацию.\n\n"
                "Выбери свою роль:",
            reply_markup=keyboard
        )


@bot.message_handler(func=lambda m: m.text in ["Владелец", "Сотрудник", "Посетитель"])
def role_handler(message):
    user_id = message.from_user.id
    role_text = message.text

    if role_text == "Посетитель":
        user_sessions[user_id] = {"role": "visitor"}
        bot.send_message(message.chat.id, "Вы вошли как Посетитель")
        return

    auth_data[user_id] = {}

    msg = bot.send_message(message.chat.id, "Введите логин:")
    bot.register_next_step_handler(msg, process_login)


def process_login(message):
    user_id = message.from_user.id

    auth_data[user_id]["username"] = message.text.strip()

    msg = bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(msg, process_password)


def process_password(message):
    user_id = message.from_user.id

    username = auth_data[user_id]["username"]
    password = message.text.strip()

    user = get_user_by_username(username)

    if not user:
        bot.send_message(message.chat.id, "Неверный логин или пароль ❌")
        auth_data.pop(user_id, None)
        return

    db_id, db_username, db_password_hash, db_role = user

    if not verify_password(password, db_password_hash):
        bot.send_message(message.chat.id, "Неверный логин или пароль ❌")
        auth_data.pop(user_id, None)
        return

    user_sessions[user_id] = {
        "role": db_role,
        "username": db_username
    }

    role_name = "Владелец" if db_role == "owner" else "Сотрудник"

    bot.send_message(
        message.chat.id,
        f"Успешный вход ✅\nВы вошли как {role_name}"
    )

    auth_data.pop(user_id, None)


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()