# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
import datetime
from peewee import PrimaryKeyField, CharField, IntegerField, DateTimeField
from lib.DataBase import BaseModel


class User(BaseModel):
    id = PrimaryKeyField(null=False)
    full_name = CharField(max_length=100)
    cache_repeat = IntegerField(null=False, default=0)

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


def find_user(id):
    user = try_user(id)
    if not user:
        add_user(id, '')
        user = try_user(id)
    return user
