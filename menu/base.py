# -*- coding: utf-8 -*-

__author__ = 'ufian'

import config
import telepot
import time
import pymongo
import datetime
import json

import utils as u

class MenuMeta(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        res = super(MenuMeta, mcs).__new__(mcs, name, bases, attrs)
        if '__not_menu__' not in attrs:
            MenuMeta.MENU.append(res)
        return res

    MENU = []


class BaseMenu(object):
    __not_menu__ = True
    __metaclass__ = MenuMeta
    MENU = dict()

    TYPE = 'Base'

    BACK_BUTTON = (u'Отмена', 'Main')


    @classmethod
    def init(cls):
        for m in MenuMeta.MENU:
            cls.MENU[m.TYPE] = m

    @classmethod
    def get(cls, context, data):
        return {}


class BaseChooseMenu(BaseMenu):
    __not_menu__ = True

    TEXT = ""
    BUTTONS = None

    _KEYBOARD = None
    _DESTINATIONS = None

    @classmethod
    def get(cls, context, data):
        if cls._KEYBOARD is None:
            cls._KEYBOARD = [cls.BUTTONS] if not isinstance(cls.BUTTONS[0], list) else cls.BUTTONS
            cls._DESTINATIONS = {cell[1] for row in cls._KEYBOARD for cell in row}

        if 'cb_data' in data and 'from' not in data:
            if data['cb_data'] in cls._DESTINATIONS:
                context.set(data['cb_data'])
                return None

        text = None
        if isinstance(cls.TEXT, basestring):
            text = cls.TEXT
        else:
            text = cls.TEXT(context, data)

        return {
            'text': text,
            'buttons': cls._KEYBOARD
        }
