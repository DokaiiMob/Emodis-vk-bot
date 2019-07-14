# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import os
from random import randint
from requests import post
from models import *
from config import *
import vk
import re


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
        print(longPoll)
        db.open_connection()
        # Here `for` need to parallelize:
        for update in longPoll['updates']:
            exist = False
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
                    text = update['text']
                    peer_id = update['peer_id']
                    attachments = update['attachments']

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
                    user = find_user(int(update['from_id']))

                    if not user[1] and user[0].id > 0:
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
                    stats.len = stats.len + len(text)
                    stats.save()

                    add_text(user.id, chat.id, text, attachments)

                    # if settings.parse():
                    handler = parse_bot(text)
                    if handler[0]:
                        text = handler[1]
                        if re.match('топ', text) and not exist:
                            stats_msg = ''
                            index = 1
                            for s in find_all_users_by_msg(chat.id):
                                name = api.users.get(user_ids=s.id_user)[0]
                                stats_msg += str(index) + ' ' + \
                                    name['first_name'] + " " + \
                                    name['last_name'] + ' ' + str(s.len) + '\n'
                                index = index + 1
                            # print(stats_msg)
                            api.messages.send(peer_id=peer_id, random_id=randint(
                                0, 2147483647), message=stats_msg)
                            exist = True

                        if re.match('помощь', text) and not exist:
                            api.messages.send(peer_id=peer_id, random_id=randint(
                                0, 2147483647), message=get_help())
                            exist = True

                        if re.match('выбери', text) and not exist:
                            api.messages.send(peer_id=peer_id, random_id=randint(
                                0, 2147483647), message=get_random_array(text))
                            exist = True

                        if re.match('инфа', text) and not exist:
                            api.messages.send(peer_id=peer_id, random_id=randint(
                                0, 2147483647), message=get_random(user.full_name))
                            exist = True

                        #  Is getting from admin name
                        admin_exist = False
                        try:
                            chat_users = api.messages.getConversationMembers(
                                peer_id=peer_id, group_id=GROUP_ID)['items']
                            for chat_user in chat_users:
                                if user.id == chat_user['member_id'] and chat_user.get('is_admin'):
                                    admin_exist = True
                                    break
                        except vk.exceptions.VkAPIError:
                            api.messages.send(peer_id=peer_id, random_id=randint(
                                0, 2147483647), message=not_access())

                        if admin_exist and not exist:
                            if re.match('установить пред', text):
                                print("установка пред")

                            if re.match('снять пред', text):
                                users = parse_users(text)
                                if users:
                                    for user_data in users:
                                        if re.match('id', user_data.split('|')[0]):
                                            stats = find_stats_addit_user_and_chat(
                                                user_data.split('|')[0].split('id')[1], chat.id)
                                            stats.is_pred = 0
                                            stats.save()

                            if re.match('снять бан', text):
                                users = parse_users(text)
                                if users:
                                    for user_data in users:
                                        if re.match('id', user_data.split('|')[0]):
                                            stats = find_stats_addit_user_and_chat(
                                                user_data.split('|')[0].split('id')[1], chat.id)
                                            stats.is_banned = 0
                                            stats.save()

                            if re.match('исключить собачек', text):
                                for chat_user in api.messages.getConversationMembers(peer_id=peer_id, group_id=GROUP_ID)['profiles']:
                                    dog_exist = False
                                    if chat_user.get('deactivated'):
                                        try:
                                            api.messages.removeChatUser(
                                                chat_id=chat.id, member_id=chat_user['id'])
                                            dog_exist = True
                                        except vk.exceptions.VkAPIError:
                                            api.messages.send(peer_id=peer_id, random_id=randint(
                                                0, 2147483647), message=not_access())
                                            break
                                if dog_exist:
                                    api.messages.send(peer_id=peer_id, random_id=randint(
                                        0, 2147483647), message=get_delete_dogs())
                                else:
                                    api.messages.send(peer_id=peer_id, random_id=randint(
                                        0, 2147483647), message=get_delete_dogs_not())

                            if re.match('бан', text):
                                # сделать когда участник входит в беседу - выкидывать
                                users = parse_users(text)
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
                                                api.messages.send(peer_id=peer_id, random_id=randint(
                                                    0, 2147483647), message=not_access())

                            if re.match('пред', text):
                                users = parse_users(text)
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
                                                    api.messages.send(peer_id=peer_id, random_id=randint(
                                                        0, 2147483647), message=get_pred(stats.is_pred, 3))

                                            except vk.exceptions.VkAPIError:
                                                api.messages.send(peer_id=peer_id, random_id=randint(
                                                    0, 2147483647), message=not_access())

                            if re.match('кик', text):
                                users = parse_users(text)
                                if users:
                                    for user_data in users:
                                        if re.match('id', user_data.split('|')[0]):
                                            try:
                                                api.messages.removeChatUser(
                                                    chat_id=chat.id, member_id=user_data.split('|')[0].split('id')[1])
                                            except vk.exceptions.VkAPIError:
                                                api.messages.send(peer_id=peer_id, random_id=randint(
                                                    0, 2147483647), message=not_access())
        db.close_connection()
    try:
        ts = longPoll['ts']
    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))
