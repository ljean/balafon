# -*- coding: utf-8 -*-
"""common place for settings. Define defaults"""

from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext as _

from ..utils import load_from_module


def is_public_api_allowed():
    """returns true if an anonymous can view some data : products, categories, tags"""
    return getattr(settings, 'BALAFON_STORE_ALLOW_PUBLIC_API', False)


def get_cart_type_name():
    """returns true if an anonymous can view some data : products, categories, tags"""
    return getattr(settings, 'BALAFON_STORE_CART_TYPE', _('Cart'))


def get_cart_confirmation_subject(profile, action):
    """returns true if an anonymous can view some data : products, categories, tags"""
    subject = getattr(settings, 'BALAFON_CART_CONFIRMATION_EMAIL_SUBJECT', _('Purchasing confirmation'))
    if callable(subject):
        return subject(profile, action)
    else:
        return subject


def get_cart_processed_callback():
    """
    returns a callback defined in BALAFON_CART_PROCESSED_CALLBACK
    This function should take an action has argument
    """
    return load_from_module('BALAFON_CART_PROCESSED_CALLBACK', None)


def get_thumbnail_size():
    """
    returns size of image when displayed as thumbnail
    """
    return getattr(settings, 'BALAFON_STORE_THUMBNAIL_SIZE', "64x64")


def get_thumbnail_crop():
    """
    returns size of image when displayed as thumbnail
    """
    return getattr(settings, 'BALAFON_STORE_THUMBNAIL_CROP', "center")


def get_image_size():
    """
    returns size of image when displayed as thumbnail
    """
    return getattr(settings, 'BALAFON_STORE_IMAGE_SIZE', "300")


def get_image_crop():
    """
    returns size of image when displayed as thumbnail
    """
    return getattr(settings, 'BALAFON_STORE_IMAGE_CROP', None)
