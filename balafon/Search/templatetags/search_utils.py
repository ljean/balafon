# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template


register = template.Library()


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
