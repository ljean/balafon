# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from sanza.Emailing.models import EmailingCounter
from datetime import datetime

class Command(BaseCommand):
    help = u"Show the list of emailing counters"

    def handle(self, *args, **options):
        
        if EmailingCounter.objects.count()==0:
            print "No emailing yet"
        else:
            columns = ('bought_date', 'total', 'credit', 'finished_date')
            
            header = u"|".join([c.capitalize().replace(u'_', u' ').center(15) for c in columns])
            print header 
            print '-' * len(header)
            for e in EmailingCounter.objects.all().order_by("bought_date"):
                print u"|".join([unicode(getattr(e, c)).center(15) for c in columns])

