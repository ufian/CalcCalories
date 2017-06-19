# -*- coding: utf-8 -*-

__author__ = 'ufian'

import datetime
import utils as u
from collections import defaultdict


class CalculatorCalories(object):
    def __init__(self, conn):
        self.db = conn.ccal

    def add_eating(self, user_id, product_id=None, weight=None, calories=None):
        row = {
            'user_id': user_id,
            'product_id': product_id,
            'weight': weight,
            'calories': calories,
            'date': datetime.datetime.utcnow()
        }
        res = self.db.eating.insert_one(row)
        return res.inserted_id

    def get_list(self, user_id, days=0, c_days=1):
        result = defaultdict(list)


        from_dt = u.utc_date(u.trunc_by_now(-days))
        to_dt = u.utc_date(u.trunc_by_now(-days + c_days))

        it = self.db.eating.find({
            'user_id': user_id,
            'date': {"$gt": from_dt, "$lte": to_dt}
        })
        #print from_dt, '< dt <=', to_dt

        dt_now = u.trunc_by_now()

        for row in it:
            dt = (dt_now - u.trunc_date(row['date'])).days
            #print row['date'], ':', dt_now, u.trunc_date(row['date']), dt
            result[dt].append(row)

        return result

    def _get_calories(self, rows=None):
        total = 0

        if not rows:
            return total

        for row in rows:
            weight = row.get('weight')
            calories = row.get('calories')

            if calories is None:
                continue

            if weight is not None:
                total += calories * weight // 100
            else:
                total += calories

        return total

    def get_today_calories(self, user_id):
        res = self.get_list(user_id, days=0, c_days=1)
        return self._get_calories(res.get(0))

    def get_today_list(self, user_id):
        res = self.get_list(user_id, days=0, c_days=1)
        return res.get(0, [])

    def get_stat_data(self, user_id, days=30, skip_days=0):
        res_dict = self.get_list(user_id, days=days + skip_days, c_days=days + 1)
        result = list()
        dt_now = u.trunc_by_now()
        for d in xrange(29, -1, -1):
            result.append({
                'days': d,
                'date': dt_now - datetime.timedelta(days=d),
                'calories': self._get_calories(res_dict.get(d))
            })
        return result

    def get_products(self, user_id):
        return list(self.db.products.find({'user_id': user_id}).sort("name"))

    def add_product(self, user_id, name, calories):
        row = {
            'user_id': user_id,
            'name': name,
            'calories': calories
        }
        self.db.products.insert_one(row)
