# -*- coding: utf-8 -*-

__author__ = 'ufian'

import mongoengine as me

class Product(me.Document):
    meta = {'collection': 'products'}
    
    user_id = me.IntField(required=True)
    calories = me.IntField(required=True)
    name = me.StringField(required=True)

class Eating(me.Document):
    meta = {'collection': 'eating'}
    
    user_id = me.IntField(required=True)
    product_id = me.IntField()
    weight = me.IntField()
    calories = me.IntField()
    date = me.DateTimeField(required=True)
