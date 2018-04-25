from column import Column,ForeignKeyColumn
from config import Config
from model import Model


def SqliteDatabase(name):
    Config.database=name


__all__=['Column','Config','SqliteDatabase','Model','ForeignKeyColumn']
