import os
from pathlib import Path
from textwrap import dedent

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile
from dotenv import load_dotenv

from models import User


async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    Path(f'data/{user_id}').mkdir(exist_ok=True)
    try:
        user = User.get(User.telegram_id == message.from_user.id)
    except User.DoesNotExist:
        user = User.create(telegram_id=message.from_user.id, name=user_name)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)
    keyboard.add('Добавить вещь')

    await message.answer(dedent('''\
        *Привет!* Я помогу тебе обменять что-то ненужное на очень нужное.
        
        Чтобы разместить вещь к обмену нажми на *Добавить вещь*.
        После этого тебе станут доступны вещи других пользователей.
        
        Нажми на *Найти вещь* и я пришлю тебе фотографии вещей определенной 
        категории для обмена.
        
        Понравилась вещь - жми *Лайк*, нет - жми *Дизлайк*.
        Нажал *Лайк*? - если владельцу вещи понравится что-то из твоих 
        вещей, то я пришлю контакты вам обоим.
        
        Нажал не на ту кнопку? - жми на кнопку *Главное меню*
        Возникли трудности? - напиши *помощь*
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

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                             one_time_keyboard=True)

        if len(os.listdir(f'data/{message.from_user.id}')):
            keyboard.add('Добавить вещь', 'Найти вещь')
        else:
            keyboard.add('Добавить вещь')

        await message.answer("Вы перемещены на главный экран",
                             reply_markup=keyboard)


async def cmd_help(message: types.Message):
    help_text = 'Пожалуйста, воспользуйтесь кнопками в нижнем меню. Если они ' \
                'у вас не отображаются, просто нажмите на эту кнопку в поле ' \
                'ввода.\n\nЕсли вы совершили ошибочное действие и хотите его ' \
                'отменить, нажмите на кнопку Главное меню'
    load_dotenv()
    bot = Bot(token=os.getenv('TG_TOKEN'))
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=InputFile('media/help.png'),
                         caption=help_text)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start")
    dp.register_message_handler(cmd_cancel, Text(equals='Главное меню'),
                                state='*')
    dp.register_message_handler(cmd_help, Text(equals='помощь'))
    dp.register_message_handler(cmd_help, Text(equals='Помощь'))
