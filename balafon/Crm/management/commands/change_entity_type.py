# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from datetime import date

from django.core.management.base import BaseCommand
from balafon.Crm import models


class Command(BaseCommand):
    help = u"change the entity type"
    use_argparse = False

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        if len(args) < 1:
            print("usage : change_entity_type new_type_name [old_type_id] [group=group_id]")
            return
        
        new_type_name = args[0]
        filter = args[1]
        if filter.find('group=')==0:
            gr_id = filter[6:]
            qs = models.Group.objects.get(id=gr_id).entities.all()
        else:
            qs = models.Entity.objects.filter(type__id=filter)
        
        entity_type, is_new = models.EntityType.objects.get_or_create(name=new_type_name)
        
        if is_new and verbose:
            print("Entity type", new_type_name, "has been created")
        
        for e in qs:
            e.type = entity_type
            e.save()
        
        if verbose:
            print(qs.count(), "entities updated")
