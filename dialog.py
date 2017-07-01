# -*- coding: utf-8 -*-

__author__ = 'ufian'

class DialogException(Exception):
    pass

class Dialog(object):
    CONTINUE = 0
    FINISH = 1
    BAD_VALUE = 2
    
    def __init__(self, params, state):
        self.params = params
        self.state = state
        self.current = None
        for param in params:
            if param['name'] in state:
                continue
            self.current = param
            break
        
    def get_question(self):
        if self.current is None:
            raise DialogException
        
        return self.current['question']
    
    def set_answer(self, value):
        if 'validate' in self.current and not self.current['validate'](value):
            return self.BAD_VALUE
        
        self.state[self.current['name']] = value
        
        if len(self.state) == len(self.params):
            return self.FINISH

        return self.CONTINUE