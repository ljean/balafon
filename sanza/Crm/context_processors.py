# -*- coding: utf-8 -*-
"""context processor"""

from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

from sanza import VERSION
from sanza.Crm.models import EntityType
from sanza.Crm import settings as crm_settings


def crm(request):
    """add constant to context"""
    
    site_url = None
    if not settings.SANZA_AS_HOMEPAGE:
        try:
            site_url = reverse('homepage')
        except NoReverseMatch:
            pass
    
    return {
        'SANZA_VERSION': VERSION,
        'SANZA_SITE_URL': site_url,
        'SANZA_ALLOW_SINGLE_CONTACT': crm_settings.ALLOW_SINGLE_CONTACT,
        'SANZA_NO_ENTITY_TYPE': crm_settings.NO_ENTITY_TYPE,
        'SANZA_ENTITY_TYPES': EntityType.objects.all(),
        'SANZA_MULTI_USER': getattr(settings, 'SANZA_MULTI_USER', True),
        'SANZA_EMAIL_LOGIN': ('sanza.Profile.backends.EmailModelBackend' in settings.AUTHENTICATION_BACKENDS),
        'NOW': datetime.now(),
    }
