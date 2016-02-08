# -*- coding: utf-8 -*-

from importlib import import_module

from django.dispatch import receiver

from djrill.signals import webhook_event


@receiver(webhook_event)
def handle_bounce(sender, event_type, data, **kwargs):
    """
    This signal is received when the mandrill webhook is called
    Manage hard_bounce and soft_bounce
    """

    # Avoid import error
    on_bounce = import_module("balafon.Emailing.utils", ".").on_bounce
    emailing_class = import_module("balafon.Emailing.models", ".").Emailing

    msg = data["msg"]
    if event_type in ('hard_bounce', 'soft_bounce', 'spam', 'reject', 'unsub'):
        emailing_id = None
        contact_uuid = None

        email = msg['email']
        description = msg['bounce_description']
        permanent = event_type != 'soft_bounce'

        if msg["tags"]:
            try:
                emailing_id = int(msg["tags"][0])
                contact_uuid = msg["tags"][1]
            except (IndexError, ValueError):
                emailing_id = None
                contact_uuid = None

        on_bounce(event_type, email, description, permanent, contact_uuid, emailing_id)
