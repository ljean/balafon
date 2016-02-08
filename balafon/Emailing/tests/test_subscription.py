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

from captcha.models import CaptchaStore
from model_mommy import mommy

from balafon.Crm import models


@override_settings(BALAFON_SUBSCRIBE_ENABLED=True)
class SubscribeTest(TestCase):
    """Subscribe to newsletter"""

    def setUp(self):
        """before each test"""
        self._lang = settings.LANGUAGES[0][0]
        activate(self._lang)

        if not getattr(settings, 'BALAFON_ALLOW_SINGLE_CONTACT', True):
            settings.BALAFON_INDIVIDUAL_ENTITY_ID = models.EntityType.objects.create(name="particulier").id

        mommy.make(models.Zone, name=settings.BALAFON_DEFAULT_COUNTRY, parent=None)

    def tearDown(self):
        """after each test"""
        activate(self._lang)

    def test_view_subscribe_newsletter(self):
        """view subscription page"""
        url = reverse("emailing_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_subscribe_newsletter_no_email(self):
        """subscribe without setting an email"""
        group1 = mommy.make(models.Group, name="ABC", subscribe_form=True)

        url = reverse("emailing_subscribe_newsletter")

        data = {
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': str(group1.id),
            'entity_type': 0,
            'email': '',
        }
        self._patch_with_captcha(url, data)

        self.assertEqual(models.Contact.objects.count(), 0)
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select("ul.errorlist")), 1)
        self.assertEqual(models.Contact.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_subscribe_newsletter_message(self):
        """subscribe with a message"""
        url = reverse("emailing_subscribe_newsletter")

        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': "pierre.dupond@mon-mail.fr",
            'message': "Hello",
        }
        self._patch_with_captcha(url, data)

        self.assertEqual(models.Contact.objects.count(), 0)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)
        contact = models.Contact.objects.all()[0]

        self.assertEqual(contact.email, data["email"])
        self.assertEqual(contact.lastname, data["lastname"])
        self.assertEqual(contact.firstname, data["firstname"])

        self.assertEqual(1, contact.action_set.count())
        action = contact.action_set.all()[0]
        self.assertEqual(data["message"], action.detail)

        #email verification
        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])

    def test_subscribe_newsletter_empty_message(self):
        """subscribe with an empty message"""
        url = reverse("emailing_subscribe_newsletter")

        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': "pierre.dupond@mon-mail.fr",
            'message': "",
        }
        self._patch_with_captcha(url, data)

        self.assertEqual(models.Contact.objects.count(), 0)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)

        self.assertEqual(models.Contact.objects.count(), 1)
        contact = models.Contact.objects.all()[0]

        self.assertEqual(contact.email, data["email"])
        self.assertEqual(contact.lastname, data["lastname"])
        self.assertEqual(contact.firstname, data["firstname"])

        self.assertEqual(0, contact.action_set.count())

        #email verification
        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])

    def test_subscribe_newsletter_no_entity(self):
        """subscribe as an individual"""
        group1 = mommy.make(models.Group, name="ABC", subscribe_form=True)

        url = reverse("emailing_subscribe_newsletter")

        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': str(group1.id),
            'email': 'pdupond@apidev.fr',
        }
        self._patch_with_captcha(url, data)

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)

        contact = models.Contact.objects.all()[0]

        self.assertNotEqual(contact.uuid, '')
        self.assertEqual(contact.favorite_language, '')
        self.assertEqual(contact.get_same_as().count(), 0)
        self.assertEqual(contact.get_same_email().count(), 0)

        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid])) >= 0)

        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])
        self.assertEqual(list(contact.entity.group_set.all()), [group1])

        #email verification
        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])

    @override_settings(LANGUAGES=(('en', 'English'), ('fr', 'French')))
    def test_subscribe_newsletter_favorite_language(self):
        """subscribe as an individual"""
        url = reverse("emailing_subscribe_newsletter")

        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': [],
            'email': 'pdupond@apidev.fr',
            'favorite_language': 'fr',
        }
        self._patch_with_captcha(url, data)

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)

        contact = models.Contact.objects.all()[0]

        self.assertNotEqual(contact.uuid, '')
        self.assertEqual(contact.favorite_language, 'fr')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid])) >= 0)

        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])

        #email verification
        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])

    def test_subscribe_existing_contact(self):
        """subscribe again to mailing list"""
        entity = mommy.make(models.Entity)
        existing_contact = entity.default_contact
        existing_contact.email = 'pdupond@apidev.fr'
        existing_contact.save()

        url = reverse("emailing_subscribe_newsletter")

        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': [],
            'email': existing_contact.email,
        }
        self._patch_with_captcha(url, data)

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
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[new_contact.uuid])) >= 0)

        self.assertEqual(new_contact.lastname, data['lastname'])
        self.assertEqual(new_contact.firstname, data['firstname'])

        #email verification
        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [new_contact.email])
        url = reverse('emailing_email_verification', args=[new_contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        email_content = notification_email.message().as_string().decode('utf-8')
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

        url = reverse("emailing_subscribe_newsletter")

        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': [],
            'email': existing_contact1.email,
        }
        self._patch_with_captcha(url, data)

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

        self.assertEqual(new_contact.get_same_as().count(), 0)
        self.assertEqual(new_contact.get_same_email().count(), 4)
        self.assertEqual(
            sorted([contact.id for contact in new_contact.get_same_email()]),
            sorted(existing_ids)
        )

        self.assertNotEqual(new_contact.uuid, '')
        self.assertEqual(new_contact.favorite_language, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[new_contact.uuid])) >= 0)

        self.assertEqual(new_contact.lastname, data['lastname'])
        self.assertEqual(new_contact.firstname, data['firstname'])

        #email verification
        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [new_contact.email])
        url = reverse('emailing_email_verification', args=[new_contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        email_content = notification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(new_contact.fullname) > 0)
        self.assertTrue(email_content.find(new_contact.get_absolute_url()) > 0)
        for existing_contact in (existing_contact1, existing_contact2, existing_contact3, existing_contact4):
            self.assertTrue(email_content.find(existing_contact.get_absolute_url()) > 0)

    def test_subscribe_newsletter_entity(self):
        """subscribe as a company member"""
        group1 = mommy.make(models.Group, name="ABC", subscribe_form=True)
        group2 = mommy.make(models.Group, name="DEF", subscribe_form=True)

        url = reverse("emailing_subscribe_newsletter")

        entity_type = mommy.make(models.EntityType, name='Pro', subscribe_form=True)

        data = {
            'entity_type': entity_type.id,
            'entity': 'Toto',
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': 'pdupond@apidev.fr',
            'groups': [group1.id, group2.id],
        }
        self._patch_with_captcha(url, data)

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)

        self.assertEqual(models.Contact.objects.count(), 1)

        contact = models.Contact.objects.all()[0]

        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid])) >= 0)

        self.assertEqual(contact.entity.name, data['entity'])
        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])
        self.assertEqual(list(contact.entity.group_set.all()), [group1, group2])

        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])

    def test_subscribe_newsletter_private_group(self):
        """test we can not subscribe to a private group"""
        group1 = mommy.make(models.Group, name="ABC", subscribe_form=True)
        group2 = mommy.make(models.Group, name="DEF", subscribe_form=False)

        url = reverse("emailing_subscribe_newsletter")

        entity_type = mommy.make(models.EntityType, name='Pro', subscribe_form=True)
        data = {
            'entity_type': entity_type.id,
            'entity': 'Toto',
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': 'pdupond@apidev.fr',
            'groups': [group1.id, group2.id],
        }
        self._patch_with_captcha(url, data)

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
        self.assertEqual(models.Contact.objects.count(), 0)

        self.assertEqual(len(mail.outbox), 0)

    def test_view_subscribe_done(self):
        """test subscribe done page"""
        contact = mommy.make(models.Contact)
        url = reverse('emailing_subscribe_done', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def _patch_with_captcha(self, url, data):
        """path form data with captcha"""
        self.failUnlessEqual(CaptchaStore.objects.count(), 0)
        self.client.get(url)
        self.failUnlessEqual(CaptchaStore.objects.count(), 1)
        captcha = CaptchaStore.objects.all()[0]
        data.update({
            'captcha_0': captcha.hashkey,
            'captcha_1': captcha.response
        })

    def test_view_subscribe_with_types(self):
        """view subscribe page"""
        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        subscribe_type1 = mommy.make(models.SubscriptionType, name="#News#abc", site=site1)
        subscribe_type2 = mommy.make(models.SubscriptionType, name="#News#def", site=site1)
        subscribe_type3 = mommy.make(models.SubscriptionType, name="#News#ghi", site=site2)
        subscribe_type4 = mommy.make(models.SubscriptionType, name="#News#jkl")

        url = reverse("emailing_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, subscribe_type1.name)
        self.assertContains(response, subscribe_type2.name)
        self.assertNotContains(response, subscribe_type3.name)
        self.assertNotContains(response, subscribe_type4.name)

    @override_settings(LANGUAGES=(('en', 'English'), ('fr', 'French')))
    def test_view_subscription_language(self):
        """make sure the favorite_language is set correctly"""
        activate('fr')

        mommy.make(models.SubscriptionType)

        url = reverse("emailing_subscribe_newsletter")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(1, len(soup.select("#id_favorite_language")))
        self.assertEqual('fr', soup.select("#id_favorite_language")[0]["value"])

    @override_settings(LANGUAGES=(('en', 'English'),))
    def test_view_subscription_no_language(self):
        """make sure the favorite_language is set correctly"""
        mommy.make(models.SubscriptionType)

        url = reverse("emailing_subscribe_newsletter")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(1, len(soup.select("#id_favorite_language")))
        self.assertEqual('', soup.select("#id_favorite_language")[0].get("value", ""))

    def test_accept_newsletter_not_in_site(self):
        """if subscribtion is not set on the site, it should not be possible to subscribe"""
        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", site=None)

        url = reverse("emailing_subscribe_newsletter")

        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': 'pdupond@apidev.fr',
            'subscription_types': [newsletter_subscription.id],
        }

        self._patch_with_captcha(url, data)

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 0)
        self.assertEqual(models.Subscription.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_accept_newsletter(self, accept_newsletter=True, accept_3rdparty=True):
        """subscribe and accept some subscribtions"""
        site1 = Site.objects.get_current()

        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", site=site1)
        third_party_subscription = mommy.make(models.SubscriptionType, name="3rd_party", site=site1)

        url = reverse("emailing_subscribe_newsletter")

        subscription_types = []
        if accept_newsletter:
            subscription_types.append(newsletter_subscription.id)
        if accept_3rdparty:
            subscription_types.append(third_party_subscription.id)

        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': 'pdupond@apidev.fr',
            'subscription_types': subscription_types,
        }

        self._patch_with_captcha(url, data)

        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)

        contact = models.Contact.objects.all()[0]

        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid])) >= 0)

        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])

        subscription_newsletter = models.Subscription.objects.get(
            contact=contact, subscription_type=newsletter_subscription)
        self.assertEqual(subscription_newsletter.accept_subscription, accept_newsletter)
        if accept_newsletter:
            self.assertEqual(subscription_newsletter.subscription_date.date(), date.today())
        else:
            self.assertEqual(subscription_newsletter.subscription_date, None)

        subscription_3rdparty = models.Subscription.objects.get(
            contact=contact, subscription_type=third_party_subscription)
        self.assertEqual(subscription_3rdparty.accept_subscription, accept_3rdparty)
        if accept_3rdparty:
            self.assertEqual(subscription_3rdparty.subscription_date.date(), date.today())
        else:
            self.assertEqual(subscription_3rdparty.subscription_date, None)

        self.assertEqual(contact.email_verified, False)

        self.assertEqual(len(mail.outbox), 2)

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email])
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url) > 0)

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])

    def test_refuse_newsletter(self):
        """test refuse all newsletters"""
        self.test_accept_newsletter(accept_newsletter=False, accept_3rdparty=False)

    def test_refuse_newsletter_accept_3rdparty(self):
        """test accept only third parties"""
        self.test_accept_newsletter(accept_newsletter=False, accept_3rdparty=True)

    def test_accept_newsletter_refuse_3rdparty(self):
        """test accept only newsletter"""
        self.test_accept_newsletter(accept_newsletter=True, accept_3rdparty=False)

    def test_verify_email(self):
        """test email verification"""
        self.client.logout()

        site1 = Site.objects.get_current()

        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", site=site1)
        third_party_subscription = mommy.make(models.SubscriptionType, name="3rd_party", site=site1)
        contact = mommy.make(models.Contact, email='toto@apidev.fr', email_verified=False)

        subscription1 = mommy.make(
            models.Subscription, contact=contact, subscription_type=newsletter_subscription, accept_subscription=True
        )
        subscription2 = mommy.make(
            models.Subscription, contact=contact, subscription_type=third_party_subscription, accept_subscription=True
        )

        url = reverse('emailing_email_verification', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email_verified, True)

        subscription1 = models.Subscription.objects.get(id=subscription1.id)
        self.assertEqual(subscription1.accept_subscription, True)
        subscription2 = models.Subscription.objects.get(id=subscription2.id)
        self.assertEqual(subscription2.accept_subscription, True)

    def test_verify_email_no_newsletter(self):
        """test email verification ofr some who refuse subscriptions"""
        self.client.logout()

        site1 = Site.objects.get_current()

        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", site=site1)
        third_party_subscription = mommy.make(models.SubscriptionType, name="3rd_party", site=site1)
        contact = mommy.make(models.Contact, email='toto@apidev.fr', email_verified=False)

        subscription1 = mommy.make(
            models.Subscription, contact=contact, subscription_type=newsletter_subscription, accept_subscription=False
        )
        subscription2 = mommy.make(
            models.Subscription, contact=contact, subscription_type=third_party_subscription, accept_subscription=False
        )

        url = reverse('emailing_email_verification', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email_verified, True)
        subscription1 = models.Subscription.objects.get(id=subscription1.id)
        self.assertEqual(subscription1.accept_subscription, False)
        subscription2 = models.Subscription.objects.get(id=subscription2.id)
        self.assertEqual(subscription2.accept_subscription, False)

    def test_verify_email_strange_uuid(self):
        """test accept verification with an invalid uuid should fail"""
        self.client.logout()
        contact = mommy.make(models.Contact, email='toto@apidev.fr', email_verified=False)

        url = reverse('emailing_email_verification', args=['abcd'])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email_verified, False)

    @override_settings(BALAFON_SUBSCRIBE_ENABLED=False)
    def test_view_subscribe_disabled(self):
        url = reverse("emailing_subscribe_newsletter")

        response = self.client.get(url,)
        self.assertEqual(404, response.status_code)

        self.assertEqual(models.Contact.objects.count(), 0)

    @override_settings(BALAFON_SUBSCRIBE_ENABLED=False)
    def test_subscribe_disabled(self):
        url = reverse("emailing_subscribe_newsletter")

        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': "pierre.dupond@mon-mail.fr",
            'message': "",
        }

        self.assertEqual(models.Contact.objects.count(), 0)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(404, response.status_code)

        self.assertEqual(models.Contact.objects.count(), 0)

        #email verification
        self.assertEqual(len(mail.outbox), 0)
