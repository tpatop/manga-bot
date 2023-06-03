from typing import Union

from sqlalchemy import select, insert, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from . import models


class BaseRepo:
    def __init__(self, session_maker):
        self._session_maker = session_maker

    @property
    def session(self) -> AsyncSession:
        session = self._session_maker()
        return session


class UserRepo(BaseRepo):
    async def create_user(self, user_data: dict) -> None:
        async with self.session as session:

            new_user = models.User(
                    user_id=user_data['user_id'],
                    username=user_data['username'],
                    fullname=user_data['fullname'],
                    update_date=user_data['update_date']
                )

            session.add(new_user)
            await session.commit()
        print(f'Добавлен пользователь c id = {user_data["user_id"]}!')

    async def get_user(self, user_id: int) -> bool:
        user_id = int(user_id)
        async with self.session as session:
            query = select(models.User).filter_by(user_id=user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()


class DescriptionRepo(BaseRepo):
    pass


class UpdateRepo(BaseRepo):
    pass


class DatabaseManagement:
    _repos = {
        'UserRepo': UserRepo,
        'DescriptionRepo': DescriptionRepo,
        'UpdateRepo': UpdateRepo
    }

    def __init__(self, session_maker) -> None:
        self._session_maker = session_maker

        for name, repo in self._repos.items():
            self._repos[name] = repo(session_maker)

    def get_user_repo(self) -> UserRepo:
        return UserRepo(self._session_maker)

    def get_description_repo(self) -> DescriptionRepo:
        return DescriptionRepo(self._session_maker)

    def get_update_repo(self) -> UpdateRepo:
        return UpdateRepo(self._session_maker)

    def get_repo(self, name):

        if name in self._repos:
            return self._repos[name]

        raise KeyError(name)
