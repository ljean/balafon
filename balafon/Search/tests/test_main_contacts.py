# -*- coding: utf-8 -*-
"""test search behavior for main and has_left contacts"""

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class MainContactAndHasLeftSearchTest(BaseTestCase):
    """test than main contact and has left are correctly taken into account"""

    def _make_contact(self, main_contact, has_left):
        """make a contact"""
        entity = mommy.make(models.Entity, name=u"TinyTinyCorp")
        contact = entity.default_contact
        contact.lastname = 'TiniMax'
        contact.firstname = 'Boss'
        contact.main_contact = main_contact
        contact.has_left = has_left
        contact.save()
        return entity, contact

    def _make_another_contact(self, entity, main_contact, has_left):
        """make another contact"""
        contact = mommy.make(models.Contact, entity=entity)
        contact.lastname = 'TinyMin'
        contact.firstname = 'Other'
        contact.main_contact = main_contact
        contact.has_left = has_left
        contact.save()
        return contact

    def test_main_contact(self):
        """test search with main contact"""
        entity, contact = self._make_contact(True, False)

        url = reverse('search')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity.name)
        self.assertContains(response, contact.lastname)

    def test_main_contact_has_left(self):
        """test search with main contact who left"""
        entity, contact = self._make_contact(True, True)

        url = reverse('search')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity.name)
        self.assertNotContains(response, contact.lastname)

    def test_only_one_main_contact(self):
        """test search not the main contact"""
        entity, contact = self._make_contact(False, False)

        url = reverse('search')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity.name)
        self.assertNotContains(response, contact.lastname)

        #the contact will be restored as main contact
        entity.save()

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity.name)
        self.assertContains(response, contact.lastname)

        self.assertEqual(1, models.Contact.objects.count())
        contact = models.Contact.objects.all()[0]
        self.assertEqual(contact.main_contact, True)

    def test_two_main_contacts(self):
        """test two main contacts"""
        entity, contact1 = self._make_contact(False, False)
        contact2 = self._make_another_contact(entity, True, False)

        url = reverse('search')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)

    def test_search_has_left_exclude(self):
        """test excluding contact who left the entity"""
        entity, contact1 = self._make_contact(True, True)
        contact2 = self._make_another_contact(entity, True, False)

        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(entity)
        group.save()

        url = reverse('search')
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)

    def test_search_has_left_include(self):
        """test including contacts who left the entity"""
        entity, contact1 = self._make_contact(True, True)
        contact2 = self._make_another_contact(entity, True, False)

        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(entity)
        group.save()

        url = reverse('search')
        data = {"gr0-_-group-_-0": group.id, "gr0-_-contact_has_left-_-1": 1}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)

    def test_search_has_left_only(self):
        """test only contacts who left the entity"""
        entity, contact1 = self._make_contact(True, True)
        contact2 = self._make_another_contact(entity, True, False)

        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(entity)
        group.save()

        url = reverse('search')
        data = {"gr0-_-group-_-0": group.id, "gr0-_-contact_has_left-_-1": 0}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
