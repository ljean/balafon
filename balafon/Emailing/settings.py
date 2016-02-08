# -*- coding: utf-8 -*-
"""common place for all Emailing settings"""

from importlib import import_module

from django.conf import settings as project_settings


def get_default_subscription_type():
    """return default subscription"""
    return getattr(project_settings, 'BALAFON_DEFAULT_SUBSCRIPTION_TYPE', None)


def is_mandrill_used():
    """return true if mandrill is used for sending emails"""
    return 'djrill' in project_settings.INSTALLED_APPS


def is_subscribe_enabled():
    """return true if subscribe page is enabled : True by default for compatibility reason"""
    return getattr(project_settings, 'BALAFON_SUBSCRIBE_ENABLED', True)


def is_email_subscribe_enabled():
    """return true if email subscribe page is enabled : True by default for compatibility reason"""
    return getattr(project_settings, 'BALAFON_EMAIL_SUBSCRIBE_ENABLED', True)


def get_subscription_form():
    """return custom from for newsletter subscription"""
    try:
        form_name = getattr(project_settings, 'BALAFON_SUBSCRIBE_FORM')
        module_name, class_name = form_name.rsplit('.', 1)
        module = import_module(module_name)
        subscribe_form = getattr(module, class_name)
    except AttributeError:
        subscribe_form = None
    return subscribe_form
