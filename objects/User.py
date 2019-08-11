# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
from peewee import *
from random import randint
import datetime
import peewee
import re
from objects.DataBase import *


class User(BaseModel):
    id = PrimaryKeyField(null=False)
    full_name = CharField(max_length=100)

    class Meta:
        db_table = "users"
        order_by = ('id',)


def add_user(id, full_name):
    row = User(
        id=id,
        full_name=full_name.strip(),
    )
    row.save(force_insert=True)


def try_user(id):
    try:
        return User.select().where(User.id == int(id)).get()
    except User.DoesNotExist:
        return False


def find_all_users():
    return User.select()


def find_user(id):
    exist = True
    try:
        user = User.select().where(User.id == id).get()
        return user
    except User.DoesNotExist:
        exist = False
    if not exist:
        add_user(id, " ")
        return User.select().where(User.id == id).get()
