from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine


db_url = 'postgresql+asyncpg://user:12345@localhost:5432/partners_db'
engine = create_async_engine(db_url, echo=True)


async def init_db():
    """Асинхронное создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
