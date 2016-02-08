# -*- coding: utf-8 -*-
"""test search actions"""
#pylint: disable=too-many-locals

from bs4 import BeautifulSoup as BeautifulSoup4
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class ActionSearchTest(BaseTestCase):
    """Search contact by actions"""

    def test_search_action_type_entities(self):
        """search by action type. Action is set on the entities"""
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

        action_type = mommy.make(models.ActionType, name=u"my action type")
        action = mommy.make(models.Action, type=action_type)
        action.entities.add(entity1)
        action.entities.add(entity2)
        action.save()

        another_action_type = mommy.make(models.ActionType, name=u"another action type")
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

        action_type = mommy.make(models.ActionType, name=u"my action type")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact2)
        action.save()

        another_action_type = mommy.make(models.ActionType, name=u"another action type")
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

        action_type = mommy.make(models.ActionType, name=u"my action type")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()

        action = mommy.make(models.Action, type=action_type)
        action.entities.add(entity2)
        action.save()

        another_action_type = mommy.make(models.ActionType, name=u"another action type")
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

    def test_search_action_in_progress_both(self):
        """search by action status"""
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        for contact in (contact1, contact2, contact4, contact5, contact7):
            contact.entity.default_contact.delete()

        url = reverse('search')

        data = {"gr0-_-action-_-0": 0}

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

        self.assertContains(response, contact7.lastname)

    def test_search_has_action(self):
        """search contacts with actions"""
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        for contact in (contact1, contact2, contact4, contact5, contact7):
            contact.entity.default_contact.delete()

        url = reverse('search')

        data = {"gr0-_-has_action-_-0": 1}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        for contact in (contact1, contact2, contact4, contact5, contact7):
            contact.entity.default_contact.delete()

        url = reverse('search')

        data = {"gr0-_-has_action-_-0": 0}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        dt1 = datetime.now() - timedelta(1)
        dt2 = datetime.now() + timedelta(1)

        data = {
            "gr0-_-action_by_done_date-_-0": u"{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        dt1 = datetime.now() - timedelta(1)
        dt2 = datetime.now() + timedelta(1)

        data = {
            "gr0-_-action_by_planned_date-_-0": u"{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        contact7 = mommy.make(models.Contact, entity=entity1, lastname=u"ZXWV", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)

        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)

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

        contact8 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        dt1 = datetime(2014, 4, 9)
        dt2 = datetime(2014, 4, 11)

        data = {
            "gr0-_-action_by_planned_date-_-0": u"{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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
        entity1 = mommy.make(models.Entity, name=u"#ENTITY-1#")
        entity2 = mommy.make(models.Entity, name=u"#ENTITY-2#")
        entity3 = mommy.make(models.Entity, name=u"#ENTITY-3#")
        entity4 = mommy.make(models.Entity, name=u"#ENTITY-4#")
        entity5 = mommy.make(models.Entity, name=u"#ENTITY-5#")
        entity6 = mommy.make(models.Entity, name=u"#ENTITY-6#")
        entity7 = mommy.make(models.Entity, name=u"#ENTITY-7#")
        entity8 = mommy.make(models.Entity, name=u"#ENTITY-8#")

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
            "gr0-_-action_by_planned_date-_-0": u"{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        dt1 = datetime.now() - timedelta(1)
        dt2 = datetime.now() + timedelta(1)

        data = {
            "gr0-_-action_by_start_date-_-0": u"{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action_by_user-_-0": user1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action_gte_amount-_-0": 15}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action_lt_amount-_-0": 15}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-action_status-_-0": status1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-opportunity-_-0": opportunity1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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

        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)

        url = reverse('search')

        data = {"gr0-_-opportunity_name-_-0": "BCD"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
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
