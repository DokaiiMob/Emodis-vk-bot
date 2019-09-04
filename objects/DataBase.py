# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from config import DB_USER, DB_NAME, DB_PASS, DB_HOST
from peewee import *
import peewee

class DataBase():
    dbhandle = MySQLDatabase(
        DB_NAME, user=DB_USER,
        password=DB_PASS,
        host=DB_HOST
    )

    def __init__(self):
        print("Init DataBase")
        self.get_db_handle()

    def get_db_handle(self):
        return self.dbhandle

    def open_connection(self):
        try:
            self.dbhandle.connect()
        except peewee.InternalError as px:
            print(str(px))

    def close_connection(self):
        self.dbhandle.close()


class BaseModel(Model):
    class Meta:
        database = DataBase().get_db_handle()
