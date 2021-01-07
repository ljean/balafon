# -*- coding: utf-8 -*-
"""
app configuration
"""

from django.utils.translation import ugettext_lazy as _

from django.apps import AppConfig


class BalafonAppConfig(AppConfig):
    name = 'balafon.Emailing'
    verbose_name = _("Balafon Emailing")
