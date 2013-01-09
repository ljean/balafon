# -*- coding: utf-8 -*-

from sanza.Crm.models import EntityType

def crm(request):
    return {
        'SANZA_ENTITY_TYPES': EntityType.objects.all(),
    }
    