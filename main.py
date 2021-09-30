import asyncio
import logging
import os
from pathlib import Path

from add_stuff import register_handlers_stuff
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from common import register_handlers_common
from dotenv import load_dotenv

from models import DB, User, Stuff


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

    await dp.start_polling(dp)

if __name__ == '__main__':
    DB.connect()
    DB.create_tables([User, Stuff])
    asyncio.run(main())
