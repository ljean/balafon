# -*- coding: utf-8 -*-
"""
app configuration
"""

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BalafonAppConfig(AppConfig):
    name = 'balafon.Profile'
    verbose_name = _("Balafon Profile")
