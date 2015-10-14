# -*- coding: utf-8 -*-
"""common place for all Emailing settings"""

from django.conf import settings as project_settings


def get_default_subscription_type():
    """return default subscription"""
    return getattr(project_settings, 'SANZA_DEFAULT_SUBSCRIPTION_TYPE', None)


def is_mandrill_used():
    """return true if mandrill is used for sending emails"""
    return 'djrill' in project_settings.INSTALLED_APPS


def is_subscribe_enabled():
    """return true if subscribe page is enabled : True by default for compatibility reason"""
    return getattr(project_settings, 'SANZA_SUBSCRIBE_ENABLED', True)


def is_email_subscribe_enabled():
    """return true if email subscribe page is enabled : True by default for compatibility reason"""
    return getattr(project_settings, 'SANZA_EMAIL_SUBSCRIBE_ENABLED', True)
