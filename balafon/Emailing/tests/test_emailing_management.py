# -*- coding: utf-8 -*-
"""test emailing configuration"""

from __future__ import unicode_literals

from datetime import datetime
from unittest import skipIf

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils import timezone

from coop_cms.models import Newsletter
from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Emailing.models import Emailing, MagicLink
from balafon.Emailing.tests import BaseTestCase


class EmailingManagementTestCase(BaseTestCase):
    """test emailing management"""

    def now(self):
        """get current timestamp"""
        if settings.USE_TZ:
            return datetime.now().replace(tzinfo=timezone.utc)
        else:
            return datetime.now()

    def test_view_newsletters_list(self):
        """list of newsletters"""
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact, entity=entity,
                email=name+'@toto.fr',
                lastname=name.capitalize()
            ) for name in names
        ]

        newsletter1 = mommy.make(Newsletter, subject='newsletter1')
        mommy.make(Newsletter, subject='newsletter2')

        emailing1 = mommy.make(
            Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt=self.now(), sending_dt=None
        )
        for contact in contacts:
            emailing1.send_to.add(contact)
        emailing1.save()

        emailing2 = mommy.make(
            Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SENDING,
            scheduling_dt=self.now(), sending_dt=None
        )
        emailing2.send_to.add(contacts[0])
        emailing2.save()

        emailing3 = mommy.make(
            Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SENT,
            scheduling_dt=self.now(), sending_dt=self.now()
        )
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
        """test next actions in emailing process"""
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact,
                entity=entity,
                email=name+'@toto.fr',
                lastname=name.capitalize()
            ) for name in names
        ]

        emailing = mommy.make(
            Emailing,
            status=Emailing.STATUS_EDITING,
            scheduling_dt=self.now(),
            sending_dt=None
        )
        for contact in contacts:
            emailing.send_to.add(contact)
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
        """test links are tracked"""
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact,
                entity=entity,
                email=name+'@toto.fr',
                lastname=name.capitalize()
            ) for name in names
        ]

        emailing = mommy.make(
            Emailing,
            status=Emailing.STATUS_SENT,
            scheduling_dt=self.now(), sending_dt=self.now()
        )
        for contact in contacts:
            emailing.send_to.add(contact)
        emailing.save()

        emailing2 = mommy.make(Emailing)

        google_link = MagicLink.objects.create(emailing=emailing, url="http://www.google.fr")
        for contact in contacts:
            google_link.visitors.add(contact)
        google_link.save()

        toto_link = MagicLink.objects.create(emailing=emailing, url="http://www.toto.fr")
        toto_link.visitors.add(contacts[0])
        toto_link.save()

        titi_link = MagicLink.objects.create(emailing=emailing2, url="http://www.titi.fr")
        titi_link.visitors.add(contacts[0])
        titi_link.save()

        url = reverse('emailing_view', args=[emailing.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, toto_link.url)
        self.assertContains(response, google_link.url)
        self.assertNotContains(response, titi_link.url)

    def test_confirm_sending(self):
        """test confirmation sending"""
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact,
                entity=entity,
                email=name+'@toto.fr',
                lastname=name.capitalize()
            ) for name in names
        ]

        emailing = mommy.make(Emailing, status=Emailing.STATUS_EDITING)
        for contact in contacts:
            emailing.send_to.add(contact)
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
        """test cancel sending"""
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact,
                entity=entity,
                email=name+'@toto.fr',
                lastname=name.capitalize()
            ) for name in names
        ]

        emailing = mommy.make(Emailing, status=Emailing.STATUS_SCHEDULED, scheduling_dt=self.now())
        for contact in contacts:
            emailing.send_to.add(contact)
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


