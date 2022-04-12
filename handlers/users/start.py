from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.default.exif_keyboards import general_markup
from loader import dp


# хендлер на команду /start
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}!", reply_markup=general_markup)
