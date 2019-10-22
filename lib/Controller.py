# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
from random import randint
import re
import requests
import vk
from config import GROUP_ID
from models.User import add_user, try_user, find_user
from models.Chat import add_chat, try_chat, find_chat
from models.Marrieds import add_marrieds, done_marry, del_marry_all, del_marry, get_marryieds
from models.Stats import add_stats, find_all_stats_sum, find_all_stats_by_datetime, find_stats_user_and_chat
from models.StatsUser import add_stats_user, get_duel_die, get_duel_save, find_all_stats_user, find_stats_addit_user_and_chat, get_preds_db, get_bans_db, get_users_by_limit, find_all_users_by_msg
from models.Settings import add_set_default, get_null_settings, find_all_settings, settings_set, parser_settings, settings
from models.TypeSet import find_all_type_set
from models.Texts import add_text
import locale
import datetime
from lib.Actions import Actions
from lib.reactions import Reactions


class Controller:
    def __init__(self, update_object):
        print("Controller init")
        self.peer_id = update_object['peer_id']
        self.chat = find_chat(self.peer_id - 2000000000)
        self.user = find_user(update_object['from_id'])

        self.settings = parser_settings(self.chat.id)
        self.reply_message = False
        if update_object.get('reply_message') and len(update_object['reply_message']) != 0:
            self.reply_message = update_object['reply_message']
        self.attachments = update_object['attachments']
        self.text = update_object['text']
        
        print("chat: {0} user: {1}".format(self.chat.id, self.user.id))

        self.reactions = Reactions()
        self.actions = Actions(self.user.id, self.chat.id,
                               self.peer_id, self.settings[1])
        self.chat = self.actions.update_chat_data(self.chat)
        self.mini_request_for_reply = {
            "бан": self.actions.ban_user, "пред": self.actions.pred_user, "кик": self.actions.remove_chat_user}
        self.d = {'герой': {"actions": self.actions.get_hero, "params": [self.get_settings], },
                  'топ': {"actions": self.actions.get_top},
                  'все преды': {"actions": self.actions.get_all_list, "params": ["pred"]},
                  'все баны': {"actions": self.actions.get_all_list, "params": ["ban"]},
                  'все браки': {"actions": self.actions.get_all_marry},
                  'все победители': {"actions": self.actions.get_duel_stats, "params": [0]},
                  'все F': {"actions": self.actions.get_duel_stats, "params": [1]},
                  'развод': {"actions": self.actions.remove_married},
                  'брак нет': {"actions": self.actions.delete_married},
                  'брак да': {"actions": self.actions.save_married},
                  'брак': {"actions": self.actions.get_married, "params": [self.get_text], },

                  'выбери': {"actions": self.actions.get_choise, "params": [self.get_text]},
                  'инфа': {"actions": self.actions.get_inform},

                  'настройка': {"actions": self.actions.settings, "params": [self.get_text], "admin": True},
                  'добавить стоп-слово': {"actions": self.actions.add_stop, "params": [self.get_text], "admin": True},
                  'убрать стоп-слово': {"actions": self.actions.remove_stop, "params": [self.get_text], "admin": True},
                  'забанить человек': {"actions": self.actions.ban_last_users, "params": [self.get_text], "admin": True},
                  'исключить собачек': {"actions": self.actions.dog_kick, "admin": True},
                  'бан': {"actions": self.actions.ban_kick_pred_users, "params": [self.get_text, "ban"], "admin": True},
                  'кик': {"actions": self.actions.ban_kick_pred_users, "params": [self.get_text, "kick"], "admin": True},
                  'пред': {"actions": self.actions.ban_kick_pred_users, "params": [self.get_text, "pred"], "admin": True},
                  'ро': {"actions": self.actions.ban_kick_pred_users, "params": [self.get_text, "ro"], "admin": True},
                  'снять бан': {"actions": self.actions.un_users, "params": [self.get_text], "admin": True},
                  'снять пред': {"actions": self.actions.un_users, "params": [self.get_text], "admin": True},
                  'снять ро': {"actions": self.actions.un_users, "params": [self.get_text], "admin": True},
                  }

    def get_settings(self):
        return self.settings

    def get_text(self):
        return self.text

    def update_user_stats(self):
        stats = find_stats_user_and_chat(self.user.id, self.chat.id)
        isAttach = False
        if len(self.attachments) > 0:
            if self.attachments[0]['type'] == 'sticker':
                stats.count_stickers = stats.count_msgs + 1
                isAttach = True
            if self.attachments[0]['type'] == 'audio_message':
                stats.count_audio = stats.count_audio + 1
                isAttach = True
        if not isAttach:
            stats.count_msgs = stats.count_msgs + 1
        stats.save()

        stats = find_stats_addit_user_and_chat(self.user.id, self.chat.id)
        stats.len = stats.len + len(self.text)
        stats.date_time_last_msg = datetime.datetime.now()
        if len(self.text) > 5:
            stats.percent_divider = stats.percent_divider + 1
            sentiment = self.actions.parse_senstiment(self.text)
            print(sentiment)
            if sentiment.get('negative'):
                stats.percent_negative += sentiment.get('negative')
            if sentiment.get('neutral'):
                stats.percent_neutral += sentiment.get('neutral')
            if sentiment.get('positive'):
                stats.percent_positive += sentiment.get('positive')
                

        stats.lvl = self.update_level_msg(stats.lvl)
        stats.save()

    def update_level_msg(self, old):
        new_lvl = self.actions.get_need_lvl(old)
        if new_lvl != old:
            old = new_lvl
            if new_lvl > 1 and int(self.user.id) > 0:
                self.actions.send_msg(msg="@id{0} ({1}) получает {2} уровень!".format(
                    self.user.id, self.user.full_name, new_lvl))
        return old

    def add_text(self):
        add_text(self.user, self.chat, self.text, self.attachments)

    def stop_lines(self):
        if not self.get_is_admin():
            if self.settings[2]:
                self.actions.parse_mat(self.text)
            self.actions.parse_stop_lines(self.text)

    def get_reaction(self):
        reaction = self.reactions.message_handler(self.text)
        if reaction:
            self.actions.send_msg(msg=reaction)

    def get_is_admin(self):
        self.is_admin = self.actions.is_admin()
        return self.is_admin

    def is_mini_request_for_reply(self):
        if self.mini_request_for_reply.get(self.text.lower()) and self.reply_message and self.get_is_admin():
            self.mini_request_for_reply[self.text.lower()](
                self.reply_message.get('from_id'))

    def is_request_bot(self):
        if len(self.text) == 0:
            return False
        text = re.sub(
            r'^(работяга|\[club183796256\|\@kanbase\])(\s)?(,)?\s', '', self.text, flags=re.IGNORECASE)
        if len(text) < len(self.text):
            # убрать начальный текст
            self.text = text
            return True
        return False

    def parse_command(self):
        self.get_is_admin()  # сделать кэш
        for command in self.d:
            if re.match(command, self.text):
                self.text = self.text.replace(self.text[:len(command)], '')

                if self.d[command].get("params") and len(self.d[command]['params']) != 0:
                    if self.d[command].get("admin") and not self.is_admin:
                        self.actions.send_msg(
                            msg="Хм... Мне кажется, у меня нет прав администратора в этой беседе или команду вызвал обычный пользователь...")
                        return False
                    if len(self.d[command]['params']) > 1:
                        self.d[command]["actions"](
                            self.d[command]['params'][0], self.d[command]['params'][1])
                    else:
                        self.d[command]["actions"](
                            self.d[command]['params'][0])
                    return True
                else:
                    self.d[command]["actions"]()
                    return True

        self.actions.send_msg(
            msg="Мне кажется, я не знаю эту команду...")

    def update_user(self, from_id):
        return self.actions.update_user_data(from_id)

    def action_parser(self, action):
        if action['type'] == 'chat_invite_user':
            self.actions.is_chat_invite_user(action['member_id'])
        if action['type'] == 'chat_invite_user_by_link':
            self.actions.is_chat_invite_user(self.user.id)
        if action['type'] == 'chat_title_update':
            print("chat title")
        if action['type'] == 'chat_kick_user':
            print("kick_user or user_exit")

    def date_duel_kd(self, sec):
        if sec > 60:
            return str(sec/60) + " мин"
        else:
            return str(sec) + " сек"

    def duel(self):
        if self.text.lower() != "дуэль":
            return False
        if self.chat.date_last_duel and (datetime.datetime.now()-self.chat.date_last_duel).total_seconds() < self.settings[3]:
            self.actions.send_msg(
                msg="Дуэль уже состоялась, включен промежуток между дуэлями в {0}".format(self.date_duel_kd(self.settings[3])))
            return False
        if self.chat.duel_id == 0:
            self.actions.send_msg(
                msg="Хорошо, {0}, ждем твоего оппонента...".format(self.user.full_name))
            self.chat.duel_id = self.user.id
            self.chat.save()
            return True
        if self.chat.duel_id != self.user.id:
            self.actions.send_msg(
                msg="{0}, принял(-а) вызов!".format(self.user.full_name))
            if randint(0, 100) > 50:
                user_ = find_user(self.chat.duel_id)
                self.actions.send_msg(
                    msg="Произошла дуэль, {0} падает замертво. F".format(user_.full_name))
            else:
                self.actions.send_msg(
                    msg="Произошла дуэль, {0} падает замертво. F".format(self.user.full_name))
            self.chat.duel_id = 0
            self.chat.date_last_duel = datetime.datetime.now()
            self.chat.save()
            return True
        self.actions.send_msg(msg="Сам себя, F")
        self.chat.duel_id = 0
        self.chat.date_last_duel = datetime.datetime.now()
        self.chat.save()
        return True
