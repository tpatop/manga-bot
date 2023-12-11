from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)


url = "sqlite+aiosqlite:///bot.db"
async_engine = create_async_engine(url, echo=False, pool_pre_ping=True)

async_session = async_sessionmaker(
    async_engine, autocommit=False, expire_on_commit=False,
    class_=AsyncSession, autoflush=False
)
