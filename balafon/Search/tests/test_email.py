# -*- coding: utf-8 -*-
"""test we can search contact by email"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class EmailSearchTest(BaseTestCase):
    """Search by email"""

    def test_search_email(self):
        """search by email"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, email="abcd@mailinator.com", entity=entity1, lastname="ABCD",
            main_contact=True, has_left=False
        )
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_entity_email-_-0": "mailinator"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

    def test_search_email_empty(self):
        """search by empty email"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, email="abcd@mailinator.com", entity=entity1, lastname="ABCD",
            main_contact=True, has_left=False
        )
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_entity_email-_-0": ""}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select('.field-error')))

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_email_entity(self):
        """search by entity email"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)
        contact4 = mommy.make(models.Contact, entity=entity2, lastname="RTYU", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_entity_email-_-0": "mailinator"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        self.assertContains(response, contact4.lastname)

    def test_search_email_full(self):
        """search full emai address"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, email="abcd@mailinator.com", entity=entity1, lastname="ABCD",
            main_contact=True, has_left=False
        )
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)
        contact4 = mommy.make(models.Contact, entity=entity2, lastname="RTYU", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_entity_email-_-0": "contact@mailinator.com"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        self.assertContains(response, contact4.lastname)

    def test_search_email_none(self):
        """search email no matches"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, email="abcd@mailinator.com", entity=entity1, lastname="ABCD",
            main_contact=True, has_left=False
        )
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)
        contact4 = mommy.make(models.Contact, entity=entity2, lastname="RTYU", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_entity_email-_-0": "toto@toto.com"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        self.assertNotContains(response, contact4.lastname)


class HasEmailSearchTest(BaseTestCase):
    """Search by HasEmail"""

    def test_search_has_email(self):
        """search has email"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, entity=entity1, lastname="ABCD", email="toto1@toto.fr", main_contact=True, has_left=False
        )
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="The big Org", email="toto2@toto.fr")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="ABCABC", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_has_email-_-0": 1}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)

    def test_search_has_no_email(self):
        """search by has no email"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, entity=entity1, lastname="ABCD", email="toto1@toto.fr", main_contact=True, has_left=False
        )
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="The big Org", email="toto2@toto.fr")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="ABCABC", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_has_email-_-0": 0}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

    def test_search_has_email_and_name(self):
        """search email and name"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, entity=entity1, lastname="ABCD", email="toto1@toto.fr", main_contact=True, has_left=False
        )
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="The big Org", email="toto2@toto.fr")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="ABCABC", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_has_email-_-0": 1, "gr0-_-entity_name-_-1": entity1.name}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
