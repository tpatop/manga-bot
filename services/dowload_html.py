# import aiohttp
# import asyncio
# from fake_useragent import UserAgent


# МОЯ РЕАЛИЗАЦИЯ
# async def process_download_html(url: str):
#     '''Выполнение get-запроса и возврат текстового содержания страницы'''
#     async def fetch(session, url):
#         headers: dict[str: str] = {'User-agent': UserAgent().chrome}
#         async with session.get(url, headers=headers) as response:
#             if response.status != 200:
#                 print(f"Error fetching {url}: "
#                         f"status code {response.status}"
#                         f'\nRestart after 10 seconds!')
#                 return None
#                 # await asyncio.sleep(10)
#                 # await process_download_html(url)
#                 # raise Exception(f"Error fetching {url}: "
#                 #                 f"status code {response.status}")
#             return await response.text()

#     async with aiohttp.ClientSession() as session:
#         html_task = asyncio.create_task(fetch(session, url))
#         html = await html_task
#         if html is None:
#             asyncio.sleep(10)
#             html_task = asyncio.create_task(fetch(session, url))
#             html = await html_task
#     return html


# import aiohttp
# import asyncio
# from fake_useragent import UserAgent


# # 1 РЕАЛИЗАЦИЯ ЧАТА
# async def process_download_html(url: str):
#     '''Выполнение get-запроса и возврат текстового содержания страницы'''

#     async def fetch(session, url):
#         headers = {'User-agent': UserAgent().chrome}
#         async with session.get(url, headers=headers) as response:
#             if response.status != 200:
#                 print(f"Error fetching {url}: status code {response.status}\nRestart after 10 seconds!")
#                 return None
#             return await response.text()

#     async def fetch_with_retry(session, url):
#         max_attempts = 5
#         retry_delay = 5  # seconds
#         for attempt in range(max_attempts):
#             try:
#                 html = await fetch(session, url)
#                 if html is not None:
#                     return html
#                 print(f"Retrying {url} after {retry_delay} seconds, attempt {attempt+1}/{max_attempts}")
#                 await asyncio.sleep(retry_delay)
#             except aiohttp.ClientError as e:
#                 print(f"Error fetching {url}: {e}\nRetrying after {retry_delay} seconds, attempt {attempt+1}/{max_attempts}")
#                 await asyncio.sleep(retry_delay)
#         raise Exception(f"Failed to fetch {url} after {max_attempts} attempts")

#     async with aiohttp.ClientSession() as session:
#         html = await fetch_with_retry(session, url)
#     return html


# 2 РЕАЛИЗАЦИЯ ЧАТА
import asyncio
import random
import aiohttp
from fake_useragent import UserAgent


async def process_download_html(url: str):
    '''Выполнение get-запроса и возврат текстового содержания страницы'''

    async def fetch(session, url):
        headers = {'User-Agent': UserAgent().chrome}
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return None
            return await response.text()

    async def fetch_with_retry(session, url):
        if '#last-updates' not in url:
            max_attempts = 1
            retry_delay = 2
        else:
            max_attempts = 3
            retry_delay = 10  # seconds
        for attempt in range(max_attempts):
            try:
                html = await fetch(session, url)
                if html is not None:
                    return html
                print_error(f"Retrying {url} after {retry_delay} seconds, attempt {attempt+1}/{max_attempts}")
            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError) as e:
                print_error(f"Error fetching {url}: {e}\nRetrying after {retry_delay} seconds, attempt {attempt+1}/{max_attempts}")
            await asyncio.sleep(random.uniform(retry_delay, retry_delay*2))
        print_error(f"Failed to fetch {url} after {max_attempts} attempts")

    def print_error(msg: str):
        print(f"Error: {msg}\nRestart after couple of seconds!")

    async with aiohttp.ClientSession() as session:
        html = await fetch_with_retry(session, url)
    return html


# # для отладки
# if __name__ == '__main__':
#     asyncio.run(process_download_html(url))
