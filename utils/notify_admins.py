import logging

from aiogram import Dispatcher

from data.config import ADMINS


async def on_startup_notify(dp: Dispatcher):
    # итерация по id админов из масива с админами из файла конфига
    for admin in ADMINS:
        try:
            # попытка отправки сообщения на id admin с текстом "Бот Запущен"
            await dp.bot.send_message(admin, "Бот Запущен")

        except Exception as err:
            # обработка исключения
            logging.exception(err)
