# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from sanza.Emailing.models import EmailingCounter
from datetime import date

class Command(BaseCommand):
    help = u"[DEPRECATED] add a new credit of emailings"

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)
        
        print "DEPRECATED"
        
        
        