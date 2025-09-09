# -*- coding: utf-8 -*-
"""
app configuration
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BalafonAppConfig(AppConfig):
    name = 'balafon.Users'
    verbose_name = _("Balafon Users")
    default_auto_field = 'django.db.models.BigAutoField'
