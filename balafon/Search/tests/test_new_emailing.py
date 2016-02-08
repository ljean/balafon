# -*- coding: utf-8 -*-
"""test we can create an emailing from search results"""

from bs4 import BeautifulSoup as BeautifulSoup4
from unittest import skipIf

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from coop_cms.models import Newsletter

from model_mommy import mommy

from balafon.Crm import models

from balafon.Emailing.models import Emailing
from balafon.Search.tests import BaseTestCase


@override_settings(BALAFON_EMAILING_SENDER_CHOICES=None)
class CreateEmailingTest(BaseTestCase):
    """Test newsletter creation"""

    def test_view_new_emailing(self):
        """test view form when BALAFON_EMAILING_SENDER_CHOICES is not set"""
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)

        mommy.make(Newsletter)
        mommy.make(models.SubscriptionType)

        # TODO
        settings.BALAFON_EMAILING_SENDER_CHOICES = []

        data = {
            'contacts': [contact1.id]
        }

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup4(response.content)

        node = soup.select("#id_from_email")[0]
        self.assertEqual("hidden", node["type"])

    def test_view_new_emailing_from_email(self):
        """test view form when BALAFON_EMAILING_SENDER_CHOICES is set"""
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)

        settings.BALAFON_EMAILING_SENDER_CHOICES = (
            ('toto@toto.fr', 'Toto',),
            ('titi@titi.com', 'Titi'),
        )

        mommy.make(Newsletter)
        mommy.make(models.SubscriptionType)

        data = {
            'contacts': [contact1.id]
        }

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup4(response.content)

        nodes = soup.select("#id_from_email option")
        self.assertEqual(2, len(nodes))
        self.assertEqual(settings.BALAFON_EMAILING_SENDER_CHOICES[0][0], nodes[0]["value"])
        self.assertEqual(settings.BALAFON_EMAILING_SENDER_CHOICES[0][1], nodes[0].text)
        self.assertEqual(settings.BALAFON_EMAILING_SENDER_CHOICES[1][0], nodes[1]["value"])
        self.assertEqual(settings.BALAFON_EMAILING_SENDER_CHOICES[1][1], nodes[1].text)

    def test_create_emailing(self):
        """test create an emailing"""
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname=u"EFGH", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, lastname=u"IJKL", main_contact=True, has_left=False)

        newsletter = mommy.make(Newsletter)
        subscription_type = mommy.make(models.SubscriptionType)

        data = {
            'create_emailing': True,
        'subject': u"",
            'subscription_type': subscription_type.id,
            'newsletter': newsletter.id,
            'contacts': u";".join([str(x) for x in [contact1.id, contact2.id]]),
            'lang': '',
            'from_email': '',
        }

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(newsletter.get_absolute_url()),
            response.content
        )

        self.assertEqual(Emailing.objects.count(), 1)
        emailing = Emailing.objects.all()[0]

        self.assertEqual(emailing.subscription_type, subscription_type)
        self.assertEqual(emailing.newsletter, newsletter)
        self.assertEqual(emailing.from_email, "")
        self.assertEqual(0, emailing.sent_to.count())
        self.assertEqual(2, emailing.send_to.count())
        self.assertTrue(contact1 in emailing.send_to.all())
        self.assertTrue(contact2 in emailing.send_to.all())
        self.assertFalse(contact3 in emailing.send_to.all())

    def test_create_emailing_anonymous(self):
        """test create an emailing: anonymous user"""
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname=u"EFGH", main_contact=True, has_left=False)

        newsletter = mommy.make(Newsletter)
        subscription_type = mommy.make(models.SubscriptionType)

        data = {
            'create_emailing': True,
            'subject': u"",
            'subscription_type': subscription_type.id,
            'newsletter': newsletter.id,
            'contacts': u";".join([str(x) for x in [contact1.id, contact2.id]]),
            'lang': '',
            'from_email': '',
        }

        self.client.logout()

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

        self.assertEqual(Emailing.objects.count(), 0)

    def test_create_emailing_not_in_staff(self):
        """test create an emailing: anonymous user"""
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname=u"EFGH", main_contact=True, has_left=False)
        mommy.make(models.Contact, lastname=u"IJKL", main_contact=True, has_left=False)

        newsletter = mommy.make(Newsletter)
        subscription_type = mommy.make(models.SubscriptionType)

        data = {
            'create_emailing': True,
            'subject': u"",
            'subscription_type': subscription_type.id,
            'newsletter': newsletter.id,
            'contacts': u";".join([str(x) for x in [contact1.id, contact2.id]]),
            'lang': '',
            'from_email': '',
        }

        self.user.is_staff = False
        self.user.save()

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

        self.assertEqual(Emailing.objects.count(), 0)

    def test_create_emailing_from_email(self):
        """test create with from_email set"""
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname=u"EFGH", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, lastname=u"IJKL", main_contact=True, has_left=False)

        settings.BALAFON_EMAILING_SENDER_CHOICES = (
            ('Toto', 'toto@toto.fr'),
            ('Titi', 'titi@titi.com'),
        )

        newsletter = mommy.make(Newsletter)
        subscription_type = mommy.make(models.SubscriptionType)

        data = {
            'create_emailing': True,
            'subject': u"",
            'subscription_type': subscription_type.id,
            'newsletter': newsletter.id,
            'contacts': u";".join([str(x) for x in [contact1.id, contact2.id]]),
            'lang': '',
            "from_email": "toto@toto.fr"
        }

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(newsletter.get_absolute_url()),
            response.content
        )

        self.assertEqual(Emailing.objects.count(), 1)
        emailing = Emailing.objects.all()[0]

        self.assertEqual(emailing.subscription_type, subscription_type)
        self.assertEqual(emailing.newsletter, newsletter)
        self.assertEqual('', emailing.lang)
        self.assertEqual(emailing.from_email, "toto@toto.fr")
        self.assertEqual(0, emailing.sent_to.count())
        self.assertEqual(2, emailing.send_to.count())
        self.assertTrue(contact1 in emailing.send_to.all())
        self.assertTrue(contact2 in emailing.send_to.all())
        self.assertFalse(contact3 in emailing.send_to.all())

    def test_create_emailing_new_newsletter(self):
        """create emailing with new newsletter set"""
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname=u"EFGH", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, lastname=u"IJKL", main_contact=True, has_left=False)

        subscription_type = mommy.make(models.SubscriptionType)

        data = {
            'create_emailing': True,
            'subject': u"Test",
            'subscription_type': subscription_type.id,
            'newsletter': 0,
            'contacts': u";".join([str(x) for x in [contact1.id, contact2.id]]),
            'lang': '',
            'from_email': '',
        }

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(Newsletter.objects.count(), 1)
        newsletter = Newsletter.objects.all()[0]

        self.assertEqual(
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(newsletter.get_absolute_url()),
            response.content
        )

        self.assertEqual(Emailing.objects.count(), 1)
        emailing = Emailing.objects.all()[0]

        self.assertEqual(emailing.subscription_type, subscription_type)
        self.assertEqual(emailing.newsletter, newsletter)
        self.assertEqual(emailing.newsletter.subject, data["subject"])
        self.assertEqual('', emailing.lang)
        self.assertEqual(0, emailing.sent_to.count())
        self.assertEqual(2, emailing.send_to.count())
        self.assertTrue(contact1 in emailing.send_to.all())
        self.assertTrue(contact2 in emailing.send_to.all())
        self.assertFalse(contact3 in emailing.send_to.all())

    def test_create_emailing_invalid_subscription(self):
        """create emailing invalid subscription type"""
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname=u"EFGH", main_contact=True, has_left=False)
        mommy.make(models.Contact, lastname=u"IJKL", main_contact=True, has_left=False)

        data = {
            'create_emailing': True,
            'subject': u"Test",
            'subscription_type': 0,
            'newsletter': 0,
            'contacts': u";".join([str(x) for x in [contact1.id, contact2.id]]),
            'lang': '',
            'from_email': '',
        }

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(Newsletter.objects.count(), 0)
        self.assertEqual(Emailing.objects.count(), 0)

    @skipIf(len(settings.LANGUAGES) < 2, "LANGUAGES less than 2")
    def test_create_emailing_language(self):
        """create emailing language is set"""
        subscription_type = mommy.make(models.SubscriptionType)

        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname=u"EFGH", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, lastname=u"IJKL", main_contact=True, has_left=False)

        data = {
            'create_emailing': True,
            'subject': u"Test",
            'subscription_type': subscription_type.id,
            'newsletter': 0,
            'contacts': u";".join([str(x) for x in [contact1.id, contact2.id]]),
            'lang': settings.LANGUAGES[1][0],
        }

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(Newsletter.objects.count(), 1)
        newsletter = Newsletter.objects.all()[0]

        self.assertEqual(
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(newsletter.get_absolute_url()),
            response.content
        )

        self.assertEqual(Emailing.objects.count(), 1)
        emailing = Emailing.objects.all()[0]

        self.assertEqual(emailing.subscription_type, subscription_type)
        self.assertEqual(emailing.newsletter, newsletter)
        self.assertEqual(emailing.newsletter.subject, data["subject"])
        self.assertEqual(settings.LANGUAGES[1][0], emailing.lang)
        self.assertEqual(0, emailing.sent_to.count())
        self.assertEqual(2, emailing.send_to.count())
        self.assertTrue(contact1 in emailing.send_to.all())
        self.assertTrue(contact2 in emailing.send_to.all())
        self.assertFalse(contact3 in emailing.send_to.all())

    @override_settings(LANGUAGES=[('fr', 'Francais'), ('en', 'English')])
    def test_view_new_emailing_language(self):
        """view emailing with several languages: language is a select"""
        mommy.make(models.SubscriptionType)

        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname=u"EFGH", main_contact=True, has_left=False)

        data = {
            'contacts': u";".join([str(x) for x in [contact1.id, contact2.id]]),
        }

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(1, len(soup.select("select#id_lang")))

    @override_settings(LANGUAGES=[('fr', 'Francais')])
    def test_view_new_emailing_language_hidden(self):
        """view emailing with just one language: The language field is hidden"""
        mommy.make(models.SubscriptionType)

        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname=u"EFGH", main_contact=True, has_left=False)

        data = {
            'contacts': u";".join([str(x) for x in [contact1.id, contact2.id]]),
        }

        url = reverse('search_emailing')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select("select#id_lang")))
        self.assertEqual(1, len(soup.select("#id_lang")))
        self.assertEqual("hidden", soup.select("#id_lang")[0]["type"])
