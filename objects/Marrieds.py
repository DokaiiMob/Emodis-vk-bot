# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
from peewee import *
from random import randint
import datetime
import peewee
import re
from objects.DataBase import *
from objects.User import *
from objects.Chat import *


class Marrieds(BaseModel):
    id = PrimaryKeyField(null=False)
    id_chat = ForeignKeyField(Chat, db_column='id_chat', related_name='fk_chat',
                              to_field='id', on_delete='cascade', on_update='cascade')
    id_user_one = ForeignKeyField(User, db_column='id_user_one', related_name='fk_user_one',
                                  to_field='id', on_delete='cascade', on_update='cascade')
    id_user_two = ForeignKeyField(User, db_column='id_user_two', related_name='fk_user_two',
                                  to_field='id', on_delete='cascade', on_update='cascade')
    date_time = DateTimeField(default=datetime.datetime.now())
    is_ok = IntegerField(null=False, default=0)

    class Meta:
        db_table = "marrieds"
        order_by = ('id',)


def add_marrieds(user_id_one, user_id_two, chat_id):
    m_exist = False

    user_one = try_user(user_id_one)
    user_two = try_user(user_id_two)
    chat = try_chat(chat_id)

    try:
        Marrieds.select().where(
            Marrieds.id_chat == int(chat_id),
            ((Marrieds.id_user_one == user_id_one) | (Marrieds.id_user_one == user_id_two) | (Marrieds.id_user_two == user_id_one) | (Marrieds.id_user_two == user_id_one))).get()
    except Marrieds.DoesNotExist:
        m_exist = True

    if user_one and user_two and chat:
        if m_exist:
            row = Marrieds(
                id_user_one=user_one,
                id_user_two=user_two,
                id_chat=chat
            )
            row.save(force_insert=True)
            return 1
    return 0


def done_marry(chat_id, user_id):
    m = Marrieds.select().where(
        Marrieds.id_chat == int(chat_id), Marrieds.id_user_two == user_id)
    if m:
        for _m in m:  
            _m.is_ok = 1
            _m.save()
        return True
    return False


def del_marry_all(chat_id, user_id):
    m = Marrieds.select().where(Marrieds.id_chat == chat_id, ((Marrieds.id_user_two == user_id) | (Marrieds.id_user_one == user_id)))
    if m:
        for _m in m:  
            _m.id_chat = 0
            _m.save()
            return True
    return False


def del_marry(chat_id, user_id):
    m = Marrieds.select().where(
        Marrieds.id_chat == int(chat_id), Marrieds.id_user_two == user_id)
    if m:
        for _m in m:  
            _m.id_chat = 0
            _m.save()
            return True
    return False


def get_marryieds(chat_id):
    return Marrieds.select(Marrieds.id_user_one, Marrieds.id_user_two, Marrieds.date_time).where(Marrieds.id_chat == int(chat_id), Marrieds.is_ok == 1).order_by(Marrieds.date_time.desc())
