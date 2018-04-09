# -*- coding: utf-8 -*-
"""test subscription"""

from __future__ import unicode_literals

from datetime import date

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils.translation import activate

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.unit_tests import TestCase
from balafon.Crm import models
from balafon.Crm.signals import new_subscription


@override_settings(BALAFON_EMAIL_SUBSCRIBE_ENABLED=True)
class SubscribeTest(TestCase):
    """Subscription with just his email address"""

    @staticmethod
    def email_as_text(email):
        return email.message().as_string()

    def setUp(self):
        """before each test"""
        super(SubscribeTest, self).setUp()
        self._lang = settings.LANGUAGES[0][0]
        activate(self._lang)

        if not getattr(settings, 'BALAFON_ALLOW_SINGLE_CONTACT', True):
            settings.BALAFON_INDIVIDUAL_ENTITY_ID = models.EntityType.objects.create(name="particulier").id

        self._default_subscription_type = getattr(settings, "BALAFON_DEFAULT_SUBSCRIPTION_TYPE", None)

        mommy.make(models.Zone, name=settings.BALAFON_DEFAULT_COUNTRY, parent=None)

    def tearDown(self):
        """after each test"""
        activate(self._lang)
        settings.BALAFON_DEFAULT_SUBSCRIPTION_TYPE = self._default_subscription_type
        super(SubscribeTest, self).tearDown()

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
        self.assertEqual('fr', soup.select("#id_favorite_language")[0]["value"])

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
        url = reverse("emailing_email_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 0)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select('form')))
        form = soup.select('form')[0]
        self.assertEqual(form['action'], url)

    def test_view_subscribe_newsletter_by_id(self):
        """view email subscription page"""
        site1 = Site.objects.get_current()
        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        url = reverse("emailing_email_subscribe_subscription", args=[subscription_type1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 0)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select('form')))
        form = soup.select('form')[0]
        self.assertEqual(form['action'], url)
        
    @override_settings(BALAFON_DEFAULT_SUBSCRIPTION_TYPE=None)
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
        email_content = self.email_as_text(verification_email)
        self.assertTrue(email_content.find(url) > 0)
        
        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        #Not an Error message
        self.assertTrue(self.email_as_text(notification_email).find("Error") < 0)
        
        for subscription_type in (subscription_type1, subscription_type2):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (subscription_type3, subscription_type4):
            queryset = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, queryset.count())
        
    @override_settings(BALAFON_DEFAULT_SUBSCRIPTION_TYPE=None)
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

    @override_settings(BALAFON_DEFAULT_SUBSCRIPTION_TYPE=None)
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

    @override_settings(BALAFON_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_default_subscription(self):
        """email subscription should set type to the default subscription type"""

        url = reverse("emailing_email_subscribe_newsletter")

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        subscription_type2 = mommy.make(models.SubscriptionType, name="def", site=site1)
        subscription_type3 = mommy.make(models.SubscriptionType, name="ghi", site=site2)
        subscription_type4 = mommy.make(models.SubscriptionType, name="jkl")

        settings.BALAFON_DEFAULT_SUBSCRIPTION_TYPE = subscription_type1.id

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
        email_content = self.email_as_text(verification_email)
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        #Not an Error message
        self.assertTrue(self.email_as_text(notification_email).find("Error") < 0)

        for subscription_type in (subscription_type1, ):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (subscription_type2, subscription_type3, subscription_type4):
            queryset = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, queryset.count())

    @override_settings(BALAFON_DEFAULT_SUBSCRIPTION_TYPE=None)
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
        email_content = self.email_as_text(verification_email)
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        # Not an Error message
        self.assertTrue(self.email_as_text(notification_email).find("Error") < 0)

        for subscription_type in (subscription_type1, ):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (subscription_type2, subscription_type3, subscription_type4):
            queryset = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, queryset.count())

    @override_settings(BALAFON_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_selected_and_default(self):
        """test given subscribe type has priority on default one"""

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        subscription_type2 = mommy.make(models.SubscriptionType, name="def", site=site1)
        subscription_type3 = mommy.make(models.SubscriptionType, name="ghi", site=site2)
        subscription_type4 = mommy.make(models.SubscriptionType, name="jkl")

        settings.BALAFON_DEFAULT_SUBSCRIPTION_TYPE = subscription_type1.id
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
        email_content = self.email_as_text(verification_email)
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        #Not an Error message
        self.assertTrue(self.email_as_text(notification_email).find("Error") < 0)

        for subscription_type in (subscription_type2, ):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (subscription_type1, subscription_type3, subscription_type4):
            queryset = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, queryset.count())

    @override_settings(BALAFON_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_selected_not_in_site(self):
        """test subscription on a type which is not associated with the current ste"""
        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        mommy.make(models.SubscriptionType, name="def", site=site1)
        subscription_type3 = mommy.make(models.SubscriptionType, name="ghi", site=site2)
        mommy.make(models.SubscriptionType, name="jkl")

        settings.BALAFON_DEFAULT_SUBSCRIPTION_TYPE = subscription_type1.id
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
        email_content = self.email_as_text(verification_email)
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        #Error message
        self.assertTrue(self.email_as_text(notification_email).find("Error") >= 0)

        queryset = models.Subscription.objects.filter(contact=contact)
        self.assertEqual(0, queryset.count())

    def test_subscribe_existing_contact(self):
        """subscribe again to mailing list"""
        entity = mommy.make(models.Entity)
        existing_contact = entity.default_contact
        existing_contact.email = 'pdupond@apidev.fr'
        existing_contact.save()

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=Site.objects.get_current())
        url = reverse("emailing_email_subscribe_subscription", args=[subscription_type1.id])

        data = {
            'email': existing_contact.email,
        }

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 2)
        self.assertEqual(models.Contact.objects.filter(email=existing_contact.email).count(), 2)

        new_contact = models.Contact.objects.filter(email=existing_contact.email).exclude(id=existing_contact.id)[0]
        self.assertEqual(new_contact.email_verified, False)

        self.assertEqual(new_contact.get_same_as().count(), 0)
        self.assertEqual(new_contact.get_same_email().count(), 1)

        self.assertNotEqual(new_contact.uuid, '')
        self.assertEqual(new_contact.favorite_language, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_email_done')) >= 0)

        queryset = models.Subscription.objects.filter(contact=new_contact, subscription_type=subscription_type1)
        self.assertEqual(1, queryset.count())

        #email verification
        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [new_contact.email])
        url = reverse('emailing_email_verification', args=[new_contact.uuid])
        email_content = self.email_as_text(verification_email)
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        email_content = self.email_as_text(notification_email)
        self.assertTrue(email_content.find(new_contact.fullname) > 0)
        self.assertTrue(email_content.find(new_contact.get_absolute_url()) > 0)
        self.assertTrue(email_content.find(existing_contact.get_absolute_url()) > 0)

    def test_subscribe_several_existing_contact(self):
        """subscribe again to mailing list"""
        entity1 = mommy.make(models.Entity)
        existing_contact1 = entity1.default_contact
        existing_contact1.email = 'pdupond@apidev.fr'
        existing_contact1.save()

        entity2 = mommy.make(models.Entity, email=existing_contact1.email)
        existing_contact2 = entity2.default_contact
        existing_contact4 = mommy.make(models.Contact, entity=entity2)

        entity3 = mommy.make(models.Entity)
        existing_contact3 = entity3.default_contact
        existing_contact3.email = existing_contact1.email
        existing_contact3.save()

        mommy.make(models.Contact, email="toto@somethingelse.fr")

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=Site.objects.get_current())
        url = reverse("emailing_email_subscribe_subscription", args=[subscription_type1.id])

        data = {
            'email': existing_contact1.email,
        }

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.filter(email=existing_contact1.email).count(), 3)

        existing_ids = [
            contact.id for contact in (existing_contact1, existing_contact2, existing_contact3, existing_contact4)
        ]
        queryset = models.Contact.objects.filter(email=existing_contact1.email).exclude(id__in=existing_ids)
        self.assertEqual(queryset.count(), 1)
        new_contact = queryset[0]
        self.assertEqual(new_contact.email_verified, False)

        queryset = models.Subscription.objects.filter(contact=new_contact, subscription_type=subscription_type1)
        self.assertEqual(1, queryset.count())

        self.assertEqual(new_contact.get_same_as().count(), 0)
        self.assertEqual(new_contact.get_same_email().count(), 4)
        self.assertEqual(
            sorted([contact.id for contact in new_contact.get_same_email()]),
            sorted(existing_ids)
        )

        self.assertNotEqual(new_contact.uuid, '')
        self.assertEqual(new_contact.favorite_language, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_email_done')) >= 0)

        #email verification
        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [new_contact.email])
        url = reverse('emailing_email_verification', args=[new_contact.uuid])
        email_content = self.email_as_text(verification_email)
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        email_content = self.email_as_text(notification_email)
        self.assertTrue(email_content.find(new_contact.fullname) > 0)
        self.assertTrue(email_content.find(new_contact.get_absolute_url()) > 0)
        for existing_contact in (existing_contact1, existing_contact2, existing_contact3, existing_contact4):
            self.assertTrue(email_content.find(existing_contact.get_absolute_url()) > 0)

    @override_settings(BALAFON_EMAIL_SUBSCRIBE_ENABLED=False)
    def test_view_subscribe_disabled(self):
        url = reverse("emailing_email_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 0)

    @override_settings(BALAFON_EMAIL_SUBSCRIBE_ENABLED=False)
    def test_subscribe_disabled(self):
        url = reverse("emailing_email_subscribe_newsletter")

        data = {
            'email': 'pdupond@apidev.fr',
        }

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 0)

        self.assertEqual(len(mail.outbox), 0)

    @override_settings(BALAFON_DEFAULT_SUBSCRIPTION_TYPE=None)
    def test_email_subscribe_signal(self):
        """test email subscription when no type is configured"""
        url = reverse("emailing_email_subscribe_newsletter")

        def add_to_group_callback(sender, instance, contact, **kwargs):
            group = models.Group.objects.get_or_create(name=instance.subscription_type.name)[0]
            group.contacts.add(contact)
            group.save()

        new_subscription.connect(add_to_group_callback, sender=models.Subscription)

        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        subscription_type1 = mommy.make(models.SubscriptionType, name="abc", site=site1)
        subscription_type2 = mommy.make(models.SubscriptionType, name="def", site=site1)
        subscription_type3 = mommy.make(models.SubscriptionType, name="def", site=site2)

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
        email_content = self.email_as_text(verification_email)
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        # Not an Error message
        self.assertTrue(self.email_as_text(notification_email).find("Error") < 0)

        for subscription_type in (subscription_type1, subscription_type2):
            subscription = models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)
            self.assertEqual(subscription.accept_subscription, True)
            self.assertEqual(subscription.subscription_date.date(), date.today())

        for subscription_type in (subscription_type3, ):
            queryset = models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type)
            self.assertEqual(0, queryset.count())

        # Check the callbacks have been called
        self.assertEqual(models.Group.objects.count(), 2)
        for subscription_type in (subscription_type1, subscription_type2, ):
            group = models.Group.objects.get(name=subscription_type.name)
            self.assertEqual(group.entities.count(), 0)
            self.assertEqual(list(group.contacts.all()), [contact])

        new_subscription.disconnect(add_to_group_callback, sender=models.Subscription)

