# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import skipIf

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core import mail
from django.test.utils import override_settings

from model_mommy import mommy
from registration.models import RegistrationProfile

from balafon.unit_tests import TestCase
from balafon.Crm import models


@skipIf(not ("balafon.Profile" in settings.INSTALLED_APPS), "registration not installed")
@override_settings(BALAFON_REGISTRATION_ENABLED=True)
class RegisterTestCase(TestCase):

    @skipIf(not ("registration" in settings.INSTALLED_APPS), "registration not installed")
    def test_register(self):
        site = Site.objects.get_current()
        subscription_type1 = mommy.make(models.SubscriptionType, site=site)
        subscription_type2 = mommy.make(models.SubscriptionType, site=site)
        subscription_type3 = mommy.make(models.SubscriptionType, site=site)
        subscription_type4 = mommy.make(models.SubscriptionType)

        url = reverse('registration_register')
        data = {
            'email': 'john@toto.fr',
            'password1': 'PAss',
            'password2': 'PAss',
            'accept_termofuse': True,
            'subscription_types': [subscription_type1.id, subscription_type2.id],
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email=data['email'])

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        rp = RegistrationProfile.objects.all()[0]
        self.assertEqual(rp.user, user)
        self.assertEqual(
            rp.user.contactprofile.subscriptions_ids,
            "{0},{1}".format(subscription_type1.id, subscription_type2.id)
        )

        activation_url = reverse('registration_activate', args=[rp.activation_key])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertTrue(mail.outbox[0].body.find(activation_url))

        response = self.client.get(activation_url, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(email=data['email'])
        self.assertEqual(contact.gender, data['gender'])

        self.assertEqual(
            True,
            models.Subscription.objects.get(contact=contact, subscription_type=subscription_type1).accept_subscription
        )

        self.assertEqual(
            True,
            models.Subscription.objects.get(contact=contact, subscription_type=subscription_type2).accept_subscription
        )

        self.assertEqual(
            False,
            models.Subscription.objects.get(contact=contact, subscription_type=subscription_type3).accept_subscription
        )

        self.assertEqual(
            0,
            models.Subscription.objects.filter(contact=contact, subscription_type=subscription_type4).count()
        )

        self.assertTrue(self.client.login(email=data['email'], password=data['password1']))

    @skipIf(not ("registration" in settings.INSTALLED_APPS), "registration not installed")
    @override_settings(BALAFON_REGISTRATION_ENABLED=False)
    def test_register_disable(self):
        site = Site.objects.get_current()
        subscription_type1 = mommy.make(models.SubscriptionType, site=site)
        subscription_type2 = mommy.make(models.SubscriptionType, site=site)
        subscription_type3 = mommy.make(models.SubscriptionType, site=site)
        subscription_type4 = mommy.make(models.SubscriptionType)

        url = reverse('registration_register')
        data = {
            'email': 'john@toto.fr',
            'password1': 'PAss',
            'password2': 'PAss',
            'accept_termofuse': True,
            'subscription_types': [subscription_type1.id, subscription_type2.id],
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 404)

    @skipIf(not ("registration" in settings.INSTALLED_APPS), "registration not installed")
    def test_register_no_subscription(self):
        site = Site.objects.get_current()

        subscription_type1 = mommy.make(models.SubscriptionType, site=site)

        url = reverse('registration_register')
        data = {
            'email': 'john@toto.fr',
            'password1': 'PAss',
            'password2': 'PAss',
            'accept_termofuse': True,
            'subscription_types': [],
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email=data['email'])

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        rp = RegistrationProfile.objects.all()[0]
        self.assertEqual(rp.user, user)
        self.assertEqual(rp.user.contactprofile.subscriptions_ids, "")

        activation_url = reverse('registration_activate', args=[rp.activation_key])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertTrue(mail.outbox[0].body.find(activation_url))

        response = self.client.get(activation_url, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(email=data['email'])
        self.assertEqual(contact.gender, data['gender'])

        self.assertEqual(
            False,
            models.Subscription.objects.get(contact=contact, subscription_type=subscription_type1).accept_subscription
        )

        self.assertTrue(self.client.login(email=data['email'], password=data['password1']))

    @skipIf(not ("registration" in settings.INSTALLED_APPS), "registration not installed")
    def test_register_one_subscription(self):
        site = Site.objects.get_current()

        subscription_type1 = mommy.make(models.SubscriptionType, site=site)
        subscription_type2 = mommy.make(models.SubscriptionType, site=site)

        url = reverse('registration_register')
        data = {
            'email': 'john@toto.fr',
            'password1': 'PAss',
            'password2': 'PAss',
            'accept_termofuse': True,
            'subscription_types': [subscription_type1.id],
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email=data['email'])

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        rp = RegistrationProfile.objects.all()[0]
        self.assertEqual(rp.user, user)
        self.assertEqual(rp.user.contactprofile.subscriptions_ids, "{0}".format(subscription_type1.id))

        activation_url = reverse('registration_activate', args=[rp.activation_key])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertTrue(mail.outbox[0].body.find(activation_url))

        response = self.client.get(activation_url, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(email=data['email'])
        self.assertEqual(contact.gender, data['gender'])

        self.assertEqual(
            True,
            models.Subscription.objects.get(contact=contact, subscription_type=subscription_type1).accept_subscription
        )

        self.assertEqual(
            False,
            models.Subscription.objects.get(contact=contact, subscription_type=subscription_type2).accept_subscription
        )

        self.assertTrue(self.client.login(email=data['email'], password=data['password1']))

    @skipIf(not ("registration" in settings.INSTALLED_APPS), "registration not installed")
    def test_activate_invalid_subscription(self):
        site = Site.objects.get_current()

        subscription_type1 = mommy.make(models.SubscriptionType, site=site)
        subscription_type2 = mommy.make(models.SubscriptionType, site=site)

        url = reverse('registration_register')
        data = {
            'email': 'john@toto.fr',
            'password1': 'PAss',
            'password2': 'PAss',
            'accept_termofuse': True,
            'subscription_types': [subscription_type1.id],
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email=data['email'])

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        rp = RegistrationProfile.objects.all()[0]
        self.assertEqual(rp.user, user)
        self.assertEqual(rp.user.contactprofile.subscriptions_ids, "{0}".format(subscription_type1.id))

        rp.user.contactprofile.subscriptions_ids = "bla"
        rp.user.contactprofile.save()

        activation_url = reverse('registration_activate', args=[rp.activation_key])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertTrue(mail.outbox[0].body.find(activation_url))

        response = self.client.get(activation_url, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(email=data['email'])
        self.assertEqual(contact.gender, data['gender'])

        self.assertEqual(
            False,
            models.Subscription.objects.get(contact=contact, subscription_type=subscription_type1).accept_subscription
        )

        self.assertEqual(
            False,
            models.Subscription.objects.get(contact=contact, subscription_type=subscription_type2).accept_subscription
        )

        self.assertTrue(self.client.login(email=data['email'], password=data['password1']))

    @skipIf(not ("registration" in settings.INSTALLED_APPS), "registration not installed")
    def test_register_no_gender(self):
        url = reverse('registration_register')
        data = {
            'email': 'john@toto.fr',
            'password1': 'PAss',
            'password2': 'PAss',
            'accept_termofuse': True,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email=data['email'])

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        rp = RegistrationProfile.objects.all()[0]
        self.assertEqual(rp.user, user)
        self.assertEqual(rp.user.contactprofile.subscriptions_ids, "")
        activation_url = reverse('registration_activate', args=[rp.activation_key])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertTrue(mail.outbox[0].body.find(activation_url))

        response = self.client.get(activation_url, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(email=data['email'])
        self.assertEqual(contact.gender, 0)

        self.assertTrue(self.client.login(email=data['email'], password=data['password1']))

    def test_register_with_very_long_email(self):
        url = reverse('registration_register')
        data = {
            'email': ('a'*30)+'@toto.fr',
            'password1': 'PAss',
            'password2': 'PAss',
            'accept_termofuse': True,
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email=data['email'])

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        rp = RegistrationProfile.objects.all()[0]
        self.assertEqual(rp.user, user)
        activation_url = reverse('registration_activate', args=[rp.activation_key])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertTrue(mail.outbox[0].body.find(activation_url))

        response = self.client.get(activation_url, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(email=data['email'])
        self.assertEqual(contact.gender, data['gender'])

        self.assertTrue(self.client.login(email=data['email'], password=data['password1']))

    def test_register_no_password(self):
        url = reverse('registration_register')
        data = {
            'email': 'toto@toto.fr',
            'password1': '',
            'password2': '',
            'accept_termofuse': True,
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email=data['email']).count(), 0)

    def test_register_different_passwords(self):
        url = reverse('registration_register')
        data = {
            'email': 'toto@toto.fr',
            'password1': 'ABC',
            'password2': 'DEF',
            'accept_termofuse': True,
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email=data['email']).count(), 0)

    def test_register_existing_email(self):
        user = mommy.make(models.User, email='toto@toto.fr')
        url = reverse('registration_register')
        data = {
            'email': 'toto@toto.fr',
            'password1': 'ABC',
            'password2': 'ABC',
            'accept_termofuse': True,
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.exclude(id=user.id).filter(email=data['email']).count(), 0)

    def test_register_existing_email_different_cases(self):
        user = mommy.make(models.User, email='toto@toto.fr')
        url = reverse('registration_register')
        data = {
            'email': 'TOTO@TOTO.FR',
            'password1': 'ABC',
            'password2': 'ABC',
            'accept_termofuse': True,
            'gender': 1,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.exclude(id=user.id).filter(email=data['email']).count(), 0)
