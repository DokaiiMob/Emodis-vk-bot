# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from random import randint
import re
import requests
import vk
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
import locale
import datetime


class CommandHandler:
    chat_id = 0
    duel_kd = 60
    peer_id = 0
    user_id = 0
    max_pred = 10
    con_msg_id = 0

    def __init__(self, api):
        print("Init CommandHandler")
        self.api = api

    def set_peer_id(self, peer_id):
        self.peer_id = peer_id

    def find_update_user(self, member_id):
        user = find_user(member_id)
        if len(user.full_name) == 0:
            user.full_name = self.api_full_name(user.id)
            user.save()

    def action_parser(self, action):
        if action['type'] == 'chat_invite_user':
            self.is_chat_invite_user(action['member_id'])
        if action['type'] == 'chat_invite_user_by_link':
            self.is_chat_invite_user(self.user_id)
        if action['type'] == 'chat_title_update':
            print("chat title")
        if action['type'] == 'chat_kick_user':
            print("kick_user or user_exit")

    def is_chat_invite_user(self, member_id):
        if member_id > 0:
            self.find_update_user(member_id)
            stats = find_stats_addit_user_and_chat(member_id, self.chat_id)
            if stats.is_banned == 1:
                self.remove_chat_user(member_id)
            return True
        if member_id < 0:
            print("Here adding to chat another bot")
        if member_id == -GROUP_ID:
            try:
                for chat_user in self.getConversationMembers():
                    self.find_update_user(chat_user['from_id'])
                self.send_msg(
                    msg="Привет, {0} &#128521; Рекомендуем администратору беседы зайти на сайт".format(self.peer_id))
            except vk.exceptions.VkAPIError:
                self.send_msg(
                    msg="Привет, {0} &#128521; Рекомендуем выдать доступ к переписке!".format(self.peer_id))
                return True

    def api_full_name(self, user_id):
        name = self.api.users.get(user_ids=user_id)[0]
        return "{0} {1}".format(name['first_name'], name['last_name'])

    def send_msg(self, msg):
        # a = self.api.messages.getByConversationMessageId(peer_id=self.peer_id,conversation_message_ids=self.con_msg_id,group_id=GROUP_ID)
        return self.api.messages.send(peer_id=self.peer_id, random_id=randint(
            -2147483647, 2147483647), message=msg)

    def delete_msg(self, id):
        # a = self.api.messages.getByConversationMessageId(
        #     peer_id=self.peer_id, conversation_message_ids=id, group_id=GROUP_ID)
        self.api.messages.delete(
            message_ids=str(id), delete_for_all=1, group_id=GROUP_ID)

    def getConversationsById(self):
        try:
            chat_data = self.api.messages.getConversationsById(
                peer_ids=self.peer_id, group_id=GROUP_ID)
            if chat_data['items']:
                if chat_data['items'][0]:
                    return chat_data['items'][0]['chat_settings']
        except vk.exceptions.VkAPIError:
            return False

    def update_user_data(self, from_id):
        user = find_user(from_id)
        now = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(now)
        if user.cache_repeat + 13600 < timestamp and user.id > 0:
            user.full_name = self.api_full_name(user.id)
            user.cache_repeat = timestamp
            user.save()
        self.user_id = user.id
        return user

    def update_chat_data(self, chat):
        now = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(now)
        if chat.cache_repeat + 3600 < timestamp:
            chat_data = self.getConversationsById()
            if chat_data:
                chat.title, chat.members_count, chat.cache_repeat = chat_data[
                    'title'], chat_data['members_count'], timestamp
                chat.save()

    def getConversationMembers(self):
        return self.api.messages.getConversationMembers(peer_id=self.peer_id, group_id=GROUP_ID)['profiles']

    def parse_attachments(self, attachments):
        if len(attachments) > 0:
            str = ''
            for attach in attachments:
                str += attach['type'] + " "
            return str
        return ''

    def parse_bot(self, text):
        text = text.strip()
        if re.match('работяга', text.lower()):
            text = text.replace(text[:9], '')
            return True, text.strip()
        if re.match("\[club183796256\|\@kanbase\],", text.lower()):
            text = text.replace(text[:24], '')
            return True, text.strip()
        if re.match("\[club183796256\|\@kanbase\]", text.lower()):
            text = text.replace(text[:23], '')
            return True, text.strip()
        return False, text

    def parse_users(self, text):
        users = re.findall(r'\w+\|@?\w+', text)
        if not users:
            return False
        return users

    def get_top(self):
        self.send_msg(
            msg="Статистика: kanbase.ru/c/{0}".format((self.chat_id*0x45785)))

    def get_choise(self, text):
        msg = text.replace(text[:6], '')
        array = msg.split('или')
        self.send_msg(msg="Я выбираю {0}".format(
            array[randint(0, len(array) - 1)]))

    def get_inform(self):
        self.send_msg(
            msg="Вероятность составляет {0}%".format(randint(0, 100)))

    def get_preds(self):
        exist = False
        msg = 'Все предупреждения:\n'
        index = 1
        for p in get_preds_db(self.chat_id, self.user_id):
            exist = True
            name = self.api.users.get(user_ids=p.id_user)[0]
            msg += "#{0} {1} {2} {3}\n".format(index,
                                               name['first_name'], name['last_name'], p.is_pred)
            index = index + 1
        if exist:
            self.send_msg(msg=msg)
        else:
            self.send_msg(msg="Предупреждений в чате нет")

    def get_bans(self):
        msg = 'Все блокировки:\n'
        index = 1
        exist = False
        for p in get_bans_db(self.chat_id, self.user_id):
            exist = True
            name = self.api.users.get(user_ids=p.id_user)[0]
            msg += "#{0} {1} {2}\n".format(index,
                                           name['first_name'], name['last_name'])
            index = index + 1
        if exist:
            self.send_msg(msg=msg)
        else:
            self.send_msg(msg="Блокировок в чате нет")

    def remove_chat_user(self, id):
        try:
            if id == GROUP_ID:
                return False
            self.api.messages.removeChatUser(
                chat_id=self.chat_id, member_id=id)
            return True
        except vk.exceptions.VkAPIError:
            self.send_msg(msg='По какой-то причине нет доступа :(')
            return False

    def give_pred_by_id(self, user_id, msg):
        stats = find_stats_addit_user_and_chat(user_id, self.chat_id)
        stats.is_pred = stats.is_pred + 1
        stats.save()
        self.send_msg(msg="{0} Предупреждение {1} из {2}".format(
            msg, stats.is_pred, self.max_pred))
        if int(stats.is_pred) >= int(self.max_pred):
            # По сути надо выбирать что делать роботу
            # stats.is_banned = 1
            stats.is_pred = 0
            self.send_msg(msg="Лимит предупреждений! Кик :-)")
            # И парсить максимальное кол-во
            self.remove_chat_user(user_id)

    def pred_user(self, id):
        id = int(id)
        stats = find_stats_addit_user_and_chat(id, self.chat_id)
        stats.is_pred = stats.is_pred + 1
        stats.save()
        if int(stats.is_pred) >= int(self.max_pred):
            # По сути надо выбирать что делать роботу
            # stats.is_banned = 1
            # stats.is_pred = 0
            # self.send_msg(msg="Лимит предупреждений! Кик :-)")
            # И парсить максимальное кол-во
            self.remove_chat_user(id)
        self.send_msg(msg="Предупреждение {0} из {1}".format(
            stats.is_pred, self.max_pred))

    def pred(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                self.pred_user(user.split('|')[0].split('id')[1])

    def kick(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                self.remove_chat_user(user.split('|')[0].split('id')[1])

    def ban_last_users(self, count):
        for users in get_users_by_limit(self.chat_id, count):
            self.ban_user(users.id)

    def ban_user(self, id):
        id = int(id)
        stats = find_stats_addit_user_and_chat(id, self.chat_id)
        stats.is_banned = 1 if self.remove_chat_user(id) else 0
        stats.save()

    def ro_user(self, id):
        id = int(id)
        stats = find_stats_addit_user_and_chat(id, self.chat_id)
        stats.is_ro = 1
        stats.save()

    def ban(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                self.ban_user(user.split('|')[0].split('id')[1])

    def ro(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                self.ro_user(user.split('|')[0].split('id')[1])

    def ban_off(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                id = user.split('|')[0].split('id')[1]
                stats = find_stats_addit_user_and_chat(id, self.chat_id)
                stats.is_banned = 0
                stats.is_pred = 0
                stats.save()

    def pred_off(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                id = user.split('|')[0].split('id')[1]
                stats = find_stats_addit_user_and_chat(id, self.chat_id)
                stats.is_pred = 0
                stats.save()

    def dog_kick(self):
        for chat_user in self.api.messages.getConversationMembers(peer_id=self.peer_id, group_id=GROUP_ID)['profiles']:
            dog_exist = False
            if chat_user.get('deactivated'):
                if self.remove_chat_user(chat_user['id']):
                    dog_exist = True
        if not dog_exist:
            self.send_msg(msg="Собачек нет!")
        else:
            self.send_msg(msg="Собачек больше нет!")

    def get_need_lvl(self, old):
        all_count_msgs = find_all_stats_sum(
            self.user_id, self.chat_id).count_msgs
        if round(int(all_count_msgs) ** 0.2) > old:
            return round(int(all_count_msgs) ** 0.2)
        else:
            return old

    def get_married(self, user):
        if re.match('id', user.split('|')[0]):
            id = user.split('|')[0].split('id')[1]
            marryed = add_marrieds(self.user_id, id, self.chat_id)
            if marryed == 1:
                self.send_msg(
                    msg="Нужно подтвердить другому участнику, написав Работяга брак да/нет")
            if marryed == 0:
                self.send_msg(msg="Брак невозможен")

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
            self.send_msg(msg=msg)
        else:
            self.send_msg(msg="Браков ещё нет")

    def delete_married(self):
        if del_marry(self.chat_id, self.user_id):
            self.send_msg(msg="В браке отказано:)")

    def remove_married(self):
        if del_marry_all(self.chat_id, self.user_id):
            self.send_msg(msg="Брак аннулирован:)")

    def save_married(self):
        if done_marry(self.chat_id, self.user_id):
            self.send_msg(msg="Поздравляю:)")

    def settings(self, text):
        text_array = text.split(' ')
        if len(text_array) >= 2:
            type_set = int(text_array[0])
            val = text_array[1]
            if type_set == 1:
                if int(val) == 0 or int(val) == 1:
                    settings_set(self.chat_id, type_set, val)
                    return True
            if type_set == 2:
                if int(val) == 0 or int(val) == 1:
                    settings_set(self.chat_id, type_set, val)
                    return True
            if type_set == 3:
                settings_set(self.chat_id, type_set, val)
                return True
            if type_set == 4:
                if int(val) == 0 or int(val) == 1:
                    settings_set(self.chat_id, type_set, val)
                    return True
            if type_set == 5:
                settings_set(self.chat_id, type_set, val)
                return True
        return False

    def is_admin(self):
        try:
            chat_users = self.api.messages.getConversationMembers(
                peer_id=self.peer_id, group_id=GROUP_ID)['items']
            for chat_user in chat_users:
                if self.user_id == chat_user['member_id'] and chat_user.get('is_admin'):
                    return True
        except vk.exceptions.VkAPIError:
            return False
        return False

    def get_duel(self, type):
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
            self.send_msg(msg=msg)
        else:
            self.send_msg(msg="Дуэлей ещё не было")
        return False

    def duel(self, chat, user, stats):
        if chat.date_last_duel and (datetime.datetime.now()-chat.date_last_duel).total_seconds() < self.duel_kd:
            self.send_msg(
                msg="Дуэль уже состоялась, включен промежуток между дуэлями в {0} сек".format(self.duel_kd))
            return False
        if chat.duel_id == 0:
            self.send_msg(msg="Хорошо, @id{0} ({1}), ждем твоего оппонента...".format(
                user.id, user.full_name))
            chat.duel_id = user.id
            chat.save()
            return True
        if chat.duel_id != user.id:
            self.send_msg(msg="@id{0} ({1}), принял вызов!".format(
                user.id, user.full_name))
            if randint(0, 100) > 50:
                user_ = find_user(chat.duel_id)
                self.send_msg(msg="Произошла дуэль, @id{0} ({1}) падает замертво. F".format(
                    user_.id, user_.full_name))
                stats.count_duel_save = stats.count_duel_save + 1
                stats.save()
                stats_ = find_stats_addit_user_and_chat(
                    chat.duel_id, chat.id)
                stats_.count_duel_die = stats.count_duel_die + 1
                stats_.save()
            else:
                self.send_msg(msg="Произошла дуэль, @id{0} ({1}) падает замертво. F".format(
                    user.id, user.full_name))
                stats.count_duel_die = stats.count_duel_die + 1
                stats.save()
                stats_ = find_stats_addit_user_and_chat(
                    chat.duel_id, chat.id)
                stats_.count_duel_save = stats.count_duel_save + 1
                stats_.save()
            chat.duel_id = 0
            chat.date_last_duel = datetime.datetime.now()
            chat.save()
            stats.save()
            return True
        self.send_msg(msg="Сам себя, F")
        chat.duel_id = 0
        stats.count_duel_die = stats.count_duel_die + 1
        chat.date_last_duel = datetime.datetime.now()
        stats.save()
        chat.save()
        return True

    def parse_command(self, text, user_id):

        self.user_id = user_id

        if re.match('герой', text):
            self.send_msg(msg="Пока героя нет")
            return True

        if re.match('топ', text):
            self.get_top()
            return True

        if re.match('выбери', text):
            self.get_choise(text)
            return True

        if re.match('инфа', text):
            self.get_inform()
            return True

        if re.match('все', text):
            text = text.replace(text[:4], '')

            if re.match('преды', text):
                self.get_preds()
                return True

            if re.match('баны', text):
                self.get_bans()
                return True

            if re.match('браки', text):
                self.get_all_marry()
                return True

            if re.match('победители', text):
                self.get_duel(1)
                return True
            if re.match('F', text):
                self.get_duel(0)
                return True

        if re.match('развод', text):
            self.remove_married()
            return True

        if re.match('брак', text):
            text = text.replace(text[:5], '')
            if re.match('нет', text):
                self.delete_married()
                return True
            if re.match('да', text):
                self.save_married()
                return True
            users = self.parse_users(text)
            if users:
                self.get_married(users[0])
            return True

        if self.is_admin():
            if re.match('настройка', text):
                if self.settings(text.replace(text[:10], '')):
                    self.send_msg(msg="Сохранено!")
                return True

            if re.match('исключить собачек', text):
                self.dog_kick()
                return True

            if re.match('забанить человек', text):
                text = text.replace(text[:17], '')
                self.ban_last_users(int(text))
                self.send_msg(msg="Готово!")
                return True

            if re.match('снять', text):
                text = text.replace(text[:6], '')
                if re.match('пред', text):
                    users = self.parse_users(text)
                    if users:
                        self.pred_off(users)
                        self.send_msg(msg="Готово!")
                    return True

                if re.match('бан', text):
                    users = self.parse_users(text)
                    if users:
                        self.ban_off(users)
                        self.send_msg(msg="Готово!")
                    return True

            if re.match('ро', text):
                users = self.parse_users(text)
                if users:
                    self.ro(users)
                return True

            if re.match('бан', text):
                users = self.parse_users(text)
                if users:
                    self.ban(users)
                return True

            if re.match('пред', text):
                users = self.parse_users(text)
                if users:
                    self.pred(users)
                return True

            if re.match('кик', text):
                users = self.parse_users(text)
                if users:
                    self.kick(users)
                return True
        self.send_msg(msg="Эй, я не знаю такую команду или у вас нет доступа!")
        return False
