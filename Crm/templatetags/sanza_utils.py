# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
from django import template
register = template.Library()
from datetime import date

@register.filter
def seq_to_br(seq):
    if seq:
        return mark_safe(u"<br>".join([unicode(x) for x in seq]))
    return mark_safe(u"&nbsp;")

@register.filter
def seq_to_dash(seq):
    if seq:
        return mark_safe(u" - ".join(seq))
    return mark_safe(u"&nbsp;")

@register.filter
def is_today(dt):
    if dt:
        d = date(dt.year, dt.month, dt.day)
        return (d == date.today())
    return False
    

@register.filter
def cut_null_hour(value):
    try:
        x = value.split(u" ")    
        d, h = u' '.join(x[:-1]), x[-1]
        if h == "00:00":
            return d
    except:
        pass
    return value
    