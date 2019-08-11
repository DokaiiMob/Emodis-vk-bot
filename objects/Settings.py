# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
from peewee import *
from random import randint
import datetime
import peewee
import re
from objects.DataBase import *
from objects.TypeSet import *
from objects.Chat import *


class Settings(BaseModel):
    id = PrimaryKeyField(null=False)
    id_type = ForeignKeyField(TypeSet, db_column='id_type', related_name='fk_type',
                              to_field='id', on_delete='cascade', on_update='cascade')
    id_chat = ForeignKeyField(Chat, db_column='id_chat', related_name='fk_chat',
                              to_field='id', on_delete='cascade', on_update='cascade')
    val = TextField(null=False, default='')

    class Meta:
        db_table = "settings"
        order_by = ('id',)


def add_set_default(chat_id, type_id, val):
    chat = try_chat(chat_id)
    _type = TypeSet.select().where(TypeSet.id == int(type_id)).get()
    if chat:
        row = Settings(
            id_type=_type,
            id_chat=chat,
            val=_type.default_val
        )
    row.save(force_insert=True)


def find_all_settings(id_chat):
    for null_settigs in get_null_settings(id_chat):
        add_set_default(id_chat, null_settigs.get('id'),
                        null_settigs.get('default_val'))
    return Settings.select().where(Settings.id_chat == id_chat)


def settings_set(chat_id, id_type, val):
    settings = Settings.get(Settings.id_chat == chat_id,
                            Settings.id_type == id_type)
    settings.val = val
    settings.save()
