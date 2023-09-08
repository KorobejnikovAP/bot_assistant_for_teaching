from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, async_engine: AsyncEngine):
        super().__init__()
        self.acync_engine = async_engine

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        #async with self.session_pool() as session:
        data["db_engine"] = self.acync_engine
        return await handler(event, data)