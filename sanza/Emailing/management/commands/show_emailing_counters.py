# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from sanza.Emailing.models import EmailingCounter
from datetime import datetime

class Command(BaseCommand):
    help = u"[DEPRECATED]: Show the list of emailing counters"

    def handle(self, *args, **options):
        
        print "DEPRECATED"

