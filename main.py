import asyncio
import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from handlers import request_hw
from handlers import start_comand
from db import BaseModel, create_async_engine, get_session_maker, proceed_schemas
from sqlalchemy.orm import sessionmaker
from middlewares.session_mdwr import DbSessionMiddleware

from db import User

from config_reader import config

logging.basicConfig(level=logging.INFO)

# Запуск процесса поллинга новых апдейтов
async def main():
    
    
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    postgres_url = URL.create(
        drivername="postgresql+asyncpg",
        username=config.db_user.get_secret_value(),
        port=config.db_port.get_secret_value(),
        host="localhost",
        database=config.db_name.get_secret_value(),
        password=config.db_password.get_secret_value()
    )

    async_engine = create_async_engine(postgres_url)
    await proceed_schemas(async_engine, BaseModel.metadata)

    #session_maker = get_session_maker(async_engine)
    

    dp.include_router(start_comand.router)
    mw = DbSessionMiddleware(async_engine)
    request_hw.router.message.outer_middleware(mw)
    dp.include_router(request_hw.router)



    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())