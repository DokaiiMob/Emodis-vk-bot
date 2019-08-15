# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
import datetime
from peewee import PrimaryKeyField, CharField, IntegerField, DateTimeField
from objects.DataBase import BaseModel


class Chat(BaseModel):
    id = PrimaryKeyField(null=False)
    title = CharField(max_length=255)
    admin_id = IntegerField(null=False)
    members_count = IntegerField(null=False)
    duel_id = IntegerField(null=False, default=0)
    date_last_duel = DateTimeField(
        default=datetime.datetime.now())

    class Meta:
        db_table = "chats"
        order_by = ('id',)


def add_chat(id, title):
    row = Chat(
        id=id,
        title=title.strip(),
    )
    row.save(force_insert=True)


def try_chat(id):
    try:
        return Chat.select().where(Chat.id == int(id)).get()
    except Chat.DoesNotExist:
        return False


def find_chat(id):
    chat = try_chat(id)
    if not chat:
        add_chat(id, '')
        chat = try_chat(id)
    return chat
