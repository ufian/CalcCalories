# -*- coding: utf-8 -*-

__author__ = 'ufian'

import config
import telepot
import utils as u
import menu as M


class Context(object):
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.user_id = chat_id
        self.ccalories = bot.ccalories
        self.state = 'Main'
        self.params = None

    def set(self, state):
        if config.DEBUG_CTX:
            print u"{0}: {1} -> {2}".format(self.user_id, self.state, state)
        self.state = state

    def send_reply(self, reply, message_idf=None):
        text = reply.get('text', 'None :(')
        markup = None
        if 'buttons' in reply:
            markup = u.do_markup(reply['buttons'])

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
            if config.DEBUG_CTX:
                print "{user}: get_reply{i} {state}: {data}".format(
                    user=self.user_id,
                    i=i,
                    state=self.state,
                    data=data
                )
            menu = M.get(state)
            if menu is None:
                menu = M.get('Main')
                state = 'Main'

            reply = menu.get(self, data)
            if reply is not None:
                return reply

            if state == self.state and state != 'Main':
                raise Exception

            data['from'] = state

        raise Exception

    @u.debug(config.DEBUG_MSG)
    def process(self, msg):

        data = {
            'text': u.get_text(msg),
            'user_id': self.user_id
        }

        reply = self.get_reply(data)
        self.send_reply(reply)

    @u.debug(config.DEBUG_MSG)
    def process_callback(self, msg):

        message_idf = telepot.message_identifier(msg['message'])

        data = {
            'user_id': self.user_id,
            'cb_data': u.get_callback_data(msg),
            'message_idf': message_idf
        }

        reply = self.get_reply(data)
        self.send_reply(reply, message_idf)
