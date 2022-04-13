import asyncio
import concurrent.futures


# обертки для запуска функции, блокирующей io
async def run_blocking_io(func, *args):
    # получаем loop
    loop = asyncio.get_running_loop()
    # выполняем функцию func с аргументами *args с помощью объекта ThreadPoolExecutor в полученном loop`е
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, func, *args
        )
        # возвращаем результат выполнения функции
        return result


# обертки для запуска функции, блокирующей cpu
async def run_blocking_cpu(func, *args):
    # получаем loop
    loop = asyncio.get_running_loop()
    # выполняем функцию func с аргументами *args с помощью объекта ProcessPoolExecutor в полученном loop`е
    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, func, *args
        )
        # возвращаем результат выполнения функции
        return result
