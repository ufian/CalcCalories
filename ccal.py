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

DEBUG_MSG = False
DEBUG_CTX = True


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

def trunc_date(date):
    return datetime.datetime.combine(date.date(), datetime.time(0)) - datetime.timedelta(0, 3*60*60)

def trunc_now():
    return trunc_date(datetime.datetime.now())

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
    def wrapper(self, msg, *args, **kwargs):
        if DEBUG_MSG:
            print '--------- {} ---------'.format(func.__name__)
            print json.dumps(msg, indent=4)
            print "\n" * 2

        return func(self, msg, *args, **kwargs)

    return wrapper


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

    BACK_BUTTON = (u'Отмена', 'back')


    @classmethod
    def init(cls):
        for m in MenuMeta.MENU:
            cls.MENU[m.TYPE] = m

    @classmethod
    def get(cls, context, data):
        return {}


class MainMenu(BaseMenu):
    TYPE = 'Main'

    @classmethod
    def get(cls, context, data):
        if 'cb_data' in data and 'from' not in data:
            if data['cb_data'] == u'EatChoose':
                context.set(data['cb_data'])
                return None

        context.params = None
        today = u"Сегодня съедено {0} ккал".format(context.ccalories.get_today_calories(context.user_id))
        text = u'{0}\nЧто делаеть?'.format(today)
        if 'from_message' in data:
            text = u"{0}\n\n{1}".format(
                data['from_message'],
                text
            )

        return {
            'text': text,
            'buttons': [[
                (u'Поесть', u'EatChoose'),
                (u'Готовое', u'Ready'),
                (u'Приготовить', u'Cook'),
                (u'Доесть', u'Finish'),
            ]]
        }

def get_int(text):
    try:
        return int(text.strip())
    except ValueError:
        return None


class EatChooseMenu(BaseMenu):
    TYPE = 'EatChoose'

    TEXT = u'Что вы хотите ввести'
    BUTTONS = [
        (u'Общую калорийность', 'EatC'),
        (u'Вес и ккал за 100г',  'EatCW'),
        BaseMenu.BACK_BUTTON
    ]

    @classmethod
    def get(cls, context, data):
        if 'cb_data' in data and 'from' not in data:
            if data['cb_data'] == 'back':
                context.set('Main')
                return None

            if data['cb_data'] in [b[1] for b in cls.BUTTONS]:
                context.set(data['cb_data'])
                return None

        return {
            'text': cls.TEXT,
            'buttons': [cls.BUTTONS]
        }


class EatCMenu(BaseMenu):
    TYPE = 'EatC'

    SAVE_BUTTON = (u'Сохранить', 'save')


    @classmethod
    def save(self, context):
        row = context.params

        context.ccalories.add_eating(
            user_id=context.user_id,
            product_id=None,
            calories=row.get('calories'),
            weight=row.get('weight')
        )

    @classmethod
    def get(cls, context, data):
        if 'cb_data' in data and 'from' not in data:
            if data['cb_data'] in ('save', 'back'):
                context.set('Main')
                return None

        if context.params is None:
            context.params = dict()
            return {
                'text': u'Введите общую калорийность съеденого',
                'buttons': [[
                    cls.BACK_BUTTON
                ]]
            }

        elif 'text' in data:
            if 'calories' not in context.params:
                calories = get_int(data['text'])
                if calories is None or calories <= 0:
                    return {
                        'text': u'Неправильное число. Введите общую калорийность съеденого',
                        'buttons': [[
                            cls.BACK_BUTTON,
                        ]]
                    }
                context.params['calories'] = calories
                cls.save(context)
                data['from_message'] = u'Сохранено'
                context.set('Main')
                return None


class EatCWMenu(BaseMenu):
    TYPE = 'EatCW'

    SAVE_BUTTON = (u'Сохранить', 'save')


    @classmethod
    def save(self, context):
        row = context.params

        context.ccalories.add_eating(
            user_id=context.user_id,
            product_id=None,
            calories=row.get('calories'),
            weight=row.get('weight')
        )

    @classmethod
    def get(cls, context, data):
        if 'cb_data' in data and 'from' not in data:
            if data['cb_data'] in ('save', 'back'):
                context.set('Main')
                return None

        if context.params is None:
            context.params = dict()
            return {
                'text': u'Введите калорийность за 100 грамм',
                'buttons': [[
                    cls.BACK_BUTTON
                ]]
            }
        elif 'text' in data:
            if 'calories' not in context.params:
                calories = get_int(data['text'])
                if calories is None or calories <= 0:
                    return {
                        'text': u'Неправильное число. Введите калорийность за 100 грамм',
                        'buttons': [[
                            cls.BACK_BUTTON,
                        ]]
                    }
                context.params['calories'] = calories

                return {
                    'text': u'Введите вес в граммах',
                    'buttons': [[
                        cls.BACK_BUTTON,
                    ]]
                }
            elif 'weight' not in context.params:
                weight = get_int(data['text'])
                if weight is None or weight <= 0:
                    return {
                        'text': u'Неправильное число. Введите вес в граммах',
                        'buttons': [[
                            cls.BACK_BUTTON,
                        ]]
                    }

                context.params['weight'] = weight
                cls.save(context)
                data['from_message'] = u'Сохранено'
                context.set('Main')
                return None



