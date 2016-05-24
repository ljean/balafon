# -*- coding: utf-8 -*-
"""
app configuration
"""

from django import VERSION
from django.utils.translation import ugettext_lazy as _


if VERSION > (1, 7, 0):
    from django.apps import AppConfig

    class BalafonAppConfig(AppConfig):
        name = 'balafon.Users'
        verbose_name = _(u"Balafon Users")
