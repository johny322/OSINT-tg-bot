from environs import Env

# библиотека environs для получения переменных окружения
env = Env()
# загружаем переменные окружения
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение BOT_TOKEN типа str из переменных окружения
ADMINS = env.list("ADMINS")  # Тут у нас будет список из id админов из переменных окружения

