import os
from pathlib import Path

from dotenv import load_dotenv

# Выводим текущую рабочую директорию
print(f"Текущая рабочая директория: {os.getcwd()}")

# Путь к .env файлу
env_path = Path(".") / ".env"
print(f"Путь к .env файлу: {env_path.absolute()}")
print(f".env файл существует: {env_path.exists()}")

# Пытаемся прочитать содержимое .env файла
try:
    with open(env_path, "r") as f:
        print("Содержимое .env файла:")
        print(f.read())
except Exception as e:
    print(f"Ошибка при чтении .env файла: {e}")

# Загружаем переменные окружения
load_dotenv(env_path)

# Проверяем значения переменных
env_vars = [
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
    "HUI",
    "DEBUG",
    "REDIS_URL",
    "TELEGRAM_BOT_TOKEN",
]

print("\nЗначения переменных окружения:")
for var in env_vars:
    value = os.getenv(var)
    print(f"{var}: {value}")

# Проверяем, есть ли другие переменные с похожими именами
print("\nВсе переменные окружения, начинающиеся с 'DB_':")
for key, value in os.environ.items():
    if key.startswith("DB_"):
        print(f"{key}: {value}")
