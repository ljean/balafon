# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from balafon.Crm import models
from datetime import date


class Command(BaseCommand):
    help = u"find the same as contacts"
    use_argparse = False

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        if len(args) < 0:
            print "usage : find_same_as [group_name]"
            return
        
        group = None
        if len(args) >= 1:
            group, is_new = models.Group.objects.get_or_create(name=args[0])
            if verbose:
                print ("create" if is_new else "update"), "group", args[0] 
        
        total_count = 0
        for i, contact in enumerate(models.Contact.objects.all()):
            if contact.lastname and contact.firstname:
                same_as = models.Contact.objects.filter(
                    lastname=contact.lastname, firstname=contact.firstname
                ).exclude(id=contact.id)
                same_as_count = same_as.count()
                if same_as_count > 0:
                    print i, contact, same_as_count, "'SameAs'"
                    total_count += 1
                    if group:
                        group.contacts.add(contact)
                        group.save()
        
        if verbose:
            print total_count, "SameAs"
