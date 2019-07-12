# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import os
from random import randint
from requests import post
from models import *
from config import *
import vk
import re
import message


session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)
longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']
db = DataBase()

while True:
    longPoll = post('%s' % server, data={'act': 'a_check',
                                         'key': key,
                                         'ts': ts,
                                         'wait': 25}).json()

    if longPoll.get('updates') and len(longPoll['updates']) != 0:
        db.open_connection()
        # Here `for` need to parallelize:
        for update in longPoll['updates']:
            exist = False
            print(update)
            if update['type'] == 'message_new':

                update = update['object']

                chat = find_chat_meth(int(update['peer_id'] - 2000000000))

                if update.get('action') and update['action']['type'] == 'chat_invite_user':
                    if update['action']['member_id'] < 0:
                        print("Here adding to chat another bot")
                    # If Emodis come to chat
                    if update['action']['member_id'] == -GROUP_ID:
                        # Getting user data from vk api
                        try:
                            chat_users = api.messages.getConversationMembers(
                                peer_id=update['peer_id'], group_id=GROUP_ID)
                            for chat_user in chat_users['profiles']:
                                user = find_user(int(chat_user['id']))
                                if not user[1]:
                                    name = api.users.get(
                                        user_ids=user[0].id)[0]
                                    user[0].full_name = name['first_name'] + \
                                        " " + name['last_name']
                                    user[0].save()
                        except vk.exceptions.VkAPIError:
                            print('not access')
                        # Adding user data to database
                        # Here `for` need to parallelize
                        # Hello, world^W chat!
                        api.messages.send(peer_id=update['peer_id'],
                                          random_id=randint(-2147483648,
                                                            2147483647),
                                          message='Привет, %s &#128521; Рекомендуем администратору беседы зайти на сайт' % update['peer_id'])
                else:
                    # Create Message object
                    msg = message.Message(update)

                    # Get chat data: chat name and count members
                    try:
                        chat_data = api.messages.getConversationsById(
                            peer_ids=update['peer_id'], group_id=GROUP_ID)
                        if chat_data['items']:
                            if chat_data['items'][0]:
                                chat.title = chat_data['items'][0]['chat_settings']['title']
                                chat.members_count = chat_data['items'][0]['chat_settings']['members_count']
                                chat.save()
                    except vk.exceptions.VkAPIError:
                        print('not access')
                    # Get user data from database
                    user = find_user(int(msg.from_id))

                    if not user[1]:
                        name = api.users.get(user_ids=user[0].id)[0]
                        user[0].full_name = name['first_name'] + \
                            " " + name['last_name']
                        user[0].save()
                    user = user[0]

                    # Here code need to parallelize:

                    stats = find_stats_user_and_chat(user.id, chat.id)
                    stats.count_msgs = stats.count_msgs + 1
                    stats.save()

                    stats = find_stats_addit_user_and_chat(user.id, chat.id)
                    stats.len = stats.len + len(msg.text)
                    stats.save()

                    add_text(user.id, chat.id, msg.text, msg.attachments)

                    # if settings.parse():

                    if msg.parse_bot():
                        if re.match('помощь', msg.text):
                            api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                0, 2147483647), message=get_help())
                            break

                        if re.match('выбери', msg.text):
                            api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                0, 2147483647), message=get_random_array(msg.text))
                            break

                        if re.match('инфа', msg.text):
                            api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                0, 2147483647), message=get_random(user.full_name))
                            break

                        #  Is getting from admin name
                        admin_exist = False
                        try:
                            chat_users = api.messages.getConversationMembers(
                                peer_id=msg.peer_id, group_id=GROUP_ID)['items']
                            for chat_user in chat_users:
                                if user.id == chat_user['member_id'] and chat_user.get('is_admin'):
                                    admin_exist = True
                                    break
                        except vk.exceptions.VkAPIError:
                            api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                0, 2147483647), message=not_access())

                        if admin_exist:
                            if re.match('установить пред', msg.text):
                                print("установка пред")

                            if re.match('снять пред', msg.text):
                                users = msg.parse_users()
                                if users:
                                    for user_data in users:
                                        if re.match('id', user_data.split('|')[0]):
                                            stats = find_stats_addit_user_and_chat(
                                                user_data.split('|')[0].split('id')[1], chat.id)
                                            stats.is_pred = 0
                                            stats.save()

                            if re.match('снять бан', msg.text):
                                users = msg.parse_users()
                                if users:
                                    for user_data in users:
                                        if re.match('id', user_data.split('|')[0]):
                                            stats = find_stats_addit_user_and_chat(
                                                user_data.split('|')[0].split('id')[1], chat.id)
                                            stats.is_banned = 0
                                            stats.save()

                            if re.match('исключить собачек', msg.text):
                                for chat_user in api.messages.getConversationMembers(peer_id=msg.peer_id, group_id=GROUP_ID)['profiles']:
                                    dog_exist = False
                                    if chat_user.get('deactivated'):
                                        try:
                                            api.messages.removeChatUser(
                                                chat_id=chat.id, member_id=chat_user['id'])
                                            dog_exist = True
                                        except vk.exceptions.VkAPIError:
                                            api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                                0, 2147483647), message=not_access())
                                            break
                                if dog_exist:
                                    api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                        0, 2147483647), message=get_delete_dogs())
                                else:
                                    api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                        0, 2147483647), message=get_delete_dogs_not())

                            if re.match('бан', msg.text):
                                # сделать когда участник входит в беседу - выкидывать
                                users = msg.parse_users()
                                if users:
                                    for user_data in users:
                                        if re.match('id', user_data.split('|')[0]):
                                            try:
                                                api.messages.removeChatUser(
                                                    chat_id=chat.id, member_id=user_data.split('|')[0].split('id')[1])
                                                stats = find_stats_addit_user_and_chat(
                                                    user_data.split('|')[0].split('id')[1], chat.id)
                                                stats.is_banned = 1
                                                stats.save()
                                            except vk.exceptions.VkAPIError:
                                                api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                                    0, 2147483647), message=not_access())

                            if re.match('пред', msg.text):
                                users = msg.parse_users()
                                if users:
                                    for user_data in users:
                                        if re.match('id', user_data.split('|')[0]):
                                            try:
                                                stats = find_stats_addit_user_and_chat(
                                                    user_data.split('|')[0].split('id')[1], chat.id)
                                                stats.is_pred = stats.is_pred + 1
                                                stats.save()
                                                if stats.is_pred == 3:
                                                    api.messages.removeChatUser(
                                                        chat_id=chat.id, member_id=user_data.split('|')[0].split('id')[1])
                                                else:
                                                    api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                                        0, 2147483647), message=get_pred(stats.is_pred, 3))

                                            except vk.exceptions.VkAPIError:
                                                api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                                    0, 2147483647), message=not_access())

                            if re.match('кик', msg.text):
                                users = msg.parse_users()
                                if users:
                                    for user_data in users:
                                        if re.match('id', user_data.split('|')[0]):
                                            try:
                                                api.messages.removeChatUser(
                                                    chat_id=chat.id, member_id=user_data.split('|')[0].split('id')[1])
                                            except vk.exceptions.VkAPIError:
                                                api.messages.send(peer_id=msg.peer_id, random_id=randint(
                                                    0, 2147483647), message=not_access())
        db.close_connection()
    if longPoll['ts']:
        ts = longPoll['ts']
