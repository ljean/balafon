# -*- coding: utf-8 -*-
"""test subscription"""

from bs4 import BeautifulSoup
from datetime import date

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from captcha.models import CaptchaStore
from model_mommy import mommy

from sanza.Crm import models


class SubscribeTest(TestCase):

    def setUp(self):

        if not getattr(settings, 'SANZA_ALLOW_SINGLE_CONTACT', True):
            settings.SANZA_INDIVIDUAL_ENTITY_ID = models.EntityType.objects.create(name="particulier").id

        default_country = mommy.make(models.Zone, name=settings.SANZA_DEFAULT_COUNTRY, parent=None)

    def test_view_subscribe_newsletter(self):
        url = reverse("emailing_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_subscribe_newsletter_no_email(self):
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

        self.assertEqual(len(mail.outbox), 2) #email verification

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])

    def test_subscribe_newsletter_empty_message(self):
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

        self.assertEqual(len(mail.outbox), 2) #email verification

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])

    def test_subscribe_newsletter_no_entity(self):
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
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid]))>=0)

        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])
        self.assertEqual(list(contact.entity.group_set.all()), [group1])

        self.assertEqual(len(mail.outbox), 2) #email verification

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])

    def test_subscribe_newsletter_entity(self):
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
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid]))>=0)

        self.assertEqual(contact.entity.name, data['entity'])
        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])
        self.assertEqual(list(contact.entity.group_set.all()), [group1, group2])

        self.assertEqual(len(mail.outbox), 2) #email verification

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])

    def test_subscribe_newsletter_private_group(self):
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

        self.assertEqual(len(mail.outbox), 0) #email verification

    def test_view_subscribe_done(self):
        contact = mommy.make(models.Contact)
        url = reverse('emailing_subscribe_done', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def _patch_with_captcha(self, url, data):
        self.failUnlessEqual(CaptchaStore.objects.count(), 0)
        self.client.get(url)
        self.failUnlessEqual(CaptchaStore.objects.count(), 1)
        captcha = CaptchaStore.objects.all()[0]
        data.update({
            'captcha_0': captcha.hashkey,
            'captcha_1': captcha.response
        })

    def test_view_subscribe(self):
        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)

        st1 = mommy.make(models.SubscriptionType, name="#News#abc")
        st2 = mommy.make(models.SubscriptionType, name="#News#def")
        st3 = mommy.make(models.SubscriptionType, name="#News#ghi")
        st4 = mommy.make(models.SubscriptionType, name="#News#jkl")

        st1.sites.add(site1, site2)
        st1.save()
        st2.sites.add(site1)
        st2.save()
        st3.sites.add(site2)
        st3.save()

        url = reverse("emailing_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, st1.name)
        self.assertContains(response, st2.name)
        self.assertNotContains(response, st3.name)
        self.assertNotContains(response, st4.name)

    def test_accept_newsletter_not_in_site(self):
        site1 = Site.objects.get_current()

        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", sites=[])

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
        site1 = Site.objects.get_current()

        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", sites=[site1])
        third_party_subscription = mommy.make(models.SubscriptionType, name="3rd_party", sites=[site1])

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
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid]))>=0)

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

        self.assertEqual(len(mail.outbox), 2) #email verification

        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification

        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])

    def test_refuse_newsletter(self):
        self.test_accept_newsletter(accept_newsletter=False, accept_3rdparty=False)

    def test_refuse_newsletter_accept_3rdparty(self):
        self.test_accept_newsletter(accept_newsletter=False, accept_3rdparty=True)

    def test_accept_newsletter_refuse_3rdparty(self):
        self.test_accept_newsletter(accept_newsletter=True, accept_3rdparty=False)

    def test_verify_email(self):
        self.client.logout()
        contact = mommy.make(models.Contact, email='toto@apidev.fr',
            accept_newsletter=True, accept_3rdparty=True, email_verified=False)

        url = reverse('emailing_email_verification', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email_verified, True)
        self.assertEqual(contact.accept_newsletter, True)
        self.assertEqual(contact.accept_3rdparty, True)

    def test_verify_email_no_newsletter(self):
        self.client.logout()
        contact = mommy.make(models.Contact, email='toto@apidev.fr',
            accept_newsletter=False, accept_3rdparty=False, email_verified=False)

        url = reverse('emailing_email_verification', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email_verified, True)
        self.assertEqual(contact.accept_newsletter, False)
        self.assertEqual(contact.accept_3rdparty, False)

    def test_verify_email_strange_uuid(self):
        self.client.logout()
        contact = mommy.make(models.Contact, email='toto@apidev.fr',
            accept_newsletter=False, accept_3rdparty=False, email_verified=False)

        url = reverse('emailing_email_verification', args=['abcd'])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email_verified, False)

