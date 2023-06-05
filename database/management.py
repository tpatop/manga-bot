from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from . import models


attribute = {
            'user_id': models.User.user_id,
            'all_target': models.User.all_target,
            'live_status': models.User.live_status
        }


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

    async def update_user(self, user: models.User):
        async with self.session as session:
            query = update(models.User).where(
                models.User.user_id == user.user_id
            ).values(
                username=user.username,
                fullname=user.fullname,
                target=user.target,
                all_target=user.all_target,
                live_status=user.live_status
            )
            await session.execute(query)
            await session.commit()

    async def get_users_list(self, change_dict: dict[str, str]):
        async with self.session as session:
            query = select(models.User).filter(
                and_(*[attribute[k] == v for k, v in change_dict.items()])
            )
            result = await session.execute(query)
            result = [user[0] for user in result.all() if user]
            return result


class DescriptionRepo(BaseRepo):
    async def create_description(self, description: dict) -> None:
        async with self.session as session:
            new_description = models.Description(
                name=description['name'],
                hash_name=description['hash_name'],
                image=description['image'],
                genre=description['genre'],
                description=description['description'],
                link=description['link']
                )
            session.add(new_description)
            await session.commit()

    async def get_description(self, hash_name: str):
        async with self.session as session:
            query = select(models.Description).filter_by(hash_name=hash_name)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def update_user_in_description(self, descr: models.Description):
        async with self.session as session:
            query = update(models.Description).where(
                models.Description.name == descr.name
            ).values(
                users=descr.users
            )
            await session.execute(query)
            await session.commit()


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
