from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    AsyncSession,
    create_async_engine
)
from sqlalchemy.orm import sessionmaker

from . import models

from .management import DatabaseManagement, UserRepo


async def init():
    url = "sqlite+aiosqlite:///bot.db"

    engine = create_async_engine(url, echo=False, pool_pre_ping=True)

    async with engine.begin() as conn:
        await conn.run_sync(models.METADATA.create_all)

    async_session_factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
    )
    async_session = async_scoped_session(async_session_factory,
                                         scopefunc=current_task)

    return async_session
