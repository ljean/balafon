# -*- coding: utf-8 -*-

from django.conf import settings as project_settings

def get_default_subscription_type():
    return getattr(project_settings, 'SANZA_DEFAULT_SUBSCRIPTION_TYPE', None)


def is_mandrill_used():
    return 'djrill' in project_settings.INSTALLED_APPS