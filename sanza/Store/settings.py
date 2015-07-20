# -*- coding: utf-8 -*-
"""common place for settings. Define defaults"""

import sys

from django.conf import settings


def is_public_api_allowed():
    """returns true if an anonymous can view some data : products, categories, tags"""
    return getattr(settings, 'SANZA_STORE_ALLOW_PUBLIC_API', False)
