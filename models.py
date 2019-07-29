# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from config import *
from peewee import *
from random import randint
import datetime
import peewee
import re


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
    title = TextField()
    default_val = TextField()

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
    is_ro = IntegerField(null=False, default=0)
    lvl = IntegerField(null=False, default=0)

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
    id_type = ForeignKeyField(TypeSet, db_column='id_type', related_name='fk_type',
                              to_field='id', on_delete='cascade', on_update='cascade')
    id_chat = ForeignKeyField(Chat, db_column='id_chat', related_name='fk_chat',
                              to_field='id', on_delete='cascade', on_update='cascade')
    val = TextField(null=False, default='')

    class Meta:
        db_table = "settings"
        order_by = ('id',)


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


def try_user(id):
    try:
        return User.select().where(User.id == int(id)).get()
    except User.DoesNotExist:
        return False


def try_chat(id):
    try:
        return Chat.select().where(Chat.id == int(id)).get()
    except Chat.DoesNotExist:
        return False


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


def add_stats_user(user_id, chat_id):
    user = try_user(user_id)
    chat = try_chat(chat_id)
    if user and chat:
        row = StatsUser(
            id_user=user,
            id_chat=chat,
        )
        row.save(force_insert=True)


def add_text(user_id, chat_id, msg, attach):
    user = try_user(user_id)
    chat = try_chat(chat_id)

    if user and chat:
        row = Texts(
            id_user=user,
            id_chat=chat,
            text=msg,
            attach=attach
        )
        row.save(force_insert=True)


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
        Marrieds.id_chat == int(chat_id), Marrieds.id_user_two == user_id).get()
    if m:
        m.is_ok = 1
        m.save()
        return True
    return False


def del_marry_all(chat_id, user_id):
    m = Marrieds.select().where(
        Marrieds.id_chat == int(chat_id), (Marrieds.id_user_two == user_id | Marrieds.id_user_one == user_id)).get()
    if m:
        m.id_chat = 0
        m.save()
        return True
    return False


def del_marry(chat_id, user_id):
    m = Marrieds.select().where(
        Marrieds.id_chat == int(chat_id), Marrieds.id_user_two == user_id).get()
    if m:
        m.id_chat = 0
        m.save()
        return True
    return False


def get_marryieds(chat_id):
    return Marrieds.select(Marrieds.id_user_one, Marrieds.id_user_two, Marrieds.date_time).where(Marrieds.id_chat == int(chat_id), Marrieds.is_ok == 1).order_by(Marrieds.date_time.desc())


def find_all_chats():
    return Chat.select()


def find_all_users():
    return User.select()


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


def find_all_settings(id_chat):
    for null_settigs in get_null_settings(id_chat):
        add_set_default(id_chat, null_settigs.get('id'),
                        null_settigs.get('default_val'))
    return Settings.select().where(Settings.id_chat == id_chat)


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


def find_user(id):
    exist = True
    try:
        user = User.select().where(User.id == id).get()
        return user
    except User.DoesNotExist:
        exist = False
    if not exist:
        add_user(id, " ")
        return User.select().where(User.id == id).get()


def update_chat_name(id, new_name):
    chat = Chat.get(Chat.id == id)
    chat.title = new_name
    chat.save()


def update_chat_count(id, new_val):
    chat = Chat.get(Chat.id == id)
    chat.members_count = new_val
    chat.save()


def find_all_users_by_msg(chat_id):
    stats = Stats.select(fn.SUM(Stats.count_msgs).alias('count_msgs'), Stats.id_user).where(
        Stats.id_chat == chat_id).group_by(Stats.id_user).order_by(Stats.count_msgs.desc()).limit(10)
    msg = ''
    index = 1
    for stat in stats:
        user_data = StatsUser.select(StatsUser.len).where(
            StatsUser.id_chat == chat_id, StatsUser.id_user == stat.id_user).get()
        msg += "#{0} {1} {2}/{3}\n".format(index,
                                           find_user(stat.id_user).full_name, user_data.len, stat.count_msgs)
        index = index + 1
    return msg


def get_preds_db(chat_id, user_id):
    return StatsUser.select(StatsUser).where(StatsUser.id_chat == chat_id, StatsUser.is_pred > 0)


def get_bans_db(chat_id, user_id):
    return StatsUser.select(StatsUser).where(StatsUser.id_chat == chat_id, StatsUser.is_banned == 1)


def settings_set(chat_id, id_type, val):
    settings = Settings.get(Settings.id_chat == chat_id,
                            Settings.id_type == id_type)
    settings.val = val
    settings.save()


def get_hello(id):
    return 'Привет, %s &#128521; Рекомендуем администратору беседы зайти на сайт' % id


def get_help():
    return 'Привет! Держи ссылку на команды: https://vk.com/@emodis-komandy-bota'


def get_delete_dogs_not():
    return "Собачек нет!"


def get_delete_dogs():
    return "Все собачки удалены!"


def not_access():
    return 'Нет доступа:('


def get_random():
    return "Вероятность составляет {0}%".format(randint(0, 100))


def get_pred(is_pred, all_pred):
    return "Предупреждение {0}/{1}".format(is_pred, all_pred)
