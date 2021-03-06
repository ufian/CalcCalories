# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

__author__ = 'ufian'

import datetime

from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import utils as u
import calculator as calc
import dialog as d

DEFAULT = 'default'
EAT = 'eat'
PRODUCT = 'product'
TODAY = 'today'
STAT = 'stat'

class StageException(Exception):
    pass


class SessionMixin(object):
    def __init__(self, session):
        self.session = session

    @property
    def user_id(self):
        return self.session.user_id
    
    @property
    def context(self):
        return self.session.context

    @property
    def user_data(self):
        return self.session.user_data
    
    def set_stage(self, stage):
        return self.session.stage(stage)

    def sendMessage(self, *args, **kwargs):
        res = self.session.sender.sendMessage(*args, **kwargs)
        
        if 'last_message' in self.user_data:
            try:
                self.session.bot.editMessageReplyMarkup(tuple(self.user_data['last_message']), reply_markup=None)
            except:
                pass
            del self.user_data['last_message']
        
        if 'last_message' in self.context:
            self.session.bot.editMessageReplyMarkup(self.context['last_message'], reply_markup=None)
        
        self.context['last_message'] = u.get_edit_id(res)
        
        return res
    
    def editMessageText(self, *args, **kwargs):
        return self.session.bot.editMessageText(*args, **kwargs)
    
    def editCBMessageText(self, *args, **kwargs):
        if 'cb_message' not in self.context:
            raise StageException('Not found callback action')
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
    
    def _get_path(self, path):
        if isinstance(path, basestring):
            stage = self.STAGE
        elif isinstance(path, tuple):
            stage, path = path
        else:
            raise StageException('Path is wrong `{0}`'.format(path))
        
        return '{0}|{1}'.format(stage, path)

    def get_keyboard(self, rows):
        keys = list()
        for row in rows:
            key_row = list()
            for name, path in row:
                key_row.append(InlineKeyboardButton(text=name, callback_data=self._get_path(path)))
            keys.append(key_row)
        
        return InlineKeyboardMarkup(
            inline_keyboard=keys
        )

    def base_keyboard(self):
        return self.get_keyboard([
            [
                ('Поесть', (EAT, u'main')),
                ('Продукты', (PRODUCT, u'main')),
            ],
            [
                ('Сегодня', (TODAY, u'main')),
                ('Статистика', (STAT, u'main')),
            ]
        ])

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
            try:
                return self.editMessageText(update_msg, msg, reply_markup=keyboard)
            except:
                pass
            
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


class ProductStage(BaseStage):
    STAGE = PRODUCT

    PARAMS = [
        d.DialogParam('name', 'название',
                      question='Введите название продукта'),
        d.DialogParam('calories', 'калории', validate='int',
                      question='Введите калорийность продукта'),
    ]

    def _get_dialog(self, state):
        return d.Dialog(self.PARAMS, state)

    def on_chat_message(self, msg, text):
        dialog = self._get_dialog(self.context['product'])
        res = dialog.set_answer(text)
        
        if res in (d.Dialog.CONTINUE, d.Dialog.BAD_VALUE):
            self.sendMessage(dialog.get_question())
            return
        
        if res == d.Dialog.FINISH:
            calc.add_product(self.user_id, **self.context['product'])
            
            self.set_stage(DEFAULT).base_message('Сохранено')
    
    def on_callback_query(self, msg, cb_data):
        if cb_data == u'main':
            parts = list()
    
            for row in calc.get_products(self.user_id):
                parts.append(u"{0}: {1} ккал".format(row.name, row.calories))
    
            text = u"\n".join(parts)
            
            self.editCBMessageText(text, reply_markup=self.get_keyboard([
                [
                    (u'Добавить', u'add'),
                    (u'Отмена', (DEFAULT, u'main'))
                ]
            ]))
        elif cb_data == u'add':
            self.context['product'] = {}
            dialog = self._get_dialog(self.context['product'])
            self.sendMessage(dialog.get_question())


class EatStage(BaseStage):
    STAGE = EAT

    def on_callback_query(self, msg, cb_data):
        self.set_stage(DEFAULT).base_message('Обеды не найдены')


class TodayStage(BaseStage):
    STAGE = TODAY

    def _today_stat(self):
        parts = list()
        for row in calc.get_today_list(self.user_id):
            line = u""

            if row.date is not None:
                line += u"{} ".format(u.get_time(row.date))

            if row.calories is not None:
                if row.weight is not None:
                    line += u"{0} ккал ({1} г, {2} ккал/100г)".format(int(row.calories * row.weight / 100), row.weight, row.calories)
                else:
                    line += u"{0} ккал".format(row.calories)

            if len(line) > 0:
                parts.append(line)

        return u"\n".join(parts)
        

    def on_callback_query(self, msg, cb_data):
        text = self._today_stat()
        
        self.editCBMessageText(text, reply_markup=self.get_keyboard([
            [
                (u'Отмена', (DEFAULT, u'main'))
            ]
        ]))


class StatStage(BaseStage):
    STAGE = STAT

    def _get_stat(self):
        parts = list()

        for row in calc.get_stat_data(self.user_id, days=31):
            date = row.get('date')
            calories = row.get('calories')

            line = u""

            if date is not None:
                line += u"{} ".format(u.get_date(date))

            if calories is not None:
                    line += u"{0} ккал".format(calories)

            if len(line) > 0:
                parts.append(line)

        return u"\n".join(parts)
        

    def on_callback_query(self, msg, cb_data):
        text = self._get_stat()
        
        self.editCBMessageText(text, reply_markup=self.get_keyboard([
            [
                (u'Отмена', (DEFAULT, u'main'))
            ]
        ]))
