# -*- coding: utf-8 -*-

import datetime

from django.dispatch import receiver
from django.utils.importlib import import_module

from djrill.signals import webhook_event


@receiver(webhook_event)
def handle_bounce(sender, event_type, data, **kwargs):
    """
    This signal is received when the mandrill webhook is called
    Manage hard_bounce and soft_bounce
    """

    #Avoid import error
    on_bounce = import_module("sanza.Emailing.utils", ".").on_bounce

    event_type = data["event"]["event_type"]
    msg = data["event"]["msg"]
    if event_type == 'hard_bounce' or event_type == 'soft_bounce':

        email = msg['email']
        description = msg['bounce_description']
        permanent = event_type == 'hard_bounce'

        on_bounce(email, description, permanent)
