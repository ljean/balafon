# -*- coding: utf-8 -*-
"""test we can search contact by entity"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models

from balafon.Search.tests import BaseTestCase


class EntitySearchTest(BaseTestCase):
    """search by entity fields"""

    def test_search_entity(self):
        """search by entity name"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-entity_name-_-0": 'tiny'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_entity_description(self):
        """search by entity description"""
        entity1 = mommy.make(models.Entity, name="My tiny corp", description="This one should be found.")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp", description="Not this one")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="The big Org", description="Found")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="ABCABC", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-entity_description-_-0": 'found'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)

    def test_search_entity_notes(self):
        """search by entity notes"""
        entity1 = mommy.make(models.Entity, name="My tiny corp", notes="This one should be found.")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp", notes="Not this one")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="The big Org", notes="Found")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="ABCABC", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-entity_notes-_-0": 'found'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)
