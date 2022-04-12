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

# запрещенные префиксы
FORBIDDEN_PREFIXES = ['#', 'tel:', 'mailto:']

# форматы файлов
# ищет только фотографии
# POSTFIXES = ['.ico', '.jpeg', '.jpg', '.png', '.gif', '.tiff', '.raw', '.bmp', '.svg']
POSTFIXES = ['.pdf', '.docx', '.doc', '.exel', '.xlsx', '.ppsx', '.pptx',
             '.ico', '.jpeg', '.jpg', '.png', '.gif', '.tiff', '.raw', '.bmp', '.svg',
             '.webp', '.avi', '.mp4', '.mpeg', '.mkv', '.mov', '.mp3', '.wav', '.flac']
#              # '.exe', '.msi', '.zip']  # можно собирать и эти файлы, но они обычно много весят

# заголовки для парсинга
headers = Headers().generate()


def add_all_links_recursive(url, DOMAIN, maxdepth, links, checked_links):
    # глубина рекурсии не более `maxdepth`

    # список ссылок, от которых в конце мы рекурсивно запустимся
    links_to_handle_recursive = []

    if url in checked_links:
        return

    # получаем html код страницы
    try:
        request = requests.get(url, headers=headers, timeout=3)
        checked_links.add(url)
        print(f'GET {url}')
    except Exception:
        return
    # парсим его с помощью BeautifulSoup
    soup = BeautifulSoup(request.text, 'lxml')
    # рассматриваем все теги с атрибутами href и src
    for tag in soup.find_all(lambda tag: tag.attrs.get('href') or tag.attrs.get('src')):
        # получаем ссылку
        if tag.get('href') is not None:
            link = tag.get('href')
            # print(link)
        elif tag.get('src') is not None:
            link = tag.get('src')
            # print(link)
        else:
            continue

        # если ссылка не начинается с одного из запрещённых префиксов
        if all(not link.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            # проверяем, является ли ссылка относительной
            # например, `/oplata` --- это относительная ссылка
            # `http://101-rosa.ru/oplata` --- это абсолютная ссылка
            if link.startswith('/') and not link.startswith('//'):
                # преобразуем относительную ссылку в абсолютную
                o = urlparse(url)
                link = f'{o.scheme}://{o.netloc}' + link
            if link.startswith('//'):
                o = urlparse(url)
                link = f'{o.scheme}:' + link
            # проверяем, что ссылка ведёт на нужный домен и подходитм по формату файла
            # и что мы ещё не обрабатывали такую ссылку
            if link not in links:
                if any(link.lower().endswith(postfix) for postfix in POSTFIXES) or any(link.lower().__contains__(postfix) for postfix in POSTFIXES):
                    links.add(link)
                    print(f'FILE    {link}')
                if all(not link.lower().endswith(postfix) for postfix in POSTFIXES) and \
                    all(not link.lower().__contains__(postfix) for postfix in POSTFIXES) and \
                        link not in checked_links and \
                    urlparse(link).netloc == DOMAIN and \
                        not link.__contains__("/map"):
                    links_to_handle_recursive.append(link)

    if maxdepth > 0:
        # запускаем рекурсивно функцию
        # print(f'Max depth {maxdepth}')
        # print(f'Links count: {len(links)}')
        for link in links_to_handle_recursive:
            add_all_links_recursive(link, DOMAIN, maxdepth=maxdepth - 1, links=links, checked_links=checked_links)


async def async_crawler(start_url, maxdepth=0):
    # дефолтно глубина 0, т.е. ищет только на стартовой странице
    links = set()  # множество всех ссылок
    checked_links = set()  # отработанные ссылки
    o = urlparse(start_url)  # распаршевание стартововй ссылки
    DOMAIN = o.netloc
    HOST = f'{o.scheme}://{o.netloc}/'
    await async_add_all_links_recursive(HOST, DOMAIN, maxdepth, links, checked_links)
    print(len(links))
    await download_files(links, "files")
    return links


# оборачиваем синхронную функцию
async def async_add_all_links_recursive(url, DOMAIN, maxdepth, links, checked_links):
    await run_blocking_io(add_all_links_recursive, url, DOMAIN, maxdepth, links, checked_links)


# асинхронная функция загрузкаи файлов с использованием aiohttp
async def download_files(urls, download_dir_path):
    tasks = []
    # создаем объект сессии
    async with aiohttp.ClientSession() as session:
        for u in urls:
            # добавляем задания
            task = asyncio.create_task(fetch_content(u, session, download_dir_path))
            tasks.append(task)
        await asyncio.gather(*tasks)


# получение файлов
async def fetch_content(url, session: ClientSession, download_dir_path):
    try:
        async with session.get(url,
                               allow_redirects=True,
                               headers=Headers(headers=True).generate(),
                               timeout=3) as response:
            data = await response.read()
            if url.endswith('/'):
                url = url[:-1]
            name = urlparse(url.split('/')[-1]).path
            await async_write_file(data, download_dir_path, name)
            # write_file(data, download_dir_path, name)
    except Exception:
        traceback.print_exc()
        # pass


# сохранение файлов
def write_file(data, download_dir_path, name):
    if not os.path.exists(download_dir_path):
        os.makedirs(download_dir_path)
    name = os.path.join(download_dir_path, name)
    # print(os.path.abspath(name))
    with open(name, 'wb') as f:
        print(f'Сохранение фото по пути: {name}')
        f.write(data)


# оборачиваем синхронную функцию
async def async_write_file(data, download_dir_path, name):
    await run_blocking_io(write_file, data, download_dir_path, name)


if __name__ == '__main__':
    asyncio.run(async_crawler("https://www.knx.org/"))
