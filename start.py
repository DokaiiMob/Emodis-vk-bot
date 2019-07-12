# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import os
from random import randint
from requests import post
from models import *
from config import *
import vk
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
        for update in longPoll['updates']:
            exist = False
            print(update)
            if update['type'] == 'message_new':

                update = update['object']

                chat = find_chat_meth(int(update['peer_id'] - 2000000000))

                if update.get('action') and update['action']['type'] == 'chat_invite_user':
                    if update['action']['member_id'] < 0:
                        print("Here adding to chat another bot")
                    if update['action']['member_id'] == -GROUP_ID:
                        api.messages.send(peer_id=update['peer_id'],
                                          random_id=randint(-2147483648,
                                                            2147483647),
                                          message='Привет, %s &#128521; Рекомендуем администратору беседы зайти на сайт' % update['peer_id'])
                else:
                    msg = message.Message(update)

                    user = find_user(int(msg.from_id))
                    if not user[1]:
                        name = api.users.get(user_ids=user[0].id)[0]
                        update_user_name(
                            user[0].id, name['first_name'] + " " + name['last_name'])
                    user = user[0]

                    stats = find_stats_user_and_chat(user.id, chat.id)
                    update_stats(stats.id, stats.count_msgs, 'msg')

                    stats = find_stats_addit_user_and_chat(user.id, chat.id)
                    update_stats_user(stats.id, len(msg.text), 'len')

                    add_text(user.id, chat.id, msg.text, msg.attachments)

                    # if settings.parse():

                    if msg.parse_bot():
                        command = msg.parse_command()
                        if command[1] == 'msg':
                            if command[0] == 'help':
                                messg = 'Привет, тебе)'
                            if command[0] == '':
                                messg = 'Шо? Бан захотели?'
                            if command[0] == 'random':
                                messg = randint(-2147483648, 2147483647)
                            api.messages.send(
                                peer_id=msg.peer_id, random_id=randint(-2147483648, 2147483647), message=messg)
                        if command[1] == 'do':
                            if command[0] == 'kick':
                                # работяга кик [id385818590|@daniilakk]
                                print(msg.text)
        db.close_connection()

    ts = longPoll['ts']
