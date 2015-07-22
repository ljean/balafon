# -*- coding: utf-8 -*-
"""common place for settings. Define defaults"""

from django.conf import settings
from django.utils.translation import ugettext as _

def is_public_api_allowed():
    """returns true if an anonymous can view some data : products, categories, tags"""
    return getattr(settings, 'SANZA_STORE_ALLOW_PUBLIC_API', False)


def get_cart_type_name():
    """returns true if an anonymous can view some data : products, categories, tags"""
    return getattr(settings, 'SANZA_STORE_CART_TYPE', _(u'Cart'))
