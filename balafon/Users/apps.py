# -*- coding: utf-8 -*-
"""
app configuration
"""

from django import VERSION

if VERSION > (1, 7, 0):
    from django.apps import AppConfig

    class BalafonAppConfig(AppConfig):
        name = 'balafon.Users'
        verbose_name = "Balafon Users"

default_app_config = 'balafon.Users.apps.BalafonAppConfig'
