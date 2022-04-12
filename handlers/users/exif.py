import os
import traceback

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import InputFile

from keyboards.default.exif_keyboards import cancel_markup, general_markup
from loader import dp
from utils.parser.crawler import async_crawler
from utils.parser.osint import async_save_exif_data


# хендлер отмены состояния
@dp.message_handler(text="\U00002716 Отмена", state="set_exif")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(message.text, reply_markup=general_markup)


# хендлер на начало парсинга
@dp.message_handler(text='\U0001F50E Поиск')
@dp.message_handler(Command("exif"))
async def set_exif_handler(message: types.Message, state: FSMContext):
    await message.answer(f"Оправь мне ссылку на сайт",
                         reply_markup=cancel_markup)
    # задаем состояние
    await state.set_state("set_exif")


# хендлер состояния set_exif
@dp.message_handler(state="set_exif")
async def get_exif_handler(message: types.Message, state: FSMContext):
    # задаем новое состояние
    await state.set_state("get_exif")
    # получаем ссылку от юзера и проверяем ее
    url = message.text
    if not url.startswith("https://") and not url.startswith("http://"):
        await state.finish()
        await message.answer('Неверный формат ссылки', reply_markup=general_markup)
        return
    # отправка сообщения и изменяем клавиатуру пользователя
    await message.answer("Поиск файлов на сайте...", reply_markup=ReplyKeyboardRemove())
    # получаем ссылки с сайта
    try:
        links = await async_crawler(url)
    except Exception:
        await message.answer("Ошибка при парсинге сайта", reply_markup=general_markup)
        await state.finish()
        return
    await message.answer("Получение данных по файлам...")
    # получаем данные
    try:
        # путь до файла
        path = await async_save_exif_data(links)
        # название файла для телеграма
        name = os.path.basename(path)
        # отправка файла юзеру
        report = InputFile(path, name)
        await message.answer_document(report, reply_markup=general_markup)
        # удаление отчета
        os.remove(path)
    except Exception:
        await message.answer("Ошибка при обработке файлов", reply_markup=general_markup)
        traceback.print_exc()
        await state.finish()
    # завершение состояния
    await state.finish()
