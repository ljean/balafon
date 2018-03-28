# -*- coding: utf-8 -*-
"""test we can search contact by its fields"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class ContactSearchTest(BaseTestCase):
    """Test search by contact fields"""

    def test_search_union_of_contacts(self):
        """search by several contact name"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="ABCABC", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_name-_-0": 'ABCD', 'gr1-_-contact_name-_-0': 'ABCA'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)

    def test_search_contact_notes(self):
        """search by notes"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(
            models.Contact, entity=entity1, lastname="ABCD", notes="This one should be found.",
            main_contact=True, has_left=False
        )
        contact3 = mommy.make(
            models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(
            models.Contact, entity=entity2, lastname="WXYZ", notes="Not this one", main_contact=True, has_left=False
        )

        entity3 = mommy.make(models.Entity, name="The big Org")
        contact4 = mommy.make(
            models.Contact, entity=entity3, lastname="ABCABC", notes="Found", main_contact=True, has_left=False
        )

        url = reverse('search')

        data = {"gr0-_-contact_notes-_-0": 'found'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)

    def test_search_contact(self):
        """search by name"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="ABCABC", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_name-_-0": 'ABC'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)

    def test_search_contact_firstname(self):
        """search by firstname"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, firstname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, firstname="ABCABC", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-contact_firstname-_-0": 'ABC'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.firstname)
        self.assertNotContains(response, contact3.firstname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.firstname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.firstname)
