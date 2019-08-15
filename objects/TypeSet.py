# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
from peewee import PrimaryKeyField, TextField
from objects.DataBase import BaseModel


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
