import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from models import User, Stuff


class AddStuff(StatesGroup):
    waiting_for_photo = State()
    waiting_for_description = State()


async def add_stuff(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add('Главное меню')
    await message.answer('Отправьте фото вещи, которую хотите обменять',
                         reply_markup=keyboard)
    await AddStuff.waiting_for_photo.set()


async def load_stuff_photo(message: types.Message, state: FSMContext):
    if message.content_type != 'photo':
        await message.answer('Отправьте фото вашей вещи.')
        return

    photo_id = message.photo[-1].file_id
    
    load_dotenv()
    bot = Bot(token=os.getenv('TG_TOKEN'))

    photo_file = await bot.get_file(photo_id)
    photo_name, photo_extension = os.path.splitext(photo_file.file_path)
    downloaded_photo = await bot.download_file(photo_file.file_path)

    src = f"data/" \
          f"{message.from_user.id}/{photo_name.split('/')[-1]}{photo_extension}"
    with open(src, 'wb') as file:
        file.write(downloaded_photo.getvalue())

    await state.update_data(photo=photo_file)
    await state.update_data(photo_name=photo_name.split('/')[-1] +
                            photo_extension)
    
    await AddStuff.waiting_for_description.set()
    await message.answer('Теперь введите описание.')


async def get_stuff_description(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add('Добавить вещь')

    if len(os.listdir(f'data/{message.from_user.id}')):
        keyboard.add('Найти вещь')

    await state.update_data(stuff_desription=message.text)
    stuff = await state.get_data()

    user = User.get(User.telegram_id == message.from_user.id)
    Stuff.create(
        owner=user,
        image_id=stuff['photo']['file_id'],
        image_path = stuff['photo_name'],
        description = stuff['stuff_desription'],
    )

    print(f"\nИзображение: {stuff['photo']}"
          f"\nОписание: {stuff['stuff_desription']}")

    await message.answer('Объявление добавлено. Вы находитесь в главном '
                         'меню.', reply_markup=keyboard)
    await state.finish()


def register_handlers_stuff(dp: Dispatcher):
    dp.register_message_handler(add_stuff, Text(equals='Добавить вещь'),
                                state="*")
    dp.register_message_handler(load_stuff_photo,
                                state=AddStuff.waiting_for_photo,
                                content_types='photo')
    dp.register_message_handler(get_stuff_description,
                                state=AddStuff.waiting_for_description,
                                content_types=types.ContentTypes.TEXT)
