# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import os
from random import randint
from requests import post
from models import *
from config import *
import vk
import re
import CommandHandler


session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)
ch = CommandHandler.CommandHandler(api)
db = DataBase()

while True:
    longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
    server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']
    longPoll = post('%s' % server, data={'act': 'a_check',
                                         'key': key,
                                         'ts': ts,
                                         'wait': 25}).json()

    if longPoll.get('updates') and len(longPoll['updates']) != 0:
        try:
            db.open_connection()
        except (IntegrityError, OperationalError):
            db = DataBase()
            db.open_connection()
        # Here `for` need to parallelize:
        for update in longPoll['updates']:
            if update['type'] != 'message_new':
                continue
            update = update['object']
            # print(update)

            ch.peer_id = update['peer_id']

            chat = find_chat_meth(int(update['peer_id'] - 2000000000))
            ch.chat_id = chat.id
            try:
                chat_data = ch.getConversationsById()
                if chat_data:
                    chat.title, chat.members_count = chat_data['title'], chat_data['members_count']
                    chat.save()
            except vk.exceptions.VkAPIError:
                print('not access')

            # settings parse
            bot_on = True
            block_url_chat = False
            block_mat = False
            for settings in find_all_settings(chat.id):
                id_type = int(settings.id_type.id)
                if id_type == 1 and int(settings.val) == 0:
                    bot_on = False
                block_url_chat = id_type == 2 and int(settings.val) == 1
                block_mat = id_type == 4 and int(settings.val) == 1
                if id_type == 3:
                    ch.max_pred = int(settings.val)
            
            if update.get('action'):
                if update['action']['type'] == 'chat_invite_user':
                    ch.is_chat_invite_user(
                        update['action']['member_id'])
                if update['action']['type'] == 'chat_invite_user_by_link':
                    ch.is_chat_invite_user(update['from_id'])
                if update['action']['type'] == 'chat_title_update':
                    print("chat title")
                if update['action']['type'] == 'chat_kick_user':
                    print("kick_user or user_exit")
                continue

            # Create Message object
            text = update['text']
            attachments = update['attachments']

            # Get user data from database
            user = find_user(update['from_id'])
            if user.id > 0 and len(user.full_name) == 0:
                user.full_name = ch.api_full_name(user.id)
                user.save()

            print(user.id)
            ch.user_id = user.id
            print(chat.id)

            stats = find_stats_user_and_chat(user.id, chat.id)
            stats.count_msgs = stats.count_msgs + 1
            stats.save()

            stats = find_stats_addit_user_and_chat(user.id, chat.id)
            stats.len = stats.len + len(text)
            stats.save()

            add_text(user.id, chat.id, text, attachments)

            if block_mat and ch.check_slang(text):
                ch.give_pred_by_id(user.id, "Мат в чате.")

            if bot_on:
                handler = ch.parse_bot(text)
                if handler[0]:
                    text = handler[1]
                    ch.parse_command(text, user.id)
        db.close_connection()

    if longPoll.get('ts') and len(longPoll['ts']) != 0:
        ts = longPoll['ts']

    if longPoll.get('failed'):
        longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
        server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']
