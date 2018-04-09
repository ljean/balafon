# -*- coding: utf-8 -*-
"""test mandrill webhooks"""

from __future__ import unicode_literals

import datetime

from model_mommy import mommy

from balafon.unit_tests import TestCase
from balafon.Crm import models
from balafon.Emailing.models import Emailing
from balafon.Emailing.utils import on_bounce


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
