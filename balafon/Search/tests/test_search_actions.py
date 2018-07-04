# -*- coding: utf-8 -*-
"""test search actions"""
#pylint: disable=too-many-locals

from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class ActionSearchTest(BaseTestCase):
    """Search contact by actions"""

    def test_search_action_type_entities(self):
        """search by action type. Action is set on the entities"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action_type = mommy.make(models.ActionType, name="my action type")
        action = mommy.make(models.Action, type=action_type)
        action.entities.add(entity1)
        action.entities.add(entity2)
        action.save()

        another_action_type = mommy.make(models.ActionType, name="another action type")
        action = mommy.make(models.Action, type=another_action_type)
        action.entities.add(entity3)
        action.save()

        url = reverse('search')

        data = {"gr0-_-action_type-_-0": action_type.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

    def test_search_action_type_contacts(self):
        """search by action type: Action is set on contact"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action_type = mommy.make(models.ActionType, name="my action type")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact2)
        action.save()

        another_action_type = mommy.make(models.ActionType, name="another action type")
        action = mommy.make(models.Action, type=another_action_type)
        action.contacts.add(contact5)
        action.save()

        url = reverse('search')

        data = {"gr0-_-action_type-_-0": action_type.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

    def test_search_action_type_both(self):
        """search by action type: action on contacts and entities"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action_type = mommy.make(models.ActionType, name="my action type")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, type=action_type)
        action.entities.add(entity2)
        action.save()

        another_action_type = mommy.make(models.ActionType, name="another action type")
        action = mommy.make(models.Action, type=another_action_type)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()

        url = reverse('search')

        data = {"gr0-_-action_type-_-0": action_type.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

    def test_search_action_subject_both(self):
        """search by action subject for contacts and entities"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        entity5 = mommy.make(models.Entity, name=u"Not really a corp")
        contact7 = mommy.make(models.Contact, entity=entity5, lastname=u"VWAB", main_contact=True, has_left=False)

        action = mommy.make(models.Action, subject="Hello world")
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, subject="Hello world")
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, subject="Bye-bye")
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()

        url = reverse('search')

        data = {"gr0-_-action_name-_-0": "Hello world"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, entity5.name)
        self.assertNotContains(response, contact7.lastname)

    def test_search_exclude_action_subject(self):
        """search by action subject for contacts and entities"""
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)

        entity5 = mommy.make(models.Entity, name=u"Not really a corp")
        contact7 = mommy.make(models.Contact, entity=entity5, lastname=u"VWAB", main_contact=True, has_left=False)

        action = mommy.make(models.Action, subject="Hello world")
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, subject="Hello world")
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, subject="Bye-bye")
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()

        url = reverse('search')

        data = {"gr0-_-exclude_action_name-_-0": "Hello world"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertContains(response, contact6.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)

        self.assertContains(response, entity4.name)
        self.assertContains(response, contact5.lastname)

        self.assertContains(response, entity5.name)
        self.assertContains(response, contact7.lastname)

    def test_search_action_subject_exclude_include(self):
        """search by action subject for contacts and entities"""
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)

        entity5 = mommy.make(models.Entity, name=u"Not really a corp")
        contact7 = mommy.make(models.Contact, entity=entity5, lastname=u"VWAB", main_contact=True, has_left=False)

        action = mommy.make(models.Action, subject="Hello world")
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, subject="Hello world")
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, subject="Bye-bye")
        action.entities.add(entity2)
        action.contacts.add(contact3)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()

        url = reverse('search')

        data = {"gr0-_-exclude_action_name-_-0": "Bye-Bye", "gr0-_-action_name-_-1": "Hello world"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, entity5.name)
        self.assertNotContains(response, contact7.lastname)

    def test_search_action_in_progress_both(self):
        """search by action status"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(models.Action, done=False)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, done=False)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action-_-0": 1}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_no_action_in_progress_both(self):
        """search by no action in progress"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(models.Action, done=False)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, done=False)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        for contact in (contact1, contact2, contact4, contact5, contact7):
            contact.entity.default_contact.delete()

        url = reverse('search')

        data = {"gr0-_-action-_-0": 0}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)

        self.assertContains(response, entity4.name)
        self.assertContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_has_action(self):
        """search contacts with actions"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(models.Action, done=False)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, done=False)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        for contact in (contact1, contact2, contact4, contact5, contact7):
            contact.entity.default_contact.delete()

        url = reverse('search')

        data = {"gr0-_-has_action-_-0": 1}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)

        self.assertContains(response, entity4.name)
        self.assertContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_no_action(self):
        """search contacts without actions"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(models.Action, done=False)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, done=False)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        for contact in (contact1, contact2, contact4, contact5, contact7):
            contact.entity.default_contact.delete()

        url = reverse('search')

        data = {"gr0-_-has_action-_-0": 0}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertContains(response, contact6.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertContains(response, contact7.lastname)

    def test_search_action_by_done_date_both(self):
        """search by action done date"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, done=True)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.done_date = datetime.now() - timedelta(10)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        dt1 = datetime.now() - timedelta(1)
        dt2 = datetime.now() + timedelta(1)

        data = {
            "gr0-_-action_by_done_date-_-0": "{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_action_by_planned_date_both(self):
        """search by action planned date"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(models.Action, planned_date=datetime.now(), end_datetime=datetime.now())
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, planned_date=datetime.now())
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, planned_date=datetime.now()- timedelta(10))
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        dt1 = datetime.now() - timedelta(1)
        dt2 = datetime.now() + timedelta(1)

        data = {
            "gr0-_-action_by_planned_date-_-0": "{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_by_planned_end_contacts(self):
        """search by no action in planned date"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)
        contact7 = mommy.make(models.Contact, entity=entity1, lastname="ZXWV", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 5, 10, 0), end_datetime=datetime(2014, 4, 15, 10, 0))
        action.contacts.add(contact1)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 5, 10, 0), end_datetime=datetime(2014, 4, 9, 10, 0)
        )
        action.contacts.add(contact2)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 9, 10, 0), end_datetime=datetime(2014, 4, 15, 10, 0)
        )
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 9, 0, 0), end_datetime=datetime(2014, 4, 11, 10, 0)
        )
        action.contacts.add(contact4)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 9, 0, 0), end_datetime=datetime(2014, 4, 9, 10, 0)
        )
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 1, 0, 0), end_datetime=datetime(2014, 4, 2, 10, 0)
        )
        action.contacts.add(contact6)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 20, 0, 0), end_datetime=datetime(2014, 4, 25, 10, 0)
        )
        action.contacts.add(contact7)
        action.save()

        contact8 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        dt1 = datetime(2014, 4, 9)
        dt2 = datetime(2014, 4, 11)

        data = {
            "gr0-_-action_by_planned_date-_-0": "{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertContains(response, contact4.lastname)
        self.assertContains(response, contact5.lastname)

        self.assertNotContains(response, contact6.lastname)
        self.assertNotContains(response, contact7.lastname)
        self.assertNotContains(response, contact8.lastname)

    def test_search_by_planned_end_entities(self):
        """earch by planned date: entiy actions"""
        entity1 = mommy.make(models.Entity, name="#ENTITY-1#")
        entity2 = mommy.make(models.Entity, name="#ENTITY-2#")
        entity3 = mommy.make(models.Entity, name="#ENTITY-3#")
        entity4 = mommy.make(models.Entity, name="#ENTITY-4#")
        entity5 = mommy.make(models.Entity, name="#ENTITY-5#")
        entity6 = mommy.make(models.Entity, name="#ENTITY-6#")
        entity7 = mommy.make(models.Entity, name="#ENTITY-7#")
        entity8 = mommy.make(models.Entity, name="#ENTITY-8#")

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 5, 10, 0), end_datetime=datetime(2014, 4, 15, 10, 0)
        )
        action.entities.add(entity1)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 5, 10, 0), end_datetime=datetime(2014, 4, 9, 10, 0)
        )
        action.entities.add(entity2)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 9, 10, 0), end_datetime=datetime(2014, 4, 15, 10, 0)
        )
        action.entities.add(entity3)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 9, 0, 0), end_datetime=datetime(2014, 4, 11, 10, 0)
        )
        action.entities.add(entity4)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 9, 0, 0), end_datetime=datetime(2014, 4, 9, 10, 0)
        )
        action.entities.add(entity5)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 1, 0, 0), end_datetime=datetime(2014, 4, 2, 10, 0)
        )
        action.entities.add(entity6)
        action.save()

        action = mommy.make(
            models.Action, planned_date=datetime(2014, 4, 20, 0, 0), end_datetime=datetime(2014, 4, 25, 10, 0)
        )
        action.entities.add(entity7)
        action.save()

        url = reverse('search')

        dt1 = datetime(2014, 4, 9)
        dt2 = datetime(2014, 4, 11)

        data = {
            "gr0-_-action_by_planned_date-_-0": "{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, entity2.name)
        self.assertContains(response, entity3.name)
        self.assertContains(response, entity4.name)
        self.assertContains(response, entity5.name)

        self.assertNotContains(response, entity6.name)
        self.assertNotContains(response, entity7.name)
        self.assertNotContains(response, entity8.name)

    def test_search_action_by_start_both(self):
        """search by action start date"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(models.Action, planned_date=datetime.now())
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, planned_date=datetime.now())
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, planned_date=datetime.now()- timedelta(10))
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        dt1 = datetime.now() - timedelta(1)
        dt2 = datetime.now() + timedelta(1)

        data = {
            "gr0-_-action_by_start_date-_-0": "{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_action_by_in_charge_both(self):
        """search by action in charge"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        user1 = mommy.make(models.TeamMember)
        user2 = mommy.make(models.TeamMember)

        action = mommy.make(models.Action, in_charge=user1)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, in_charge=user1)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, in_charge=user2)
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action_by_user-_-0": user1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_action_by_amount_gte_both(self):
        """search by action amount greater than"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(models.Action, amount=20)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, amount=30)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, amount=10)
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action_gte_amount-_-0": 15}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_action_by_amout_lt_both(self):
        """seacrh by action amount less than"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        action = mommy.make(models.Action, amount=10)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, amount=5)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, amount=20)
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action_lt_amount-_-0": 15}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)  #amount default value is None
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_action_status_both(self):
        """search by action status"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        status1 = mommy.make(models.ActionStatus)
        status2 = mommy.make(models.ActionStatus)

        action = mommy.make(models.Action, status=status1)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, status=status1)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, status=status2)
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action_status-_-0": status1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_action_opportunity_both(self):
        """search by action opportunity"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        opportunity1 = mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)

        action = mommy.make(models.Action, opportunity=opportunity1)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, opportunity=opportunity1)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, opportunity=opportunity2)
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-opportunity-_-0": opportunity1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_action_opportunity_name_both(self):
        """search by action opprtunities; contacts and entities"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        opportunity1 = mommy.make(models.Opportunity, name="ABCD")
        opportunity2 = mommy.make(models.Opportunity, name="BCDA")
        opportunity3 = mommy.make(models.Opportunity, name="ZZZZ")

        action = mommy.make(models.Action, opportunity=opportunity1)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, opportunity=opportunity2)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, opportunity=opportunity3)
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-opportunity_name-_-0": "BCD"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_action_without_status(self):
        """search by action status"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname="EFGH", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name="A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname="RSTU", main_contact=True, has_left=False)

        status1 = mommy.make(models.ActionStatus)
        status2 = mommy.make(models.ActionStatus)

        action = mommy.make(models.Action, status=status1)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, status=status1)
        action.entities.add(entity2)
        action.save()

        action = mommy.make(models.Action, status=status2)
        action.contacts.add(contact5)
        action.save()

        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()

        contact7 = mommy.make(models.Contact, lastname="@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action_without_status-_-0": status1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)

        self.assertContains(response, entity4.name)
        self.assertContains(response, contact5.lastname)

        self.assertNotContains(response, contact7.lastname)

    def test_search_action_multi_criteria(self):
        """search by action status"""
        contact1 = mommy.make(models.Contact, lastname="ABCD", main_contact=True, has_left=False)

        contact2 = mommy.make(models.Contact, lastname="EFGH", main_contact=True, has_left=False)

        contact3 = mommy.make(models.Contact, lastname="IJKL", main_contact=True, has_left=False)

        type1 = mommy.make(models.ActionType)
        type2 = mommy.make(models.ActionType)

        status1 = mommy.make(models.ActionStatus)
        status2 = mommy.make(models.ActionStatus)

        action1 = mommy.make(models.Action, type=type1, status=status1, planned_date=datetime(2016, 6, 21))
        action1.contacts.add(contact1)
        action1.save()

        action2 = mommy.make(models.Action, type=type2, status=status1, planned_date=datetime(2016, 6, 21))
        action2.contacts.add(contact2)
        action2.save()

        action3 = mommy.make(models.Action, type=type1, status=status1, planned_date=datetime(2015, 6, 21))
        action3.contacts.add(contact3)
        action3.save()

        url = reverse('search')

        data = {
            "gr0-_-action_status-_-0": status1.id,
            "gr0-_-action_type-_-1": type1.id,
            "gr0-_-action_by_planned_date-_-2": "15/06/2016 22/06/2016"
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)

    def test_search_action_multi_criteria_without_status(self):
        """search by action status"""
        contact1 = mommy.make(models.Contact, lastname="ABCD", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname="EFGH", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, lastname="IJKL", main_contact=True, has_left=False)
        contact4 = mommy.make(models.Contact, lastname="MNOP", main_contact=True, has_left=False)

        type1 = mommy.make(models.ActionType)
        type2 = mommy.make(models.ActionType)

        status1 = mommy.make(models.ActionStatus)
        status2 = mommy.make(models.ActionStatus)

        action1 = mommy.make(models.Action, type=type1, status=status1)
        action1.contacts.add(contact1)
        action1.save()

        action2 = mommy.make(models.Action, type=type2, status=status2)
        action2.contacts.add(contact2)
        action2.save()

        action3 = mommy.make(models.Action, type=type1, status=status2)
        action3.contacts.add(contact3)
        action3.save()

        action4 = mommy.make(models.Action, type=type1, status=None)
        action4.contacts.add(contact4)
        action4.save()

        url = reverse('search')

        data = {
            "gr0-_-action_without_status-_-0": status1.id,
            "gr0-_-action_type-_-1": type1.id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertContains(response, contact4.lastname)

    def test_search_action_multi_group(self):
        """search by action status"""
        contact1 = mommy.make(models.Contact, lastname="ABCDEF", main_contact=True, has_left=False)
        contact2 = mommy.make(models.Contact, lastname="EFGHIJ", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, lastname="IJKLMN", main_contact=True, has_left=False)
        contact4 = mommy.make(models.Contact, lastname="MNOPQR", main_contact=True, has_left=False)

        type1 = mommy.make(models.ActionType)
        type2 = mommy.make(models.ActionType)

        status1 = mommy.make(models.ActionStatus)
        status2 = mommy.make(models.ActionStatus)

        action1 = mommy.make(models.Action, type=type1, status=status1, planned_date=datetime(2016, 6, 21))
        action1.contacts.add(contact1)
        action1.save()

        action2 = mommy.make(models.Action, type=type2, status=status1, planned_date=datetime(2016, 6, 21))
        action2.contacts.add(contact2)
        action2.save()

        action3 = mommy.make(models.Action, type=type1, status=status1, planned_date=datetime(2015, 6, 21))
        action3.contacts.add(contact3)
        action3.save()

        action4 = mommy.make(models.Action, type=type1, status=status1, planned_date=datetime(2014, 6, 21))
        action4.contacts.add(contact4)
        action4.save()

        url = reverse('search')

        data = {
            "gr0-_-action_status-_-0": status1.id,
            "gr0-_-action_type-_-1": type1.id,
            "gr0-_-action_by_planned_date-_-2": "15/06/2016 22/06/2016",
            "gr1-_-action_status-_-0": status1.id,
            "gr1-_-action_type-_-1": type1.id,
            "gr1-_-action_by_planned_date-_-2": "15/06/2015 22/06/2015"
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual([], list(soup.select(".field-error")))

        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact4.lastname)
