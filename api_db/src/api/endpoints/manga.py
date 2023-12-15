import logging
from typing import Annotated, Union, List
from fastapi import APIRouter, Depends

from src.api.schemas.schemas import MangaUpdate
from src.services.manga_services import MangaServices


router = APIRouter()


@router.get('/updates')
async def process_get_updates():
    '''Для отслеживания выхода обновлений со стороны бота'''
    pass


@router.post('/add_updates')
async def process_add_updates(updates: list[MangaUpdate]):
    '''Для добавления новых обновлений манги со стороны парсера'''
    logging.info('process_add_updates')

    ms = MangaServices()
    await ms.process_all_updates_data(updates)