class CalculatorCalories(object):
    def __init__(self, conn):
        self.db = conn.ccal

    def add_eating(self, user_id, product_id=None, weight=None, calories=None):
        row = {
            'user_id': user_id,
            'product_id': product_id,
            'weight': weight,
            'calories': calories,
            'date': datetime.datetime.utcnow()
        }
        res = self.db.eating.insert_one(row)
        return res.inserted_id

    def get_today_calories(self, user_id):
        cur = self.db.eating.find({
            'user_id': user_id,
            'date': {"$gt": trunc_now()}
        })

        total = 0

        for row in cur:
            weight = row.get('weight')
            calories = row.get('calories')

            if calories is None:
                continue

            if weight is not None:
                total += calories * weight // 100
            else:
                total += calories

        return total


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


class Context(object):
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.user_id = chat_id
        self.ccalories = bot.ccalories
        self.state = 'Main'
        self.params = None

    def set(self, state):
        if DEBUG_CTX:
            print u"{0}: {1} -> {2}".format(self.user_id, self.state, state)
        self.state = state

    def send_reply(self, reply, message_idf=None):
        text = reply.get('text', 'None :(')
        markup = None
        if 'buttons' in reply:
            markup = do_markup(reply['buttons'])

        if message_idf is None:
            self.bot.sendMessage(self.user_id, text, reply_markup=markup)
        else:
            self.bot.editMessageText(message_idf, text, reply_markup=markup)

    def apply_state(self, message_idf=None, text=None, markup=None):
        m = BaseMenu.MENU[self.state]
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

    def get_reply(self, data):
        reply = None
        i = 0

        while reply is None and i < 10:
            i += 1
            state = self.state
            if DEBUG_CTX:
                print "{user}: get_reply{i} {state}: {data}".format(
                    user=self.user_id,
                    i=i,
                    state=self.state,
                    data=data
                )
            menu = BaseMenu.MENU.get(state)
            if menu is None:
                raise Exception

            reply = menu.get(self, data)
            if reply is not None:
                return reply

            if state == self.state:
                raise Exception

            data['from'] = state

        raise Exception

    @debug
    def process(self, msg):

        data = {
            'text': msg.get('text'),
            'user_id': self.user_id
        }

        reply = self.get_reply(data)
        self.send_reply(reply)




        '''if self.state == 'Main':
            self.apply_state()
        elif self.state == 'Eat':
            self.apply_state()
        elif self.state == 'Cook':
            self.process_cook()
        elif self.state == 'Finish':
            self.apply_state()
        else:
            self.state = 'Main'
            self.apply_state()'''

    @debug
    def process_callback(self, msg):

        message_idf = telepot.message_identifier(msg['message'])

        data = {
            'user_id': self.user_id,
            'cb_data': get_callback_data(msg),
            'message_idf': message_idf
        }

        reply = self.get_reply(data)
        self.send_reply(reply, message_idf)


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
        self.db = ccalories.db

        self.user_context = dict()

        BaseMenu.init()

    def get_context(self, user_id):
        if user_id not in self.user_context:
            self.user_context[user_id] = Context(self, user_id)

        return self.user_context[user_id]

    def main_menu(self, user_id):
        m = MENU['Main']
        res = self.sendMessage(user_id, m['text'], reply_markup=do_markup(m['buttons']))
        self.inliner[user_id] = Context(self, user_id)

    def save_message(self, msg, skip_reply=False):
        user_id = get_user_id(msg)
        msg_copy = msg.copy()
        msg_copy['date'] = datetime.datetime.utcnow()
        self.db.messages.insert_one(msg_copy)
        if not skip_reply:
            self.sendMessage(user_id, u'Дамп из телегарма сохранен')

    @debug
    def on_chat_message(self, msg):
        self.save_message(msg)

        user_id = get_user_id(msg)
        context = self.get_context(user_id)
        context.process(msg)

        '''if user_id in self.inliner:
            inline = self.inliner[user_id]
            inline.process(msg)
        else:
            self.main_menu(user_id)'''

    @debug
    def on_callback_query(self, msg):
        self.save_message(msg, skip_reply=True)

        user_id = get_user_id(msg)
        context = self.get_context(user_id)
        context.process_callback(msg)

        return


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