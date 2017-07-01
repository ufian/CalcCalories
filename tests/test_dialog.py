# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

__author__ = 'ufian'

from dialog import Dialog, DialogParam

class TestDialog(object):
    
    def test_simple(self):
        params = [
            DialogParam('calories'),
            DialogParam('weight'),
        ]
        state = {}
        
        d = Dialog(params, state)
        
        assert d.get_question() == 'calories?'
        assert d.set_answer(10) == Dialog.CONTINUE

        assert d.get_question() == 'weight?'
        assert d.set_answer(10) == Dialog.FINISH

        assert d.is_end()