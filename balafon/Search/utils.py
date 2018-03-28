# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import date


def get_date_bounds(text):
    date1, date2 = text.split(' ')
    date1, date2 = [int(elt) for elt in date1.split('/')], [int(elt) for elt in date2.split('/')]
    date1.reverse(), date2.reverse()
    return date(*date1), date(*date2)
