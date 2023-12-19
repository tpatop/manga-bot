from abc import ABC, abstractclassmethod
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from .models import Manga, UpdateManga, Users


class Basic(ABC):
    def __init__(self, session_maker):
        self._session_maker = session_maker

    @property
    def session(self) -> AsyncSession:
        session = self._session_maker
        return session

    @abstractclassmethod
    async def create_one(self):
        ...

    @abstractclassmethod
    async def get_one(self):
        ...

    @abstractclassmethod
    async def update_one(self):
        ...

    @abstractclassmethod
    async def delete_one(self):
        ...


class MangaRepo(Basic):

    async def get_one_on_url(self, url_id: int, link: str):
        async with self.session as session:
            query = select(Manga).filter_by(url_id=url_id, link=link)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_one(self, manga_id: int):
        async with self.session as session:
            query = select(Manga).filter_by(manga_id=manga_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def create_one(self, manga: Manga):
        async with self.session as session:
            session.add(manga)
            try:
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise exc

    async def update_one(self):
        pass

    async def delete_one(self, manga: Manga):
        async with self.session as session:
            await session.delete(manga)
            try:
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise exc


class UpdateMangaRepo(Basic):

    async def get_one(self, update: UpdateManga):
        async with self.session as session:
            query = select(UpdateManga).filter_by(
                manga_id=update.manga_id,
                chapters=update.chapters
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def create_one(self, update_manga: UpdateManga):
        async with self.session as session:
            session.add(update_manga)
            try:
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise exc

    async def update_one(self):
        pass

    async def delete_one(self):
        pass


class UserRepo(Basic):

    async def create_one(self, user: Users):
        async with self.session as session:
            session.add(user)
            try:
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise exc

    async def get_one(self, user: Users):
        async with self.session as session:
            query = select(Users).filter_by(
                user_id=user.user_id
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def update_one(self):
        pass

    async def delete_one(self):
        pass
