import os
from random import choice

import emoji
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile
from dotenv import load_dotenv
from models import User, LikedStuff, ViewedStuff

import db


def get_random_stuff(unseen_stuff):
    stuff = choice(unseen_stuff)
    stuff_photo = InputFile(
        f'data/{stuff.owner.telegram_id}/{stuff.image_path}'
    )
    return stuff_photo, stuff


async def send_match(bot, user_id, stuff):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    load_dotenv()
    bot = Bot(token=os.getenv('TG_TOKEN'))
    current_user = User.get(User.telegram_id == message.from_user.id)
    unseen_stuff = db.select_unseen_stuff(current_user)

    try:
        stuff_photo, stuff = get_random_stuff(unseen_stuff)
    except (IndexError, FileNotFoundError):
        keyboard.add('Главное меню')
        await message.answer('Новых объявлений нет.\nПопробуйте повторить '
                             'попытку позже.', reply_markup=keyboard)
    else:
        keyboard.add(emoji.emojize(':thumbs_up:'),
                     emoji.emojize(':thumbs_down:'))
        keyboard.add('Главное меню')
        await bot.send_photo(chat_id=message.from_user.id, photo=stuff_photo,
                             caption=stuff.description, reply_markup=keyboard)

        ViewedStuff.create(user=current_user, stuff=stuff)

        if message.text == emoji.emojize(':thumbs_up:'):
            print('Like')
            LikedStuff.create(user=current_user, stuff=stuff)
            stuff_liked_by_owner = db.select_stuff_owner_liked_stuff(
                current_user, stuff.owner
            )
            if stuff_liked_by_owner:
                print("Отправялем уведомление пользователям")
                # send_match(bot, message.from_user.id, stuff)
                # send_match(bot, stuff.owner.telegram_id, users_stuff)


def register_handlers_ads(dp: Dispatcher):
    dp.register_message_handler(find_stuff, Text(equals='Найти вещь'))
    dp.register_message_handler(find_stuff,
                                Text(equals=emoji.emojize(':thumbs_down:')))
    dp.register_message_handler(find_stuff,
                                Text(equals=emoji.emojize(':thumbs_up:')))
