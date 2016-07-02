# -*- coding: utf-8 -*-

__author__ = 'ufian'

from base import BaseChooseMenu
import datetime

class MainMenu(BaseChooseMenu):
    TYPE = 'Main'

    BUTTONS = [
        [
            (u'Поесть', u'EatChoose'),
            (u'Готовое', u'Ready'),
            (u'Приготовить', u'Cook'),
            (u'Доесть', u'Finish'),
        ],
        [
            (u'Сегодня', u'Today'),
            (u'Статистика', u'Stat'),
        ]
    ]

    MAIN_TEXT = u'Что делать?'

    @classmethod
    def get_text(cls, context, data):
        parts = list()
        context.params = None


        if 'from_message' in data:
            parts.append(data['from_message'])
            parts.append('')


        parts.append(u"Сегодня съедено {0} ккал".format(context.ccalories.get_today_calories(context.user_id)))
        parts.append(u"Обновлено: {}".format(datetime.datetime.utcnow()))

        return u"\n".join(parts)

    TEXT = get_text


    # @classmethod
    # def get(cls, context, data):
    #     if 'cb_data' in data and 'from' not in data:
    #         if data['cb_data'] == u'EatChoose':
    #             context.set(data['cb_data'])
    #             return None
    #
    #     context.params = None
    #     today = u"Сегодня съедено {0} ккал".format(context.ccalories.get_today_calories(context.user_id))
    #     text = u'{0}\nЧто делаеть?'.format(today)
    #     if 'from_message' in data:
    #         text = u"{0}\n\n{1}".format(
    #             data['from_message'],
    #             text
    #         )
    #
    #     return {
    #         'text': text,
    #         'buttons': [[
    #         ]]
    #     }

