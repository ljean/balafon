# -*- coding: utf-8 -*-
"""
app configuration
"""

from django import VERSION

if VERSION > (1, 7, 0):
    from django.apps import AppConfig

    class SanzaAppConfig(AppConfig):
        name = 'sanza'
        verbose_name = "Sanza"

