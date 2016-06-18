# -*- coding: utf-8 -*-

__author__ = 'ufian'

import config
import telepot
import time
import pymongo
import datetime
import json

import utils as u
import menu as M
from context import Context



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
            'date': {"$gt": u.trunc_now()}
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




class CcalBot(telepot.Bot):
    def __init__(self, token, ccalories):
        super(CcalBot, self).__init__(token)
        self._answerer = telepot.helper.Answerer(self)
        self.ccalories = ccalories
        self.db = ccalories.db

        M.init()
        self.user_context = dict()



    def get_context(self, user_id):
        if user_id not in self.user_context:
            self.user_context[user_id] = Context(self, user_id)

        return self.user_context[user_id]

    def save_message(self, msg, skip_reply=False):
        user_id = u.get_user_id(msg)
        msg_copy = msg.copy()
        msg_copy['date'] = datetime.datetime.utcnow()
        self.db.messages.insert_one(msg_copy)
        if not skip_reply:
            self.sendMessage(user_id, u'Дамп из телегарма сохранен')

    @u.debug(config.DEBUG_MSG)
    def on_chat_message(self, msg):
        self.save_message(msg, skip_reply=True)

        user_id = u.get_user_id(msg)
        context = self.get_context(user_id)
        context.process(msg)

    @u.debug(config.DEBUG_MSG)
    def on_callback_query(self, msg):
        self.save_message(msg, skip_reply=True)

        user_id = u.get_user_id(msg)
        context = self.get_context(user_id)
        context.process_callback(msg)

        return

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


if __name__ == '__main__':
    conn = pymongo.MongoClient(config.DB['host'], config.DB['port'])
    ccalories = CalculatorCalories(conn)
    bot = CcalBot(config.BOT_TOKEN, ccalories)
    bot.message_loop()
    print ('Listening ...')

    # Keep the program running.
    while 1:
        time.sleep(10)