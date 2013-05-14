# -*- coding: utf-8 -*-

from datetime import date

def get_date_bounds(text):
    d1, d2 = text.split(' ')
    d1, d2 = [int(x) for x in d1.split('/')], [int(x) for x in d2.split('/')]
    d1.reverse(), d2.reverse()
    return date(*d1), date(*d2)