from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# клавиатуры
cancel_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='\U00002716 Отмена')  # кнопка
        ]
    ],
    resize_keyboard=True
)

general_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='\U0001F50E Поиск')
        ]
    ],
    resize_keyboard=True
)
