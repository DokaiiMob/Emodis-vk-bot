# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
import datetime
from peewee import PrimaryKeyField, ForeignKeyField, TextField, IntegerField
from models.BaseModel import BaseModel
from models.User import User, try_user
from models.Chat import Chat, try_chat


class StopLines(BaseModel):
    id = PrimaryKeyField(null=False)
    id_chat = ForeignKeyField(Chat, db_column='id_chat', related_name='fk_chat',
      to_field='id', on_delete='cascade', on_update='cascade')
    type_do = IntegerField(null=False, default=0)
    line = TextField(null=False, default='')

    class Meta:
        db_table = "stop_lines"
        order_by = ('id',)


def add_stop_line(id_chat, line, type_do):
    print(id_chat, line, type_do)
    row = StopLines(
        id_chat=id_chat,
        type_do=type_do,
        line=line.lower().strip(),
    )
    row.save(force_insert=True)


def remove_stop_line(id_chat, line):
    tmp = line.lower().split()
    m = StopLines.delete().where(StopLines.id_chat == id_chat,
                                 StopLines.line == tmp[0].strip())
    m.execute()
    return True


def getting_stop_lines(id_chat):
    m = StopLines.select().where(StopLines.id_chat == id_chat)
    if m:
        return m
    return False
