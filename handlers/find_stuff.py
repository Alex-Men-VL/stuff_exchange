import os

import emoji
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile
from dotenv import load_dotenv


def generate_ad(message):
    # ad = достать из бд рандомное объявление
    stuff_owner_id = message.from_user.id  # заменить на id из базы, хотя можно и не заменять
    stuff_photo = InputFile('data/154383987/file_13.jpg')  # заменить
    stuff_description = 'Котейка'  # заменить
    return stuff_owner_id, stuff_photo, stuff_description


async def find_stuff(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    like_button = types.KeyboardButton(emoji.emojize(':thumbs_up:'))
    dislike_button = types.KeyboardButton(emoji.emojize(':thumbs_down:'))
    keyboard.add('Главное меню')
    keyboard.add(like_button, dislike_button)

    load_dotenv()
    bot = Bot(token=os.getenv('TG_TOKEN'))

    stuff_owner_id, stuff_photo, stuff_description = generate_ad(message)
    await bot.send_photo(chat_id=stuff_owner_id, photo=stuff_photo,
                         caption=stuff_description, reply_markup=keyboard)

    if message.text == emoji.emojize(':thumbs_up:'):
        print('Like')


def register_handlers_ads(dp: Dispatcher):
    dp.register_message_handler(find_stuff, Text(equals='Найти вещь'))
    dp.register_message_handler(find_stuff,
                                Text(equals=emoji.emojize(':thumbs_down:')))
    dp.register_message_handler(find_stuff,
                                Text(equals=emoji.emojize(':thumbs_up:')))
