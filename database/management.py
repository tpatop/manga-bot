from sqlalchemy import desc, select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from . import models


user_attr = {
            'user_id': models.User.user_id,
            'all_target': models.User.all_target,
            'live_status': models.User.live_status
        }

update_attr = {
    'name': models.Update.name,
    'chapter_start': models.Update.chapter_start,
    'chapter_end': models.Update.chapter_end,
    'status': models.Update.status
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
                and_(*[user_attr[k] == v for k, v in change_dict.items()])
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
    async def create_or_update_updates(self, updates: list[models.Update]):
        async with self.session as session:
            session.add_all(updates)
            await session.commit()

    async def get_updates(self, filter: dict[str, str]):
        async with self.session as session:
            query = select(models.Update).filter(
                and_(*[update_attr[k] == v for k, v in filter.items()])
            )
            result = await session.execute(query)
            result = [upd[0] for upd in result.all() if upd]
            return result

    async def count_update(self):
        async with self.session as session:
            query = select(func.count()).select_from(models.Update)
            result = await session.execute(query)
            count = result.scalar()
            return count

    async def delete_updates(self, excess: int):
        Update = models.Update
        async with self.session as session:
            query = select(Update).order_by(Update.id.asc()).limit(excess)
            result = await session.execute(query)
            to_delete = result.scalars()
            for upd in to_delete:
                await session.delete(upd)
            await session.commit()

    async def get_unique_name_update(
        self, limit: int = None, updates: list[models.Update] = None
    ):
        async with self.session as session:
            if limit is not None:
                query = select(models.Update.name).distinct(). \
                        order_by(desc(models.Update.id)).limit(limit)
                result = await session.execute(query)
                result = [upd[0] for upd in result.all()]
            elif updates is not None:
                result = []
                for upd in updates:
                    if upd.name not in result:
                        result.append(upd.name)
            return result


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
