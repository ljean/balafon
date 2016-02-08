# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from balafon.Emailing.models import Emailing
from balafon.Emailing.utils import send_newsletter
from datetime import datetime


class Command(BaseCommand):
    help = u"send all emailing marked ready for sending"
    use_argparse = False

    def handle(self, *args, **options):
        #look for emailing to be sent
        verbose = options.get('verbosity', 0)
        
        max_nb = args[0] if len(args) > 0 else 20
        emailings = Emailing.objects.filter(
            status__in=(Emailing.STATUS_SCHEDULED, Emailing.STATUS_SENDING),
            scheduling_dt__lte=datetime.now()
        )
        total_sent = 0
        for emailing in emailings:
            emailing.status = Emailing.STATUS_SENDING
            emailing.save()
            
            nb_sent = send_newsletter(emailing, max_nb)
            
            if verbose:
                print nb_sent, "emails sent for emailing", emailing.id
            
            total_sent += nb_sent
            
            if emailing.send_to.count() == 0:
                if verbose:
                    print "emailing", emailing.id, "done"
                emailing.status = Emailing.STATUS_SENT
                emailing.save()
                
            if total_sent > max_nb:
                break #stop sending if we reached the allowed number
