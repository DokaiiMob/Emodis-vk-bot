# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import os
from random import randint
from requests import post
from config import *
from objects.Mat import Mat
from objects.DataBase import *
from objects.User import *
from objects.Chat import *
from objects.Marrieds import *
from objects.Stats import *
from objects.StatsUser import *
from objects.Settings import *
from objects.TypeSet import *
from objects.Texts import *

import random
import vk
import re
import CommandHandler
from reactions import Reactions

session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)
ch = CommandHandler.CommandHandler(api)
db = DataBase()
reactions = Reactions()
mat = Mat()
longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']

while True:
    try:
        try:
            db.open_connection()
        except (peewee.OperationalError):
            print("connection")
    except (IntegrityError, OperationalError):
        db = DataBase()
        db.open_connection()

    print("new LongPoll post request")
    longPoll = post('%s' % server, data={'act': 'a_check',
                                         'key': key,
                                         'ts': ts,
                                         'wait': 25}).json()

    if longPoll.get('updates') and len(longPoll['updates']) != 0:
        for update in longPoll['updates']:
            ch.peer_id = int(update['object']['peer_id'])
            chat = find_chat(ch.peer_id - 2000000000)
            ch.peer_id, ch.chat_id = update['object']['peer_id'], chat.id

            settings = parser_settings(chat.id)
            block_url_chat = settings[0]
            ch.max_pred, ch.duel_kd = settings[1], settings[3]

            # # Get user data from database
            user = find_user(update['object']['from_id'])
            if user.id > 0 and len(user.full_name) == 0:
                user.full_name = ch.api_full_name(user.id)
                user.save()
            ch.user_id = user.id
            print("chat: {0} user: {1}".format(chat.id, user.id))

            if update['object'].get('action'):
                ch.action_parser(update['object']['action'])
            else:
                # Create Message object
                # update['object']['fwd_messages']
                reply_message = False
                if update['object'].get('reply_message') and len(update['object']['reply_message']) != 0:
                    reply_message = update['object']['reply_message']

                text, ch.con_msg_id, attachments = update['object']['text'], update['object'][
                    'conversation_message_id'], update['object']['attachments']

                print(text)

                stats = find_stats_user_and_chat(user.id, chat.id)

                isAttach = False
                if len(attachments) > 0:
                    if attachments[0]['type'] == 'sticker':
                        stats.count_stickers = stats.count_msgs + 1
                        isAttach = True
                    if attachments[0]['type'] == 'audio_message':
                        stats.count_audio = stats.count_audio + 1
                        isAttach = True

                if isAttach:
                    stats.count_msgs = stats.count_msgs + 1
                stats.save()

                stats = find_stats_addit_user_and_chat(user.id, chat.id)
                stats.len = stats.len + len(text)
                stats.date_time_last_msg = datetime.datetime.now()
                if int(stats.is_ro) == 1:
                    ch.delete_msg(ch.con_msg_id)

                new_lvl = ch.get_need_lvl(stats.lvl)
                if new_lvl != stats.lvl:
                    stats.lvl = new_lvl
                    if new_lvl > 1 and int(user.id) > 0:
                        ch.send_msg(msg="@id{0} ({1}) получает {2} уровень!".format(
                            user.id, user.full_name, new_lvl))
                stats.save()

                add_text(user.id, chat.id, text, attachments)

                if settings[2]:
                    if mat.check_slang(text) and int(user.id) > 0:
                        ch.give_pred_by_id(user.id, "Некультурно общаемся?")

                if re.match('дуэль', text.strip().lower()):
                    ch.duel(chat, user, stats)
                else:
                    is_reaction = reactions.message_handler(text)

                    if is_reaction:
                        ch.send_msg(msg=is_reaction)

                    if reply_message and ch.is_admin():
                        if re.match('бан', text.strip().lower()):
                            ch.ban_user(reply_message.get('from_id'))
                        if re.match('пред', text.strip().lower()):
                            ch.pred_user(reply_message.get('from_id'))
                        if re.match('кик', text.strip().lower()):
                            ch.remove_chat_user(reply_message.get('from_id'))

                    if not is_reaction:
                        handler = ch.parse_bot(text)
                        if handler[0]:
                            chat_data = ch.getConversationsById()
                            if chat_data:
                                chat.title, chat.members_count = chat_data['title'], chat_data['members_count']
                                chat.save()
                            text = handler[1]
                            ch.parse_command(text, user.id)
    db.close_connection()
    if longPoll.get('failed'):
        longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
        server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']
    ts = longPoll['ts']
