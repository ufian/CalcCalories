# -*- coding: utf-8 -*-

__author__ = 'ufian'

import config
import telepot
import time
import mongoengine as me
import datetime

from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space

import utils as u
import menu as M
import model
import calculator as calc
from context import Context
from calculator import CalculatorCalories



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


def get_connect():
    return me.connect(config.DB['db'], host=config.DB['host'], port=config.DB['port'])

class BaseStage(object):
    def __init__(self, session):
        self.session = session
        
    @property
    def user_id(self):
        return self.session.user_id

    def sendMessage(self, *args, **kwargs):
        self.session.sender.sendMessage(*args, **kwargs)

    def on_chat_message(self, msg, text):
        pass
    
    def on_callback_query(self, msg, cb_data):
        pass
    
class DefaultStage(BaseStage):

    def _today_text(self):
        return u"Сегодня съедено {0} ккал".format(
            calc.get_today_calories(self.user_id)
        )
    
    def _last_update(self):
        udt = datetime.datetime.utcnow()
        return u"Обновлено: {time} {date}".format(
            date=u.get_date(udt),
            time=u.get_time(udt)
        )
        
    def main(self, message=None):
        parts = list()
        if message:
            parts.extend([message, u''])

        parts.append(self._today_text())
        parts.append(self._last_update())
        
        self.sendMessage(u"\n".join(parts))

    def on_chat_message(self, msg, text):
        print "On chat default"
        self.main()
    
    def on_callback_query(self, msg, cb_data):
        pass


class EatSession(telepot.helper.ChatHandler):
    STAGES = {
        'default': DefaultStage
    }

    @property
    def context(self):
        return self.user_config.context
    
    @property
    def db(self):
        return getattr(get_connect(), config.DB['db'])
    
    def stage(self):
        stage = self.context.get('stage', 'default')
        if stage not in self.STAGES:
            stage = 'default'
            
        self.context['stage'] = stage
        return self.STAGES[stage](self)

    def save_message(self, msg, skip_reply=False):
        user_id = u.get_user_id(msg)
        msg_copy = msg.copy()
        msg_copy['date'] = datetime.datetime.utcnow()
        self.db.messages.insert_one(msg_copy)
        if not skip_reply:
            self.sendMessage(user_id, u'Дамп из телегарма сохранен')
        
    def open(self, initial_msg, seed):
        self.user_id = seed
        self.user_config = model.UserConfig.objects.filter(user_id=self.user_id).first()
        print "Load ", self.user_config, 'by', seed
        if self.user_config is None:
            self.user_config = model.UserConfig(user_id=self.user_id)
            self.user_config.save()

        if self.user_config.context is None:
            self.user_config.context = dict()

        return False

    def on_chat_message(self, msg):
        print "On chat"
        self.save_message(msg, skip_reply=True)
        
        self.stage().on_chat_message(msg, u.get_text(msg))
        
    def on_callback_query(self, msg):
        self.save_message(msg, skip_reply=True)

        self.stage().on_callback_query(msg, u.get_callback_data(msg))
    
    
    def on_close(self, ex):
        self.user_config.context = dict()
        self.user_config.save()

        


if __name__ == '__main__':
    conn = get_connect()
    ccalories = CalculatorCalories(conn)

    bot = telepot.DelegatorBot(config.BOT_TOKEN, [
        pave_event_space()(
            per_chat_id(('private',)), create_open, EatSession, timeout=10),
    ])
    
    
    #bot = CcalBot(config.BOT_TOKEN, ccalories)
    #bot.message_loop()
    MessageLoop(bot).run_as_thread()
    print('Listening ...')
    
    while 1:
        time.sleep(10)