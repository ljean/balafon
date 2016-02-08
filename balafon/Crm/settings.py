# -*- coding: utf-8 -*-
"""common place for settings. Define defaults"""

import sys

from django.conf import settings as project_settings
from django.utils.translation import ugettext as _

ENTITY_LOGO_DIR = getattr(project_settings, 'ENTITY_LOGO_DIR', 'entities/logos')

CONTACT_PHOTO_DIR = getattr(project_settings, 'CONTACT_PHOTO_DIR', 'contacts/photos')

CONTACTS_IMPORT_DIR = getattr(project_settings, 'CSV_IMPORT_DIR', 'imports')

OPPORTUNITY_DISPLAY_ON_BOARD_DEFAULT = getattr(project_settings, 'OPPORTUNITY_DISPLAY_ON_BOARD_DEFAULT', True)

ZONE_GROUP_SEARCH = getattr(project_settings, 'BALAFON_ZONE_GROUP_SEARCH', False)


def get_default_country():
    """returns configured default coutry or 'France'"""
    return getattr(project_settings, 'BALAFON_DEFAULT_COUNTRY', 'France')

ALLOW_COUPLE_GENDER = getattr(project_settings, 'BALAFON_ALLOW_COUPLE_GENDER', False)

ALLOW_SINGLE_CONTACT = getattr(project_settings, 'BALAFON_ALLOW_SINGLE_CONTACT', True)

NO_ENTITY_TYPE = getattr(project_settings, 'BALAFON_NO_ENTITY_TYPE', False)


def is_unaccent_filter_supported():
    """returns True if Postgres unaccent is installed (we can make accent search)"""
    if 'test' in sys.argv:
        return False
    return getattr(project_settings, 'BALAFON_UNACCENT_FILTER_SUPPORT', False)


def city_formatters():
    """get callback for city nae formmating"""
    return getattr(project_settings, 'BALAFON_CITY_FORMATTERS', ())


def get_language_choices(default_label=None):
    """returns list of languages"""
    if default_label is None:
        default_label = _(u'Default')
    return [('', default_label)] + list(project_settings.LANGUAGES)


def has_language_choices():
    """returns true if we should propose language choices"""
    return len(project_settings.LANGUAGES) >= 2


def get_subscription_default_value():
    """returns the default value for subscriptions when """
    return getattr(project_settings, 'BALAFON_SUBSCRIPTION_DEFAULT_VALUE', False)


def show_billing_address():
    """returns True if we must display the Billing address tab on contact and entity form"""
    return getattr(project_settings, 'BALAFON_SHOW_BILLING_ADDRESS', True)