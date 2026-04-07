import bcrypt

password = input("Введите пароль: ").strip()

hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
print("\nХеш пароля:")
print(hashed.decode("utf-8"))

INSERT INTO users (username, password_hash, role)
VALUES ('admin', '$2b$12$4lYl3qInQmnvOij.9jZsNOiz9V7I61TF49VzhnIOsnmPYR4p0FtbO', 'owner');