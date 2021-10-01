import os
from pathlib import Path
from textwrap import dedent

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from models import User


async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    Path(f'data/{user_id}').mkdir(exist_ok=True)
    try:
        user = User.get(User.telegram_id == message.from_user.id)
    except User.DoesNotExist:
        user = User.create(telegram_id=message.from_user.id, name=user_name)

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    keyboard.add('Добавить вещь')

    await message.answer(dedent('''\
        *Привет!* Я помогу тебе обменять что-то ненужное на очень нужное.\n
        Чтобы разместить вещь к обмену нажми на *Добавить вещь*.
        После этого тебе станут доступны вещи других пользователей.\n
        Нажми на *Найти вещь* и я пришлю тебе фотографии вещей для обмена.\n
        Понравилась вещь - жми *Обменяться*, нет - снова нажимай *Найти вещь*.\n
        Нажал *обменяться*? - если владельцу вещи понравится что-то из твоих
        вещей, то я пришлю контакты вам обоим.
        '''), reply_markup=keyboard, parse_mode='Markdown')


async def cmd_cancel(message: types.Message, state: FSMContext):
    try:
        stuff = await state.get_data()
        photo = f"data/{message.from_user.id}/{stuff['photo_name']}"
        os.remove(photo)
    except KeyError:
        pass
    finally:
        await state.finish()

        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard.add('Добавить вещь')
        if len(os.listdir(f'data/{message.from_user.id}')):
            keyboard.add('Найти вещь')

        await message.answer("Вы перемещены на главный экран",
                             reply_markup=keyboard)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start")
    dp.register_message_handler(cmd_cancel, Text(equals='Главное меню'),
                                state='*')
