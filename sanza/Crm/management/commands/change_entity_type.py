# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from sanza.Crm import models
from datetime import date

class Command(BaseCommand):
    help = u"add a new credit of emailings"

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        if len(args) < 1:
            print "usage : new_type_name [old_type_id] [group=group_id]"
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
            print "Entity type", new_type_name, "has been created"
        
        for e in qs:
            e.type = entity_type
            e.save()
        
        if verbose:
            print qs.count(), "entities updated"
        