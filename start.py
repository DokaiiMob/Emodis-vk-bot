# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import os
from random import randint
from requests import post
from models import *
from config import *
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

    print("while")
    longPoll = post('%s' % server, data={'act': 'a_check',
                                         'key': key,
                                         'ts': ts,
                                         'wait': 25}).json()

    if longPoll.get('updates') and len(longPoll['updates']) != 0:
        for update in longPoll['updates']:
            updateNew = update['object']
            ch.peer_id = updateNew['peer_id']

            chat = find_chat_meth(int(updateNew['peer_id'] - 2000000000))
            ch.chat_id = chat.id

            # chat_data = ch.getConversationsById()
            # if chat_data:
            #     chat.title, chat.members_count = chat_data['title'], chat_data['members_count']
            #     chat.save()

            # settings parse
            # block_url_chat = False
            # block_mat = False
            # for settings in find_all_settings(chat.id):
            # id_type = int(settings.id_type.id)
            # block_mat = id_type == 4 and int(settings.val) == 1
            # block_url_chat = id_type == 2 and int(settings.val) == 1
            #     if id_type == 3:
            #         ch.max_pred = int(settings.val)

            if updateNew.get('action'):
                if updateNew['action']['type'] == 'chat_invite_user':
                    ch.is_chat_invite_user(
                        updateNew['action']['member_id'])
                if updateNew['action']['type'] == 'chat_invite_user_by_link':
                    ch.is_chat_invite_user(updateNew['from_id'])
                if updateNew['action']['type'] == 'chat_title_update':
                    print("chat title")
                if updateNew['action']['type'] == 'chat_kick_user':
                    print("kick_user or user_exit")
            else:
                # Create Message object
                print(updateNew)
                send_id_message = 0
                text = updateNew['text']
                fwd_messages = updateNew['fwd_messages']
                reply_message = False
                if updateNew.get('reply_message')  and len(updateNew['reply_message']) != 0:
                    reply_message = updateNew['reply_message']
                
                conversation_message_id = updateNew['conversation_message_id']
                ch.con_msg_id = conversation_message_id
                attachments = updateNew['attachments']

                # # Get user data from database
                user = find_user(updateNew['from_id'])
                if user.id > 0 and len(user.full_name) == 0:
                    user.full_name = ch.api_full_name(user.id)
                    user.save()

                ch.user_id = user.id
                print("chat: {0} user: {1}".format(chat.id, user.id))

                stats = find_stats_user_and_chat(user.id, chat.id)
                stats.count_msgs = stats.count_msgs + 1
                stats.save()

                stats = find_stats_addit_user_and_chat(user.id, chat.id)
                stats.len = stats.len + len(text)

                # # if int(stats.is_ro) == 1:
                # #     ch.delete_msg(conversation_message_id)

                new_lvl = ch.get_need_lvl(stats.lvl)
                if new_lvl != stats.lvl:
                    stats.lvl = new_lvl
                    if new_lvl > 1 and int(user.id) > 0:
                        ch.send_msg(msg="@id{0} ({1}) получает {2} уровень!".format(
                            user.id, user.full_name, new_lvl))
                stats.save()

                add_text(user.id, chat.id, text, attachments)
                print("added")

                # if block_mat:
                # if chat.id != 4 and ch.check_slang(text) and int(user.id) > 0:
                #     ch.give_pred_by_id(user.id, "Некультурно общаемся?")

                if re.match('дуэль', text.strip().lower()):
                    if chat.id != 4 and chat.date_last_duel and (datetime.datetime.now()-chat.date_last_duel).total_seconds() < 60:
                        ch.send_msg(
                            msg="Дуэль уже состоялась, проводятся один раз в минуту")
                    else:
                        if chat.duel_id == 0:
                            ch.send_msg(msg="Хорошо, @id{0} ({1}), ждем твоего оппонента...".format(
                                user.id, user.full_name))
                            chat.duel_id = user.id
                            chat.save()
                        else:
                            if chat.duel_id != user.id:
                                ch.send_msg(msg="@id{0} ({1}), принял вызов!".format(
                                    user.id, user.full_name))
                                if randint(0, 100) > 50:
                                    user_ = find_user(chat.duel_id)
                                    ch.send_msg(msg="Произошла дуэль, @id{0} ({1}) падает замертво. F".format(
                                        user_.id, user_.full_name))
                                    stats.count_duel_save = stats.count_duel_save + 1
                                    stats.save()
                                    stats_ = find_stats_addit_user_and_chat(
                                        chat.duel_id, chat.id)
                                    stats_.count_duel_die = stats.count_duel_die + 1
                                    stats_.save()
                                else:
                                    ch.send_msg(msg="Произошла дуэль, @id{0} ({1}) падает замертво. F".format(
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
                            else:
                                ch.send_msg(msg="Сам себя, F")
                                chat.duel_id = 0
                                stats.count_duel_die = stats.count_duel_die + 1
                                chat.date_last_duel = datetime.datetime.now()
                                stats.save()
                                chat.save()
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
                            text = handler[1]
                            ch.parse_command(text, user.id)

    db.close_connection()
    if longPoll.get('failed'):
        longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
        server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']
    ts = longPoll['ts']
    print(ts)
