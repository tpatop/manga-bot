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
