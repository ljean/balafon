# -*- coding: utf-8 -*-
"""
app configuration
"""

from django import VERSION

if VERSION > (1, 7, 0):
    from django.apps import AppConfig

    class BalafonAppConfig(AppConfig):
        name = 'balafon.Store'
        verbose_name = "Balafon Store"

