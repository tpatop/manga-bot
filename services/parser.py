from typing import List, Tuple
from bs4 import BeautifulSoup
from services.dowload_html import process_download_html
from lexicon.const_url import URL_MANGA


async def _process_parsing_html(html: str) -> Tuple[List[str], List[str], List[str], List[List[str]], List[str]]:
    '''Функция сбора необходимой информации с сайта'''
    if html is None:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', {'id': 'last-updates'})
    # !сбор данных об обновленных элементах
    # Получение названия
    title = [links.find('a', href=True)['title'] for links in div.find_all('div', {'class': 'desc'})]
    # Получение ссылки на мангу
    manga_link = [links.find('a', href=True)['href'] for links in div.find_all('div', {'class': 'desc'})]
    # print(*manga_link, sep='\n')

    # Получение ссылки на изображение
    images_links = div.find_all('a', {'class': 'non-hover'})  # вспомогательное
    image_orig_link = []
    for link in images_links:
        if link.find('div', {'class': 'no-image'}):  # отсутствие картинки
            image_orig_link.append('https://w7.pngwing.com/pngs/360/55/png-transparent-fate-grand-order-fate-stay-night-http-404-server-404-error-purple-violet-text.png')
        else:
            image_orig_link.append(link.find('img')['data-original'].replace('_p.', '.'))

    # Получение списка обновленных глав
    chapters = div.find_all('div', {'class': 'chapters-text'})
    chapters = tuple([' '.join(x.text.strip().split()[:3])
                    for x in par.find_all('a', href=True)]
                    for par in chapters)
    # print(*zip(title, image_orig_link, chapters), sep='\n')

    # получение информации о произведении
    manga_description = [dscr.text.strip() for dscr in div.find_all('div', {'class': 'manga-description'})]
    # print(*manga_description, sep='\n\n')

    # получение списка жанров
    manga_genre = [[genre.text for genre in x.find_all('span', {'class': 'badge badge-light'})]
                    for x in div.find_all('div', {'class': 'html-popover-holder'})]
    manga_genre = [x for x in manga_genre if x != []]
    # print(*manga_genre, sep='\n\n')
    # print(title, chapters, image_orig_link, manga_genre, manga_description, manga_link, sep='\n')
    return title, chapters, image_orig_link, manga_genre, manga_description, manga_link


async def process_start_parsing(page: int = 0):
    # создание url страницы
    url: str = f'{URL_MANGA}/?offset={page * 30}#last-updates'
    # забираем страницу с сайта
    html = await process_download_html(url)
    title, chapters, image_orig_link, manga_genre, manga_description, manga_link = await _process_parsing_html(html)
    # print(title, chapters, image_orig_link, manga_genre, manga_description, manga_link, sep='\n\n')
    # Упаковываем
    data_tuple = zip(title, chapters, image_orig_link, manga_genre, manga_description, manga_link)
    return data_tuple


async def process_manga_add_parsing(url: str):
    html = await process_download_html(url)
    if html is not None:
        manga_link = url.replace(f'{URL_MANGA}', '')
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.find('span', {'class': 'name'})
        if name is not None:
            name = name.text
        image_orig_link = soup.find('div', {'class': 'subject-cover col-sm-5'}).find('img')
        if image_orig_link is not None:
            image_orig_link = image_orig_link['src']
        manga_genre = [genre.text for genre in soup.find_all('span', {'class': 'elem_genre'})]
        manga_description = soup.find('div', {'class': 'manga-description'})
        if manga_description is not None:
            manga_description = manga_description.text
        return name, None, image_orig_link, manga_genre, manga_description, manga_link
    else:
        return None

# asyncio.run(process_manga_add_parsing(f'{URL_MANGa}/skazaniia_o_demonah_i_bogah__A5664'))

# для отладки
# asyncio.run(process_start_parsing())
