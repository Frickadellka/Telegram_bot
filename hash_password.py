import bcrypt

password = input("Введите пароль: ").strip()

hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
print("\nХеш пароля:")
print(hashed.decode("utf-8"))

