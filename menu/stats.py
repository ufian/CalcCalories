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