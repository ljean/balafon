# -*- coding: utf-8 -*-
"""test mandrill webhooks"""

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

import datetime
import json
from unittest import skipIf

from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from sanza.Crm import models
from sanza.Emailing.utils import on_bounce

@skipIf(not ("djrill" in settings.INSTALLED_APPS), "djrill is not installed")
class MandrillBounceTestCase(TestCase):

    def test_bounce(self):
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        subscription2 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        url = reverse("djrill_webhook")+"?secret={0}".format(settings.DJRILL_WEBHOOK_SECRET)

        msg = {
            "email": contact.email,
            "bounce_description": "Just an error"
        }
        post_data = [
            {
                'event': {
                    "event_type": "soft_bounce",
                    'msg': msg,
                }
            },
            {
                'event': {
                    "event_type": "soft_bounce",
                    'msg': {
                        "email": "unknonw@xyz.fr",
                        "bounce_description": "No email for this one"
                    },
                }
            }
        ]

        json_content = json.dumps(post_data)

        data = {
            "mandrill_events": json_content,
        }

        self.assertEqual(models.Action.objects.count(), 0)

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(models.Action.objects.count(), 2)
        action = models.Action.objects.all().order_by("id")[0]
        self.assertEqual(action.detail, msg["bounce_description"])
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, post_data[0]["event"]["event_type"])
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 0)
        contact = action.contacts.all()[0]
        self.assertEqual(contact.email, msg["email"])
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, True)

        action = models.Action.objects.all().order_by("id")[1]
        self.assertEqual(action.type.name, post_data[0]["event"]["event_type"])
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 0)

    def test_hard_bounce(self):
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        subscription2 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        url = reverse("djrill_webhook")+"?secret={0}".format(settings.DJRILL_WEBHOOK_SECRET)

        msg = {
            "email": contact.email,
            "bounce_description": "Just an error"
        }
        post_data = [{
            'event': {
                "event_type": "hard_bounce",
                'msg': msg,
            }
        }]

        json_content = json.dumps(post_data)

        data = {
            "mandrill_events": json_content,
        }

        self.assertEqual(models.Action.objects.count(), 0)

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.detail, msg["bounce_description"])
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, post_data[0]["event"]["event_type"])

        self.assertEqual(action.contacts.count(), 1)

        self.assertEqual(action.entities.count(), 0)

        contact = action.contacts.all()[0]
        self.assertEqual(contact.email, msg["email"])
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, False)


class BounceTestCase(TestCase):

    def test_soft_bounce(self):
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        subscription2 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        self.assertEqual(models.Action.objects.count(), 0)

        email = contact.email
        description = "Just an error"
        on_bounce(email, description, False)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.detail, description)
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "soft_bounce")

        self.assertEqual(action.contacts.count(), 1)

        self.assertEqual(action.entities.count(), 0)

        contact = action.contacts.all()[0]
        self.assertEqual(contact.email, email)
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, True)

    def test_hard_bounce(self):
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        subscription2 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        self.assertEqual(models.Action.objects.count(), 0)

        email = contact.email
        description = "Just an error"
        on_bounce(email, description, True)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.detail, description)
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "hard_bounce")

        self.assertEqual(action.contacts.count(), 1)

        self.assertEqual(action.entities.count(), 0)

        contact = action.contacts.all()[0]
        self.assertEqual(contact.email, email)
        self.assertEqual(contact.subscription_set.count(), 2)
        for subscription in contact.subscription_set.all():
            self.assertEqual(subscription.accept_subscription, False)

    def test_hard_bounce_no_contact(self):
        self.assertEqual(models.Action.objects.count(), 0)

        email = "toto@toto.fr"
        description = "Just an error"
        on_bounce(email, description, True)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.detail, description)
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "hard_bounce")

        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 0)

    def test_hard_bounce_several_contacts(self):
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        subscription2 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        contact = mommy.make(models.Contact, email=contact.email)
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        subscription2 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        self.assertEqual(models.Action.objects.count(), 0)

        email = contact.email
        description = "Just an error"
        on_bounce(email, description, True)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.detail, description)
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "hard_bounce")

        self.assertEqual(action.contacts.count(), 2)
        self.assertEqual(action.entities.count(), 0)

        for contact in action.contacts.all():
            self.assertEqual(contact.email, email)
            self.assertEqual(contact.subscription_set.count(), 2)
            for subscription in contact.subscription_set.all():
                self.assertEqual(subscription.accept_subscription, False)

    def test_hard_bounce_several_contacts(self):
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        subscription1 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)
        subscription2 = mommy.make(models.Subscription, contact=contact, accept_subscription=True)

        entity = mommy.make(models.Entity, email=contact.email)
        default_contact = entity.default_contact
        subscription1 = mommy.make(models.Subscription, contact=default_contact, accept_subscription=True)
        subscription2 = mommy.make(models.Subscription, contact=default_contact, accept_subscription=True)

        self.assertEqual(models.Action.objects.count(), 0)

        email = contact.email
        description = "Just an error"
        on_bounce(email, description, True)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.detail, description)
        self.assertEqual(action.planned_date.date(), datetime.date.today())
        self.assertEqual(action.type.name, "hard_bounce")

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
