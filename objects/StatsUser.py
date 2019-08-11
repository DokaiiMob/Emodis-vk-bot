# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from peewee import *
from random import randint
import datetime
import peewee
from objects.DataBase import *
from objects.User import *
from objects.Chat import *
from objects.Stats import *


class StatsUser(BaseModel):
    id = PrimaryKeyField(null=False)
    id_user = ForeignKeyField(User, db_column='id_user', related_name='fk_user',
                              to_field='id', on_delete='cascade', on_update='cascade')
    id_chat = ForeignKeyField(Chat, db_column='id_chat', related_name='fk_chat',
                              to_field='id', on_delete='cascade', on_update='cascade')
    date_time_adding = DateTimeField(
        default=datetime.datetime.now())
    date_time_last_msg = DateTimeField(
        default=datetime.datetime.now())
    len = IntegerField(null=False, default=0)
    is_banned = IntegerField(null=False, default=0)
    is_pred = IntegerField(null=False, default=0)
    is_ro = IntegerField(null=False, default=0)
    lvl = IntegerField(null=False, default=0)
    count_duel_save = IntegerField(null=False, default=0)
    count_duel_die = IntegerField(null=False, default=0)

    class Meta:
        db_table = "user_to_chat"
        order_by = ('id',)


def add_stats_user(user_id, chat_id):
    user = try_user(user_id)
    chat = try_chat(chat_id)
    if user and chat:
        row = StatsUser(
            id_user=user,
            id_chat=chat,
        )
        row.save(force_insert=True)


def get_duel_die(id_chat):
    return StatsUser.select().where(
        StatsUser.id_chat == id_chat,
        StatsUser.count_duel_die > 0
    ).order_by(StatsUser.count_duel_die.desc()).limit(10)


def get_duel_save(id_chat):
    return StatsUser.select().where(
        StatsUser.id_chat == id_chat,
        StatsUser.count_duel_save > 0
    ).order_by(StatsUser.count_duel_save.desc()).limit(10)


def find_all_stats_user(id_user, id_chat):
    try:
        User.select().where(User.id == id_user).get()
    except User.DoesNotExist:
        add_user(id_user, '')

    return StatsUser.select().where(
        StatsUser.id_user == id_user,
        StatsUser.id_chat == id_chat
    ).get()


def find_stats_addit_user_and_chat(id_user, id_chat):
    exist = True
    try:
        stats = find_all_stats_user(id_user, id_chat)
    except StatsUser.DoesNotExist:
        exist = False
    if not exist:
        add_stats_user(id_user, id_chat)
        stats = find_all_stats_user(id_user, id_chat)
    return stats


def get_preds_db(chat_id, user_id):
    return StatsUser.select(StatsUser).where(StatsUser.id_chat == chat_id, StatsUser.is_pred > 0, StatsUser.id_user > 0)


def get_bans_db(chat_id, user_id):
    return StatsUser.select(StatsUser).where(StatsUser.id_chat == chat_id, StatsUser.is_banned == 1, StatsUser.id_user > 0)


def find_all_users_by_msg(chat_id):
    stats = Stats.select(fn.SUM(Stats.count_msgs).alias('count_msgs'), Stats.id_user).where(
        Stats.id_chat == chat_id, Stats.id_user > 0).group_by(Stats.id_user).order_by(fn.SUM(Stats.count_msgs).desc()).limit(10)
    msg = ''
    index = 1
    for stat in stats:
        user_data = StatsUser.select().where(
            StatsUser.id_chat == chat_id, StatsUser.id_user == stat.id_user).get()
        msg += "#{0} {1} {2} сообщений, {3} ур.\n".format(index,
                                                          find_user(stat.id_user).full_name, stat.count_msgs, user_data.lvl)
        index = index + 1

    msg += "Остальная статистика: kanbase.ru/c/{0}".format(chat_id)
    return msg
