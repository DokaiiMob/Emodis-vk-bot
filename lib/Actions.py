# /usr/bin/env python3.7
# -*- coding: utf-8 -*-
from random import randint, choice
import vk
import re
import requests
from config import GROUP_ID
from models.User import add_user, try_user, find_user
from models.Chat import add_chat, try_chat, find_chat
from models.Marrieds import add_marrieds, done_marry, del_marry_all, del_marry, get_marryieds
from models.Stats import add_stats, find_all_stats_sum, find_all_stats_by_datetime, find_stats_user_and_chat
from models.StatsUser import add_stats_user, get_duel_die, get_duel_save, find_all_stats_user, find_stats_addit_user_and_chat, get_preds_db, get_bans_db, get_users_by_limit, find_all_users_by_msg
from models.Settings import add_set_default, get_null_settings, find_all_settings, settings_set, parser_settings, settings, getListChats
from models.TypeSet import find_all_type_set
from models.Texts import add_text
from models.StopLines import add_stop_line, remove_stop_line, getting_stop_lines
from lib.Requests import Requests
from lib.Mat import mat
import locale
import datetime


class Actions:
    peer_id = 0

    def __init__(self, user_id, chat_id, peer_id, max_pred):
        # print("Actions init")
        self.is_ban_or_kik = False
        self.user_id = user_id
        self.chat_id = chat_id
        self.peer_id = peer_id
        self.max_pred = max_pred
        self.requests = Requests(peer_id, chat_id)

    def ban_user(self, id):
        stats = find_stats_addit_user_and_chat(id, self.chat_id)
        stats.is_banned = 1 if self.remove_chat_user(id) else 0
        stats.save()
    def ban_user_by_id(self, id, chat_id):
        stats = find_stats_addit_user_and_chat(id, chat_id)
        stats.is_banned = 1 if self.requests.remove_chat_user_by_chat_id(id, chat_id) else 0
        stats.save()

    def pred_user(self, id, text = ""):
        stats = find_stats_addit_user_and_chat(id, self.chat_id)
        stats.is_pred = stats.is_pred + 1
        self.requests.send_msg(msg="{0} Предупреждение {1} из {2}".format(
            text, stats.is_pred, self.max_pred))
        if int(stats.is_pred) >= int(self.max_pred):
            # По сути надо выбирать что делать роботу
            # stats.is_banned = 1
            stats.is_pred = 0
            self.requests.send_msg(msg="Лимит предупреждений! Кик :-)")
            # И парсить максимальное кол-во
            self.remove_chat_user(id)
        stats.save()
        
    def remove_chat_user(self, id):
        return self.requests.remove_chat_user(id)

    def send_msg(self, msg):
        self.requests.send_msg(msg)

    def get_need_lvl(self, old):
        all_count_msgs = find_all_stats_sum(
            self.user_id, self.chat_id).count_msgs
        if round(int(all_count_msgs) ** 0.2) > old:
            return round(int(all_count_msgs) ** 0.2)
        else:
            return old

    def is_admin(self):
        chat_users = self.requests.getConversationMembers()
        if chat_users:
            for chat_user in chat_users['items']:
                if self.user_id == chat_user['member_id'] and chat_user.get('is_admin'):
                    return True
        return False

    def update_user_data(self, from_id):
        self.from_id = from_id
        user = find_user(from_id)
        now = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(now)
        if user.cache_repeat + 13600 < timestamp and user.id > 0:
            user.full_name = self.requests.api_full_name(user.id)
            user.cache_repeat = timestamp
            user.save()
        self.user_id = user.id
        return user

    def update_chat_data(self, chat):
        now = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(now)

        if chat.cache_repeat + 3600 < timestamp:
            chat_data = self.requests.getConversationsById()
            if chat_data:
                chat.title, chat.members_count = chat_data[
                    'title'], chat_data['members_count']
            else:
                chat.title = chat.title
            chat.cache_repeat = timestamp
            chat.save()
        return chat

    def bot_come_to_chat(self):
        members = self.requests.getConversationMembers()
        if not members:
            self.requests.send_msg(
                msg="Привет, чат №{0} &#128521; Рекомендуем выдать доступ к переписке!".format(self.peer_id))
            return True
        for chat_user in members['profiles']:
            self.requests.find_update_user(chat_user['from_id'])

        self.requests.send_msg(
            msg="Привет, чат №{0} &#128521; Напиши: Работяга помощь".format(self.chat_id))
        return True

    def is_chat_invite_user(self, member_id):
        if member_id > 0:
            self.requests.find_update_user(member_id)
            stats = find_stats_addit_user_and_chat(member_id, self.chat_id)
            if stats.is_banned == 1:
                self.requests.remove_chat_user(member_id)
        if member_id == -GROUP_ID:
            self.bot_come_to_chat()

    def get_hero(self, get_settings):
        users = self.requests.getConversationMembers()

        if users:
            settings_array = get_settings()
            today = int(datetime.date.today().strftime("%j"))
            if today != settings_array[5]:
                choice_id = choice(users['profiles'])['id']
                self.requests.send_msg(
                    msg="Герой дня на сегодня ... @id{0}".format(choice_id))
                settings_set(self.chat_id, 6, today)
                settings_set(self.chat_id, 1, choice_id)
            else:
                self.requests.send_msg(
                    msg="Герой дня на сегодня уже выбран @id{0}".format(settings_array[4]))
        else:
            self.requests.send_msg(
                msg="У меня нет доступа к участникам беседы...")
        return True

    def get_top(self):
        self.send_msg(
            msg="Статистика: kanbase.ru/c/{0}".format((self.chat_id)))  # *0x45785
        return True
    
    def get_help(self):
        self.send_msg(msg="Привет! Держи ссылку на команды: https://vk.com/@kanbase-komandy-bota")
        return True

    def get_all_list(self, params):
        if params == "pred":
            msg = 'Все предупреждения:\n'
            arr_p = get_preds_db(self.chat_id, self.user_id)
        else:
            msg = 'Все блокировки:\n'
            arr_p = get_bans_db(self.chat_id, self.user_id)
        index = 1
        exist = False
        for p in arr_p:
            exist = True
            msg += "#{0} {1} {2}\n".format(index,
                                           p.id_user.full_name, p.is_pred)
            index = index + 1
        if exist:
            self.requests.send_msg(msg=msg)
        else:
            if params == "pred":
                self.requests.send_msg(msg="Предупреждений в чате нет")
            else:
                self.requests.send_msg(msg="Блокировок в чате нет")
        return True

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
            self.requests.send_msg(msg=msg)
        else:
            self.requests.send_msg(msg="Браков ещё нет")
        return True

    def get_duel_stats(self, type):
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
            self.requests.send_msg(msg=msg)
        else:
            self.requests.send_msg(msg="Дуэлей ещё не было")
        return True

    def remove_married(self):
        if del_marry_all(self.chat_id, self.user_id):
            self.requests.send_msg(msg="Брак аннулирован:)")
        return True

    def delete_married(self):
        if del_marry(self.chat_id, self.user_id):
            self.send_msg(msg="В браке отказано:)")

    def save_married(self):
        if done_marry(self.chat_id, self.user_id):
            self.requests.send_msg(msg="Поздравляю:)")
        return True

    def get_married(self, text, is_may):
        if is_may:
            self.requests.send_msg(msg="Творческий режим выключен")
            return True
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="Выберите участника беседы через @")
            return True
        if len(users) > 1:
            self.requests.send_msg(msg="Больше двух участников нельзя)")
            return True
        marryed = add_marrieds(self.user_id, users[0], self.chat_id)
        if marryed == 1:
            self.requests.send_msg(
                msg="Нужно подтвердить другому участнику, написав Работяга брак да/нет")
        else:
            self.requests.send_msg(msg="Брак невозможен")
        return True

    def get_choise(self, text):
        self.requests.send_msg(msg="Я выбираю {0}".format(
            choice(text().split('или')).strip()))

    def get_inform(self):
        self.requests.send_msg(
            msg="Вероятность составляет {0}%".format(randint(0, 100)))
        return True

    def settings(self, text):
        text_array = text().strip().split(' ')
        if len(text_array) >= 2:
            try:
                type_set = int(text_array[0])
            except:
                return False
            val = text_array[1]
            if type_set == 1:
                try:
                    val = int(val)
                except:
                    return False
                if val == 0 or val == 1:
                    settings_set(self.chat_id, type_set, val)
                    self.requests.send_msg(msg="Сохранено!")
                    return True
            if type_set == 2:
                try:
                    val = int(val)
                except:
                    return False
                if val == 0 or val == 1:
                    settings_set(self.chat_id, type_set, val)
                    self.requests.send_msg(msg="Сохранено!")
                    return True
            if type_set == 3:
                settings_set(self.chat_id, type_set, val)
                self.requests.send_msg(msg="Сохранено!")
                return True
            if type_set == 4:
                try:
                    val = int(val)
                except:
                    return False
                if val == 0 or val == 1:
                    settings_set(self.chat_id, type_set, val)
                    self.requests.send_msg(msg="Сохранено!")
                    return True
            if type_set == 5:
                try:
                    val = int(val)
                except:
                    return False
                settings_set(self.chat_id, type_set, val)
                self.requests.send_msg(msg="Сохранено!")
                return True
            if type_set == 7:
                val = val.replace(' ', '')
                settings_set(self.chat_id, type_set, val)
                self.requests.send_msg(msg="Сохранено!")
                return True
        return False

    def ban_last_users(self, count):
        if len(count()) == 0:
            self.send_msg("Напишите сколько человек")
            return True
        for users in get_users_by_limit(self.chat_id, int(count())):
            self.ban_user(users.id_user)
        return True

    def dog_kick(self):
        users = self.requests.getConversationMembers()
        if users:
            for chat_user in users['profiles']:
                dog_exist = False
                if chat_user.get('deactivated'):
                    if self.remove_chat_user(chat_user['id']):
                        dog_exist = True
            if not dog_exist:
                self.requests.send_msg(msg="Собачек нет!")
            else:
                self.requests.send_msg(msg="Собачек больше нет!")
        return True

    def ban_kick_pred_users(self, text, type):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            if type == "ban":
                self.requests.send_msg(msg="И кого мне банить?")
            if type == "kick":
                self.requests.send_msg(msg="И кого мне кикать?")
            if type == "pred":
                self.requests.send_msg(msg="И кому мне давать предупреждение?")
            if type == "ro":
                self.requests.send_msg(msg="И кому мне давать ReadOnly?")
            return True
        for user in users:
            if type == "ban":
                self.ban_user(user)
            if type == "kick":
                self.remove_chat_user(user)
            if type == "pred":
                self.pred_user(user)
            # if type == "ro":
                # print("")
        return True
    
    def superban_user(self, id):
        listChats = getListChats(self.chat_id, settings)
        if not listChats or len(listChats) == 0:
            self.requests.send_msg(msg="Не настроено")
            return True
        for chatL in listChats:
            self.ban_user_by_id(user, chatL)
            stats = find_stats_addit_user_and_chat(id, chatL)
            stats.is_banned = 1 if self.requests.remove_chat_user_by_chat_id(id, chatL) else 0
            stats.save()

    
    def superban(self, text, settings):
        # print(settings)
        listChats = getListChats(self.chat_id, settings)
        if not listChats or len(listChats) == 0:
            self.requests.send_msg(msg="Не настроено")
            return True
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="И кого мне банить?")
            return True
        for user in users:
            # self.ban_user(user)
            for chatL in listChats:
                self.ban_user_by_id(user, chatL)
        return True

    def un_users(self, text):
        users = re.findall(r'id(\d+)\|@?', text())
        if len(users) == 0:
            self.requests.send_msg(msg="Ну выберите кого-нибудь...")
            return True
        for user in users:
            stats = find_stats_addit_user_and_chat(user, self.chat_id)
            stats.is_banned = 0
            stats.is_pred = 0
            stats.save()
        self.requests.send_msg(msg="Готово!")

    def remove_stop(self, text):
        remove_stop_line(self.chat_id, text())
        self.requests.send_msg(msg="Готово!")

    def add_stop(self, text):
        tmp = text().split()
        if len(tmp) != 2:
            self.requests.send_msg(
                msg="Введите в формате Работяга добавить стоп-слово СЛОВО X")
            return False
        type_stop = 0
        if len(tmp[1]) == 0:
            type_stop = 0
        else:
            type_stop = int(tmp[1])
        add_stop_line(self.chat_id, tmp[0], type_stop)
        self.requests.send_msg(msg="Готово!")
        return True

    def parse_stop_lines(self, text):
        stop_lines = getting_stop_lines(self.chat_id)
        texts = text.lower().split()
        if stop_lines:
            for stop_line in stop_lines:
                for text in texts:
                    if text == stop_line.line:
                        if stop_line.type_do == 0:
                            self.remove_chat_user(self.user_id)
                        if stop_line.type_do == 1:
                            self.ban_user(self.user_id)

    def parse_mat(self, text):
        if mat.check_slang(text):
            self.pred_user(self.user_id, "Некультурно общаемся?")