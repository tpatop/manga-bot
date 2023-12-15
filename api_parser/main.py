import logging
from fake_useragent import UserAgent
from requests import get, post
from bs4 import BeautifulSoup
from pydantic import BaseModel
from time import sleep


# Конфигурация логгирования
logging.basicConfig(
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Вывод на консоль
        logging.FileHandler('logfile.log')  # Запись в файл
    ],
    level=logging.INFO
)


HEADERS = {'User-Agent': UserAgent().chrome}
URLS = ('https://readmanga.live', 'https://mintmanga.com')


class UpdateManga(BaseModel):
    url_id: int
    link: str
    chapters: str
    name: str


def process_download_page(url: str, headers):
    result = get(url, headers=headers)
    logging.info(f'process_download_page - {url = }, {result.status_code}')
    return result.text


def process_validate_chapters(data: list) -> str:
    result = []
    for el in data:
        if el.lower() in ('...', '-', 'сингл', 'экстра', 'трейлер') \
                or not any([x.isalpha() for x in el]):
            result.append(el)
        else:
            logging.info(f'Не попадает элемент: {el}')
    if result:
        return ' '.join(result)


def process_parsing_html(html: str, url_id: int):
    '''Функция сбора необходимой информации с сайта'''
    if html is None:
        return None
    soup = BeautifulSoup(html, 'lxml')
    # Выбираем область "Последних обновлений каталога"
    last_updates = soup.find('div', {'id': 'last-updates'})
    # Получаем список обновлений
    updates = last_updates.find_all('div', {'class': 'tile'})
    # Проходим по списку и собираем необходимую информацию
    result = []
    for data in updates:
        # # поиск названия
        name = data.find('div', {'class': 'desc'}).find('a')['title']
        # # # поиск жанров
        # print(update.find('div', {'class': 'tile-info'}).text.strip())
        # # # поиск картинки
        # if update.find('div', {'class': 'no-image'}):  # отсутствие картинки
        #     print(IMAGE_NOT_FOUND)
        # else:
        #     print(update.find('img')['data-original'].replace('_p.', '.'))
        # # # поиск ссылки
        link = data.find('div', {'class': 'desc'}).find('a')['href']
        # # # поиск информации по обновлению глав
        chapters = process_validate_chapters(
            data.find('div', {'class': 'chapters-text'}).text.split()
        )
        if chapters is not None:
            update = UpdateManga(
                url_id=url_id,
                link=link,
                chapters=chapters,
                name=name
            )
            result.append(update)
    return result


def get_url_id(url: str):
    for x in range(len(URLS)):
        if URLS[x] in url:
            return x


def process_send_updates_in_db(updates):
    updates = [update.model_dump() for update in updates]
    response = post('http://api_db:8080/manga/add_updates', json=updates)
    logging.info(f'process_send_updates_in_db - status_code = {response.status_code}')
    if response.status_code == 400:
        return False
    return True


def process_start_parsing():
    for _url in URLS:
        for page in range(1):
            url_id = get_url_id(_url)
            url = _url + f'/?offset={page * 50}#last-updates'
            html = process_download_page(url, HEADERS)
            result = process_parsing_html(html, url_id)
            status = process_send_updates_in_db(result)
            if not status:
                break
            sleep(10)


if __name__ == '__main__':
    while True:
        try:
            sleep(5)  # Доп. время для запуска uvicorn на 1 запуске
            logging.info('Start process')
            process_start_parsing()
        except Exception as e:
            logging.error(f'An error occurred: {str(e)}')
        finally:
            logging.info('Process sleep on 10 minutes')
            sleep(10 * 60)
