# -*- coding: utf-8 -*-

__author__ = 'ufian'

from base import BaseMenu, BaseChooseMenu
from main import MainMenu
from eat import EatChooseMenu, EatCMenu, EatCWMenu
from stats import TodayMenu

def init():
    BaseMenu.init()

def get(menu):
    return BaseMenu.MENU.get(menu)
