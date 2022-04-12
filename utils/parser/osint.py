import os
import time
import traceback
from multiprocessing import Pool

import exiftool

from utils.functions import run_blocking_io
from utils.parser.exel_worker import Excel


# класс не использовал
class Exif:
    def __init__(self):
        self.ex = Excel()
        self.main_key = "File:FileName"
        self.data = {
            self.main_key: []
        }
        self.ex.set_main_key(self.main_key)
        self.ex.set_data(self.data)

    @staticmethod
    def get_exif(file_path) -> dict:
        with exiftool.ExifToolHelper() as et:
            try:
                metadata = et.get_tags(file_path, None)[0]
                # чистка ненужной информации
                # из информации по файлу берется только размер и название
                metadata = {key: value for key, value in metadata.items()
                            if (not key.startswith("File:") or key.__contains__("FileName") or key.__contains__(
                        "FileSize"))
                            and (not key.startswith("SourceFile")) and (not key.startswith("ExifTool:"))
                            }
            except Exception:
                # traceback.print_exc()
                metadata = {}
        return metadata

    def exif_work(self, file_path):
        exif = self.get_exif(file_path)
        # print(file_path)
        for key, value in exif.items():
            # добавлеие данных
            self.ex.add_key_value(key, value)

    def get_exif_new(self, dir_path):
        files = [os.path.join(dir_path, file) for file in os.listdir(dir_path)]
        p = Pool(4)
        p.map(self.exif_work, files)
        self.ex.write_exel("report.xlsx", now_date=True)


# получение информации из файла с помощью exiftool
def get_exif(file_path) -> dict:
    with exiftool.ExifToolHelper() as et:
        try:
            metadata = et.get_tags(file_path, None)[0]
            # чистка ненужной информации
            # из информации по файлу берется только размер и название
            metadata = {key: value for key, value in metadata.items()
                        if (not key.startswith("File:") or key.__contains__("FileName") or key.__contains__("FileSize"))
                        and (not key.startswith("SourceFile")) and (not key.startswith("ExifTool:"))
                        }
        except Exception:
            # traceback.print_exc()
            metadata = {}
    return metadata


# сохранение данных
def save_exif_data(links, dir_path='files'):
    # небольшой модуль для работы с excel
    ex = Excel()
    # main_key = "File:FileName"
    # задаем начальные данные для работы
    main_key = 'Url'
    data = {
        main_key: []
    }
    ex.set_main_key(main_key)
    ex.set_data(data)

    # итарация по файлам в папке
    for file in os.listdir(dir_path):
        file_link = ''
        for link in links:
            # ищем ссылку на файл
            if link.endswith(file):
                file_link = link
                links.remove(link)
                break
            if link.__contains__(file):
                file_link = link
                links.remove(link)
                break
        # добавление значения для сохранения
        ex.add_key_value(main_key, file_link)
        # путь до файла
        file_path = os.path.join(dir_path, file)
        # file_path = os.path.abspath(file)
        # print(file_path)
        # получение данных файла
        exif = get_exif(file_path)
        for key, value in exif.items():
            # добавлеие данных
            ex.add_key_value(key, value)
        # удаление отработанного файла
        os.remove(file_path)
    # сохранение файла
    # now_date добавляет время сохранения в название файла
    return ex.write_exel("report.xlsx", now_date=True)


# оборачиваем синхронную функцию
async def async_save_exif_data(links, dir_path='files'):
    return await run_blocking_io(save_exif_data, links, dir_path)


if __name__ == '__main__':
    start = time.time()
    save_exif_data("files")
    print("TIME:", time.time() - start)
