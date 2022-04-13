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


@dp.message_handler(text="\U00002716 Отмена", state="set_exif")
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    в этот хендлер летят сообщения с текстом \U00002716 Отмена и состоянием set_exif

    :param message: объект сообщения
    :param state: объект состояния
    :return:
    """
    # завершение состояния
    await state.finish()
    # отправка сообщения юзера с текстом полученного сообщения и основной клавиатурой general_markup
    await message.answer(message.text, reply_markup=general_markup)


@dp.message_handler(text='\U0001F50E Поиск')
@dp.message_handler(Command("exif"))
async def set_exif_handler(message: types.Message, state: FSMContext):
    """
    в этот хендлер летят сообщения с текстом \U0001F50E Поиск и командой exif

    :param message:
    :param state:
    :return:
    """
    # тправка сообщения с тектом Оправь мне ссылку на сайт и клавиатурой отмены cancel_markup
    await message.answer(f"Оправь мне ссылку на сайт",
                         reply_markup=cancel_markup)
    # задаем состояние set_exif
    await state.set_state("set_exif")


@dp.message_handler(state="set_exif")
async def get_exif_handler(message: types.Message, state: FSMContext):
    """
    в этот хендлер летят сообщения с состоянием set_exif

    :param message:
    :param state:
    :return:
    """
    # задаем новое состояние get_exif
    await state.set_state("get_exif")
    # получаем ссылку от юзера и проверяем ее
    url = message.text
    # если текст сообщения не начинвется с https:// или с http://
    if not url.startswith("https://") and not url.startswith("http://"):
        # завершение состояния
        await state.finish()
        # отправка сообщения Неверный формат ссылки с основной клавиатурой
        await message.answer('Неверный формат ссылки', reply_markup=general_markup)
        # выход из функции
        return
    # отправка сообщения Поиск файлов на сайте... и убираем клавиатуру у пользователя с помощью ReplyKeyboardRemove
    await message.answer("Поиск файлов на сайте...", reply_markup=ReplyKeyboardRemove())
    # получаем ссылки с сайта
    try:
        # запускаем функция получения ссылок с сайта по ссылке url
        links = await async_crawler(url)
    except Exception:
        # ри ошибке отправка Ошибка при парсинге сайта и основной клавиатуры
        await message.answer("Ошибка при парсинге сайта", reply_markup=general_markup)
        # завершение состояния
        await state.finish()
        # выход
        return
    # отправка сообщения Получение данных по файлам...
    await message.answer("Получение данных по файлам...")
    # получаем данные
    try:
        # путь до файла в который сохранены данные по скаченным файлам по ссылкам links
        path = await async_save_exif_data(links)
        # получение названия файла по полному пути
        name = os.path.basename(path)
        # отправка файла отчета по пути path и именем в телеграме name юзеру
        report = InputFile(path, name)
        await message.answer_document(report, reply_markup=general_markup)
        # удаление файла отчета по пути path
        os.remove(path)
    except Exception:
        # при ошибке отправка сообщения Ошибка при обработке файлов и основной клавиатуры
        await message.answer("Ошибка при обработке файлов", reply_markup=general_markup)
        # вывод ошибки
        traceback.print_exc()
        # завершение состояния
        await state.finish()
    # завершение состояния
    await state.finish()
