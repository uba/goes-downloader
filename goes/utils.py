# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import datetime

def generateListOfDays(start, end):
    '''This function returns all-days between given two dates.'''
    delta = end - start
    return [start + datetime.timedelta(i) for i in range(delta.days + 1)]