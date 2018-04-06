# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from django.core.management.base import BaseCommand

from balafon.Crm import models


class Command(BaseCommand):
    help = "find the same as contacts"

    def add_arguments(self, parser):
        parser.add_argument('group_name', type=str, default="", nargs='?')

    def handle(self, group_name, *args, **options):
        verbose = options.get('verbosity', 0)

        group = None
        if group_name:
            group, is_new = models.Group.objects.get_or_create(name=group_name)
            if verbose > 0:
                print("create" if is_new else "update", "group", group_name)
        
        total_count = 0
        for index, contact in enumerate(models.Contact.objects.all()):
            if contact.lastname and contact.firstname:
                same_as = models.Contact.objects.filter(
                    lastname=contact.lastname, firstname=contact.firstname
                ).exclude(id=contact.id)
                same_as_count = same_as.count()
                if same_as_count > 0:
                    print(index, contact, same_as_count, "SameAs")
                    total_count += 1
                    if group:
                        group.contacts.add(contact)
                        group.save()
        
        if verbose > 0:
            print(total_count, "SameAs")
