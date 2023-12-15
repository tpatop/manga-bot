import logging
from fastapi import HTTPException, status

from src.db.session import async_session
from src.db.models import Manga, UpdateManga
from src.api.schemas.schemas import MangaUpdate
from src.db.repository import MangaRepo, UpdateMangaRepo


class MangaServices:
    '''TODO:
        Необходимо продумать логику, по сути это должна быть точка соприкосновения БД и эндпоинтов
    '''
    async def get_one_manga(self, data: MangaUpdate):
        logging.info('MangaServices - get_one_manga')
        async with async_session() as session:
            mr: MangaRepo = MangaRepo(session)
            result = await mr.get_one_on_url(url_id=data.url_id, link=data.link)
            logging.info(f'{result}')
            return result

    async def add_one_manga(self, data: MangaUpdate):
        logging.info('MangaServices - add_one_manga')
        async with async_session() as session:
            mr: MangaRepo = MangaRepo(session)
            manga = Manga(
                url_id=data.url_id,
                link=data.link,
                name=data.name
            )
            await mr.create_one(manga)

    async def get_one_update(self, update: UpdateManga):
        logging.info('MangaServices - get_one_update')
        async with async_session() as session:
            umr: UpdateMangaRepo = UpdateMangaRepo(session)
            result = await umr.get_one(update)
            logging.info(f'{result}')
            return result

    async def add_one_update(self, update: UpdateManga):
        logging.info('MangaServices - add_one_update')
        async with async_session() as session:
            umr: UpdateMangaRepo = UpdateMangaRepo(session)
            await umr.create_one(update)

    async def process_all_updates_data(self, data_list: list[MangaUpdate]):
        for data in data_list:
            manga = await self.get_one_manga(data)
            if not manga:
                await self.add_one_manga(data)
                manga = await self.get_one_manga(data)
            update = UpdateManga(
                manga_id=manga.manga_id,
                chapters=data.chapters
            )
            result = await self.get_one_update(update)
            if result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Duplicates detected'
                )
            await self.add_one_update(update)

            # Возможно, неплохим решением будет обычное добавление, а проверки на этапе парсера
            # по крайней мере на повторы обновлений