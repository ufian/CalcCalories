# -*- coding: utf-8 -*-

__author__ = 'ufian'

from dialog import Dialog

class TestClass(object):
    
    def test_simple(self):
        params = [
            {'name': 'calories', 'question': 'Calories?'},
            {'name': 'weight', 'question': 'Weight?'}
        ]
        state = {}
        
        d = Dialog(params, state)
        
        assert d.get_question() == 'Calories?'
        assert d.set_answer(10) == Dialog.CONTINUE
