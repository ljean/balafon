# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
from django import template
register = template.Library()
from datetime import date

@register.filter
def dt_from(dt):
    try:
        return dt.split(" ")[0]
    except:
        return ""

@register.filter
def dt_to(dt):
    try:
        return dt.split(" ")[1]
    except:
        return ""
    
