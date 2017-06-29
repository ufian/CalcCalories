# -*- coding: utf-8 -*-

__author__ = 'ufian'

import datetime

from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton

import utils as u
import calculator as calc

DEFAULT = 'default'
PRODUCT = 'product'

class SessionMixin(object):
    def __init__(self, session):
        self.session = session

    @property
    def user_id(self):
        return self.session.user_id
    
    @property
    def context(self):
        return self.session.context

    def sendMessage(self, *args, **kwargs):
        res = self.session.sender.sendMessage(*args, **kwargs)
        self.context['last_message'] = u.get_edit_id(res)
        
        return res
    
    def editMessageText(self, *args, **kwargs):
        return self.session.bot.editMessageText(*args, **kwargs)
    
    def editCBMessageText(self, *args, **kwargs):
        if 'cb_message' not in self.context:
            raise CCalException('Not found callback action')
        return self.editMessageText(self.context['cb_message'], *args, **kwargs)

    
class BaseStage(SessionMixin):
    STAGE = None

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
                    InlineKeyboardButton(text=u'Продукты', callback_data=u'{0}|main'.format(PRODUCT)),
                ],
                [
                    InlineKeyboardButton(text=u'Сегодня', callback_data=u'today|main'),
                    InlineKeyboardButton(text=u'Статистика', callback_data=u'stat|main'),
                ],
            ]
        )

    def base_message(self, message=None, update_msg=None, with_keyboard=True):
        parts = list()
        if message:
            parts.extend([message, u''])

        parts.append(self._today_text())
        parts.append(self._last_update())
    
        msg = u"\n".join(parts)
        
        if with_keyboard:
            keyboard = self.base_keyboard()
        else:
            keyboard = None
        
        if update_msg:
            return self.editMessageText(update_msg, msg, reply_markup=keyboard)
            
        return self.sendMessage(msg, reply_markup=keyboard)

    def on_chat_message(self, msg, text):
        pass
    
    def on_callback_query(self, msg, cb_data):
        pass
    

class DefaultStage(BaseStage):
    STAGE = DEFAULT

    def on_chat_message(self, msg, text):
        sep = u' по '
        result = u'Ошибка'
        
        if sep in text:
            weight, calories = text.split(sep, 1)
            try:
                weight = int(weight)
                calories = int(calories)

                calc.add_eating(
                    user_id=self.user_id,
                    product_id=None,
                    calories=calories,
                    weight=weight
                )

                result = u'Сохранено'
            except ValueError:
                result = u'Не сохранено. Проблема с целыми числами.'
            except:
                pass
        else:
            try:
                calories = int(text)
                calc.add_eating(
                    user_id=self.user_id,
                    product_id=None,
                    calories=calories,
                    weight=None
                )
                result = u'Сохранено'
            except ValueError:
                result = u'Не сохранено. Проблема с целыми числами.'
            except:
                pass

        res = self.base_message(result)
        
        # {u'date': 1498604286,
        #  u'text': u'\u0421\u0435\u0433\u043e\u0434\u043d\u044f \u0441\u044a\u0435\u0434\u0435\u043d\u043e 0 \u043a\u043a\u0430\u043b\n\u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043e: 15:59 27.06.2017',
        #  u'from': {u'username': u'hsetestbot', u'first_name': u'nonamebot', u'id': 161113648},
        #  u'message_id': 114,
        #  u'chat': {u'username': u'Ufian', u'first_name': u'Mikhail', u'last_name': u'Ufian', u'type': u'private', u'id': 113239144}}
        
    def on_callback_query(self, msg, cb_data):
        self.base_message(update_msg=self.context['cb_message'])

class ProductSession(BaseStage):
    STAGE = PRODUCT
    
    def on_callback_query(self, msg, cb_data):
        if cb_data == 'main':
            self.editCBMessageText(u'Продукты')