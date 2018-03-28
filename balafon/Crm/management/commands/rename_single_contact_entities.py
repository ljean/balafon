# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from django.core.management.base import BaseCommand

from balafon.Crm import models
from balafon.Crm.settings import ALLOW_SINGLE_CONTACT


class Command(BaseCommand):
    help = "add a new credit of emailings"
    use_argparse = False

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        if not ALLOW_SINGLE_CONTACT:
            print("this command is disabled if BALAFON_ALLOW_SINGLE_CONTACT is not set")
            return
        
        for entity in models.Entity.objects.filter(is_single_contact=True):
            entity.name = "{0.lastname} {0.firstname}".format(entity.default_contact).strip().lower()
            entity.save()
        
            if verbose:
                print(entity.name)
        print(models.Entity.objects.filter(is_single_contact=True).count(), "entities have been renamed")
