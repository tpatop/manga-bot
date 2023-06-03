from typing import Any, Dict, Awaitable, Callable
from aiogram import types
from database.management import UserRepo, DatabaseManagement
from aiogram import BaseMiddleware


class PassManagementMiddleware(BaseMiddleware):
    def __init__(self, database_management: DatabaseManagement):
        super().__init__()
        self.database_management = database_management

    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: dict):
        data["database_management"] = self.database_management
        return await handler(event, data)


async def user_in_database_middleware(
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        message: types.Message,  # == event: Message
        data: dict[str, Any],
):
    db_manegement = data['database_management']
    if message.text == '/start':
        user_repo: UserRepo = db_manegement.get_repo('UserRepo')
        user_id = message.from_user.id
        result = await user_repo.get_user(user_id)
        if not result:  # необходимо добавить пользователя в БД
            user_data = {
                'user_id': message.from_user.id,
                'username': message.from_user.username,
                'fullname': message.from_user.full_name,
                'update_date': message.date
            }
            await user_repo.create_user(user_data)
        else:
            print(f'Пользователя c id = {user_id} уже существует!')
    return await handler(message, data)
