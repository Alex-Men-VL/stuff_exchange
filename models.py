from peewee import *

DB = SqliteDatabase('db.sqlite3', pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = DB


class User(BaseModel):
    telegram_id = IntegerField()
    name = TextField(default='')


class Category(BaseModel):
    name = TextField(unique=True)


class Location(BaseModel):
    address = TextField()


class Stuff(BaseModel):
    owner = ForeignKeyField(User, backref='stuff')
    image_id = TextField(default='')
    image_path = TextField(default='')
    description = TextField(default='')
    category = ForeignKeyField(Category, backref='stuff', null=True)
    location = TextField(default='')


class LikedStuff(BaseModel):
    user = ForeignKeyField(User, backref='likes')
    stuff = ForeignKeyField(Stuff, backref='likes')


class ViewedStuff(BaseModel):
    user = ForeignKeyField(User, backref='viewed')
    stuff = ForeignKeyField(Stuff, backref='viewed')


if __name__ == '__main__':
    DB.connect()
    DB.create_tables([
        User,
        Category,
        Location,
        Stuff,
        LikedStuff,
        ViewedStuff,
    ])