class UpdateEmailingTestCase(BaseTestCase):
    """update emailing"""

    def test_view_update_emailing(self):
        """check the display of the page"""
        subscription_type1 = mommy.make(models.SubscriptionType)
        subscription_type2 = mommy.make(models.SubscriptionType)

        newsletter1 = mommy.make(Newsletter)
        newsletter2 = mommy.make(Newsletter)

        emailing = mommy.make(Emailing, subscription_type=subscription_type1, newsletter=newsletter1)

        url = reverse("emailing_update_emailing", kwargs={'pk': emailing.id})

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(2, len(soup.select("select#id_subscription_type option")))
        self.assertEqual(subscription_type1.id, int(soup.select("select#id_subscription_type option")[0]["value"]))
        self.assertEqual("selected", soup.select("select#id_subscription_type option")[0]["selected"])
        self.assertEqual(subscription_type2.id, int(soup.select("select#id_subscription_type option")[1]["value"]))

        self.assertEqual(2, len(soup.select("select#id_newsletter option")))
        self.assertEqual(newsletter1.id, int(soup.select("select#id_newsletter option")[0]["value"]))
        self.assertEqual("selected", soup.select("select#id_newsletter option")[0]["selected"])
        self.assertEqual(newsletter2.id, int(soup.select("select#id_newsletter option")[1]["value"]))

    def test_view_update_emailing_anonymous(self):
        """check the display of the page"""
        self.client.logout()

        emailing = mommy.make(Emailing)

        url = reverse("emailing_update_emailing", kwargs={'pk': emailing.id})

        response = self.client.get(url)

        self.assertEqual(302, response.status_code)

    def test_view_update_emailing_not_allowed(self):
        """check the display of the page"""
        self.user.is_staff = False
        self.user.save()

        emailing = mommy.make(Emailing)

        url = reverse("emailing_update_emailing", kwargs={'pk': emailing.id})

        response = self.client.get(url)

        self.assertEqual(302, response.status_code)
        redirect_url = "{0}?next={1}".format(settings.LOGIN_URL, url)
        self.assertTrue(response['Location'].find(redirect_url) >= 0)

    @override_settings(BALAFON_EMAILING_SENDER_CHOICES=(('toto@toto.fr', 'toto'), ('titi@titi.fr', 'titi')))
    def test_view_update_emailing_from_email(self):
        """check the display of the page"""
        emailing = mommy.make(Emailing)

        url = reverse("emailing_update_emailing", kwargs={'pk': emailing.id})

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(2, len(soup.select("select#id_from_email option")))

    @override_settings(BALAFON_EMAILING_SENDER_CHOICES=None)
    def test_view_update_emailing_no_from_email(self):
        """check the display of the page"""
        emailing = mommy.make(Emailing)

        url = reverse("emailing_update_emailing", kwargs={'pk': emailing.id})

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(0, len(soup.select("select#id_from_email option")))
        self.assertEqual("hidden", soup.select("#id_from_email")[0]["type"])

    @override_settings(LANGUAGES=(('en', 'English'), ('fr', 'French')))
    def test_view_update_emailing_lang(self):
        """check the display of the page"""
        emailing = mommy.make(Emailing)

        url = reverse("emailing_update_emailing", kwargs={'pk': emailing.id})

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(3, len(soup.select("select#id_lang option")))
        self.assertEqual('', soup.select("select#id_lang option")[0]["value"])
        self.assertEqual('en', soup.select("select#id_lang option")[1]["value"])
        self.assertEqual('fr', soup.select("select#id_lang option")[2]["value"])

    @override_settings(LANGUAGES=(('en', 'English'),))
    def test_view_update_emailing_no_lang(self):
        """check the display of the page"""
        emailing = mommy.make(Emailing)

        url = reverse("emailing_update_emailing", kwargs={'pk': emailing.id})

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(0, len(soup.select("select#id_lang option")))
        self.assertEqual("hidden", soup.select("#id_lang")[0]["type"])

    def test_update_emailing(self):
        """update an emailing"""
        subscription_type1 = mommy.make(models.SubscriptionType)
        subscription_type2 = mommy.make(models.SubscriptionType)

        newsletter1 = mommy.make(Newsletter)
        newsletter2 = mommy.make(Newsletter)

        emailing = mommy.make(
            Emailing,
            subscription_type=subscription_type1,
            newsletter=newsletter1,
        )

        url = reverse("emailing_update_emailing", args=[emailing.id])

        data = {
            'subscription_type': subscription_type2.id,
            'newsletter': newsletter2.id,
            'lang': '',
            'from_email': '',
        }

        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)

        emailing = Emailing.objects.get(id=emailing.id)

        self.assertEqual(emailing.newsletter, newsletter2)
        self.assertEqual(emailing.subscription_type, subscription_type2)

    def test_update_emailing_anonymous(self):
        """update an emailing"""
        subscription_type1 = mommy.make(models.SubscriptionType)
        subscription_type2 = mommy.make(models.SubscriptionType)

        newsletter1 = mommy.make(Newsletter)
        newsletter2 = mommy.make(Newsletter)

        emailing = mommy.make(
            Emailing,
            subscription_type=subscription_type1,
            newsletter=newsletter1,
        )

        self.client.logout()
        url = reverse("emailing_update_emailing", args=[emailing.id])

        data = {
            'subscription_type': subscription_type2.id,
            'newsletter': newsletter2.id,
            'lang': '',
            'from_email': '',
        }

        response = self.client.post(url, data=data)

        self.assertEqual(302, response.status_code)

        emailing = Emailing.objects.get(id=emailing.id)

        self.assertEqual(emailing.newsletter, newsletter1)
        self.assertEqual(emailing.subscription_type, subscription_type1)

    def test_update_emailing_not_allowed(self):
        """update an emailing"""
        subscription_type1 = mommy.make(models.SubscriptionType)
        subscription_type2 = mommy.make(models.SubscriptionType)

        newsletter1 = mommy.make(Newsletter)
        newsletter2 = mommy.make(Newsletter)

        emailing = mommy.make(
            Emailing,
            subscription_type=subscription_type1,
            newsletter=newsletter1,
        )

        url = reverse("emailing_update_emailing", args=[emailing.id])

        data = {
            'subscription_type': subscription_type2.id,
            'newsletter': newsletter2.id,
            'lang': '',
            'from_email': '',
        }
        self.user.is_staff = False
        self.user.save()
        response = self.client.post(url, data=data)

        self.assertEqual(302, response.status_code)

        emailing = Emailing.objects.get(id=emailing.id)

        self.assertEqual(emailing.newsletter, newsletter1)
        self.assertEqual(emailing.subscription_type, subscription_type1)


    @skipIf(len(settings.LANGUAGES) < 2, "not multi languages")
    def test_update_emailing_lang(self):
        """update an emailing: lang"""
        subscription_type1 = mommy.make(models.SubscriptionType)

        newsletter1 = mommy.make(Newsletter)

        emailing = mommy.make(
            Emailing,
            subscription_type=subscription_type1,
            newsletter=newsletter1,
            lang=settings.LANGUAGES[0][0],
        )

        url = reverse("emailing_update_emailing", args=[emailing.id])

        data = {
            'subscription_type': subscription_type1.id,
            'newsletter': newsletter1.id,
            'lang': settings.LANGUAGES[1][0],
            'from_email': '',
        }

        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)

        emailing = Emailing.objects.get(id=emailing.id)

        self.assertEqual(emailing.newsletter, newsletter1)
        self.assertEqual(emailing.subscription_type, subscription_type1)
        self.assertEqual(emailing.lang, settings.LANGUAGES[1][0])

    @override_settings(BALAFON_DEFAULT_SUBSCRIPTION_TYPE=(('toto@toto.fr', 'toto'), ('titi@titi.fr', 'titi')))
    def test_update_emailing_from_email(self):
        """update an emailing: from_email"""
        subscription_type1 = mommy.make(models.SubscriptionType)

        newsletter1 = mommy.make(Newsletter)

        emailing = mommy.make(
            Emailing,
            subscription_type=subscription_type1,
            newsletter=newsletter1,
            lang='',
            from_email='toto@toto.fr'
        )

        url = reverse("emailing_update_emailing", args=[emailing.id])

        data = {
            'subscription_type': subscription_type1.id,
            'newsletter': newsletter1.id,
            'lang': '',
            'from_email': settings.BALAFON_DEFAULT_SUBSCRIPTION_TYPE[1][0],
        }

        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)

        emailing = Emailing.objects.get(id=emailing.id)

        self.assertEqual(emailing.newsletter, newsletter1)
        self.assertEqual(emailing.subscription_type, subscription_type1)
        self.assertEqual(emailing.lang, '')
        self.assertEqual(emailing.from_email, settings.BALAFON_DEFAULT_SUBSCRIPTION_TYPE[1][0])
