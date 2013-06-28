# -*- coding: utf-8 -*-

from sanza.Crm.models import EntityType
from django.conf import settings 
from sanza.Crm import settings as crm_settings

def crm(request):
    return {
        'SANZA_ALLOW_SINGLE_CONTACT': crm_settings.ALLOW_SINGLE_CONTACT,
        'SANZA_ENTITY_TYPES': EntityType.objects.all(),
        'SANZA_MULTI_USER': getattr(settings, 'SANZA_MULTI_USER', True),
        'SANZA_EMAIL_LOGIN': ('sanza.Profile.backends.EmailModelBackend' in settings.AUTHENTICATION_BACKENDS),
    }
