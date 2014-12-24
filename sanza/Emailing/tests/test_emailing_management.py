# -*- coding: utf-8 -*-
"""test emailing configuration"""

from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone

from coop_cms.models import Newsletter
from model_mommy import mommy

from sanza.Crm import models
from sanza.Emailing.models import Emailing, MagicLink
from sanza.Emailing.tests import BaseTestCase


class EmailingManagementTestCase(BaseTestCase):

    def now(self):
        if settings.USE_TZ:
            return datetime.now().replace(tzinfo=timezone.utc)
        else:
            return datetime.now()

    def test_view_newsletters_list(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]

        newsletter1 = mommy.make(Newsletter, subject='newsletter1')
        newsletter2 = mommy.make(Newsletter, subject='newsletter2')

        emailing1 = mommy.make(Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = self.now(), sending_dt = None)
        for c in contacts:
            emailing1.send_to.add(c)
        emailing1.save()

        emailing2 = mommy.make(Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SENDING,
            scheduling_dt = self.now(), sending_dt = None)
        emailing2.send_to.add(contacts[0])
        emailing2.save()

        emailing3 = mommy.make(Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SENT,
            scheduling_dt = self.now(), sending_dt = self.now())
        emailing3.send_to.add(contacts[-1])
        emailing3.save()

        response = self.client.get(reverse('emailing_newsletter_list'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'newsletter1')
        self.assertContains(response, 'newsletter2')

        self.assertContains(response, emailing1.get_info())
        self.assertContains(response, emailing2.get_info())
        self.assertContains(response, emailing3.get_info())

    def test_emailing_next_action(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]

        emailing = mommy.make(Emailing,
            status=Emailing.STATUS_EDITING,
            scheduling_dt = self.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()

        next_url = reverse('emailing_confirm_send_mail', args=[emailing.id])
        self.assertTrue(emailing.next_action().find(next_url))

        emailing.status = Emailing.STATUS_SCHEDULED
        emailing.save()
        next_url = reverse('emailing_cancel_send_mail', args=[emailing.id])
        self.assertTrue(emailing.next_action().find(next_url))

        emailing.status = Emailing.STATUS_SENDING
        emailing.save()
        self.assertEqual(emailing.next_action(), "")

        emailing.status = Emailing.STATUS_SENT
        emailing.save()
        self.assertEqual(emailing.next_action(), "")

    def test_view_magic_link(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]

        emailing = mommy.make(Emailing,
            status=Emailing.STATUS_SENT,
            scheduling_dt = self.now(), sending_dt = self.now())
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()

        emailing2 = mommy.make(Emailing)

        google = "http://www.google.fr"
        google_link = MagicLink.objects.create(emailing=emailing, url=google)
        for c in contacts:
            google_link.visitors.add(c)
        google_link.save()

        toto = "http://www.toto.fr"
        toto_link = MagicLink.objects.create(emailing=emailing, url=toto)
        toto_link.visitors.add(contacts[0])
        toto_link.save()

        titi = "http://www.titi.fr"
        titi_link = MagicLink.objects.create(emailing=emailing2, url=titi)
        titi_link.visitors.add(contacts[0])
        titi_link.save()

        url = reverse('emailing_view', args=[emailing.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, toto)
        self.assertContains(response, google)
        self.assertNotContains(response, titi)

    def test_confirm_sending(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]

        emailing = mommy.make(Emailing, status=Emailing.STATUS_EDITING)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()

        next_url = reverse('emailing_confirm_send_mail', args=[emailing.id])
        response = self.client.get(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)

        response = self.client.post(next_url, data={"scheduling_dt": "01/01/2120 00:00"})
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)

        response = self.client.post(next_url, data={"confirm": "1", "scheduling_dt": "01/01/2120 00:00"})
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SCHEDULED)
        self.assertNotEqual(emailing.scheduling_dt, None)
        if settings.USE_TZ:
            self.assertTrue(emailing.scheduling_dt > datetime.now().replace(tzinfo=timezone.get_current_timezone()))
        else:
            self.assertTrue(emailing.scheduling_dt > datetime.now())

    def test_cancel_sending(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]

        emailing = mommy.make(Emailing, status=Emailing.STATUS_SCHEDULED, scheduling_dt=self.now())
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()

        next_url = reverse('emailing_cancel_send_mail', args=[emailing.id])
        response = self.client.get(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SCHEDULED)
        self.assertNotEqual(emailing.scheduling_dt, None)

        response = self.client.post(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SCHEDULED)
        self.assertNotEqual(emailing.scheduling_dt, None)

        response = self.client.post(next_url, data={"confirm": "1"})
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)
