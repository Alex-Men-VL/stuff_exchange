import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

import db
from models import Stuff, User, Location, Category


class AddStuff(StatesGroup):
    waiting_for_category = State()
    waiting_for_photo = State()
    waiting_for_description = State()
    waiting_for_location = State()


async def add_stuff(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)

    for category_number in range(0, len(db.CATEGORIES) - 1, 2):
        keyboard.add(db.CATEGORIES[category_number],
                     db.CATEGORIES[category_number + 1])
    keyboard.add('Главное меню')
    await message.answer('Выберите категорию', reply_markup=keyboard)
    await AddStuff.waiting_for_category.set()


async def get_stuff_category(message: types.Message, state: FSMContext):
    category = message.text
    if category not in db.CATEGORIES:
        await message.answer('Неверная категория')
        return
    await state.update_data(category=category)

    await message.answer('Отправьте фото вещи')
    await AddStuff.waiting_for_photo.set()


async def load_stuff_photo(message: types.Message, state: FSMContext):
    if message.content_type != 'photo':
        await message.answer('Отправьте фото вашей вещи.')
        return

    load_dotenv()
    bot = Bot(token=os.getenv('TG_TOKEN'))

    photo_id = message.photo[-1].file_id
    photo_file = await bot.get_file(photo_id)
    photo_path, photo_extension = os.path.splitext(photo_file.file_path)

    downloaded_photo = await bot.download_file(photo_file.file_path)
    photo_name = photo_path.split('/')[-1] + photo_extension

    src = f"data/{message.from_user.id}/{photo_name}"
    with open(src, 'wb') as file:
        file.write(downloaded_photo.getvalue())

    await state.update_data(photo=photo_file)
    await state.update_data(photo_name=photo_name)
    
    await AddStuff.waiting_for_description.set()
    await message.answer('Введите описание.')


async def get_stuff_description(message: types.Message, state: FSMContext):
    if message.content_type != 'text':
        await message.answer('Введите описание')
        return

    await state.update_data(stuff_description=message.text)

    await message.answer('Введите адрес, где находится эта вещь.')
    await AddStuff.waiting_for_location.set()


async def get_location(message: types.Message, state: FSMContext):
    # location = Location.create(address=message.text)
    await state.update_data(location=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if len(os.listdir(f'data/{message.from_user.id}')):
        keyboard.add('Добавить вещь', 'Найти вещь')
    else:
        keyboard.add('Добавить вещь')

    stuff = await state.get_data()

    # category = Category.get(Category.name == stuff['category'])
    category = Category.get(Category.name == stuff['category'])
    user = User.get(User.telegram_id == message.from_user.id)
    Stuff.create(
        owner=user,
        image_id=stuff['photo']['file_id'],
        image_path=stuff['photo_name'],
        description=stuff['stuff_description'],
        category=category,
        location=stuff['location']
    )

    await message.answer('Объявление добавлено. Вы находитесь в главном '
                         'меню.', reply_markup=keyboard)
    await state.finish()


def register_handlers_stuff(dp: Dispatcher):
    dp.register_message_handler(add_stuff, Text(equals='Добавить вещь'),
                                state="*")
    dp.register_message_handler(get_stuff_category,
                                state=AddStuff.waiting_for_category,
                                content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(load_stuff_photo,
                                state=AddStuff.waiting_for_photo,
                                content_types='photo')
    dp.register_message_handler(get_stuff_description,
                                state=AddStuff.waiting_for_description,
                                content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(get_location,
                                state=AddStuff.waiting_for_location)
