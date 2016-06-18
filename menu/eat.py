# -*- coding: utf-8 -*-

__author__ = 'ufian'

from base import BaseMenu, BaseChooseMenu
import utils as u

class EatChooseMenu(BaseChooseMenu):
    TYPE = 'EatChoose'

    TEXT = u'Что вы хотите ввести'
    BUTTONS = [
        (u'Общую калорийность', 'EatC'),
        (u'Вес и ккал за 100г',  'EatCW'),
        BaseMenu.BACK_BUTTON
    ]

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
                calories = u.get_int(data['text'])
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

        data['from_message'] = u'Ошибка'
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
                calories = u.get_int(data['text'])
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
                weight = u.get_int(data['text'])
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

        data['from_message'] = u'Ошибка'
        context.set('Main')
        return None
