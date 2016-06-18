# -*- coding: utf-8 -*-

__author__ = 'ufian'

import datetime
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


def trunc_date(date):
    return datetime.datetime.combine(date.date() - datetime.timedelta(0, 3*60*60), datetime.time(0))

def trunc_now():
    return trunc_date(datetime.datetime.now())

def do_markup(keys=None):
    if keys is None:
        return None

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=name, callback_data=data)
                for (name, data) in row
            ] for row in keys
        ])

def get_int(text):
    try:
        return int(text.strip())
    except ValueError:
        return None

def get_text(msg):
    return msg.get('text')

def get_user_id(msg):
    return msg.get('from', {}).get('id')

def get_callback_data(msg):
    return msg.get('data')

def get_message_id(msg):
    return msg.get('message', {}).get('message_id', -1)