# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from config import *
from peewee import *
from random import randint
import datetime
import peewee


class DataBase():
    dbhandle = MySQLDatabase(
        DB_NAME, user=DB_USER,
        password=DB_PASS,
        host=DB_HOST
    )

    def __init__(self):
        self.get_db_handle()

    def get_db_handle(self):
        return self.dbhandle

    def open_connection(self):
        try:
            self.dbhandle.connect()
        except peewee.InternalError as px:
            print(str(px))

    def close_connection(self):
        self.dbhandle.close()


class BaseModel(Model):
    class Meta:
        database = DataBase().get_db_handle()


class Chat(BaseModel):
    id = PrimaryKeyField(null=False)
    title = CharField(max_length=255)
    admin_id = IntegerField(null=False)
    members_count = IntegerField(null=False)

    class Meta:
        db_table = "chats"
        order_by = ('id',)


class TypeSet(BaseModel):
    id = PrimaryKeyField(null=False)
    title = CharField(max_length=255)

    class Meta:
        db_table = "type_set"
        order_by = ('id',)


class User(BaseModel):
    id = PrimaryKeyField(null=False)
    full_name = CharField(max_length=100)

    class Meta:
        db_table = "users"
        order_by = ('id',)


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

    class Meta:
        db_table = "user_to_chat"
        order_by = ('id',)


class Texts(BaseModel):
    id = PrimaryKeyField(null=False)
    id_user = ForeignKeyField(User, db_column='id_user', related_name='fk_user',
                              to_field='id', on_delete='cascade', on_update='cascade')
    id_chat = ForeignKeyField(Chat, db_column='id_chat', related_name='fk_chat',
                              to_field='id', on_delete='cascade', on_update='cascade')
    text = TextField(null=False, default='')
    attach = TextField(null=False, default='')
    date_time = DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = "texts"
        order_by = ('id',)


class Settings(BaseModel):
    id = PrimaryKeyField(null=False)
    id_type = ForeignKeyField(User, db_column='id_type', related_name='fk_type',
                              to_field='id', on_delete='cascade', on_update='cascade')
    id_chat = ForeignKeyField(Chat, db_column='id_chat', related_name='fk_chat',
                              to_field='id', on_delete='cascade', on_update='cascade')
    val = TextField(null=False, default='')

    class Meta:
        db_table = "settings"
        order_by = ('id',)


def add_chat(id, title):
    row = Chat(
        id=id,
        title=title.strip(),
    )
    row.save(force_insert=True)


def add_user(id, full_name):
    row = User(
        id=id,
        full_name=full_name.strip(),
    )
    row.save(force_insert=True)


def add_stats(user_id, chat_id):
    user_exist = chat_exist = True

    try:
        user = User.select().where(User.id == int(user_id)).get()
    except DoesNotExist as de:
        user_exist = False

    try:
        chat = Chat.select().where(Chat.id == int(chat_id)).get()
    except DoesNotExist as de:
        chat_exist = False

    if user_exist and chat_exist:
        row = Stats(
            id_user=user,
            id_chat=chat,
        )
        row.save(force_insert=True)


def add_stats_user(user_id, chat_id):
    user_exist = chat_exist = True

    try:
        user = User.select().where(User.id == int(user_id)).get()
    except User.DoesNotExist as de:
        user_exist = False

    try:
        chat = Chat.select().where(Chat.id == int(chat_id)).get()
    except Chat.DoesNotExist as de:
        chat_exist = False

    if user_exist and chat_exist:
        row = StatsUser(
            id_user=user,
            id_chat=chat,
        )
        row.save(force_insert=True)


def add_text(user_id, chat_id, msg, attach):
    user_exist = chat_exist = True

    try:
        user = User.select().where(User.id == int(user_id)).get()
    except User.DoesNotExist as de:
        user_exist = False

    try:
        chat = Chat.select().where(Chat.id == int(chat_id)).get()
    except Chat.DoesNotExist as de:
        chat_exist = False

    if user_exist and chat_exist:
        row = Texts(
            id_user=user,
            id_chat=chat,
            text=msg,
            attach=attach
        )
        row.save(force_insert=True)


def find_all_chats():
    return Chat.select()


def find_all_users():
    return User.select()


def find_all_stats(id_user, id_chat):
    return Stats.select().where(
        Stats.id_user == id_user,
        Stats.id_chat == id_chat,
        Stats.date_time == datetime.datetime.now().strftime('%Y-%m-%d %H:00:00')
    ).get()


def find_stats_user_and_chat(id_user, id_chat):
    exist = True
    try:
        stats = find_all_stats(id_user, id_chat)
    except Stats.DoesNotExist as de:
        exist = False
    if not exist:
        add_stats(id_user, id_chat)
        stats = find_all_stats(id_user, id_chat)
    return stats


def find_all_stats_user(id_user, id_chat):
    return StatsUser.select().where(
        StatsUser.id_user == id_user,
        StatsUser.id_chat == id_chat
    ).get()


def find_stats_addit_user_and_chat(id_user, id_chat):
    exist = True
    try:
        stats = find_all_stats_user(id_user, id_chat)
    except StatsUser.DoesNotExist as de:
        exist = False
    if not exist:
        add_stats_user(id_user, id_chat)
        stats = find_all_stats_user(id_user, id_chat)
    return stats


def find_chat(id):
    return Chat.select().where(Chat.id == id).get()


def find_chat_meth(id):
    exist = True
    try:
        chat = find_chat(id)
    except Chat.DoesNotExist as de:
        exist = False
    if not exist:
        add_chat(id, '')
        chat = find_chat(id)
    return chat


def find_user(id):
    exist = True
    try:
        user = User.select().where(User.id == id).get()
        return (user, True)
    except User.DoesNotExist as de:
        exist = False
    if not exist:
        add_user(id, " ")
        return (User.select().where(User.id == id).get(), False)


def update_chat_name(id, new_name):
    chat = Chat.get(Chat.id == id)
    chat.title = new_name
    chat.save()


def update_chat_count(id, new_val):
    chat = Chat.get(Chat.id == id)
    chat.members_count = new_val
    chat.save()


def get_help():
    return 'Привет! Слушай, а зачем тебе я? Хорошо, держи ссылку на команды: https://vk.com/wall-183796256_4'


def get_delete_dogs():
    return "Все собачки удалены!"


def not_access():
    return 'Нет доступа:('


def get_random(full_name):
    return full_name + ', вероятность составляет ' + str(randint(0, 100)) + '%!'


def get_pred(is_pred, all_pred):
    return 'Предупреждение, ' + str(is_pred) + '/' + str(all_pred)


def get_random_array(msg):
    msg = msg.replace(msg[:6], '')
    array = msg.split('или')
    return 'Я выбираю ' + array[randint(0, len(array) - 1)]
# print(stats_data)
# stats_data = []
# for stat in find_all_stats_by_id_user_and_id_chat(385818590, 1):
#     stats_data.append({
#         'id_user': stat.id_user,
#         'id_chat': stat.id_chat,
#         'date_time': stat.date_time,
#         'count_msgs': stat.count_msgs,
#     })
# # add_stats_user(385818590, 1)
# stats_data = []
# for stat in find_all_stats_user_by_id_user_and_id_chat(385818590, 1):
#     stats_data.append({
#         'id_user': stat.id_user,
#         'id_chat': stat.id_chat,
#         'date_time_last_msg': stat.date_time_last_msg,
#     })


# add_chat(12, 'None')
# add_user(12, '')
# add_stats(385818590, 1)
# update_user(385818590, 'Kindle Books')
