import os
from random import choice

import emoji
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile
from dotenv import load_dotenv
from models import Stuff, User


def get_random_stuff(message):
    ads = Stuff.select()
    ad = choice([ad for ad in ads if (
        ad.owner.telegram_id != message.from_user.id
    )])  # добавить проверку, что нет лайка и дизлайка

    stuff_owner_id = ad.owner.telegram_id
    stuff_photo = InputFile(f'data/{stuff_owner_id}/{ad.image_path}')
    stuff_description = ad.description
    return stuff_owner_id, stuff_photo, stuff_description


async def find_stuff(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    like_button = types.KeyboardButton(emoji.emojize(':thumbs_up:'))
    dislike_button = types.KeyboardButton(emoji.emojize(':thumbs_down:'))
    keyboard.add(like_button, dislike_button)
    keyboard.add('Главное меню')

    load_dotenv()
    bot = Bot(token=os.getenv('TG_TOKEN'))

    stuff_owner_id, stuff_photo, stuff_description = get_random_stuff(message)
    await bot.send_photo(chat_id=message.from_user.id, photo=stuff_photo,
                         caption=stuff_description, reply_markup=keyboard)

    if message.text == emoji.emojize(':thumbs_up:'):
        print('Like')
        # добавляем like в бд к вещи
        # вызов функции для проверки взаимности лайка


def register_handlers_ads(dp: Dispatcher):
    dp.register_message_handler(find_stuff, Text(equals='Найти вещь'))
    dp.register_message_handler(find_stuff,
                                Text(equals=emoji.emojize(':thumbs_down:')))
    dp.register_message_handler(find_stuff,
                                Text(equals=emoji.emojize(':thumbs_up:')))
