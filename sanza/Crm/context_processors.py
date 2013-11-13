# -*- coding: utf-8 -*-

from sanza.Crm.models import EntityType
from django.conf import settings 
from sanza.Crm import settings as crm_settings
from django.core.urlresolvers import reverse, NoReverseMatch

def crm(request):
    
    site_url = None
    if not settings.SANZA_AS_HOMEPAGE:
        try:
            site_url = reverse('homepage')
        except NoReverseMatch:
            pass
    
    return {
        'SANZA_SITE_URL': site_url,
        'SANZA_ALLOW_SINGLE_CONTACT': crm_settings.ALLOW_SINGLE_CONTACT,
        'SANZA_NO_ENTITY_TYPE': crm_settings.NO_ENTITY_TYPE,
        'SANZA_ENTITY_TYPES': EntityType.objects.all(),
        'SANZA_MULTI_USER': getattr(settings, 'SANZA_MULTI_USER', True),
        'SANZA_EMAIL_LOGIN': ('sanza.Profile.backends.EmailModelBackend' in settings.AUTHENTICATION_BACKENDS),
    }
