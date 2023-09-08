from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: sessionmaker):
        super().__init__()
        self.session_maker = session_maker

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        #async with self.session_pool() as session:
        data["session_maker"] = self.session_maker
        return await handler(event, data)