# -*- coding: utf-8 -*-
"""test mandrill webhooks"""

import datetime
import json
from unittest import skipIf

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from balafon.Crm import models
from balafon.Emailing.models import Emailing
from balafon.Emailing.settings import is_mandrill_used
from balafon.Emailing.utils import on_bounce


@skipIf(not (is_mandrill_used()), "mandrill is not used")
class MandrillBounceTestCase(TestCase):
    """Test mandrill webhook"""

    def test_bounce(self):
        """test bounce received"""
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        emailing = mommy.make(Emailing, subscription_type=subscription1.subscription_type)

        url = reverse("djrill_webhook")+"?secret={0}".format(settings.DJRILL_WEBHOOK_SECRET)

        mandrill_events = [
            {
                "event": "soft_bounce",
                "_id": "01234567890123456789012345678901",
                "msg": {
                    "ts": 1421340778,
                    "_id": "01234567890123456789012345678901",
                    "state": "soft-bounced",
                    "subject": "demo",
                    "email": contact.email,
                    "tags": ["{0}".format(emailing.id), contact.uuid],
                    "smtp_events": [],
                    "resends": [],
                    "_version": "UfoAzdddArJmfiXqHrxyDB",
                    "diag": "",
                    "bgtools_code": 21,
                    "sender": "ljean@apidev.fr",
                    "template": None,
                    "bounce_description": "invalid_domain",
                },
                "ts":1421341522,
            }, {
                "event": "soft_bounce",
                "_id": "01234567890123456789012345678902",
                "msg": {
                    "ts": 1421340778,
                    "_id": "01234567890123456789012345678902",
                    "state": "soft-bounced",
                    "subject": "demo",
                    "email": "unknonw@xyz.fr",
                    "tags": [],
                    "smtp_events": [],
                    "resends": [],
                    "_version": "UfoAzdddArJmfiXqHrxyDB",
                    "diag": "",
                    "bgtools_code": 21,
                    "sender": "ljean@apidev.fr",
                    "template": None,
                    "bounce_description": "invalid_domain"
                },
                "ts": 1421341522
            },
        ]

        json_content = json.dumps(mandrill_events)

        post_data = {
            "mandrill_events": json_content,
        }

        self.assertEqual(models.Action.objects.count(), 0)

        response = self.client.post(url, data=post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(models.Action.objects.count(), 2)
        action = models.Action.objects.all().order_by("id")[0]
        self.assertEqual(action.subject, "toto@toto.fr - soft_bounce: invalid_domain")
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "bounce")
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 0)
        contact = action.contacts.all()[0]
        self.assertEqual(contact.email, "toto@toto.fr")
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, True)

        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.soft_bounce.count(), 1)

        action = models.Action.objects.all().order_by("id")[1]
        self.assertEqual(action.type.name, "bounce")
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 0)

    def test_hard_bounce(self):
        """test hard bounce received from mandrill"""
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        url = reverse("djrill_webhook")+"?secret={0}".format(settings.DJRILL_WEBHOOK_SECRET)

        mandrill_events = [
            {
                "event": "hard_bounce",
                "_id": "01234567890123456789012345678901",
                "msg": {
                    "ts": 1421340778,
                    "_id": "01234567890123456789012345678901",
                    "state": "hard-bounced",
                    "subject": "demo",
                    "email": contact.email,
                    "tags": [],
                    "smtp_events": [],
                    "resends": [],
                    "_version": "UfoAzdddArJmfiXqHrxyDB",
                    "diag": "",
                    "bgtools_code": 21,
                    "sender": "ljean@apidev.fr",
                    "template": None,
                    "bounce_description": "invalid_domain",
                },
                "ts":1421341522,
            }
        ]

        json_content = json.dumps(mandrill_events)

        post_data = {
            "mandrill_events": json_content,
        }

        self.assertEqual(models.Action.objects.count(), 0)

        response = self.client.post(url, data=post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, "toto@toto.fr - hard_bounce: invalid_domain")
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "bounce")

        self.assertEqual(action.contacts.count(), 1)

        self.assertEqual(action.entities.count(), 0)

        contact = action.contacts.all()[0]
        self.assertEqual(contact.email, "toto@toto.fr")
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, False)


