import os
from random import choice

import emoji
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile
from dotenv import load_dotenv
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import db
from models import LikedStuff, User, ViewedStuff, Stuff, Category


class FindStuff(StatesGroup):
    waiting_for_category = State()
    waiting_for_rate = State()
    waiting_for_continue = State()


def get_random_stuff(unseen_stuff):
    stuff = choice(unseen_stuff)
    stuff_photo = InputFile(
        f'data/{stuff.owner.telegram_id}/{stuff.image_path}'
    )
    return stuff_photo, stuff


async def send_match(bot, user, stuff_bunch):
    user_id = user.telegram_id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Главное меню')
    await bot.send_photo(chat_id=user_id, photo=InputFile('media/match.png'),
                         reply_markup=keyboard)
    for stuff in stuff_bunch:
        stuff_owner_id = stuff.owner.telegram_id
        stuff_photo = InputFile(f'data/{stuff_owner_id}/{stuff.image_path}')
        stuff_location = stuff.location if stuff.location else 'не указано'
        stuff_details = (
            f'Описание: {stuff.description}\n'
            f'Категория: {stuff.category.name}\n'
            f'Место нахождения: {stuff_location}\n'
        )
        await bot.send_photo(chat_id=user_id, photo=stuff_photo,
                             caption=stuff_details)

    await bot.send_message(
        chat_id=user_id,
        text=(
            f'Пользователь @{stuff.owner.name} лайкнул вашу вещь!\n'
            f'Вы можете обменяться. '
            f'Выше список вещей, которые вам понравились.'
        )
    )


def get_categories_keyboard(available_categories):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if len(available_categories) == 1:
        keyboard.add(available_categories[0])
    elif len(available_categories) == 0:
        return False
    elif len(available_categories) % 2 == 0:
        for category_number in range(0, len(available_categories) - 1, 2):
            keyboard.add(available_categories[category_number],
                         available_categories[category_number + 1])
    else:
        for category_number in range(0, len(available_categories) - 2, 2):
            keyboard.add(available_categories[category_number],
                         available_categories[category_number + 1])
        keyboard.add(available_categories[-1])
    keyboard.add('Главное меню')
    return keyboard


async def get_category(message: types.Message, state: FSMContext):
    user = User.get(User.telegram_id == message.from_user.id)

    available_categories = list(db.select_unseen_categories(user))

    keyboard = get_categories_keyboard(available_categories)
    if not keyboard:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Главное меню')
        await message.answer('Все объявления просмотренны. Повторите попытку '
                             'позже.', reply_markup=keyboard)
        return

    await message.answer('Выберите категорию.',
                         reply_markup=keyboard)
    await state.finish()
    await FindStuff.waiting_for_category.set()


async def show_stuff(message: types.Message, state: FSMContext):
    try:
        category = (await state.get_data())['category']
    except KeyError:
        category = message.text

    if category not in db.CATEGORIES:
        await message.answer('Неверная категория')
        return

    await state.update_data(category=category)

    current_user = User.get(User.telegram_id == message.from_user.id)
    unseen_stuff = db.select_unseen_stuff(current_user, category)

    await state.update_data(current_user_id=current_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    try:
        stuff_photo, stuff = get_random_stuff(unseen_stuff)
    except (IndexError, FileNotFoundError):
        await state.finish()
        keyboard.add('Главное меню', 'Сменить категорию')
        await message.answer('Новых объявлений нет.\nПопробуйте изменить '
                             'категорию.',
                             reply_markup=keyboard)
        return

    keyboard.add(emoji.emojize(':thumbs_up:'), emoji.emojize(':thumbs_down:'))
    keyboard.add('Главное меню')
    photo_caption = f'Категория: {category}\n' \
                    f'Описание: {stuff.description}\n' \
                    f'Место нахождения: {stuff.location}'

    load_dotenv()
    bot = Bot(token=os.getenv('TG_TOKEN'))

    await bot.send_photo(chat_id=message.from_user.id, photo=stuff_photo,
                         caption=photo_caption, reply_markup=keyboard)

    ViewedStuff.create(user=current_user, stuff=stuff)

    await state.update_data(stuff_id=stuff.id)
    await FindStuff.waiting_for_rate.set()


async def rate_stuff(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Продолжить в этой категории', 'Сменить категорию')
    keyboard.add('Главное меню')

    await message.answer('Спасибо за оценку!', reply_markup=keyboard)

    if message.text == emoji.emojize(':thumbs_up:'):
        liked_stuff = await state.get_data()
        stuff = Stuff[liked_stuff['stuff_id']]
        current_user = User[liked_stuff['current_user_id']]

        LikedStuff.create(user=current_user,
                          stuff=stuff)
        stuffs_liked_by_owner = db.select_stuff_owner_liked_stuff(
            current_user,
            stuff.owner
        )
        if stuffs_liked_by_owner:
            load_dotenv()
            bot = Bot(token=os.getenv('TG_TOKEN'))

            await send_match(bot, current_user, [stuff])
            await send_match(bot, stuff.owner, stuffs_liked_by_owner)

    await FindStuff.waiting_for_continue.set()


def register_handlers_ads(dp: Dispatcher):
    dp.register_message_handler(get_category,
                                Text(equals='Найти вещь'),
                                state='*')
    dp.register_message_handler(get_category,
                                Text(equals='Сменить категорию'),
                                state='*')

    dp.register_message_handler(show_stuff,
                                state=FindStuff.waiting_for_category)
    dp.register_message_handler(show_stuff,
                                Text(equals='Продолжить в этой категории'),
                                state=FindStuff.waiting_for_continue)

    dp.register_message_handler(rate_stuff,
                                Text(equals=emoji.emojize(':thumbs_down:')),
                                state=FindStuff.waiting_for_rate)
    dp.register_message_handler(rate_stuff,
                                Text(equals=emoji.emojize(':thumbs_up:')),
                                state=FindStuff.waiting_for_rate)
