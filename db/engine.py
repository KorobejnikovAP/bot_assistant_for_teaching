from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

def create_async_engine(url: URL and str) -> AsyncEngine:
    return _create_async_engine(url=url, echo=True)

def get_session_maker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, class_=AsyncSession) 