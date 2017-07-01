# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

__author__ = 'ufian'


class DialogException(Exception):
    pass

def check_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
        

class DialogParam(object):
    
    VALIDATORS = {
        'int': check_int
    }
    
    def __init__(self, name, title=None, validate=None, question=None):
        self.name = name
        self.title = title or name
        self.question = question or '{0}?'.format(self.title)
        self._validate = validate
        
    def validate(self, value):
        if self._validate is None:
            return True
        
        if callable(self._validate):
            return self._validate(value)
        
        if self._validate in self.VALIDATORS:
            return self.VALIDATORS[self._validate](value)


class Dialog(object):
    CONTINUE = 0
    FINISH = 1
    BAD_VALUE = 2
    
    def __init__(self, params, state):
        self.params = params
        self.state = state
        self.current = None
        
        self.it_params = iter(self.params)
        while True:
            self.current = self._next_param()
            
            if self.current is None:
                return
            
            if self.current.name not in self.state:
                break
    
    def _next_param(self):
        try:
            return next(self.it_params)
        except StopIteration:
            return None
        
    def get_question(self):
        if self.current is None:
            raise DialogException
        
        return self.current.question
    
    def set_answer(self, value):
        if self.current is None:
            raise DialogException

        if not self.current.validate(value):
            return self.BAD_VALUE
        
        self.state[self.current.name] = value
        self.current = self._next_param()
        
        if self.current is None:
            return self.FINISH

        return self.CONTINUE
