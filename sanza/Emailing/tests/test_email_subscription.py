# -*- coding: utf-8 -*-
"""test subscription"""

from bs4 import BeautifulSoup
from datetime import date

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import activate

from model_mommy import mommy

from sanza.Crm import models
from sanza.Emailing.utils import get_language


class SubscribeTest(TestCase):
    """Subscription with just his email address"""
    
    def setUp(self):
        """before each test"""
        self._lang = settings.LANGUAGES[0][0]
        activate(self._lang)

        if not getattr(settings, 'SANZA_ALLOW_SINGLE_CONTACT', True):
            settings.SANZA_INDIVIDUAL_ENTITY_ID = models.EntityType.objects.create(name="particulier").id

        self._default_subscription_type = getattr(settings, "SANZA_DEFAULT_SUBSCRIPTION_TYPE", None)

        mommy.make(models.Zone, name=settings.SANZA_DEFAULT_COUNTRY, parent=None)

    def tearDown(self):
        """after each test"""
        activate(self._lang)
        settings.SANZA_DEFAULT_SUBSCRIPTION_TYPE = self._default_subscription_type

    @override_settings(LANGUAGES=(('en', 'English'), ('fr', 'French')))
    def test_view_subscription_language(self):
        """make sure the favorite_language is set correctly"""
        activate('fr')

        mommy.make(models.SubscriptionType)

        url = reverse("emailing_email_subscribe_newsletter")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(1, len(soup.select("#id_favorite_language")))
        self.assertEqual(get_language(), soup.select("#id_favorite_language")[0]["value"])

    @override_settings(LANGUAGES=(('en', 'English'),))
    def test_view_subscription_no_language(self):
        """make sure the favorite_language is set correctly"""
        mommy.make(models.SubscriptionType)

        url = reverse("emailing_email_subscribe_newsletter")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(1, len(soup.select("#id_favorite_language")))
        self.assertEqual('', soup.select("#id_favorite_language")[0].get("value", ""))

    def test_view_subscribe_newsletter(self):
        """view email subscription page"""
        url = reverse("emailing_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_newsletter(self):
        """test email subscription when no type is configured"""
        url = reverse("emailing_email_subscribe_newsletter")
        
        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)
        
        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        subscription_type2 = mommy.make(models.SubscriptionType, name="def", site=site1)
        subscription_type3 = mommy.make(models.SubscriptionType, name="ghi", site=site2)
        subscription_type4 = mommy.make(models.SubscriptionType, name="jkl")
        
        data = {
            'email': 'pdupond@apidev.fr',
        }
        
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)
        
        contact = models.Contact.objects.all()[0]
        
        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_email_done')) >= 0)
        
        self.assertEqual(contact.email, data['email'])
        
        self.assertEqual(len(mail.outbox), 2)
        
        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)
        
        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        #Not an Error message
        self.assertTrue(notification_email.message().as_string().decode('utf-8').find("Error") < 0)
        
        for subscription_type in (subscription_type1, subscription_type2):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (subscription_type3, subscription_type4):
            queryset = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, queryset.count())
        
    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_no_email(self):
        """test email subscription with empty email should fail"""
        url = reverse("emailing_email_subscribe_newsletter")

        data = {
            'email': '',
        }

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select("ul.errorlist")), 1)
        self.assertEqual(models.Contact.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_invalid_email(self):
        """email subscription with an invalid email should fail"""

        url = reverse("emailing_email_subscribe_newsletter")
        
        data = {
            'email': 'coucou',
        }
        
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select("ul.errorlist")), 1)
        self.assertEqual(models.Contact.objects.count(), 0)
        
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_default_subscription(self):
        """email subscription should set type to the default subscription type"""

        url = reverse("emailing_email_subscribe_newsletter")

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        subscription_type2 = mommy.make(models.SubscriptionType, name="def", site=site1)
        subscription_type3 = mommy.make(models.SubscriptionType, name="ghi", site=site2)
        subscription_type4 = mommy.make(models.SubscriptionType, name="jkl")

        settings.SANZA_DEFAULT_SUBSCRIPTION_TYPE = subscription_type1.id

        data = {
            'email': 'pdupond@apidev.fr',
        }

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)

        contact = models.Contact.objects.all()[0]

        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_email_done')) >= 0)

        self.assertEqual(contact.email, data['email'])

        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        #Not an Error message
        self.assertTrue(notification_email.message().as_string().decode('utf-8').find("Error") < 0)

        for subscription_type in (subscription_type1, ):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (subscription_type2, subscription_type3, subscription_type4):
            queryset = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, queryset.count())

    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_selected(self):
        """test subscribe for the given subscription type"""

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        subscription_type2 = mommy.make(models.SubscriptionType, name="def", site=site1)
        subscription_type3 = mommy.make(models.SubscriptionType, name="ghi", site=site2)
        subscription_type4 = mommy.make(models.SubscriptionType, name="jkl")

        url = reverse("emailing_email_subscribe_subscription", args=[subscription_type1.id])

        data = {
            'email': 'pdupond@apidev.fr',
        }

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)

        contact = models.Contact.objects.all()[0]

        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_email_done')) >= 0)

        self.assertEqual(contact.email, data['email'])

        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        #Not an Error message
        self.assertTrue(notification_email.message().as_string().decode('utf-8').find("Error") < 0)

        for subscription_type in (subscription_type1, ):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (subscription_type2, subscription_type3, subscription_type4):
            queryset = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, queryset.count())

    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_selected_and_default(self):
        """test given subscribe type has priority on default one"""

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        subscription_type2 = mommy.make(models.SubscriptionType, name="def", site=site1)
        subscription_type3 = mommy.make(models.SubscriptionType, name="ghi", site=site2)
        subscription_type4 = mommy.make(models.SubscriptionType, name="jkl")

        settings.SANZA_DEFAULT_SUBSCRIPTION_TYPE = subscription_type1.id
        url = reverse("emailing_email_subscribe_subscription", args=[subscription_type2.id])

        data = {
            'email': 'pdupond@apidev.fr',
        }

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)

        contact = models.Contact.objects.all()[0]

        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_email_done')) >= 0)

        self.assertEqual(contact.email, data['email'])

        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        #Not an Error message
        self.assertTrue(notification_email.message().as_string().decode('utf-8').find("Error") < 0)

        for subscription_type in (subscription_type2, ):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (subscription_type1, subscription_type3, subscription_type4):
            queryset = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, queryset.count())

    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_selected_not_in_site(self):
        """test subscription on a type which is not associated with the current ste"""
        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        mommy.make(models.SubscriptionType, name="def", site=site1)
        subscription_type3 = mommy.make(models.SubscriptionType, name="ghi", site=site2)
        mommy.make(models.SubscriptionType, name="jkl")

        settings.SANZA_DEFAULT_SUBSCRIPTION_TYPE = subscription_type1.id
        url = reverse("emailing_email_subscribe_subscription", args=[subscription_type3.id])

        data = {
            'email': 'pdupond@apidev.fr',
        }

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)

        contact = models.Contact.objects.all()[0]

        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_email_done')) >= 0)

        self.assertEqual(contact.email, data['email'])

        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        #Error message
        self.assertTrue(notification_email.message().as_string().decode('utf-8').find("Error") >= 0)

        queryset = models.Subscription.objects.filter(contact=contact)
        self.assertEqual(0, queryset.count())
