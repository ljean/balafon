# -*- coding: utf-8 -*-
"""miscellaneous searches"""

from unittest import skipIf

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm import settings as crm_settings
from balafon.Search.tests import BaseTestCase


class SameAsEmailTest(BaseTestCase):
    """Search same-as"""

    def test_search_same_as_not_allowed1(self):
        """same as not allowed: search on entity group"""

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(contact1.entity)
        group.entities.add(contact2.entity)
        group.save()

        contact1.same_as = models.SameAs.objects.create()
        contact1.same_as_priority = 1
        contact1.save()
        contact2.same_as = contact1.same_as
        contact2.same_as_priority = 2
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '0'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)

    def test_search_same_as_not_allowed2(self):
        """same as not allowed"""
        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(contact1.entity)
        group.entities.add(contact2.entity)
        group.save()

        contact1.same_as = models.SameAs.objects.create()
        contact1.same_as_priority = 2
        contact1.save()
        contact2.same_as = contact1.same_as
        contact2.same_as_priority = 1
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '0'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, contact1.email)
        self.assertContains(response, contact2.email)

    def test_search_same_as_not_allowed3(self):
        """same as not allowed: two groups"""
        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        group1 = mommy.make(models.Group, name="GROUP1")
        group1.entities.add(contact1.entity)
        group1.save()

        group2 = mommy.make(models.Group, name="GROUP2")
        group2.entities.add(contact2.entity)
        group2.save()

        contact1.same_as = models.SameAs.objects.create()
        contact1.same_as_priority = 2
        contact1.save()
        contact2.same_as = contact1.same_as
        contact2.same_as_priority = 1
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group1.id, "gr0-_-no_same_as-_-1": '0', "gr1-_-group-_-0": group2.id, }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, contact1.email)
        self.assertContains(response, contact2.email)

    def test_search_same_as_allowed(self):
        """same as allowed"""
        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(contact1.entity)
        group.entities.add(contact2.entity)
        group.save()

        contact1.same_as = models.SameAs.objects.create()
        contact1.same_as_priority = 1
        contact1.save()
        contact2.same_as = contact1.same_as
        contact2.same_as_priority = 2
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '1'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact1.email)
        self.assertContains(response, contact2.email)

    def test_search_same_one_not_in_results(self):
        """
        The same-as contact without priority should be display if the same-as with priority is not returned by search
        """
        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        group = mommy.make(models.Group, name="GROUP1")
        group.contacts.add(contact2)
        group.save()

        contact1.same_as = models.SameAs.objects.create()
        contact1.same_as_priority = 1
        contact1.save()
        contact2.same_as = contact1.same_as
        contact2.same_as_priority = 2
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, contact1.email)
        self.assertContains(response, contact2.email)

    def test_search_same_as_priority_not_in_results(self):
        """
        The same-as contact without priority should be display if the same-as with priority is not returned by search
        """
        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact3@email3.fr", main_contact=True, has_left=False
        )
        contact3.entity.name = u'Big Corp'
        contact3.entity.default_contact.delete()
        contact3.entity.save()

        group = mommy.make(models.Group, name="GROUP1")
        group.contacts.add(contact2)
        group.contacts.add(contact3)
        group.save()

        contact1.same_as = models.SameAs.objects.create()
        contact1.same_as_priority = 1
        contact1.save()

        contact2.same_as = contact1.same_as
        contact2.same_as_priority = 3
        contact2.save()

        contact3.same_as = contact1.same_as
        contact3.same_as_priority = 2
        contact3.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '0'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact3.email)
        self.assertNotContains(response, contact2.email)
        self.assertNotContains(response, contact1.email)

    def test_search_same_as_priority_not_in_results2(self):
        """
        The same-as contact without priority should be display if the same-as with priority is not returned by search
        """
        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact3@email3.fr", main_contact=True, has_left=False
        )
        contact3.entity.name = u'Big Corp'
        contact3.entity.default_contact.delete()
        contact3.entity.save()

        group = mommy.make(models.Group, name="GROUP1")
        group.contacts.add(contact2)
        group.contacts.add(contact3)
        group.save()

        contact1.same_as = models.SameAs.objects.create()
        contact1.same_as_priority = 1
        contact1.save()

        contact2.same_as = contact1.same_as
        contact2.same_as_priority = 2
        contact2.save()

        contact3.same_as = contact1.same_as
        contact3.same_as_priority = 3
        contact3.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '0'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, contact3.email)
        self.assertContains(response, contact2.email)
        self.assertNotContains(response, contact1.email)

    def test_search_same_as_priority_not_in_results3(self):
        """
        The same-as contact without priority should be display if the same-as with priority is not returned by search
        """
        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact3@email3.fr", main_contact=True, has_left=False
        )
        contact3.entity.name = u'Big Corp'
        contact3.entity.default_contact.delete()
        contact3.entity.save()

        group = mommy.make(models.Group, name="GROUP1")
        group.contacts.add(contact2)
        group.save()

        contact1.same_as = models.SameAs.objects.create()
        contact1.same_as_priority = 1
        contact1.save()

        contact2.same_as = contact1.same_as
        contact2.same_as_priority = 2
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '0'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact2.email)
        self.assertNotContains(response, contact1.email)


