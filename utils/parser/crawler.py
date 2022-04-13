import asyncio
import os
import traceback
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import requests
import lxml
from fake_headers import Headers

from utils.functions import run_blocking_io

# массив с запрещенными префиксы
FORBIDDEN_PREFIXES = ['#', 'tel:', 'mailto:']

# массив с форматасми файлов
# ищет только фотографии
# POSTFIXES = ['.ico', '.jpeg', '.jpg', '.png', '.gif', '.tiff', '.raw', '.bmp', '.svg']
POSTFIXES = ['.pdf', '.docx', '.doc', '.exel', '.xlsx', '.ppsx', '.pptx',
             '.ico', '.jpeg', '.jpg', '.png', '.gif', '.tiff', '.raw', '.bmp', '.svg',
             '.webp', '.avi', '.mp4', '.mpeg', '.mkv', '.mov', '.mp3', '.wav', '.flac']
#              # '.exe', '.msi', '.zip']  # можно собирать и эти файлы, но они обычно много весят

# получаем заголовки для парсинга
headers = Headers().generate()


def add_all_links_recursive(url, DOMAIN, maxdepth, links, checked_links):
    """
    Функция парсинга ссылок

    :param url: ссылка для парсинга
    :param DOMAIN: домен основного сайта
    :param maxdepth: максимальная глубина рекурсии
    :param links: собранные ссылки
    :param checked_links: отработанные ссылки
    :return:
    """
    # глубина рекурсии не более `maxdepth`

    # список ссылок, от которых в конце мы рекурсивно запустимся
    links_to_handle_recursive = []

    # если ссылка уже отработа, то выходим из функции
    if url in checked_links:
        return

    # получаем html код страницы
    try:
        # запрос на сайт по ссылке url, с заголовками headers, максимальным ожиданием ответа 3с
        request = requests.get(url, headers=headers, timeout=3)
        # добавляем ссылку в отработанные
        checked_links.add(url)
        print(f'GET {url}')
    except Exception:
        # при ошибке выход из функции
        return
    # парсим его с помощью BeautifulSoup
    # передаем текст ответа с сайта request.text и используем парсер lxml
    soup = BeautifulSoup(request.text, 'lxml')
    # рассматриваем все теги с атрибутами href и src
    for tag in soup.find_all(lambda tag: tag.attrs.get('href') or tag.attrs.get('src')):
        # получаем арибут href у найденного тэга и если он есть, то задаем link равным ему
        if tag.get('href') is not None:
            link = tag.get('href')
            # print(link)
        # иначе получаем арибут src у найденного тэга и если он есть, то задаем link равным ему
        elif tag.get('src') is not None:
            link = tag.get('src')
            # print(link)
        # иначе пропускаем тэг
        else:
            continue

        # если ссылка не начинается с одного из запрещённых префиксов
        if all(not link.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            # проверяем, является ли ссылка относительной
            # например, `/oplata` --- это относительная ссылка
            # `http://101-rosa.ru/oplata` --- это абсолютная ссылка
            # сли ссылка начинается с / и не начинается с //, то добавляем к ней тип протокола и домен
            if link.startswith('/') and not link.startswith('//'):
                # преобразуем относительную ссылку в абсолютную
                o = urlparse(url)  # получаем части ссылки
                # o.scheme - протокол, o.netloc - домен
                link = f'{o.scheme}://{o.netloc}' + link
            # сли ссылка начинается с //, то добавляем к ней тип протокола
            if link.startswith('//'):
                o = urlparse(url)
                link = f'{o.scheme}:' + link
            # проверяем, что ссылка ведёт на нужный домен и подходитм по формату файла
            # и что мы ещё не обрабатывали такую ссылку
            # если ссылка еще не добавлена во множество всех ссылок
            if link not in links:
                # если ссылка заканчивается на нужный формат файла или содержит его, то добавляем ее
                # во множество всех ссылок
                if any(link.lower().endswith(postfix) for postfix in POSTFIXES) or any(
                        link.lower().__contains__(postfix) for postfix in POSTFIXES):
                    links.add(link)
                    print(f'FILE    {link}')
                # сли ссылка не заканчивается на нужный формат файла и не содержит его и ссылка не была отработана и
                # домен ссылки совпадает с доменом основного сайта и ссылка не содержит /map,
                # то добавляем ее во множество ссылок для рекурсивного запуска
                if all(not link.lower().endswith(postfix) for postfix in POSTFIXES) and \
                        all(not link.lower().__contains__(postfix) for postfix in POSTFIXES) and \
                        link not in checked_links and \
                        urlparse(link).netloc == DOMAIN and \
                        not link.__contains__("/map"):
                    links_to_handle_recursive.append(link)
    # если глубина больше 1
    if maxdepth > 1:

        # print(f'Max depth {maxdepth}')
        # print(f'Links count: {len(links)}')
        # итерация по ссылкам из рекурсивного множества
        for link in links_to_handle_recursive:
            # запускаем рекурсивно функцию с такими же параметрами, кроме ссылки и уменьшаем максимальную глубину
            add_all_links_recursive(link, DOMAIN, maxdepth=maxdepth - 1, links=links, checked_links=checked_links)


async def async_crawler(start_url, maxdepth=0):
    # дефолтно глубина 0, т.е. ищет только на стартовой странице
    links = set()  # множество всех ссылок
    checked_links = set()  # отработанные ссылки
    o = urlparse(start_url)  # распаршевание стартововй ссылки
    DOMAIN = o.netloc  # домен стартового сайта
    HOST = f'{o.scheme}://{o.netloc}/'  # хост стартового сайта
    # запуск функции с этими данными
    await async_add_all_links_recursive(HOST, DOMAIN, maxdepth, links, checked_links)
    print(len(links))
    # загрузка файлов по ссылкам links в папку files
    await download_files(links, "files")
    # возвращаем links
    return links


# оборачиваем синхронную функцию
async def async_add_all_links_recursive(url, DOMAIN, maxdepth, links, checked_links):
    await run_blocking_io(add_all_links_recursive, url, DOMAIN, maxdepth, links, checked_links)


async def download_files(urls, download_dir_path):
    """
    асинхронная функция загрузкаи файлов с использованием aiohttp

    :param urls: список ссылок для скачивания
    :param download_dir_path: путь к папке сохранения файла
    :return:
    """
    tasks = []
    # создаем объект сессии
    async with aiohttp.ClientSession() as session:
        # итерация по ссылкам
        for u in urls:
            # создаем задание скачивания файла по ссылке u в папку по пути download_dir_path
            task = asyncio.create_task(fetch_content(u, session, download_dir_path))
            # добавление задания task в список заданий
            tasks.append(task)
        # выполнение заданий
        await asyncio.gather(*tasks)


# получение файлов
async def fetch_content(url, session: ClientSession, download_dir_path):
    """
    функция получения файла по ссылке

    :param url: ссылка на файл
    :param session: объект сессии
    :param download_dir_path: путь до папки сохранения
    :return:
    """
    try:
        async with session.get(url,
                               allow_redirects=True,  # разрешаем ридеректы
                               headers=Headers(headers=True).generate(),  # заголовки
                               timeout=3  # максимальное ожидание загрузки ссылки
                               ) as response:
            # получение результата ответа
            data = await response.read()
            # если ссылка заканчивается на /, то обрезаем его
            if url.endswith('/'):
                url = url[:-1]
            # получаем имя файла через парсинг ссылки
            # берем последнюю часть ссылки, разделяя ее через /, и получаем его имя
            name = urlparse(url.split('/')[-1]).path
            # сохраняетм файл с данными data с именем name папку download_dir_path
            await async_write_file(data, download_dir_path, name)
            # write_file(data, download_dir_path, name)
    except Exception:
        # при ошибке выводим ее
        traceback.print_exc()
        # pass


def write_file(data, download_dir_path, name):
    """
    запись данных в файл

    :param data: данные для сохранения
    :param download_dir_path: путь до папки сохранения
    :param name: имя файла
    :return:
    """
    # проверка если не существует путь download_dir_path
    if not os.path.exists(download_dir_path):
        # создаем папки по пути download_dir_path
        os.makedirs(download_dir_path)
    # полный путь к файлу сохранения вместе с его именем
    # происходит соединение пути download_dir_path и названия файла name
    name = os.path.join(download_dir_path, name)
    # print(os.path.abspath(name))

    # открытие файла по пути name на побитовую запись
    with open(name, 'wb') as f:
        print(f'Сохранение фото по пути: {name}')
        # запись данных data в файл по пути name
        f.write(data)


# оборачиваем синхронную функцию
async def async_write_file(data, download_dir_path, name):
    await run_blocking_io(write_file, data, download_dir_path, name)


if __name__ == '__main__':
    asyncio.run(async_crawler("https://www.knx.org/"))
