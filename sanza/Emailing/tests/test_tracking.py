# -*- coding: utf-8 -*-
"""test email tracking"""

from datetime import datetime, date

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import management
from django.core import mail
from django.core.urlresolvers import reverse

from model_mommy import mommy
from coop_cms.models import Newsletter

from sanza.Crm import models
from sanza.Emailing.models import Emailing
from sanza.Emailing.tests import BaseTestCase


class EmailTrackingTest(BaseTestCase):

    def setUp(self):
        super(EmailTrackingTest, self).setUp()
        settings.COOP_CMS_FROM_EMAIL = 'toto@toto.fr'
        settings.COOP_CMS_REPLY_TO = 'titi@toto.fr'

        settings.COOP_CMS_SITE_PREFIX = "toto.fr"
        site = Site.objects.get_current()
        site.domain = "toto.fr"
        site.save()

    def test_track_image(self):

        entity = mommy.make(models.Entity, name="my corp")

        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]

        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a><a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)

        emailing = mommy.make(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SENT,
            scheduling_dt = datetime.now(), sending_dt = datetime.now())
        for c in contacts:
            emailing.sent_to.add(c)
        emailing.save()

        self.assertEqual(emailing.opened_emails.count(), 0)

        for c in contacts[:-1]:
            tracking_url = reverse("emailing_email_tracking", args=[emailing.id, c.uuid])
            response = self.client.get(tracking_url)
            self.assertEqual(response.status_code, 200)

        self.assertEqual(emailing.opened_emails.count(), len(contacts)-1)
        for c in contacts[:-1]:
            self.assertTrue(c in list(emailing.opened_emails.all()))

        for c in contacts[-1:]:
            self.assertFalse(c in list(emailing.opened_emails.all()))

    def test_track_image_twice(self):

        entity = mommy.make(models.Entity, name="my corp")

        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]

        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a><a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)

        emailing = mommy.make(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SENT,
            scheduling_dt = datetime.now(), sending_dt = datetime.now())
        for c in contacts:
            emailing.sent_to.add(c)
        emailing.save()

        self.assertEqual(emailing.opened_emails.count(), 0)

        for c in contacts[:-1]:
            tracking_url = reverse("emailing_email_tracking", args=[emailing.id, c.uuid])
            response = self.client.get(tracking_url)
            self.assertEqual(response.status_code, 200)

            response = self.client.get(tracking_url)
            self.assertEqual(response.status_code, 200)

        self.assertEqual(emailing.opened_emails.count(), len(contacts)-1)
        for c in contacts[:-1]:
            self.assertTrue(c in list(emailing.opened_emails.all()))

        for c in contacts[-1:]:
            self.assertFalse(c in list(emailing.opened_emails.all()))

    def test_send_newsletter_check_tracking(self):

        entity = mommy.make(models.Entity, name="my corp")

        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]

        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a><a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)

        emailing = mommy.make(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()

        management.call_command('emailing_scheduler', verbosity=0, interactive=False)

        emailing = Emailing.objects.get(id=emailing.id)

        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))

        self.assertEqual(len(mail.outbox), len(contacts))

        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)

        for email, contact in zip(outbox, contacts):
            self.assertNotEqual(newsletter.get_site_prefix(), "")
            tracking_url = newsletter.get_site_prefix() + reverse("emailing_email_tracking",
                args=[emailing.id, contact.uuid])
            self.assertTrue(email.alternatives[0][1], "text/html")
            self.assertTrue(email.alternatives[0][0].find(tracking_url)>=0)