class SameAsNameTest(BaseTestCase):
    """Search same-as"""

    def _make_contact(self, **kwargs):
        kwargs.setdefault('has_left', False)
        kwargs.setdefault('main_contact', True)
        entity = mommy.make(models.Entity)
        contact = mommy.make(models.Contact, entity=entity, **kwargs)
        contact.entity.default_contact.delete()
        contact.entity.save()
        return contact

    def test_search_duplicated_contacts(self):
        """same as not allowed: search on entity group"""

        contact1 = self._make_contact(firstname=u"Pierre", lastname=u"Dupond", email="a@me.fr")
        contact2 = self._make_contact(firstname=u"Paul", lastname=u"Dupond", email="b@me.fr")
        contact3 = self._make_contact(firstname=u"Pierre", lastname=u"Dupond", email="c@me.fr")
        contact4 = self._make_contact(firstname=u"Pierre", lastname=u"Dupont", email="d@me.fr")

        url = reverse('search')

        data = {"gr0-_-duplicated_contacts-_-1": '1'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)
        self.assertContains(response, contact3.email)
        self.assertNotContains(response, contact4.email)

    def test_search_several_duplicated_contacts(self):
        """same as not allowed: search on entity group"""

        contact1 = self._make_contact(firstname=u"Pierre", lastname=u"Dupond", email="a@me.fr")
        contact2 = self._make_contact(firstname=u"Paul", lastname=u"Dupond", email="b@me.fr")
        contact3 = self._make_contact(firstname=u"Pierre", lastname=u"Dupond", email="c@me.fr")
        contact4 = self._make_contact(firstname=u"Pierre", lastname=u"Dupont", email="d@me.fr")
        contact5 = self._make_contact(firstname=u"Pierre", lastname=u"Dupond", email="e@me.fr")
        contact6 = self._make_contact(firstname=u"Pierre", lastname=u"Dupond", email="f@me.fr")

        url = reverse('search')

        data = {"gr0-_-duplicated_contacts-_-1": '1'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)
        self.assertContains(response, contact3.email)
        self.assertNotContains(response, contact4.email)
        self.assertContains(response, contact5.email)
        self.assertContains(response, contact6.email)

    def test_search_duplicated_contacts_name_only(self):
        """same as not allowed: search on entity group"""

        contact1 = self._make_contact(firstname=u"Pierre", lastname=u"Dupond", email="a@me.fr")
        contact2 = self._make_contact(firstname=u"Paul", lastname=u"Dupond", email="b@me.fr")
        contact3 = self._make_contact(firstname=u"Pierre", lastname=u"Dupond", email="c@me.fr")
        contact4 = self._make_contact(firstname=u"Pierre", lastname=u"Dupont", email="d@me.fr")

        url = reverse('search')

        data = {"gr0-_-duplicated_contacts-_-1": '2'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.email)
        self.assertContains(response, contact2.email)
        self.assertContains(response, contact3.email)
        self.assertNotContains(response, contact4.email)

    def test_search_ignore_unknown(self):
        """same as not allowed: search on entity group"""

        contact1 = self._make_contact(firstname=u"", lastname=u"", email="a@me.fr")
        contact2 = self._make_contact(firstname=u"", lastname=u"", email="b@me.fr")

        url = reverse('search')

        data = {"gr0-_-duplicated_contacts-_-1": '1'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)

    def test_search_ignore_unknown_name_only(self):
        """same as not allowed: search on entity group"""

        contact1 = self._make_contact(firstname=u"A", lastname=u"", email="a@me.fr")
        contact2 = self._make_contact(firstname=u"B", lastname=u"", email="b@me.fr")

        url = reverse('search')

        data = {"gr0-_-duplicated_contacts-_-1": '2'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)

