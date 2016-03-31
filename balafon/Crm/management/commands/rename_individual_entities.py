# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import BaseCommand

from balafon.Crm import models
from balafon.Crm.settings import ALLOW_SINGLE_CONTACT


class Command(BaseCommand):
    help = u"add a new credit of emailings"
    use_argparse = False

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        if ALLOW_SINGLE_CONTACT:
            print "this command is disabled if BALAFON_ALLOW_SINGLE_CONTACT is set"
            return
        
        individual_entity_id = getattr(settings, 'BALAFON_INDIVIDUAL_ENTITY_ID', 1)
        
        for entity in models.Entity.objects.filter(type__id=individual_entity_id):
            entity.name = u"{0.lastname} {0.firstname}".format(entity.default_contact).strip().upper()
            entity.save()
        
            if verbose:
                print entity.name
        print models.Entity.objects.filter(type__id=individual_entity_id).count(), "entities have been renamed"
