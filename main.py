import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from handlers.add_stuff import register_handlers_stuff
from handlers.common import register_handlers_common
from handlers.find_stuff import register_handlers_ads

from models import DB, User, Stuff, UserLikes, UserViewed


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    load_dotenv()
    Path('data').mkdir(exist_ok=True)

    bot = Bot(token=os.getenv('TG_TOKEN'))
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_common(dp)
    register_handlers_stuff(dp)
    register_handlers_ads(dp)

    await dp.start_polling(dp)

if __name__ == '__main__':
    DB.connect()
    DB.create_tables([User, Stuff, UserLikes, UserViewed])
    asyncio.run(main())
