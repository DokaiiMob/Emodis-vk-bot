# /usr/bin/env python3.7
# -*- coding: utf-8 -*-

from random import randint


def get_hello(id):
    return 'Привет, %s &#128521; Рекомендуем администратору беседы зайти на сайт' % id


def get_delete_dogs_not():
    return "Собачек нет!"


def get_delete_dogs():
    return "Все собачки удалены!"


def not_access():
    return 'По какой-то причине нет доступа :('


def get_random():
    return "Вероятность составляет {0}%".format(randint(0, 100))


def get_pred(is_pred, all_pred):
    return "Предупреждение {0}/{1}".format(is_pred, all_pred)
