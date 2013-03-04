# -*- coding: utf-8 -*-

from sanza.Crm.models import EntityType
from django.conf import settings 

def crm(request):
    return {
        'SANZA_ENTITY_TYPES': EntityType.objects.all(),
        'SANZA_MULTI_USER': getattr(settings, 'SANZA_MULTI_USER', True),
    }
    