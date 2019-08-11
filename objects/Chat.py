# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
from peewee import *
from random import randint
import datetime
import peewee
import re
from objects.DataBase import *


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


def find_all_chats():
    return Chat.select()


def find_chat(id):
    return Chat.select().where(Chat.id == id).get()


def find_chat_meth(id):
    exist = True
    try:
        chat = find_chat(id)
    except Chat.DoesNotExist:
        exist = False
    if not exist:
        add_chat(id, '')
        chat = find_chat(id)
    return chat


def update_chat_name(id, new_name):
    chat = Chat.get(Chat.id == id)
    chat.title = new_name
    chat.save()


def update_chat_count(id, new_val):
    chat = Chat.get(Chat.id == id)
    chat.members_count = new_val
    chat.save()
