# import logging
# from fastapi import HTTPException, status

from src.db.session import async_session
from src.db.models import Users
from src.db.repository import UserRepo
# from src.api.schemas.schemas import UserPydanticModel


class UserServices:

    async def add_one_user(self, user_id: int):
        user = Users(user_id=user_id)
        async with async_session() as session:
            ur: UserRepo = UserRepo(session)
            user_in_db = await ur.get_one(user)

            if user_in_db is None or not user_in_db.status:
                await ur.create_one(user)
