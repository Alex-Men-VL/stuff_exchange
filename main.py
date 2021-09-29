import logging
import os
from pathlib import Path
from textwrap import dedent

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import load_dotenv


load_dotenv()
Path('data').mkdir(exist_ok=True)

# Initialize bot and dispatcher
bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

# Configure logging
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def send_start_message(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    # TODO: добавление пользователя в JSON

    keyboard = types.ReplyKeyboardMarkup()
    add_stuff_button = types.KeyboardButton(text='Добавить вещь')
    keyboard.add(add_stuff_button)

    await message.answer(dedent('''\
        *Привет!* Я помогу тебе обменять что-то ненужное на очень нужное.\n
        Чтобы разместить вещь к обмену нажми на *Добавить вещь*.
        После этого тебе станут доступны вещи других пользователей.\n
        Нажми на *Найти вещь* и я пришлю тебе фотографии вещей для обмена.\n
        Понравилась вещь - жми *Обменяться*, нет - снова нажимай *Найти вещь*.\n
        Нажал *обменяться*? - если владельцу вещи понравится что-то из твоих
        вещей, то я пришлю контакты вам обоим.
        '''), reply_markup=keyboard, parse_mode='Markdown')


class AddStuff(StatesGroup):
    waiting_for_photo = State()
    waiting_for_description = State()


@dp.message_handler(Text(equals='Добавить вещь'), state='*')
async def add_stuff(message: types.Message):
    await message.answer('Отправьте фото вещи, которую хотите обменять')
    await AddStuff.waiting_for_photo.set()


@dp.message_handler(state=AddStuff.waiting_for_photo, content_types='photo')
async def get_stuff_photo(message: types.Message, state: FSMContext):
    if message.content_type != 'photo':
        await message.answer('Отправьте фото вашей вещи.')
        return

    photo_id = message.photo[-1].file_id
    # TODO: добавление id объявления пользователю
    photo_file = await bot.get_file(photo_id)
    await state.update_data(user_stuff_photo=photo_file)

    await AddStuff.waiting_for_description.set()
    await message.answer('Теперь введите описание.')


@dp.message_handler(state=AddStuff.waiting_for_description,
                    content_types=types.ContentTypes.TEXT)
async def get_stuff_description(message: types.Message, state: FSMContext):
    stuff = await state.get_data()

    print(f"\nИзображение: {stuff['user_stuff_photo']}"
          f"\nОписание: {message.text}")

    photo = stuff['user_stuff_photo']
    photo_name, photo_extension = os.path.splitext(photo.file_path)
    downloaded_photo = await bot.download_file(photo.file_path)

    src = f"data/{photo_name.split('/')[-1]}{photo_extension}"
    with open(src, 'wb') as file:
        file.write(downloaded_photo.getvalue())

    await message.answer('Объявление добавлено. Вы находитесь в главном меню.')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
