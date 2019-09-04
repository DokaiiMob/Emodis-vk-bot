# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
from random import randint
import vk
import re
import requests
from config import GROUP_ID
from objects.DataBase import *
from objects.User import *
from objects.Chat import *
from objects.Marrieds import *
from objects.Stats import *
from objects.StatsUser import *
from objects.Settings import *
from objects.TypeSet import *
from objects.Texts import *
import Requests
import locale
import datetime
# Объект действий робота


class Actions:
    peer_id = 0

    def __init__(self):
        print("Actions init")
        self.requests = Requests.Requests()

    def update_temp_data(self, user_id, chat_id, peer_id, max_pred):
        self.is_ban_or_kik = False
        self.user_id = user_id
        self.chat_id = chat_id
        self.peer_id = peer_id
        self.max_pred = max_pred
        self.requests.update_temp_data(peer_id, chat_id)

    def ban_user(self, id):
        stats = find_stats_addit_user_and_chat(id, self.chat_id)
        stats.is_banned = 1 if self.remove_chat_user(id) else 0
        stats.save()

    def pred_user(self, id):
        stats = find_stats_addit_user_and_chat(id, self.chat_id)
        stats.is_pred = stats.is_pred + 1
        if int(stats.is_pred) >= int(self.max_pred):
            # По сути надо выбирать что делать роботу
            # stats.is_banned = 1
            stats.is_pred = 0
            self.requests.send_msg(msg="Лимит предупреждений! Кик :-)")
            # И парсить максимальное кол-во
            self.remove_chat_user(id)
        stats.save()
        self.requests.send_msg(msg="Предупреждение {0} из {1}".format(
            stats.is_pred, self.max_pred))

    def remove_chat_user(self, id):
        self.requests.remove_chat_user(id)

    def send_msg(self, msg):
        self.requests.send_msg(msg)

    def get_need_lvl(self, old):
        all_count_msgs = find_all_stats_sum(
            self.user_id, self.chat_id).count_msgs
        if round(int(all_count_msgs) ** 0.2) > old:
            return round(int(all_count_msgs) ** 0.2)
        else:
            return old

    def is_admin(self):
        try:
            chat_users = self.requests.api.messages.getConversationMembers(
                peer_id=self.peer_id, group_id=GROUP_ID)['items']
            for chat_user in chat_users:
                if self.user_id == chat_user['member_id'] and chat_user.get('is_admin'):
                    return True
        except vk.exceptions.VkAPIError:
            return False
        return False
    # def get_api_full_name(self)

    def update_user_data(self, from_id):
        self.from_id = from_id
        user = find_user(from_id)
        now = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(now)
        if user.cache_repeat + 13600 < timestamp and user.id > 0:
            user.full_name = self.requests.api_full_name(user.id)
            user.cache_repeat = timestamp
            user.save()
        self.user_id = user.id
        return user

    def update_chat_data(self, chat):
        now = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(now)
        if chat.cache_repeat + 3600 < timestamp:
            chat_data = self.requests.getConversationsById()
            if chat_data:
                chat.title, chat.members_count = chat_data[
                    'title'], chat_data['members_count']
            else:
                chat.title = chat.title
            chat.cache_repeat = timestamp
            chat.save()
        return chat

    def bot_come_to_chat(self):
        exist = False
        for chat_user in self.requests.getConversationMembers():
            exist = True
            self.requests.find_update_user(chat_user['from_id'])
        if exist:
            self.requests.send_msg(
                msg="Привет, чат №{0} &#128521; Рекомендуем администратору беседы зайти на сайт".format(self.chat_id))
        else:
            self.requests.send_msg(
                msg="Привет, чат №{0} &#128521; Рекомендуем выдать доступ к переписке!".format(self.peer_id))

    def is_chat_invite_user(self, member_id):
        if member_id > 0:
            self.requests.find_update_user(member_id)
            stats = find_stats_addit_user_and_chat(member_id, self.chat_id)
            if stats.is_banned == 1:
                self.requests.remove_chat_user(member_id)
        if member_id == -GROUP_ID:
            self.bot_come_to_chat()

    def get_hero(self):
        self.requests.send_msg(msg="Пока что героя нет")
        return True

    def get_top(self):
        self.send_msg(
            msg="Статистика: kanbase.ru/c/{0}".format((self.chat_id)))  # *0x45785
        return True

    def get_all_list(self, params):
        if params == "pred":
            msg = 'Все предупреждения:\n'
            arr_p = get_preds_db(self.chat_id, self.user_id)
        else:
            msg = 'Все блокировки:\n'
            arr_p = get_bans_db(self.chat_id, self.user_id)
        index = 1
        exist = False
        for p in arr_p:
            exist = True
            msg += "#{0} {1} {2}\n".format(index,
                                           p.id_user.full_name, p.is_pred)
            index = index + 1
        if exist:
            self.requests.send_msg(msg=msg)
        else:
            if params == "pred":
                self.requests.send_msg(msg="Предупреждений в чате нет")
            else:
                self.requests.send_msg(msg="Блокировок в чате нет")
        return True

    def get_all_marry(self):
        m = get_marryieds(self.chat_id)
        if m:
            msg = 'Все браки: \n'
            index = 1
            time = datetime.datetime.now()
            for mr in m:
                msg += "#{0} {1} и {2} {3} дн.\n".format(
                    index, mr.id_user_one.full_name, mr.id_user_two.full_name, abs(time - mr.date_time).days)
                index = index + 1
            self.requests.send_msg(msg=msg)
        else:
            self.requests.send_msg(msg="Браков ещё нет")
        return True

    def get_duel_stats(self, type):
        if type == 1:
            arr_duel = get_duel_save(self.chat_id)
        else:
            arr_duel = get_duel_die(self.chat_id)
        if len(arr_duel) > 0:
            msg = ''
            index = 1
            for duel in arr_duel:
                if type == 1:
                    msg += "#{0} {1} {2} р.\n".format(
                        index, duel.id_user.full_name, duel.count_duel_save)
                else:
                    msg += "#{0} {1} {2} р.\n".format(
                        index, duel.id_user.full_name, duel.count_duel_die)
                index = index + 1
            self.requests.send_msg(msg=msg)
        else:
            self.requests.send_msg(msg="Дуэлей ещё не было")
        return True

    def remove_married(self):
        if del_marry_all(self.chat_id, self.user_id):
            self.requests.send_msg(msg="Брак аннулирован:)")
        return True

    def delete_married(self):
        if del_marry(self.chat_id, self.user_id):
            self.send_msg(msg="В браке отказано:)")

    def save_married(self):
        if done_marry(self.chat_id, self.user_id):
            self.requests.send_msg(msg="Поздравляю:)")
        return True

    def get_married(self, text):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="Выберите участника беседы через @")
            return True
        if len(users) > 1:
            self.requests.send_msg(msg="Больше двух участников нельзя)")
            return True
        marryed = add_marrieds(self.user_id, users[0], self.chat_id)
        if marryed == 1:
            self.requests.send_msg(
                msg="Нужно подтвердить другому участнику, написав Работяга брак да/нет")
        else:
            self.requests.send_msg(msg="Брак невозможен")
        return True

    def get_choise(self, text):
        array = text().split('или')
        self.requests.send_msg(msg="Я выбираю {0}".format(
            array[randint(0, len(array) - 1)].strip()))

    def get_inform(self):
        self.requests.send_msg(
            msg="Вероятность составляет {0}%".format(randint(0, 100)))
        return True

    def settings(self, text):
        text_array = text().strip().split(' ')
        if len(text_array) >= 2:
            type_set = int(text_array[0])
            val = text_array[1]
            if type_set == 1:
                if int(val) == 0 or int(val) == 1:
                    settings_set(self.chat_id, type_set, val)
                    self.requests.send_msg(msg="Сохранено!")
                    return True
            if type_set == 2:
                if int(val) == 0 or int(val) == 1:
                    settings_set(self.chat_id, type_set, val)
                    self.requests.send_msg(msg="Сохранено!")
                    return True
            if type_set == 3:
                settings_set(self.chat_id, type_set, val)
                self.requests.send_msg(msg="Сохранено!")
                return True
            if type_set == 4:
                if int(val) == 0 or int(val) == 1:
                    settings_set(self.chat_id, type_set, val)
                    self.requests.send_msg(msg="Сохранено!")
                    return True
            if type_set == 5:
                settings_set(self.chat_id, type_set, val)
                self.requests.send_msg(msg="Сохранено!")
                return True
        return False

    def ban_last_users(self, count):
        for users in get_users_by_limit(self.chat_id, int(count)):
            self.ban_user(users.id)
        return True

    def dog_kick(self):
        for chat_user in self.requests.api.messages.getConversationMembers(peer_id=self.peer_id, group_id=GROUP_ID)['profiles']:
            dog_exist = False
            if chat_user.get('deactivated'):
                if self.remove_chat_user(chat_user['id']):
                    dog_exist = True
        if not dog_exist:
            self.requests.send_msg(msg="Собачек нет!")
        else:
            self.requests.send_msg(msg="Собачек больше нет!")
        return True

    def ban_users(self, text):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="И кого мне банить?")
            return True
        for user in users:
            self.ban_user(user)
        return True

    def kik_users(self, text):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="И кого мне кикать?")
            return True
        for user in users:
            self.pred_user(user)
        return True

    def pred_users(self, text):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="И кого мне банить?")
            return True
        for user in users:
            self.pred_user(user)
        return True

    def ro_users(self, text):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="И кого мне в рид-онли кидать?")
            return True
        # no
        return True

    def unban_users(self, text):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="Ну ты выбери кого-нибудь...")
            return True
        for user in users:
            stats = find_stats_addit_user_and_chat(user, self.chat_id)
            stats.is_banned = 0
            stats.is_pred = 0
            stats.save()

    def unpred_users(self, text):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="Ну ты выбери кого-нибудь...")
            return True
        for user in users:
            stats = find_stats_addit_user_and_chat(user, self.chat_id)
            stats.is_banned = 0
            stats.is_pred = 0
            stats.save()

    def unro_users(self, text):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="Ну ты выбери кого-нибудь...")
            return True
        # no
        return True
