from typing import Any, Dict, Awaitable, Callable
from aiogram.types import Message, ChatMemberUpdated
from database.db_users import check_user_in_db, add_user_in_db


async def user_in_database_middleware(
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,  # == event: Message
        data: dict[str, Any]):
    if message.text == '/start':
        user_id = message.from_user.id
        result = await check_user_in_db(user_id)
        if not result:  # необходимо добавить пользователя в БД
            user_data = {
                'user_id': message.from_user.id,
                'username': message.from_user.username,
                'fullname': message.from_user.full_name,
                'update_date': message.date
            }
            await add_user_in_db(user_data)
        else:
            print(f'Пользователя c id = {user_id} уже существует!')
    return await handler(message, data)


# async def check_bot_blocked_middleware(
#         update: ChatMemberUpdated,
#         message: Message,
#         data: dict):
#     if update.new_chat_member.id == data["self"].id and update.new_chat_member.is_kicked():
#         print('!!!!FUCKING KILL THIS USER!!!!!')