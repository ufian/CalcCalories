# -*- coding: utf-8 -*-

__author__ = 'ufian'

from base import BaseMenu, BaseChooseMenu
import utils as u

class ReadyChooseMenu(BaseChooseMenu):
    TYPE = 'Ready'

    TEXT = u'Что вы хотите сделать'
    BUTTONS = [
        [
            (u'Поесть', 'ReadyAdd'),
            (u'Добавить', 'ReadyAdd'),
            (u'Обзор',  'ReadyView'),
        ],
        [BaseMenu.BACK_BUTTON]
    ]