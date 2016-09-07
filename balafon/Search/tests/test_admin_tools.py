# -*- coding: utf-8 -*-
"""test we can search contacts by action"""

from unittest import skipIf

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class SubscribeAdminContactsTest(BaseTestCase):
    """create actions from results"""

    def setUp(self):
        """before"""
        super(SubscribeAdminContactsTest, self).setUp()
        self.user.is_superuser = True
        self.user.save()

    def test_get_form(self):
        """test GET on url"""
        url = reverse('search_subscribe_contacts_admin')
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_view_form(self):
        """test view action form"""

        mommy.make(models.SubscriptionType)
        mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = entity2.default_contact

        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1, entity2)
        group.save()

        url = reverse('search_subscribe_contacts_admin')

        data = {"gr0-_-group-_-0": group.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        id_contacts = soup.select('input#id_contacts')
        self.assertEqual(1, len(id_contacts))
        self.assertEqual(
            sorted([int(x) for x in id_contacts[0]['value'].split(';')]),
            sorted([contact1.id, contact2.id])
        )

        subscription_types = soup.select('select#id_subscription_type option')
        self.assertEqual(2, len(subscription_types))

    def test_view_form_not_logged(self):
        """test view form is not logged"""
        self.client.logout()

        mommy.make(models.SubscriptionType)
        mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        entity2 = mommy.make(models.Entity, name=u"Other corp")

        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1, entity2)
        group.save()

        url = reverse('search_subscribe_contacts_admin')

        data = {"gr0-_-group-_-0": group.id}

        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_subscribe_contacts(self):
        """test create actions for contact"""

        subscription_type1 = mommy.make(models.SubscriptionType)
        subscription_type2 = mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = entity2.default_contact
        entity3 = mommy.make(models.Entity, name=u"Big corp")
        contact3 = entity3.default_contact
        contact4 = mommy.make(models.Contact, entity=entity1)
        contact5 = mommy.make(models.Contact, entity=entity1)

        mommy.make(
            models.Subscription, subscription_type=subscription_type1, contact=contact1, accept_subscription=False
        )
        mommy.make(
            models.Subscription, subscription_type=subscription_type2, contact=contact1, accept_subscription=False
        )
        mommy.make(
            models.Subscription, subscription_type=subscription_type1, contact=contact4, accept_subscription=True
        )
        mommy.make(
            models.Subscription, subscription_type=subscription_type1, contact=contact5, accept_subscription=False
        )

        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1, entity2)
        group.save()

        contacts = (contact1.id, contact2.id, contact4.id, contact5.id, )

        data = {
            'contacts': u";".join([unicode(i) for i in contacts]),
            'subscription_type': subscription_type1.id,
            'subscribe': True,
            'subscribe_contacts_admin': True,
        }

        url = reverse('search_subscribe_contacts_admin')
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)

        for contact in contacts:
            subscription = models.Subscription.objects.get(subscription_type=subscription_type1, contact=contact)
            self.assertEqual(subscription.accept_subscription, True)

        subscription = models.Subscription.objects.get(subscription_type=subscription_type2, contact=contact1)
        self.assertEqual(subscription.accept_subscription, False)

        try:
            models.Subscription.objects.get(subscription_type=subscription_type1, contact=contact3)
            self.assertTrue(False)  # Error : this subscription should not exist
        except models.Subscription.DoesNotExist:
            pass  # Ok

        try:
            models.Subscription.objects.get(subscription_type=subscription_type2, contact=contact4)
            self.assertTrue(False)  # Error : this subscription should not exist
        except models.Subscription.DoesNotExist:
            pass  # Ok

    def test_unsubscribe_contacts(self):
        """test create actions for contact"""

        subscription_type1 = mommy.make(models.SubscriptionType)
        subscription_type2 = mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = entity2.default_contact
        entity3 = mommy.make(models.Entity, name=u"Big corp")
        contact3 = entity3.default_contact
        contact4 = mommy.make(models.Contact, entity=entity1)
        contact5 = mommy.make(models.Contact, entity=entity1)

        mommy.make(
            models.Subscription, subscription_type=subscription_type1, contact=contact1, accept_subscription=True
        )
        mommy.make(
            models.Subscription, subscription_type=subscription_type2, contact=contact1, accept_subscription=True
        )
        mommy.make(
            models.Subscription, subscription_type=subscription_type1, contact=contact4, accept_subscription=False
        )
        mommy.make(
            models.Subscription, subscription_type=subscription_type1, contact=contact5, accept_subscription=True
        )

        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1, entity2)
        group.save()

        contacts = (contact1.id, contact2.id, contact4.id, contact5.id,)

        data = {
            'contacts': u";".join([unicode(i) for i in contacts]),
            'subscription_type': subscription_type1.id,
            'subscribe': False,
            'subscribe_contacts_admin': True,
        }

        url = reverse('search_subscribe_contacts_admin')
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)

        for contact in (contact1, contact4, contact5):
            subscription = models.Subscription.objects.get(subscription_type=subscription_type1, contact=contact)
            self.assertEqual(subscription.accept_subscription, False)

        subscription = models.Subscription.objects.get(subscription_type=subscription_type2, contact=contact1)
        self.assertEqual(subscription.accept_subscription, True)

        try:
            models.Subscription.objects.get(subscription_type=subscription_type1, contact=contact3)
            self.assertTrue(False)  # Error : this subscription should not exist
        except models.Subscription.DoesNotExist:
            pass  # Ok

        try:
            models.Subscription.objects.get(subscription_type=subscription_type2, contact=contact4)
            self.assertTrue(False)  # Error : this subscription should not exist
        except models.Subscription.DoesNotExist:
            pass  # Ok

    def test_subscribe_contacts_not_allowed(self):
        """test create actions for contact"""

        self.user.is_superuser = False
        self.user.save()

        subscription_type1 = mommy.make(models.SubscriptionType)
        subscription_type2 = mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = entity2.default_contact
        entity3 = mommy.make(models.Entity, name=u"Big corp")
        contact3 = entity3.default_contact
        contact4 = mommy.make(models.Contact, entity=entity1)
        contact5 = mommy.make(models.Contact, entity=entity1)

        mommy.make(
            models.Subscription, subscription_type=subscription_type1, contact=contact1, accept_subscription=False
        )
        mommy.make(
            models.Subscription, subscription_type=subscription_type2, contact=contact1, accept_subscription=False
        )
        mommy.make(
            models.Subscription, subscription_type=subscription_type1, contact=contact4, accept_subscription=True
        )
        mommy.make(
            models.Subscription, subscription_type=subscription_type1, contact=contact5, accept_subscription=False
        )

        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1, entity2)
        group.save()

        contacts = (contact1.id, contact2.id, contact4.id, contact5.id,)

        data = {
            'contacts': u";".join([unicode(i) for i in contacts]),
            'subscription_type': subscription_type1.id,
            'subscribe': True,
            'subscribe_contacts_admin': True,
        }

        url = reverse('search_subscribe_contacts_admin')
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

        subscription = models.Subscription.objects.get(subscription_type=subscription_type1, contact=contact1)
        self.assertEqual(subscription.accept_subscription, False)
