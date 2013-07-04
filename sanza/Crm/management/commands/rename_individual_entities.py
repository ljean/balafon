# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from sanza.Crm import models
from datetime import date
from sanza.Crm.settings import ALLOW_SINGLE_CONTACT
from django.conf import settings

class Command(BaseCommand):
    help = u"add a new credit of emailings"

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        if ALLOW_SINGLE_CONTACT:
            print "this command is disabled if SANZA_ALLOW_SINGLE_CONTACT is set"
            return
        
        individual_entity_id = getattr(settings, 'SANZA_INDIVIDUAL_ENTITY_ID', 1)
        
        for e in models.Entity.objects.filter(type__id=individual_entity_id):
            e.name = u"{0.lastname} {0.firstname}".format(e.default_contact).strip().upper()
            e.save()
        
            if verbose:
                print e.name
        print models.Entity.objects.filter(type__id=individual_entity_id).count(), "entities have been renamed"
            