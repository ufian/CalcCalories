# -*- coding: utf-8 -*-

__author__ = 'ufian'

import json
import datetime
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

DELTA = 3
TIMEZONE = -7

def utc_date(date):
    return date - datetime.timedelta(hours=TIMEZONE - DELTA)

def trunc_date(date):
    return datetime.datetime.combine((date + datetime.timedelta(hours=TIMEZONE - DELTA)).date(), datetime.time(0))

def trunc_by_now(days=0):
    #print 'Now', days, datetime.datetime.utcnow(), trunc_date(datetime.datetime.utcnow() + datetime.timedelta(days=days))
    return trunc_date(datetime.datetime.utcnow() + datetime.timedelta(days=days))

def get_time(date):
    return (date + datetime.timedelta(hours=TIMEZONE)).strftime("%H:%M")

def get_date(date):
    return (date + datetime.timedelta(hours=TIMEZONE)).strftime("%d.%m.%Y")


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

def get_chat_id(msg):
    return msg.get('chat', {}).get('id')

def get_callback_data(msg):
    return msg.get('data')

def get_message_id(msg):
    return msg.get('message_id', -1)

def get_edit_id(msg):
    return (get_chat_id(msg), get_message_id(msg))

def debug(debug):
    def deco(func):
        def wrapper(self, msg, *args, **kwargs):
            if debug:
                print '--------- {} ---------'.format(func.__name__)
                print json.dumps(msg, indent=4)
                print "\n" * 2

            return func(self, msg, *args, **kwargs)

        return wrapper
    return deco
