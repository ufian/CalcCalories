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


class BaseEatMenu(BaseMenu):
    __not_menu__ = True

    @classmethod
    def get_init(cls, context, data):
        return {
            'text': u'Введите общую калорийность съеденого',
            'buttons': [[
                cls.BACK_BUTTON
            ]]
        }

    @classmethod
    def q_full_calories(cls, context, data):
        return {
            'text': u'Введите общую калорийность съеденого',
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

        context.ccalories.add_eating(
            user_id=context.user_id,
            product_id=None,
            calories=row.get('calories'),
            weight=row.get('weight')
        )

    @classmethod
    def getter_int(cls, context, data):
        if 'text' not in data:
            return None, None

        num = u.get_int(data['text'])

        if num is None or num <= 0:
            return None, u'Неправильное число'

        return num, None

    STEPS = []

    @classmethod
    def get(cls, context, data):
        if 'cb_data' in data and 'from' not in data:
            if data['cb_data'] in ('save', 'back'):
                context.set('Main')
                return None

        if context.params is None:
            context.params = dict()

        for step in cls.STEPS:
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


class EatCMenu(BaseEatMenu):
    TYPE = 'EatC'

    STEPS = [
        ('calories', BaseEatMenu.q_full_calories, BaseEatMenu.getter_int),
        ('weight', BaseEatMenu.q_weight, BaseEatMenu.getter_int)
    ]

class EatCWMenu(BaseEatMenu):
    TYPE = 'EatCW'

    STEPS = [
        ('calories', BaseEatMenu.q_calories_by_weight, BaseEatMenu.getter_int),
        ('weight', BaseEatMenu.q_weight, BaseEatMenu.getter_int)
    ]


'''class EatCMenu(BaseMenu):
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
        return None'''
