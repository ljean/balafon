# -*- coding: utf-8 -*-
"""
app configuration
"""

from django.utils.translation import gettext_lazy as _

from django.apps import AppConfig


class BalafonAppConfig(AppConfig):
    name = 'balafon.Emailing'
    verbose_name = _("Balafon Emailing")
    default_auto_field = 'django.db.models.BigAutoField'
