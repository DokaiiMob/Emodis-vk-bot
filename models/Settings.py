# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
from peewee import PrimaryKeyField, ForeignKeyField, TextField, JOIN
from models.BaseModel import BaseModel
from models.TypeSet import TypeSet
from models.Chat import Chat, try_chat


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


def get_null_settings(id_chat):
    null_settings = []
    for s in TypeSet.select(TypeSet.id, TypeSet.default_val, Settings.val.alias('title')).join(Settings, JOIN.LEFT_OUTER, Settings.id_type == TypeSet.id).where(TypeSet.id.not_in(Settings.select(Settings.id_type).where(Settings.id_chat == id_chat))).group_by(TypeSet.id):
        null_settings.append({
            'id': s.id,
            'default_val': s.default_val
        })
    return null_settings

def getListChats(my_id,ids):
    if len(ids) == 0:
        return False
    ids = [int(a) for a in ids.split(",") if int(a) > 0]
    ans = [my_id]
    for id in ids:
        string = Settings.select(Settings.val).where((Settings.id_chat == id) & (Settings.id_type == 7)).scalar()
        if len(string) > 0:
            if my_id in [int(a) for a in string.split(",") if int(a) > 0]:
                ans.append(id)
    return ans

    
    null_settings = []
    for s in TypeSet.select(TypeSet.id, TypeSet.default_val, Settings.val.alias('title')).join(Settings, JOIN.LEFT_OUTER, Settings.id_type == TypeSet.id).where(TypeSet.id.not_in(Settings.select(Settings.id_type).where(Settings.id_chat == id_chat))).group_by(TypeSet.id):
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


def settings_set(chat_id, id_type, val):
    settings = Settings.get(Settings.id_chat == chat_id,
                            Settings.id_type == id_type)
    settings.val = val
    settings.save()


def parser_settings(id_chat):
    block_mat = False
    block_url_chat = False
    comments = False
    max_pred = 3
    duel_kd = 5
    neubor = ""
    for settings in find_all_settings(id_chat):
        id_type = int(settings.id_type.id)
        # Убрать комментарии
        if id_type == 2 and int(settings.val) == 1:
            comments = True
        # Задать количество предупреждений
        if id_type == 3:
            max_pred = int(settings.val)
        # Фильтр мата
        if id_type == 4 and int(settings.val) == 1:
            block_mat = True
        # Ограничение на дуэль, в секундах
        if id_type == 5:
            if not settings.val:
                settings_set(id_chat,5, 60)
                duel_kd = 60
            else:
                duel_kd = int(settings.val)
        # Герой дня
        if id_type == 1:
            hero_id = int(settings.val)
        # Герой дня
        if id_type == 6:
            hero_day = int(settings.val)
        # Товарищеские беседы
        if id_type == 7:
            neubor = settings.val
    return block_url_chat, max_pred, block_mat, duel_kd, hero_id, hero_day, comments, neubor


def settings(chat_id, text):
    text_array = text.split(' ')
    if len(text_array) >= 2:
        try:
            type_set = int(text_array[0])
        except:
            return False
        val = text_array[1]
        if type_set == 1:
            try:
                val = int(val)
            except:
                return False
            if val == 0 or val == 1:
                settings_set(chat_id, type_set, val)
                return True
        if type_set == 2:
            try:
                val = int(val)
            except:
                return False
            if val == 0 or val == 1:
                settings_set(chat_id, type_set, val)
                return True
        if type_set == 3:
            settings_set(chat_id, type_set, val)
            return True
        if type_set == 4:
            try:
                val = int(val)
            except:
                return False
            if val == 0 or val == 1:
                settings_set(chat_id, type_set, val)
                return True
        if type_set == 5:
            settings_set(chat_id, type_set, val)
            return True
        if type_set == 7:
            val = val.replace(' ', '')
            settings_set(chat_id, type_set, val)
            return True
    return False
