import logging
from typing import Annotated, Union, List
from fastapi import APIRouter, Depends

from src.api.schemas.schemas import UpdateManga


router = APIRouter()


@router.get('/updates')
async def process_get_updates():
    '''Для отслеживания выхода обновлений со стороны бота'''
    pass


@router.post('/add_update')
async def process_add_updates(updates: list[UpdateManga]):
    '''Для добавления новых обновлений манги со стороны парсера'''
    logging.info(f'process_add_updates')

    return
