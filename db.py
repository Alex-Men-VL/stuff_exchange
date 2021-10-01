from peewee import SqliteDatabase

import models


CATEGORIES = [
    {'name': 'транспорт'},
    {'name': 'одежда, обувь'},
    {'name': 'аксессуары и украшения'},
    {'name': 'детская одежда и обувь'},
    {'name': 'игрушки и детские вещи'},
    {'name': 'бытовая техника'},
    {'name': 'мебель и интерьерные вещи'},
    {'name': 'кухонная утварь'},
    {'name': 'продукты питания'},
    {'name': 'ремонт и строительство'},
    {'name': 'растения'},
    {'name': 'электроника'},
    {'name': 'спортивные вещи'},
    {'name': 'творчество и хобби'},
    {'name': 'коллекционные вещи'},
]


def init_db():
    db = models.DB
    db.connect()
    db.create_tables([
        models.User,
        models.Category,
        models.Location,
        models.Stuff,
        models.LikedStuff,
        models.ViewedStuff,
    ])
    models.Category.insert_many(CATEGORIES).execute()


if __name__ == '__main__':
    init_db()
