from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config

# бъект бота, в который передается токен и метод парсинга сообщений в телеграмме
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
# объект памяти, в которой будет храниться данные из состояний
storage = MemoryStorage()
# управляющий объект Dispatcher библиотеки aiogram, в него передаем объекты бота и памяти
dp = Dispatcher(bot, storage=storage)
