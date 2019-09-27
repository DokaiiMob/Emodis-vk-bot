
# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from config import DB_USER, DB_NAME, DB_PASS, DB_HOST
from peewee import *
import peewee
from lib.DataBase import DataBase


class BaseModel(Model):
    class Meta:
        database = DataBase().get_db_handle()
