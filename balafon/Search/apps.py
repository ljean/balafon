# -*- coding: utf-8 -*-
"""
app configuration
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BalafonAppConfig(AppConfig):
    name = 'balafon.Search'
    verbose_name = _("Balafon Search")
