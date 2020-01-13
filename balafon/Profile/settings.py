# -*- coding: utf-8 -*-
"""common place for all Emailing settings"""

from django.conf import settings as project_settings


def is_registration_enabled():
    """return true if subscribe page is enabled : True by default for compatibility reason"""
    return getattr(project_settings, 'BALAFON_REGISTRATION_ENABLED', True)
