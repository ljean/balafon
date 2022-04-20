# -*- coding: utf-8 -*-
"""test we can search contact by subscription type"""

from django.urls import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class SubscriptionSearchTest(BaseTestCase):
    """subscriptions"""

    def test_search_accept_subscription(self):
        """search by accept subscriptions"""
        mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, entity=entity1, email="abcd@acme.fr", lastname="ABCD", main_contact=True, has_left=False
        )
        contact3 = mommy.make(
            models.Contact, entity=entity1, email="ijkl@acme.fr", lastname="IJKL", main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(
            models.Contact, entity=entity2, email="wxyz@acme.fr", lastname="WXYZ", main_contact=True, has_left=False
        )

        url = reverse('search')

        subscription_type = mommy.make(models.SubscriptionType)

        mommy.make(
            models.Subscription, contact=contact1, subscription_type=subscription_type, accept_subscription=True
        )
        mommy.make(
            models.Subscription, contact=contact3, subscription_type=subscription_type, accept_subscription=False
        )

        data = {"gr0-_-accept_subscription-_-0": subscription_type.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_refuse_subscription(self):
        """search by refuse subscription"""
        mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, entity=entity1, email="abcd@acme.fr", lastname="ABCD", main_contact=True, has_left=False
        )
        contact3 = mommy.make(
            models.Contact, entity=entity1, email="ijkl@acme.fr", lastname="IJKL", main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(
            models.Contact, entity=entity2, email="wxyz@acme.fr", lastname="WXYZ", main_contact=True, has_left=False
        )

        url = reverse('search')

        subscription_type = mommy.make(models.SubscriptionType)

        mommy.make(
            models.Subscription, contact=contact1, subscription_type=subscription_type, accept_subscription=True
        )
        mommy.make(
            models.Subscription, contact=contact3, subscription_type=subscription_type, accept_subscription=False
        )

        data = {"gr0-_-refuse_subscription-_-0": subscription_type.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_no_subscription(self):
        """search by refuse subscription"""
        mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, entity=entity1, email="abcd@acme.fr", lastname="ABCD", main_contact=True, has_left=False
        )
        contact3 = mommy.make(
            models.Contact, entity=entity1, email="ijkl@acme.fr", lastname="IJKL", main_contact=True, has_left=False
        )
        entity1.default_contact.delete()

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(
            models.Contact, entity=entity2, email="wxyz@acme.fr", lastname="WXYZ", main_contact=True, has_left=False
        )
        entity2.default_contact.delete()

        url = reverse('search')

        subscription_type = mommy.make(models.SubscriptionType)

        mommy.make(
            models.Subscription, contact=contact1, subscription_type=subscription_type, accept_subscription=True
        )
        mommy.make(
            models.Subscription, contact=contact3, subscription_type=subscription_type, accept_subscription=False
        )

        data = {"gr0-_-no_subscription-_-0": subscription_type.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

    def test_search_accept_subscription_but_other_with_same_email_refuse(self):
        """search by accept subscriptions"""
        mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, entity=entity1, email="abcd@acme.fr", lastname="ABCD", main_contact=True, has_left=False
        )
        contact3 = mommy.make(
            models.Contact, entity=entity1, email="ijkl@acme.fr", lastname="IJKL", main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(
            models.Contact, entity=entity2, email="wxyz@acme.fr", lastname="WXYZ", main_contact=True, has_left=False
        )
        contact4 = mommy.make(
            models.Contact, entity=entity2, email="abcd@acme.fr", lastname="ABCE", main_contact=True, has_left=False
        )

        url = reverse('search')

        subscription_type = mommy.make(models.SubscriptionType)

        mommy.make(
            models.Subscription, contact=contact1, subscription_type=subscription_type, accept_subscription=True
        )
        mommy.make(
            models.Subscription, contact=contact3, subscription_type=subscription_type, accept_subscription=True
        )
        mommy.make(
            models.Subscription, contact=contact4, subscription_type=subscription_type, accept_subscription=False
        )

        data = {"gr0-_-accept_subscription-_-0": subscription_type.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        self.assertNotContains(response, contact4.lastname)

    def test_search_other_with_same_email_refuse(self):
        """search by accept subscriptions"""
        mommy.make(models.SubscriptionType)

        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, entity=entity1, email="abcd@acme.fr", lastname="ABCD", main_contact=True, has_left=False
        )
        contact3 = mommy.make(
            models.Contact, entity=entity1, email="ijkl@acme.fr", lastname="IJKL", main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(
            models.Contact, entity=entity2, email="wxyz@acme.fr", lastname="WXYZ", main_contact=True, has_left=False
        )
        contact4 = mommy.make(
            models.Contact, entity=entity2, email="abcd@acme.fr", lastname="ABCE", main_contact=True, has_left=False
        )

        url = reverse('search')

        subscription_type = mommy.make(models.SubscriptionType)

        mommy.make(
            models.Subscription, contact=contact1, subscription_type=subscription_type, accept_subscription=True
        )
        mommy.make(
            models.Subscription, contact=contact3, subscription_type=subscription_type, accept_subscription=True
        )
        mommy.make(
            models.Subscription, contact=contact4, subscription_type=subscription_type, accept_subscription=False
        )

        data = {"gr0-_-refuse_subscription-_-0": subscription_type.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        self.assertContains(response, contact4.lastname)