class BounceTestCase(TestCase):
    """test bounce behavior"""

    def test_soft_bounce(self):
        """soft bounce: it should trace it but keep contact subscribed"""
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        emailing = mommy.make(Emailing, subscription_type=subscription1.subscription_type)

        self.assertEqual(models.Action.objects.count(), 0)

        email = contact.email
        description = "Just an error"
        on_bounce("soft_bounce", email, description, False, contact.uuid, emailing.id)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, "toto@toto.fr - soft_bounce: "+description)
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "bounce")

        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 0)

        contact = action.contacts.all()[0]
        self.assertEqual(contact.email, email)
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, True)

        self.assertEqual(emailing.soft_bounce.count(), 1)
        self.assertEqual(emailing.hard_bounce.count(), 0)
        self.assertEqual(emailing.unsub.count(), 0)
        self.assertEqual(emailing.spam.count(), 0)
        self.assertEqual(emailing.rejected.count(), 0)

    def test_bounce_types(self):
        """test different types of bounces"""
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        emailing = mommy.make(Emailing, subscription_type=subscription1.subscription_type)

        self.assertEqual(models.Action.objects.count(), 0)

        event_types = ("soft_bounce", "hard_bounce", "rejected", "spam", "unsub")

        email = contact.email
        description = "Just an error"
        for event_type in event_types:
            on_bounce(event_type, email, description, False, contact.uuid, emailing.id)

        self.assertEqual(emailing.soft_bounce.count(), 1)
        self.assertEqual(emailing.hard_bounce.count(), 1)
        self.assertEqual(emailing.unsub.count(), 1)
        self.assertEqual(emailing.spam.count(), 1)
        self.assertEqual(emailing.rejected.count(), 1)

    def test_bounce_long_description(self):
        """test what happen if bounce description is too long"""

        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        emailing = mommy.make(Emailing, subscription_type=subscription1.subscription_type)

        self.assertEqual(models.Action.objects.count(), 0)

        email = contact.email
        description = "Just an error"*100
        on_bounce("soft_bounce", email, description, False, contact.uuid, emailing.id)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        text = "toto@toto.fr - soft_bounce: "+description
        self.assertEqual(action.subject, text[:200])
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "bounce")

        self.assertEqual(emailing.soft_bounce.count(), 1)
        self.assertEqual(emailing.hard_bounce.count(), 0)
        self.assertEqual(emailing.unsub.count(), 0)
        self.assertEqual(emailing.spam.count(), 0)
        self.assertEqual(emailing.rejected.count(), 0)

    def test_hard_bounce(self):
        """test hard bounce: trace it and unsubscribe"""
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        emailing = mommy.make(Emailing, subscription_type=subscription1.subscription_type)

        self.assertEqual(models.Action.objects.count(), 0)

        email = contact.email
        description = "Just an error"
        on_bounce("hard_bounce", email, description, True, contact.uuid, emailing.id)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, "toto@toto.fr - hard_bounce: "+description)
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "bounce")

        self.assertEqual(action.contacts.count(), 1)

        self.assertEqual(action.entities.count(), 0)

        contact = action.contacts.all()[0]
        self.assertEqual(contact.email, email)
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, False)

        self.assertEqual(emailing.soft_bounce.count(), 0)
        self.assertEqual(emailing.hard_bounce.count(), 1)
        self.assertEqual(emailing.unsub.count(), 0)
        self.assertEqual(emailing.spam.count(), 0)
        self.assertEqual(emailing.rejected.count(), 0)

    def test_hard_bounce_no_contact(self):
        """test hard bounce and no contact is matching"""
        self.assertEqual(models.Action.objects.count(), 0)

        emailing = mommy.make(Emailing)

        email = "toto@toto.fr"
        description = "Just an error"
        on_bounce("hard_bounce", email, description, True, None, emailing.id)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, "toto@toto.fr - hard_bounce: "+description)
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "bounce")

        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 0)

        self.assertEqual(emailing.soft_bounce.count(), 0)
        self.assertEqual(emailing.hard_bounce.count(), 0)
        self.assertEqual(emailing.unsub.count(), 0)
        self.assertEqual(emailing.spam.count(), 0)
        self.assertEqual(emailing.rejected.count(), 0)

    def test_hard_bounce_several_contacts(self):
        """hard bounce for several contacts"""

        contact = mommy.make(models.Contact, email="toto@toto.fr")
        mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        entity = mommy.make(models.Entity, email=contact.email)
        default_contact = entity.default_contact
        subscription1 = mommy.make(models.Subscription, contact=default_contact, accept_subscription=True)
        mommy.make(models.Subscription, contact=default_contact, accept_subscription=True)

        emailing = mommy.make(Emailing, subscription_type=subscription1.subscription_type)

        self.assertEqual(models.Action.objects.count(), 0)

        email = contact.email
        description = "Just an error"
        on_bounce("hard_bounce", email, description, True, contact.uuid, emailing.id)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, "toto@toto.fr - hard_bounce: "+description)
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "bounce")

        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 1)

        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email, email)
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, False)

        contact = models.Contact.objects.get(id=default_contact.id)
        self.assertEqual(contact.email, "")
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, False)

        self.assertEqual(emailing.soft_bounce.count(), 0)
        self.assertEqual(emailing.hard_bounce.count(), 1)
        self.assertEqual(emailing.unsub.count(), 0)
        self.assertEqual(emailing.spam.count(), 0)
        self.assertEqual(emailing.rejected.count(), 0)
