# -*- coding: utf-8 -*-

__author__ = 'ufian'

import config
import telepot
import time
import mongoengine as me
import datetime

from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, per_callback_query_chat_id, create_open, pave_event_space
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton

import utils as u
import model
import stages as st
import calculator as calc

class CCalException(Exception):
    pass

def get_connect():
    return me.connect(
        config.DB['db'],
        host=config.DB['host'],
        port=config.DB['port'],
        serverSelectionTimeoutMS=2500
    )



class EatSession(telepot.helper.ChatHandler):
    STAGES = {
        st.DEFAULT: st.DefaultStage,
        st.PRODUCT: st.ProductSession,
    }

    @property
    def context(self):
        return self.user_config.context
    
    @property
    def db(self):
        return getattr(get_connect(), config.DB['db'])
    
    def stage(self, new_stage=None):
        stage = new_stage or self.context.get('stage', st.DEFAULT)
        if stage not in self.STAGES:
            stage = st.DEFAULT
            
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
        self.save_message(msg, skip_reply=True)
        
        self.stage().on_chat_message(msg, u.get_text(msg))
        
    def on_callback_query(self, msg):
        self.save_message(msg, skip_reply=True)
        cb_data = u.get_callback_data(msg)
        stage, sep, cb_data = cb_data.partition('|')
        if sep != '|':
            cb_data = stage
            stage = None
            
        self.context['cb_message'] = u.get_edit_id(msg['message'])
        self.stage(stage).on_callback_query(msg, cb_data)
    
    
    def on_close(self, ex):
        # st.DEFAULT -> fix message
        stage = self.stage(st.DEFAULT)
        if 'last_message' in self.context:
            stage.base_message('Finish', update_msg=self.context['last_message'])
            
        if 'cb_message' in self.context and self.context['cb_message'] != self.context.get('last_message'):
            stage.base_message(
                'Finish',
                update_msg=self.context['cb_message'],
                with_keyboard= 'last_message' not in self.context
            )
        
        self.user_config.context = dict()
        self.user_config.save()

        


if __name__ == '__main__':
    conn = get_connect()
    params = list(model.GlobalConfig.objects.timeout(True))

    bot = telepot.DelegatorBot(config.BOT_TOKEN, [
        pave_event_space()(
            [per_chat_id(('private',)), per_callback_query_chat_id(('private',))],
            create_open,
            EatSession,
            include_callback_query=True, timeout=10),
    ])
    
    MessageLoop(bot).run_as_thread()
    print('Listening ...')
    
    while 1:
        time.sleep(10)