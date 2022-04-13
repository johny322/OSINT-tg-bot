from aiogram import types

from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    # отправка сообщения с тектом Эхо: текст сообщения от юзера
    await message.answer(f"Эхо: {message.text}")
