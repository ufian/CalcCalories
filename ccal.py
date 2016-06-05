# -*- coding: utf-8 -*-

__author__ = 'ufian'

import config
import telepot
import time
import pymongo
import datetime
import json
from collections import defaultdict

from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent


MENU = {
    'Main': {
        'text': u'Что делаеть?',
        'buttons': [[
            (u'Поесть', u'Eat'),
            (u'Готовое', u'Ready'),
            (u'Приготовить', u'Cook'),
            (u'Доесть', u'Finish'),
        ]]
    },
    'Eat': {
        'text': u'Что едим?',
        'text_fail': u'Нечего есть'
    },
    'Ready': {
        'text': u'Что едим?',
        'text_fail': u'Нечего есть'
    },
    'Cook': {
        'text': u'Что готовим?',
        'buttons': [[
            (u'Новое блюдо', u'Cook|New'),
            (u'Известное', u'Cook|Base'),
            (u'Ингридиент', u'Cook|Ingredient')
        ]],
        'steps': {
            'Ingredient': [
                (u'Название', u'name'),
                (u'Калорийность', u'calories'),
            ]
        }
    },
    'Finish': {
        'text': u'Что доели?',
        'text_fail': u'Нечего доедать'
    }
}

def do_markup(keys):
    if keys is None:
        return None

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=name, callback_data=data)
                for (name, data) in row
            ] for row in keys
        ])


def debug(func):
    def wrapper(self, msg):
        print '--------- {} ---------'.format(func.__name__)
        print json.dumps(msg, indent=4)
        print "\n" * 2

        return func(self, msg)

    return wrapper



class CalculatorCalories(object):
    def __init__(self, conn):
        self.db = conn.ccal

    def add_eating(self, user_id, product_id, weight=None, calories=None):
        row = {
            'user_id': user_id,
            'product_id': product_id,
            'weight': weight,
            'calories': calories,
            'date': datetime.datetime.utcnow()
        }
        res = self.db.eating.insert_one(row)
        return res.inserted_id

    def get_products(self, user_id):
        return list(self.db.products.find({'user_id': user_id}))

    def add_product(self, user_id, name, calories):
        row = {
            'user_id': user_id,
            'name': name,
            'calories': calories
        }
        self.db.products.insert_one(row)

def get_text(msg):
    return msg.get('text')

def get_user_id(msg):
    return msg.get('from', {}).get('id')

def get_callback_data(msg):
    return msg.get('data')

def get_message_id(msg):
    return msg.get('message', {}).get('message_id', -1)


class InlineMenu(object):
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.user_id = chat_id
        self.ccalories = bot.ccalories
        self.state = 'Main'
        self.params = None

    def set(self, state):
        self.state = state

    def apply_state(self, message_idf=None, text=None, markup=None):
        m = MENU[self.state]
        text = text or m['text']
        if markup is list:
            markup = do_markup(markup)
        elif markup is False:
            markup = None
        else:
            markup = do_markup(m.get('buttons'))

        if message_idf is None:
            self.bot.sendMessage(self.user_id, text, reply_markup=markup)
        else:
            self.bot.editMessageText(message_idf, text, reply_markup=markup)

    @debug
    def process(self, msg):
        if self.state == 'Main':
            self.apply_state()
        elif self.state == 'Eat':
            self.apply_state()
        elif self.state == 'Cook':
            self.process_cook()
        elif self.state == 'Finish':
            self.apply_state()
        else:
            self.state = 'Main'
            self.apply_state()

    @debug
    def process_callback(self, msg):

        data = get_callback_data(msg)
        message_idf = telepot.message_identifier(msg['message'])

        self.params = data.split('|')
        if self.params[0] in MENU:
            self.state = self.params[0]

        if self.state == 'Main':
            self.apply_state(message_idf)
        elif self.state == 'Eat':
            self.apply_state(message_idf)
        elif self.state == 'Cook':
            self.process_cook(message_idf)
        elif self.state == 'Finish':
            self.apply_state(message_idf)
        else:
            self.state = 'Main'
            self.apply_state(message_idf)
    
    def process_cook(self,message_idf=None):
        m = MENU[self.state]
        if len(self.params) == 1:
            self.apply_state(message_idf)
        elif len(self.params) == 2:
            if self.params[1] == 'Ingredient':
                self.params.append(0)
                self.apply_state(message_idf=message_idf, text=m['steps']['Ingredient'][0][0], markup=False)




class CcalBot(telepot.Bot):
    def __init__(self, token, ccalories):
        super(CcalBot, self).__init__(token)
        self._answerer = telepot.helper.Answerer(self)
        self.ccalories = ccalories

        self.inliner = dict()

    def main_menu(self, user_id):
        m = MENU['Main']
        res = self.sendMessage(user_id, m['text'], reply_markup=do_markup(m['buttons']))
        self.inliner[user_id] = InlineMenu(self, user_id)

    @debug
    def on_chat_message(self, msg):
        user_id = get_user_id(msg)
        if user_id in self.inliner:
            inline = self.inliner[user_id]
            inline.process(msg)
        else:
            self.main_menu(user_id)

    @debug
    def on_callback_query(self, msg):
        user_id = get_user_id(msg)
        if user_id in self.inliner:
            inline = self.inliner[user_id]
            inline.process_callback(msg)
        else:
            message_idf = telepot.message_identifier(msg['message'])
            self.editMessageReplyMarkup(message_idf, reply_markup=None)

            self.main_menu(user_id)




    def on_inline_query(self, msg):
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print('Inline Query:', query_id, from_id, query_string)

        def compute_answer():
            # Compose your own answers
            articles = [{'type': 'article',
                            'id': 'abc', 'title': query_string, 'message_text': query_string}]

            return articles

        self._answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        print('Chosen Inline Result:', result_id, from_id, query_string)


conn = pymongo.MongoClient(config.DB['host'], config.DB['port'])
ccalories = CalculatorCalories(conn)
bot = CcalBot(config.BOT_TOKEN, ccalories)
bot.message_loop()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)