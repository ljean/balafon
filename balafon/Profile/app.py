# -*- coding: utf-8 -*-
"""
app configuration
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BalafonAppConfig(AppConfig):
    name = 'balafon.Profile'
    verbose_name = _("Balafon Profile")
    default_auto_field = 'django.db.models.BigAutoField'
