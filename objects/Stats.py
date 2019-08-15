# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import datetime
from peewee import fn, PrimaryKeyField, ForeignKeyField, DateTimeField, IntegerField
from objects.DataBase import BaseModel
from objects.User import User, try_user, add_user
from objects.Chat import Chat, try_chat


class Stats(BaseModel):
    id = PrimaryKeyField(null=False)
    id_user = ForeignKeyField(User, db_column='id_user', related_name='fk_user',
                              to_field='id', on_delete='cascade', on_update='cascade')
    id_chat = ForeignKeyField(Chat, db_column='id_chat', related_name='fk_chat',
                              to_field='id', on_delete='cascade', on_update='cascade')
    date_time = DateTimeField(
        default=datetime.datetime.now().strftime('%Y-%m-%d %H:00:00'))
    count_msgs = IntegerField(null=False, default=0)
    count_stickers = IntegerField(null=False, default=0)
    count_audio = IntegerField(null=False, default=0)

    class Meta:
        db_table = "stats"
        order_by = ('date_time',)


def add_stats(user_id, chat_id, _datetime):
    user = try_user(user_id)
    chat = try_chat(chat_id)

    if user and chat:
        row = Stats(
            id_user=user,
            id_chat=chat,
            date_time=_datetime
        )
        row.save(force_insert=True)


def find_all_stats_sum(id_user, id_chat):
    try:
        User.select().where(User.id == int(id_user)).get()
    except User.DoesNotExist:
        add_user(id_user, '')

    return Stats.select(fn.SUM(Stats.count_msgs).alias("count_msgs")).where(
        Stats.id_user == id_user,
        Stats.id_chat == id_chat
    ).get()


def find_all_stats_by_datetime(id_user, id_chat, _datetime):
    try:
        User.select().where(User.id == int(id_user)).get()
    except User.DoesNotExist:
        add_user(id_user, '')

    return Stats.select().where(
        Stats.id_user == id_user,
        Stats.id_chat == id_chat,
        Stats.date_time == _datetime
    ).get()


def find_stats_user_and_chat(id_user, id_chat):
    exist = True
    _datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:00:00')
    try:
        stats = find_all_stats_by_datetime(id_user, id_chat, _datetime)
    except Stats.DoesNotExist:
        exist = False
    if not exist:
        add_stats(id_user, id_chat, _datetime)
        stats = find_all_stats_by_datetime(id_user, id_chat, _datetime)
    return stats
