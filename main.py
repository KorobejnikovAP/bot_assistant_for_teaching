import asyncio
import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from aiogram import Bot, Dispatcher, types
from db import BaseModel, create_async_engine, get_session_maker, proceed_schemas
from middlewares.session_mdwr import DbSessionMiddleware

from handlers import routers
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
        host=config.db_host.get_secret_value(),
        database=config.db_name.get_secret_value(),
        password=config.db_password.get_secret_value()
    )

    #создание бд и пула сессий
    async_engine = create_async_engine(postgres_url)
    #Делегировано alembic
    #await proceed_schemas(async_engine, BaseModel.metadata)
    session_maker = get_session_maker(async_engine)
    
    #подключение мидлварей и роутеров 
    mw = DbSessionMiddleware(session_maker)
    for router in routers:
        router.message.outer_middleware(mw)
        dp.include_router(router)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())