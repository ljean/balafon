# -*- coding: utf-8 -*-
"""miscellaneous searches"""

from bs4 import BeautifulSoup as BeautifulSoup4
from datetime import date, timedelta

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class ModificationBySearchTest(BaseTestCase):
    """modification"""

    def test_search_modified_by(self):
        """by modification"""

        user1 = mommy.make(models.User, is_staff=True, is_active=True)
        user2 = mommy.make(models.User, is_staff=True, is_active=True)

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False,
            last_modified_by=user1
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"IJKL", email="contact2@email2.fr", main_contact=True, has_left=False,
            last_modified_by=user2
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"MNOP", email="contact3@email3.fr", main_contact=True, has_left=False,
            last_modified_by=None
        )
        contact3.entity.name = u'Big Corp'
        contact3.entity.default_contact.delete()
        contact3.entity.save()

        url = reverse('search')

        data = {"gr0-_-contacts_modified_by-_-0": user1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)
        self.assertNotContains(response, contact3.email)

    def test_search_not_staff_modified_by(self):
        """by modification"""

        user1 = mommy.make(models.User, is_staff=False, is_active=True)
        user2 = mommy.make(models.User, is_staff=True, is_active=True)

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False,
            last_modified_by=user1
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"IJKL", email="contact2@email2.fr", main_contact=True, has_left=False,
            last_modified_by=user2
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"MNOP", email="contact3@email3.fr", main_contact=True, has_left=False,
            last_modified_by=None
        )
        contact3.entity.name = u'Big Corp'
        contact3.entity.default_contact.delete()
        contact3.entity.save()

        url = reverse('search')

        data = {"gr0-_-contacts_modified_by-_-0": user1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(1, len(soup.select('.field-error')))

        self.assertNotContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)
        self.assertNotContains(response, contact3.email)

    def test_search_modified_by_inactive(self):
        """by modification"""

        user1 = mommy.make(models.User, is_staff=True, is_active=False)
        user2 = mommy.make(models.User, is_staff=True, is_active=True)

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False,
            last_modified_by=user1
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"IJKL", email="contact2@email2.fr", main_contact=True, has_left=False,
            last_modified_by=user2
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"MNOP", email="contact3@email3.fr", main_contact=True, has_left=False,
            last_modified_by=None
        )
        contact3.entity.name = u'Big Corp'
        contact3.entity.default_contact.delete()
        contact3.entity.save()

        url = reverse('search')

        data = {"gr0-_-contacts_modified_by-_-0": user1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)
        self.assertNotContains(response, contact3.email)

    def test_search_entity_modified_by(self):
        """by modification"""

        user1 = mommy.make(models.User, is_staff=True, is_active=True)
        user2 = mommy.make(models.User, is_staff=True, is_active=True)

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False,
            last_modified_by=None
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.last_modified_by = user1
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"IJKL", email="contact2@email2.fr", main_contact=True, has_left=False,
            last_modified_by=user1
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"MNOP", email="contact3@email3.fr", main_contact=True, has_left=False,
            last_modified_by=None
        )
        contact3.entity.name = u'Big Corp'
        contact3.entity.default_contact.delete()
        contact3.entity.last_modified_by = user2
        contact3.entity.save()

        url = reverse('search')

        data = {"gr0-_-entities_modified_by-_-0": user1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)
        self.assertNotContains(response, contact3.email)

    def test_search_contact_or_entity_modified_by(self):
        """by modification"""

        user1 = mommy.make(models.User, is_staff=True, is_active=True)
        user2 = mommy.make(models.User, is_staff=True, is_active=True)

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False,
            last_modified_by=None
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.last_modified_by = user1
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"IJKL", email="contact2@email2.fr", main_contact=True, has_left=False,
            last_modified_by=user1
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"MNOP", email="contact3@email3.fr", main_contact=True, has_left=False,
            last_modified_by=None
        )
        contact3.entity.name = u'Big Corp'
        contact3.entity.default_contact.delete()
        contact3.entity.last_modified_by = user2
        contact3.entity.save()

        url = reverse('search')

        data = {"gr0-_-contacts_and_entities_modified_by-_-0": user1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, contact1.email)
        self.assertContains(response, contact2.email)
        self.assertNotContains(response, contact3.email)



class ModificationDateSearchTest(BaseTestCase):
    """search by modified"""

    def test_contact_modified_today(self):
        """modified today"""

        contact1 = mommy.make(models.Contact, lastname="Azertuiop")

        url = reverse('search')

        data = {"gr0-_-contact_by_modified_date-_-0": '{0} {0}'.format(date.today().strftime("%d/%m/%Y"))}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.lastname)

    def test_search_contacts_and_entities_by_date(self):
        """by modification date"""

        # when saved 'modified' is updated
        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False,
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        url = reverse('search')

        data = {"gr0-_-contacts_and_entities_by_change_date-_-0": '{0} {0}'.format(date.today().strftime("%d/%m/%Y"))}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, contact1.lastname)

    def test_contact_modified_tomorrow(self):
        """modified tomorrow"""

        contact1 = mommy.make(models.Contact, lastname="Azertuiop")

        url = reverse('search')

        tomorrow = date.today() + timedelta(1)
        data = {"gr0-_-contact_by_modified_date-_-0": '{0} {0}'.format(tomorrow.strftime("%d/%m/%Y"))}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, contact1.lastname)

    def test_entity_modified_today(self):
        """entity modified today"""

        contact1 = mommy.make(models.Contact, lastname="Azertuiop")

        url = reverse('search')

        data = {"gr0-_-entity_by_modified_date-_-0": '{0} {0}'.format(date.today().strftime("%d/%m/%Y"))}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.lastname)

    def test_entity_modified_today2(self):
        """entity modified today no single contact"""

        contact1 = mommy.make(models.Contact, lastname="Azertuiop")
        entity2 = mommy.make(models.Entity, is_single_contact=True)
        contact2 = entity2.default_contact
        contact2.lastname = "QWERTYUIOP"
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-entity_by_modified_date-_-0": '{0} {0}'.format(date.today().strftime("%d/%m/%Y"))}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)

    def test_entity_modified_tomorrow(self):
        """entity modified tomorrow"""

        contact1 = mommy.make(models.Contact, lastname="Azertuiop")

        url = reverse('search')

        tomorrow = date.today() + timedelta(1)
        data = {"gr0-_-entity_by_modified_date-_-0": '{0} {0}'.format(tomorrow.strftime("%d/%m/%Y"))}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, contact1.lastname)