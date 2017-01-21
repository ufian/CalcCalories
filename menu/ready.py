# -*- coding: utf-8 -*-

__author__ = 'ufian'

from base import BaseMenu, BaseChooseMenu
import utils as u

class ReadyChooseMenu(BaseChooseMenu):
    TYPE = 'Ready'

    TEXT = u'Что вы хотите сделать'
    BUTTONS = [
        [
            (u'Добавить', 'ReadyAdd'),
            (u'Обзор',  'ReadyView'),
        ],
        [BaseMenu.BACK_BUTTON]
    ]

    
class ReadyAddMenu(BaseMenu):
    TYPE = 'ReadyAdd'

    BUTTONS = [
        BaseMenu.BACK_BUTTON
    ]

    @classmethod
    def q_name(cls, context, data):
        return {
            'text': u'Введите название',
            'buttons': [[
                cls.BACK_BUTTON
            ]]
        }

    @classmethod
    def q_calories_by_weight(cls, context, data):
        return {
            'text': u'Введите калорийность за 100 грамм',
            'buttons': [[
                cls.BACK_BUTTON
            ]]
        }

    @classmethod
    def q_weight(cls, context, data):
        return {
            'text': u'Введите вес в граммах',
            'buttons': [[
                cls.BACK_BUTTON,
            ]]
        }

    @classmethod
    def save(self, context):
        row = context.params

        context.ccalories.add_product(
            user_id=context.user_id,
            name=row.get('name'),
            calories=row.get('calories')
        )

    @classmethod
    def getter_text(cls, context, data):
        if 'text' not in data:
            return None, None

        text = data['text']

        if len(text) == 0:
            return None, u'Неправильное название'

        del data['text']

        return text, None

    @classmethod
    def getter_int(cls, context, data):
        if 'text' not in data:
            return None, None

        num = u.get_int(data['text'])

        if num is None or num <= 0:
            return None, u'Неправильное число'

        del data['text']

        return num, None

    @classmethod
    def get(cls, context, data):
        STEPS = [
            ('name', cls.q_name, cls.getter_text),
            ('calories', cls.q_calories_by_weight, cls.getter_int),
        ]
        
        if 'cb_data' in data and 'from' not in data:
            if data['cb_data'] in ('save', 'back', 'Main'):
                context.set('Main')
                return None

        if context.params is None:
            context.params = dict()

        for step in STEPS:
            param, question, getter = step

            if param not in context.params:
                val, err = getter(context, data)

                if val is not None:
                    context.params[param] = val
                    continue

                res = question(context, data)
                if err is not None:
                    res['text']  = u"{err}\n{text}".format(
                        err=err,
                        text=res['text']
                    )

                return res

        cls.save(context)
        data['from_message'] = u'Сохранено'
        context.set('Main')
        return None


class ReadyViewMenu(BaseChooseMenu):
    TYPE = 'ReadyView'
    BUTTONS = [BaseChooseMenu.BACK_BUTTON]

    @classmethod
    def get_text(cls, context, data):
        parts = list()

        for row in context.ccalories.get_products(context.user_id):
            name = row.get('name')
            calories = row.get('calories')

            parts.append(u"{0}: {1} ккал".format(name, calories))

        return u"\n".join(parts)

    TEXT = get_text
