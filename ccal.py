# -*- coding: utf-8 -*-

__author__ = 'ufian'

import config
import telepot
import time
import mongoengine as me
import datetime

from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton

import utils as u
import model
import calculator as calc

def get_connect():
    return me.connect(config.DB['db'], host=config.DB['host'], port=config.DB['port'])

class BaseStage(object):
    DEFAULT = 'default'
    STAGE = None
    
    def __init__(self, session):
        self.session = session

    @property
    def user_id(self):
        return self.session.user_id
    
    @property
    def context(self):
        return self.session.context

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

    def base_keyboard(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=u'Поесть', callback_data=u'eat|main'),
                    InlineKeyboardButton(text=u'Продукты', callback_data=u'products|main'),
                ],
                [
                    InlineKeyboardButton(text=u'Сегодня', callback_data=u'today|main'),
                    InlineKeyboardButton(text=u'Статистика', callback_data=u'stat|main'),
                ],
            ]
        )

    def base_message(self, message=None, update=False):
        parts = list()
        if message:
            parts.extend([message, u''])

        parts.append(self._today_text())
        parts.append(self._last_update())
    
        msg = u"\n".join(parts)
        
        if update and 'last_message' in self.context:
            return self.editMessageText(self.context['last_message'], msg, reply_markup=self.base_keyboard())
            
        return self.sendMessage(msg, reply_markup=self.base_keyboard())

    def sendMessage(self, *args, **kwargs):
        res = self.session.sender.sendMessage(*args, **kwargs)
        self.context['last_message'] = (res['chat']['id'], res['message_id'])
        
        return res
    
    def editMessageText(self, *args, **kwargs):
        return self.session.bot.editMessageText(*args, **kwargs)

    def on_chat_message(self, msg, text):
        pass
    
    def on_callback_query(self, msg, cb_data):
        pass
    
class DefaultStage(BaseStage):
    STAGE = BaseStage.DEFAULT

    def on_chat_message(self, msg, text):
        print "On chat default"
        res = self.base_message()
        
        # {u'date': 1498604286,
        #  u'text': u'\u0421\u0435\u0433\u043e\u0434\u043d\u044f \u0441\u044a\u0435\u0434\u0435\u043d\u043e 0 \u043a\u043a\u0430\u043b\n\u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043e: 15:59 27.06.2017',
        #  u'from': {u'username': u'hsetestbot', u'first_name': u'nonamebot', u'id': 161113648},
        #  u'message_id': 114,
        #  u'chat': {u'username': u'Ufian', u'first_name': u'Mikhail', u'last_name': u'Ufian', u'type': u'private', u'id': 113239144}}
        
    def on_callback_query(self, msg, cb_data):
        pass

class EatSession(BaseStage):
    STAGE = 'eat'
    


class EatSession(telepot.helper.ChatHandler):
    STAGES = {
        BaseStage.DEFAULT: DefaultStage
    }

    @property
    def context(self):
        return self.user_config.context
    
    @property
    def db(self):
        return getattr(get_connect(), config.DB['db'])
    
    def stage(self, new_stage=None):
        stage = new_stage or self.context.get('stage', BaseStage.DEFAULT)
        if stage not in self.STAGES:
            stage = BaseStage.DEFAULT
            
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
        cb_data = u.get_callback_data(msg)
        stage, sep, cb_data = cb_data.partition('|')
        if sep != '|':
            cb_data = stage
            stage = None

        self.stage(stage).on_callback_query(msg, cb_data)
    
    
    def on_close(self, ex):
        # BaseStage.DEFAULT -> fix message
        if 'last_message' in self.context:
            self.stage(BaseStage.DEFAULT).base_message('Finish', update=True)
        
        self.user_config.context = dict()
        self.user_config.save()

        


if __name__ == '__main__':
    conn = get_connect()

    bot = telepot.DelegatorBot(config.BOT_TOKEN, [
        pave_event_space()(
            per_chat_id(('private',)), create_open, EatSession, timeout=10),
    ])
    
    MessageLoop(bot).run_as_thread()
    print('Listening ...')
    
    while 1:
        time.sleep(10)