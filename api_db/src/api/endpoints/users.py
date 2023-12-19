import logging
from typing import Annotated, Union, List
from fastapi import APIRouter, Depends

from src.api.schemas.schemas import UserPydanticModel
from src.services.user_services import UserServices


router = APIRouter()


@router.post('/registration')
async def process_add_user(user_id: int):
    '''Для добавления нового пользователя со стороны бота'''

    us: UserServices = UserServices()
    await us.add_one_user(user_id)
