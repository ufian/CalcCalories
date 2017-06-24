# -*- coding: utf-8 -*-

__author__ = 'ufian'

import datetime
import utils as u
from collections import defaultdict

from model import Eating, Product

def add_eating(user_id, product_id=None, weight=None, calories=None):
    return Eating(
        user_id=user_id,
        product_id=product_id,
        weight=weight,
        calories=calories,
        date=datetime.datetime.utcnow()
    ).save()

def add_product(user_id, name, calories):
    return Product(
        user_id=user_id,
        name=name,
        calories=calories
    ).save()



class CalculatorCalories(object):
    def __init__(self, conn):
        self.db = conn.ccal

        
def get_list(user_id, days=0, c_days=1):
    result = defaultdict(list)

    from_dt = u.utc_date(u.trunc_by_now(-days))
    to_dt = u.utc_date(u.trunc_by_now(-days + c_days))

    it = Eating.objects.filter(
        user_id=user_id,
        date__gt=from_dt,
        date__lte=to_dt
    )
    #print from_dt, '< dt <=', to_dt

    dt_now = u.trunc_by_now()

    for row in it:
        dt = (dt_now - u.trunc_date(row.date)).days
        #print row['date'], ':', dt_now, u.trunc_date(row['date']), dt
        result[dt].append(row)

    return result

def _get_calories(rows=None):
    total = 0

    if not rows:
        return total

    for row in rows:
        weight = row.weight
        calories = row.calories

        if calories is None:
            continue

        if weight is not None:
            total += calories * weight // 100
        else:
            total += calories

    return total

def get_today_calories(user_id):
    res = get_list(user_id, days=0, c_days=1)
    return _get_calories(res.get(0))

def get_today_list(user_id):
    res = get_list(user_id, days=0, c_days=1)
    return res.get(0, [])

def get_stat_data(user_id, days=30, skip_days=0):
    res_dict = get_list(user_id, days=days + skip_days, c_days=days + 1)
    result = list()
    dt_now = u.trunc_by_now()
    for d in xrange(29, -1, -1):
        result.append({
            'days': d,
            'date': dt_now - datetime.timedelta(days=d),
            'calories': _get_calories(res_dict.get(d))
        })
    return result

def get_products(user_id):
    return list(Product.objects.filter(user_id=user_id).order_by("+name"))

