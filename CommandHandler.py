# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from random import randint
import re
import vk
from config import GROUP_ID
from models import *


class CommandHandler:

    def __init__(self, api):
        self.api = api

    def set_peer_id(self, peer_id):
        self.peer_id = peer_id

    def is_chat_invite_user(self, member_id, peer_id):
        if member_id > 0:
            user = find_user(member_id)
            if len(user.full_name) == 0:
                user.full_name = ch.api_full_name(user.id)
                user.save()
        if member_id < 0:
            print("Here adding to chat another bot")
        if member_id == -GROUP_ID:
            try:
                for chat_user in self.getConversationMembers(peer_id):
                    user = find_user(chat_user['from_id'])
                    if len(user.full_name) == 0:
                        user.full_name = self.api_full_name(user.id)
                        user.save()
            except vk.exceptions.VkAPIError:
                self.send_msg(msg=get_hello(peer_id))

    def api_full_name(self, user_id):
        name = self.api.users.get(user_ids=user_id)[0]
        return '%s %s', name['first_name'], name['last_name']

    def send_msg(self, msg):
        self.api.messages.send(peer_id=self.peer_id, random_id=randint(
            0, 2147483647), message=msg)

    def getConversationsById(self, peer_id):
        chat_data = self.api.messages.getConversationsById(
            peer_ids=peer_id, group_id=GROUP_ID)
        if chat_data['items']:
            if chat_data['items'][0]:
                return chat_data['items'][0]['chat_settings']['title'], chat_data['items'][0]['chat_settings']['members_count']
        return False

    def getConversationMembers(self, peer_id):
        return self.api.messages.getConversationMembers(peer_id=peer_id, group_id=GROUP_ID)['profiles']

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
            msg += '№%s %s %s %s\n' % str(
                index),  name['first_name'], name['last_name'], str(s.len)
            index = index + 1
        self.send_msg(msg)

    def get_help(self):
        self.send_msg(msg=get_help())

    def get_choise(self, text):
        self.send_msg(msg=get_random_array(text))

    def get_inform(self):
        self.send_msg(msg=get_random())

    def get_pred(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                try:
                    stats = find_stats_addit_user_and_chat(
                        user.split('|')[0].split('id')[1], self.chat_id)
                    stats.is_pred = stats.is_pred + 1
                    stats.save()
                    if stats.is_pred == 3:
                        self.api.messages.removeChatUser(
                            chat_id=self.chat_id, member_id=user.split('|')[0].split('id')[1])
                    else:
                        self.send_msg(msg=get_pred(stats.is_pred, 3))
                except vk.exceptions.VkAPIError:
                    self.send_msg(msg=not_access())

    def get_kick(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                try:
                    self.api.messages.removeChatUser(
                        chat_id=self.chat_id, member_id=user.split('|')[0].split('id')[1])
                except vk.exceptions.VkAPIError:
                    self.send_msg(msg=not_access())

    def get_ban(self, users):
        # сделать когда участник входит в беседу - выкидывать
        for user in users:
            if re.match('id', user.split('|')[0]):
                try:
                    self.api.messages.removeChatUser(
                        chat_id=self.chat_id, member_id=user.split('|')[0].split('id')[1])
                    stats = find_stats_addit_user_and_chat(
                        user.split('|')[0].split('id')[1], self.chat_id)
                    stats.is_banned = 1
                    stats.save()
                except vk.exceptions.VkAPIError:
                    self.send_msg(msg=not_access())

    def ban_off(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                stats = find_stats_addit_user_and_chat(
                    user.split('|')[0].split('id')[1], self.chat_id)
                stats.is_banned = 0
                stats.save()

    def pred_off(self, users):
        for user in users:
            if re.match('id', user.split('|')[0]):
                stats = find_stats_addit_user_and_chat(
                    user.split('|')[0].split('id')[1], self.chat_id)
                stats.is_pred = 0
                stats.save()

    def dog_kick(self):
        for chat_user in self.api.messages.getConversationMembers(peer_id=self.peer_id, group_id=GROUP_ID)['profiles']:
            dog_exist = False
            if chat_user.get('deactivated'):
                try:
                    self.api.messages.removeChatUser(
                        chat_id=self.chat_id, member_id=chat_user['id'])
                    dog_exist = True
                except vk.exceptions.VkAPIError:
                    self.send_msg(msg=not_access())
                    break
        if not dog_exist:
            self.send_msg(msg=get_delete_dogs())
        else:
            self.send_msg(msg=get_delete_dogs_not())

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

    def parse_command(self, peer_id, text, user_id, chat_id):

        self.peer_id = peer_id
        self.chat_id = chat_id
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
                    self.get_ban(users)
                return True

            if re.match('пред', text):
                users = self.parse_users(text)
                if users:
                    self.get_pred(users)
                return True

            if re.match('кик', text):
                users = self.parse_users(text)
                if users:
                    self.get_kick(users)
                return True
