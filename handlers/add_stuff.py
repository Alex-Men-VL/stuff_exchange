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
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Главное меню')
    await message.answer('Выберите категорию:\n')

    text = ''
    for number, category in enumerate(db.CATEGORIES, start=1):
        text += f'{number}. {category}\n'

    await message.answer(text, reply_markup=keyboard)
    await AddStuff.waiting_for_category.set()


async def get_stuff_category(message: types.Message, state: FSMContext):
    if message.text not in [str(acceptable_number) for acceptable_number in
                        range(1, len(db.CATEGORIES) + 1)]:
        await message.answer('Неверный номер категории')
        return
    await state.update_data(category=message.text)

    await message.answer('Отправьте фото вещи')
    await AddStuff.waiting_for_photo.set()


async def load_stuff_photo(message: types.Message, state: FSMContext):
    if message.content_type != 'photo':
        await message.answer('Отправьте фото вашей вещи.')
        return

    photo_id = message.photo[-1].file_id
    
    load_dotenv()
    bot = Bot(token=os.getenv('TG_TOKEN'))

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
    await message.answer('Теперь введите описание.')


async def get_stuff_description(message: types.Message, state: FSMContext):
    if message.content_type != 'text':
        await message.answer('Введите описание')
        return

    await state.update_data(stuff_description=message.text)

    await message.answer('Введите адрес, где находится эта вещь.')
    await AddStuff.waiting_for_location.set()


async def get_location(message: types.Message, state: FSMContext):
    location = Location.create(address=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Добавить вещь')

    if len(os.listdir(f'data/{message.from_user.id}')):
        keyboard.add('Найти вещь')

    stuff = await state.get_data()

    try:
        category = Category.get(name=stuff['category'])
    except Category.DoesNotExist:
        category = Category.create(name=stuff['category'])

    user = User.get(User.telegram_id == message.from_user.id)
    Stuff.create(
        owner=user,
        image_id=stuff['photo']['file_id'],
        image_path=stuff['photo_name'],
        description=stuff['stuff_description'],
        category=category,
        location=location
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
