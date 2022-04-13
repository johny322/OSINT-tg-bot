from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# клавиатуры отмены
cancel_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='\U00002716 Отмена')  # кнопка с текстом \U00002716 Отмена
        ]
    ],
    resize_keyboard=True  # подгонять размер кнопок под экран
)

# основная клавиатура
general_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='\U0001F50E Поиск')  # кнопка с текстом \U0001F50E Поиск
        ]
    ],
    resize_keyboard=True  # подгонять размер кнопок под экран
)
