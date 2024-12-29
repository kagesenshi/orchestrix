from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated
from .env import env

metadata = MetaData()

def db_engine():
    engine = create_async_engine(env.db_url)
    return engine

async def _db_session_dependency():
    async with AsyncSession(db_engine()) as session:
        yield session
        await session.commit()

DbSession = Annotated[AsyncSession, Depends(_db_session_dependency)]