# -*- coding: utf-8 -*-

__author__ = 'ufian'

from base import BaseChooseMenu
import utils as u

class TodayMenu(BaseChooseMenu):
    TYPE = 'Today'
    BUTTONS = [BaseChooseMenu.BACK_BUTTON]

    @classmethod
    def get_text(cls, context, data):
        parts = list()
        for row in context.ccalories.get_today_list(context.user_id):
            date = row.get('date')
            weight = row.get('weight')
            calories = row.get('calories')

            line = u""

            if date is not None:
                line += u"{} ".format(u.get_time(date))

            if calories is not None:
                if weight is not None:
                    line += u"{0} ккал ({1} г, {2} ккал/100г)".format(int(calories * weight / 100), weight, calories)
                else:
                    line += u"{0} ккал".format(calories)

            if len(line) > 0:
                parts.append(line)

        return u"\n".join(parts)

    TEXT = get_text


class StatMonthMenu(BaseChooseMenu):
    TYPE = 'StatMonth'
    BUTTONS = [BaseChooseMenu.BACK_BUTTON]

    @classmethod
    def get_text(cls, context, data):
        parts = list()

        for row in context.ccalories.get_stat_data(context.user_id, days=31):
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

    TEXT = get_text

class StatMenu(BaseChooseMenu):
    TYPE = 'Stat'
    BUTTONS = [
        (u'Подробнее', u'StatMonth'),
        BaseChooseMenu.BACK_BUTTON
    ]

    @classmethod
    def get_text(cls, context, data):
        parts = list()
        def get_average(rows):
            rows = [row['calories'] for row in rows if row['calories'] > 0]

            if not rows:
                return u'Ошибка'

            return sum(rows) // len(rows)


        week_rows = context.ccalories.get_stat_data(context.user_id, days=7, skip_days=1)
        month_rows = context.ccalories.get_stat_data(context.user_id, days=30, skip_days=1)

        parts.append(u'Среднее за неделю {} ккал'.format(get_average(week_rows)))
        parts.append(u'Среднее за месяц {} ккал'.format(get_average(month_rows)))

        return u"\n".join(parts)

    TEXT = get_text