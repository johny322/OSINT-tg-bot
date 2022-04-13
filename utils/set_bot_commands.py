from aiogram import types


async def set_default_commands(dp):
    # установка команд в боте, которые будут пордсказываться в боте
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),  # добавление комманды /start с поясением Запустить бота
            types.BotCommand("help", "Вывести справку"),  # добавление комманды /help с поясением Вывести справку
            types.BotCommand("exif", "Поиск файлов на сайте"),  # добавление комманды /exif с поясением Поиск файлов на сайте
        ]
    )
