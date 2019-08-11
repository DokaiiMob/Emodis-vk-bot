# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from peewee import *
from random import randint
import datetime
import peewee
import re
from objects.DataBase import *


class TypeSet(BaseModel):
    id = PrimaryKeyField(null=False)
    title = TextField()
    default_val = TextField()

    class Meta:
        db_table = "type_set"
        order_by = ('id',)


def find_all_type_set():
    types = []
    for _type in TypeSet.select():
        types.append({
            'id': _type.id,
            'val': '',
            'default_val': _type.default_val,
        })
    return types


def get_null_settings(id_chat):
    null_settings = []
    for s in TypeSet.select(TypeSet.id, TypeSet.default_val, Settings.val.alias('title')).join(Settings, JOIN.LEFT_OUTER, Settings.id_type == TypeSet.id).where(TypeSet.id.not_in(Settings.select(Settings.id_type).where(Settings.id_chat == id_chat))):
        null_settings.append({
            'id': s.id,
            'default_val': s.default_val
        })
    return null_settings
