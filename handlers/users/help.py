from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


# хендлер на команду /help
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")
    # отправка сообщения с текстом состоящим из элементов массива text и разделенных \n
    await message.answer("\n".join(text))
