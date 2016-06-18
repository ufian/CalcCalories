# -*- coding: utf-8 -*-

__author__ = 'ufian'

from base import *

def init():
    BaseMenu.init()

def get(menu):
    return BaseMenu.MENU.get(menu)
