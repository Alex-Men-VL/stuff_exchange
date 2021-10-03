from peewee import SqliteDatabase

from models import *


CATEGORIES = [
    'Транспорт',
    'Одежда, обувь',
    'Аксессуары и украшения',
    'Детская одежда и обувь',
    'Игрушки и детские вещи',
    'Бытовая техника',
    'Мебель и интерьерные вещи',
    'Кухонная утварь',
    'Продукты питания',
    'Ремонт и строительство',
    'Растения',
    'Электроника',
    'Спортивные вещи',
    'Творчество и хобби',
    'Коллекционные вещи',
]


def init_db():
    db = DB
    db.connect()
    db.create_tables([
        User,
        Category,
        Location,
        Stuff,
        LikedStuff,
        ViewedStuff,
    ])
    for category in CATEGORIES:
        Category.get_or_create(name=category)


def select_unseen_stuff(user, category):
    """
    Выбирает вещи, которые пользователь еще не смотрел.
    Вещи самого пользователя пропускаются.
    """
    return [
        stuff for stuff in Stuff.select() if
        (stuff.owner != user and
         stuff not in [viewed.stuff for viewed in user.viewed] and
         stuff.category.name == category)
    ]


def select_stuff_owner_liked_stuff(current_user, stuff_owner):
    """
    Выбирает вещи текущего пользователя, которые понравились владельцу
    лайкнутой вещи
    """
    return [
        like.stuff for like in stuff_owner.likes
        if like.stuff.owner == current_user
    ]


def select_unseen_categories(user):
    """
    Выбирает категории, в которых есть вещи, не просмотренные пользователем
    """
    return set([
        stuff.category.name for stuff in Stuff.select() if
        (stuff.owner != user and
         stuff not in [viewed.stuff for viewed in user.viewed])
    ])


if __name__ == '__main__':
    init_db()
