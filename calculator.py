# -*- coding: utf-8 -*-

__author__ = 'ufian'

import datetime
import utils as u


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

    def get_today_list(self, user_id):
        return self.db.eating.find({
            'user_id': user_id,
            'date': {"$gt": u.trunc_now()}
        })

    def get_today_calories(self, user_id):

        total = 0

        for row in self.get_today_list(user_id):
            weight = row.get('weight')
            calories = row.get('calories')

            if calories is None:
                continue

            if weight is not None:
                total += calories * weight // 100
            else:
                total += calories

        return total


    def get_products(self, user_id):
        return list(self.db.products.find({'user_id': user_id}))

    def add_product(self, user_id, name, calories):
        row = {
            'user_id': user_id,
            'name': name,
            'calories': calories
        }
        self.db.products.insert_one(row)
