import os
from random import choice

import emoji
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile
from dotenv import load_dotenv
from models import Stuff, User


def get_random_stuff(message):
    stuffs = Stuff.select()
    stuff = choice([stuff for stuff in stuffs if (
            stuff.owner.telegram_id != message.from_user.id
    )])  # добавить проверку, что нет лайка и дизлайка

    stuff_owner_id = stuff.owner.telegram_id
    stuff_photo = InputFile(f'data/{stuff_owner_id}/{stuff.image_path}')
    return stuff_owner_id, stuff_photo, stuff


async def send_match(bot, user_id, stuff):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add('Главное меню')
    await bot.send_photo(chat_id=user_id, photo='media/match.png',
                         reply_markup=keyboard)
    stuff_owner_id = stuff.owner.telegram_id
    stuff_photo = InputFile(f'data/{stuff_owner_id}/{stuff.image_path}')
    await bot.send_photo(chat_id=user_id, photo=stuff_photo,
                         caption=stuff.description)

    await bot.send_message(chat_id=user_id,
                           text='Ссылка на пользователя: tg://user?id'
                                f'={stuff_owner_id}\n')


async def find_stuff(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    like_button = types.KeyboardButton(emoji.emojize(':thumbs_up:'))
    dislike_button = types.KeyboardButton(emoji.emojize(':thumbs_down:'))
    keyboard.add(like_button, dislike_button)
    keyboard.add('Главное меню')

    load_dotenv()
    bot = Bot(token=os.getenv('TG_TOKEN'))

    stuff_owner_id, stuff_photo, stuff = get_random_stuff(message)
    await bot.send_photo(chat_id=message.from_user.id, photo=stuff_photo,
                         caption=stuff.description, reply_markup=keyboard)

    if message.text == emoji.emojize(':thumbs_up:'):
        # добавляем like в бд к вещи
        print('Like')
        ''' Проверка взаимности лайка
        try:
            users_stuff = вещь пользователя (меня), которая понравилась тебе
            send_match(bot, message.from_user.id, stuff)
            send_match(bot, stuff_owner_id, users_stuff)
        '''


def register_handlers_ads(dp: Dispatcher):
    dp.register_message_handler(find_stuff, Text(equals='Найти вещь'))
    dp.register_message_handler(find_stuff,
                                Text(equals=emoji.emojize(':thumbs_down:')))
    dp.register_message_handler(find_stuff,
                                Text(equals=emoji.emojize(':thumbs_up:')))
