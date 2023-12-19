import logging

from typing import Any, Dict, Awaitable, Callable
from aiogram import types

from src.services.requests import UserRequests


async def user_in_database_middleware(
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        message: types.Message,  # == event: Message
        data: dict[str, Any],
):
    if message.text == '/start':
        ur: UserRequests = UserRequests()
        user_id = message.from_user.id

        await ur.requests_post_user_data(user_id)

        logging.info('middleware - добавление пользователя в БД')
    return await handler(message, data)
