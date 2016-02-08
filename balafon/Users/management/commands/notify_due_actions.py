# -*- coding: utf-8 -*-
"""notify_due_actions command"""

from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from balafon.utils import logger


def notify_due_actions(user, actions):
    """send message by email"""

    notification_email = user.email
    from_email = settings.DEFAULT_FROM_EMAIL
        
    data = {
        'user': user,
        'actions': actions,
        'site': settings.COOP_CMS_SITE_PREFIX,
    }
    template = get_template('Users/due_actions_notification_email.txt')
    content = template.render(Context(data))
    
    email = EmailMessage(
        _(u"Balafon: You have due actions"),
        content,
        from_email,
        [notification_email]
    )
    
    try:
        email.send()
    except Exception:  #pylint: disable=broad-except
        logger.exception("notify_due_actions")


class Command(BaseCommand):
    """The command"""
    help = u"notify due actions"
    use_argparse = False

    def handle(self, *args, **options):
        """main of command"""

        verbose = options.get('verbosity', 0)
        tomorrow = date.today() + timedelta(1)

        for user in User.objects.filter(userpreferences__notify_due_actions=True, teammember__active=True):
            
            actions = user.teammember.action_set.filter(planned_date__lt=tomorrow, done=False).order_by("planned_date")
            if actions.count() == 0:
                if verbose:
                    print "no due actions for", user.username
            else:
                if verbose:
                    print "send", actions.count(), "due actions to", user.username

                notify_due_actions(user, actions)
            
        if verbose:
            print "done"
