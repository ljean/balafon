# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from sanza.Crm import models
from datetime import date
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from sanza.utils import logger
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from sanza.Crm import settings as crm_settings
from datetime import timedelta

def notify_due_actions(user, actions):
    #send message by email
    notification_email = user.email
    from_email = settings.DEFAULT_FROM_EMAIL
        
    data = {
        'user': user,
        'actions': actions,
        'site': settings.COOP_CMS_SITE_PREFIX,
    }
    t = get_template('Users/due_actions_notification_email.txt')
    content = t.render(Context(data))
    
    email = EmailMessage(
        _(u"Sanza: You have due actions"),
        content,
        from_email,
        [notification_email]
    )
    
    try:
        email.send()
    except Exception:
        logger.exception("notify_due_actions")


class Command(BaseCommand):
    help = u"notify due actions"

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)
        tomorrow = date.today() + timedelta(1)
        
        for user in User.objects.filter(is_staff=True, userpreferences__notify_due_actions=True):
            
            actions = user.action_set.filter(planned_date__lt=tomorrow, done=False).order_by("planned_date")
            if actions.count() == 0:
                if verbose:
                    print "no due actions for", user.username
            else:
                if verbose:
                    print "send", actions.count(),"due actions to", user.username

                notify_due_actions(user, actions)
            
        if verbose:
            print "done"
        