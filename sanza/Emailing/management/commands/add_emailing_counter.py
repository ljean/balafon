# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from sanza.Emailing.models import EmailingCounter
from datetime import date

class Command(BaseCommand):
    help = u"add a new credit of emailings"

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        if len(args) < 1:
            print "usage : add_emailing_counter 1000"
            return
        
        credit = args[0]
        
        EmailingCounter.objects.create(
            total = credit, credit = credit, bought_date = date.today()
        )
        
        if verbose:
            print "a new credit of ", credit, "has been added"
        