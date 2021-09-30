from peewee import *

DB = SqliteDatabase('db.sqlite3')


class BaseModel(Model):
    class Meta:
        database = DB


class User(BaseModel):
    user_id = AutoField(column_name='id')
    telegram_id = IntegerField()


class Stuff(BaseModel):
    user = ForeignKeyField(User, backref='stuff')
    image_id = TextField(default='')
    image_path = TextField(default='')
    description = TextField(default='')


if __name__ == '__main__':
    DB.connect()
    DB.create_tables([User, Stuff])
