# -*- coding: utf-8 -*-
"""context processor"""

from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

from balafon import VERSION
from balafon.Crm.models import EntityType, ActionType
from balafon.Crm import settings as crm_settings
from balafon.utils import is_allowed_homepage


def crm(request):
    """add constant to context"""
    
    site_url = None
    if not settings.BALAFON_AS_HOMEPAGE:
        try:
            site_url = reverse('homepage')
        except NoReverseMatch:
            pass

    return {
        'BALAFON_VERSION': VERSION,
        'BALAFON_SITE_URL': site_url,
        'BALAFON_ALLOW_SINGLE_CONTACT': crm_settings.ALLOW_SINGLE_CONTACT,
        'BALAFON_NO_ENTITY_TYPE': crm_settings.NO_ENTITY_TYPE,
        'BALAFON_ENTITY_TYPES': EntityType.objects.all(),
        'BALAFON_MULTI_USER': getattr(settings, 'BALAFON_MULTI_USER', True),
        'BALAFON_EMAIL_LOGIN': ('balafon.Profile.backends.EmailModelBackend' in settings.AUTHENTICATION_BACKENDS),
        'BALAFON_STORE_INSTALLED': 'balafon.Store' in settings.INSTALLED_APPS,
        'NOW': datetime.now(),
        'is_allowed_homepage': is_allowed_homepage(request.path),
        'addable_action_types': ActionType.objects.filter(set__isnull=False),
    }
