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

from model_mommy import mommy

from sanza.Crm import models


class SubscribeTest(TestCase):
    
    def setUp(self):
        
        if not getattr(settings, 'SANZA_ALLOW_SINGLE_CONTACT', True):
            settings.SANZA_INDIVIDUAL_ENTITY_ID = models.EntityType.objects.create(name="particulier").id
        
        mommy.make(models.Zone, name=settings.SANZA_DEFAULT_COUNTRY, parent=None)
    
    def test_view_subscribe_newsletter(self):
        url = reverse("emailing_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    def test_view_email_subscribe_newsletter(self):
        url = reverse("emailing_email_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_newsletter(self):
        url = reverse("emailing_email_subscribe_newsletter")
        
        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)
        
        st1 = mommy.make(models.SubscriptionType, name="abc")
        st2 = mommy.make(models.SubscriptionType, name="def")
        st3 = mommy.make(models.SubscriptionType, name="ghi")
        st4 = mommy.make(models.SubscriptionType, name="jkl")
        
        st1.sites.add(site1, site2)
        st1.save()
        st2.sites.add(site1)
        st2.save()
        st3.sites.add(site2)
        st3.save()
        
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
        
        for subscription_type in (st1, st2):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (st3, st4):
            qs = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, qs.count())
        
    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_newsletter_no_email(self):
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
    def test_email_subscribe_newsletter_invalid_email(self):
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
    def test_email_subscribe_newsletter_default_subscription(self):
        url = reverse("emailing_email_subscribe_newsletter")

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        st1 = mommy.make(models.SubscriptionType, name="abc")
        st2 = mommy.make(models.SubscriptionType, name="def")
        st3 = mommy.make(models.SubscriptionType, name="ghi")
        st4 = mommy.make(models.SubscriptionType, name="jkl")

        st1.sites.add(site1, site2)
        st1.save()
        st2.sites.add(site1)
        st2.save()
        st3.sites.add(site2)
        st3.save()

        settings.SANZA_DEFAULT_SUBSCRIPTION_TYPE = st1.id

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

        for subscription_type in (st1, ):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (st2, st3, st4):
            qs = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, qs.count())

    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_newsletter_selected_subscription(self):

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        st1 = mommy.make(models.SubscriptionType, name="abc")
        st2 = mommy.make(models.SubscriptionType, name="def")
        st3 = mommy.make(models.SubscriptionType, name="ghi")
        st4 = mommy.make(models.SubscriptionType, name="jkl")

        st1.sites.add(site1, site2)
        st1.save()
        st2.sites.add(site1)
        st2.save()
        st3.sites.add(site2)
        st3.save()

        url = reverse("emailing_email_subscribe_subscription", args=[st1.id])

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

        for subscription_type in (st1, ):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (st2, st3, st4):
            qs = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, qs.count())

    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_newsletter_selected_subscription_override_default(self):

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        st1 = mommy.make(models.SubscriptionType, name="abc")
        st2 = mommy.make(models.SubscriptionType, name="def")
        st3 = mommy.make(models.SubscriptionType, name="ghi")
        st4 = mommy.make(models.SubscriptionType, name="jkl")

        st1.sites.add(site1, site2)
        st1.save()
        st2.sites.add(site1)
        st2.save()
        st3.sites.add(site2)
        st3.save()

        settings.SANZA_DEFAULT_SUBSCRIPTION_TYPE = st1.id
        url = reverse("emailing_email_subscribe_subscription", args=[st2.id])

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

        for subscription_type in (st2, ):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (st1, st3, st4):
            qs = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, qs.count())

    @override_settings(SANZA_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_newsletter_selected_subscription_not_in_site(self):

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        st1 = mommy.make(models.SubscriptionType, name="abc")
        st2 = mommy.make(models.SubscriptionType, name="def")
        st3 = mommy.make(models.SubscriptionType, name="ghi")
        st4 = mommy.make(models.SubscriptionType, name="jkl")

        st1.sites.add(site1, site2)
        st1.save()
        st2.sites.add(site1)
        st2.save()
        st3.sites.add(site2)
        st3.save()

        settings.SANZA_DEFAULT_SUBSCRIPTION_TYPE = st1.id
        url = reverse("emailing_email_subscribe_subscription", args=[st3.id])

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
