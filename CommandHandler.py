# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from random import randint
import re
import vk
from config import GROUP_ID
from models import get_pred, get_hello, find_user, not_access, find_all_users_by_msg, get_help, get_random, find_stats_addit_user_and_chat, get_delete_dogs_not, get_delete_dogs


class CommandHandler:
    chat_id = 0
    peer_id = 0
    user_id = 0

    def __init__(self, api):
        self.api = api

    def set_peer_id(self, peer_id):
        self.peer_id = peer_id

    def find_update_user(self, member_id):
        user = find_user(member_id)
        if len(user.full_name) == 0:
            user.full_name = self.api_full_name(user.id)
            user.save()

    def is_chat_invite_user(self, member_id):
        if member_id > 0:
            self.find_update_user(member_id)
            stats = find_stats_addit_user_and_chat(member_id, self.chat_id)
            if stats.is_banned == 1:
                self.remove_chat_user(member_id)

        if member_id < 0:
            print("Here adding to chat another bot")
        if member_id == -GROUP_ID:
            try:
                for chat_user in self.getConversationMembers():
                    self.find_update_user(chat_user['from_id'])
            except vk.exceptions.VkAPIError:
                self.send_msg(msg=get_hello(self.peer_id))

    def api_full_name(self, user_id):
        name = self.api.users.get(user_ids=user_id)[0]
        return "{0} {1}".format(name['first_name'], name['last_name'])

    def send_msg(self, msg):
        self.api.messages.send(peer_id=self.peer_id, random_id=randint(
            -2147483647, 2147483647), message=msg)

    def getConversationsById(self):
        chat_data = self.api.messages.getConversationsById(
            peer_ids=self.peer_id, group_id=GROUP_ID)
        if chat_data['items']:
            if chat_data['items'][0]:
                return chat_data['items'][0]['chat_settings']
        return False

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
            return True, text
        if re.match("\[club183796256\|\@emodis\],", text.lower()):
            text = text.replace(text[:24], '')
            text = text.strip()
            return True, text
        if re.match("\[club183796256\|\@emodis\]", text.lower()):
            text = text.replace(text[:23], '')
            text = text.strip()
            return True, text
        return False, text

    def parse_users(self, text):
        users = re.findall(r'\w+\|@?\w+', text)
        if not users:
            return False
        return users

    def get_top(self):
        msg = ''
        index = 1
        for s in find_all_users_by_msg(self.chat_id):
            name = self.api.users.get(user_ids=s.id_user)[0]
            msg += "#{0} {1} {2} {3}\n".format(index,
                                                name['first_name'], name['last_name'], s.len)
            index = index + 1
        self.send_msg(msg)

    def get_help(self):
        self.send_msg(msg=get_help())

    def get_choise(self, text):
        msg = text.replace(text[:6], '')
        array = msg.split('или')
        self.send_msg(msg="Я выбираю {0}".format(
            array[randint(0, len(array) - 1)]))

    def get_inform(self):
        self.send_msg(msg=get_random())

    def remove_chat_user(self, id):
        try:
            self.api.messages.removeChatUser(
                chat_id=self.chat_id, member_id=id)
            return True
        except vk.exceptions.VkAPIError:
            self.send_msg(msg=not_access())
            return False

    def pred(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                id = user.split('|')[0].split('id')[1]
                stats = find_stats_addit_user_and_chat(id, self.chat_id)
                stats.is_pred = stats.is_pred + 1
                stats.save()

                if stats.is_pred == 3:
                    # По сути надо выбирать что делать роботу
                    # stats.is_banned = 1
                    # stats.is_pred = 0
                    # self.send_msg(msg="Лимит предупреждений! Кик :-)")
                    # И парсить максимальное кол-во
                    self.remove_chat_user(id)
                self.send_msg(msg=get_pred(stats.is_pred, 3))

    def kick(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                self.remove_chat_user(user.split('|')[0].split('id')[1])

    def ban(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                id = user.split('|')[0].split('id')[1]
                stats = find_stats_addit_user_and_chat(id, self.chat_id)
                if self.remove_chat_user(id):
                    stats.is_banned = 1
                else:
                    stats.is_banned = 0
                stats.save()

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
            self.send_msg(msg=get_delete_dogs_not())
        else:
            self.send_msg(msg=get_delete_dogs())

    def is_admin(self):
        try:
            chat_users = self.api.messages.getConversationMembers(
                peer_id=self.peer_id, group_id=GROUP_ID)['items']
            for chat_user in chat_users:
                if self.user_id == chat_user['member_id'] and chat_user.get('is_admin'):
                    return True
        except vk.exceptions.VkAPIError:
            self.send_msg(msg=not_access())
            return False
        return False

    def parse_command(self, text, user_id):

        self.user_id = user_id

        if re.match('топ', text):
            self.get_top()
            return True

        if re.match('помощь', text):
            self.get_help()
            return True

        if re.match('выбери', text):
            self.get_choise(text)
            return True

        if re.match('инфа', text):
            self.get_inform()
            return True

        if re.match('преды', text):
            # self.get_inform()
            return True

        if re.match('баны', text):
            # self.get_inform()
            return True

        if re.match('браки', text):
            # self.get_inform()
            return True

        if re.match('баны', text):
            # self.get_inform()
            return True

        if self.is_admin():
            if re.match('установить пред', text):
                return True

            if re.match('исключить собачек', text):
                self.dog_kick()
                return True

            if re.match('снять пред', text):
                users = self.parse_users(text)
                if users:
                    self.pred_off(users)
                    self.send_msg(msg="Готово!")
                return True

            if re.match('снять бан', text):
                users = self.parse_users(text)
                if users:
                    self.ban_off(users)
                    self.send_msg(msg="Готово!")
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
