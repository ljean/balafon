# -*- coding: utf-8 -*-
"""miscellaneous searches"""

from unittest import skipIf

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm import settings as crm_settings
from balafon.Search.tests import BaseTestCase


class SearchTest(BaseTestCase):
    """a few basic things"""

    def test_view_search(self):
        """test view search and field choice is populated"""
        response = self.client.get(reverse('search'))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertTrue(len(soup.select("#id_field_choice option")) > 0)

    def test_view_anonymous(self):
        """test view search as anonymous user"""
        self.client.logout()
        response = self.client.get(reverse('search'))
        self.assertEqual(302, response.status_code)

    def test_view_non_staff(self):
        """test view search as anonymous user"""
        self.user.is_staff = False
        self.user.save()
        response = self.client.get(reverse('search'))
        self.assertEqual(302, response.status_code)

    def test_search_contact(self):
        """search by name"""
        """search by name"""
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)

        response = self.client.post(reverse('search'), data={"gr0-_-contact_name-_-0": 'ABC'})
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.lastname)

    def test_search_contact_anonymous(self):
        """search as anonymous user"""
        self.client.logout()
        mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)

        response = self.client.post(reverse('search'), data={"gr0-_-contact_name-_-0": 'ABC'})
        self.assertEqual(302, response.status_code)

    def test_search_contact_non_staff(self):
        """search as anonymous user"""
        self.user.is_staff = False
        self.user.save()
        mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)

        response = self.client.post(reverse('search'), data={"gr0-_-contact_name-_-0": 'ABC'})
        self.assertEqual(302, response.status_code)


class SameAsTest(BaseTestCase):
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

        # data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '0'}
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


class HasCityAndZipTest(BaseTestCase):
    """test has city and zip"""

    def _make_contact(self, name, city, zip_code):
        """make a contact"""
        entity = mommy.make(models.Entity, city=city, zip_code=zip_code)
        contact = entity.default_contact
        contact.lastname = name
        contact.main_contact = True
        contact.has_left = False
        contact.save()
        return entity, contact

    def test_has_address_entity(self, has_address=True):
        """has address on entity"""

        city1 = mommy.make(models.City, name="ZooPark")
        mommy.make(models.City, name="VodooPark")

        entity1, contact1 = self._make_contact("ABCD", city1, "44444")

        contact5 = mommy.make(models.Contact, entity=entity1, lastname="QRST")

        entity2, contact2 = self._make_contact("EFGH", city1, "")

        entity3, contact3 = self._make_contact("IJKL", None, "44444")

        entity4, contact4 = self._make_contact("MNOP", None, "")

        response = self.client.post(
            reverse('search'),
            data={"gr0-_-has_city_and_zip-_-0": 1 if has_address else 0}
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, len(BeautifulSoup(response.content).select('.field-error')))

        if has_address:
            self.assertContains(response, entity1.name)
            self.assertContains(response, contact1.lastname)
            self.assertContains(response, contact5.lastname)

            self.assertNotContains(response, entity2.name)
            self.assertNotContains(response, contact2.lastname)

            self.assertNotContains(response, entity3.name)
            self.assertNotContains(response, contact3.lastname)

            self.assertNotContains(response, entity4.name)
            self.assertNotContains(response, contact4.lastname)
        else:
            self.assertNotContains(response, entity1.name)
            self.assertNotContains(response, contact1.lastname)
            self.assertNotContains(response, contact5.lastname)

            self.assertContains(response, entity2.name)
            self.assertContains(response, contact2.lastname)

            self.assertContains(response, entity3.name)
            self.assertContains(response, contact3.lastname)

            self.assertContains(response, entity4.name)
            self.assertContains(response, contact4.lastname)

    def test_has_address_contact(self, has_address=True):
        """has address on contacts"""

        city1 = mommy.make(models.City, name="ZooPark")
        mommy.make(models.City, name="VodooPark")

        entity1, contact1 = self._make_contact("ABCD", None, "")
        contact1.city = city1
        contact1.zip_code = "44444"
        contact1.save()

        contact5 = mommy.make(models.Contact, entity=entity1, lastname="QRST")

        entity2, contact2 = self._make_contact("EFGH", None, "")
        contact2.city = city1
        contact2.zip_code = ""
        contact2.save()

        entity3, contact3 = self._make_contact("IJKL", None, "44444")
        contact3.city = None
        contact3.zip_code = "44444"
        contact3.save()

        entity4, contact4 = self._make_contact("MNOP", None, "")
        contact4.city = None
        contact4.zip_code = ""
        contact4.save()

        response = self.client.post(
            reverse('search'),
            data={"gr0-_-has_city_and_zip-_-0": 1 if has_address else 0}
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, len(BeautifulSoup(response.content).select('.field-error')))

        if has_address:
            self.assertContains(response, entity1.name)
            self.assertContains(response, contact1.lastname)
            self.assertNotContains(response, contact5.lastname)

            self.assertNotContains(response, entity2.name)
            self.assertNotContains(response, contact2.lastname)

            self.assertNotContains(response, entity3.name)
            self.assertNotContains(response, contact3.lastname)

            self.assertNotContains(response, entity4.name)
            self.assertNotContains(response, contact4.lastname)
        else:
            self.assertContains(response, entity1.name)
            self.assertNotContains(response, contact1.lastname)
            self.assertContains(response, contact5.lastname)

            self.assertContains(response, entity2.name)
            self.assertContains(response, contact2.lastname)

            self.assertContains(response, entity3.name)
            self.assertContains(response, contact3.lastname)

            self.assertContains(response, entity4.name)
            self.assertContains(response, contact4.lastname)

    def test_has_address_mix(self, has_address=True):
        """has address contacts and entities"""

        city1 = mommy.make(models.City, name="ZooPark")
        mommy.make(models.City, name="VodooPark")

        entity1, contact1 = self._make_contact("ABCD", city1, "")
        contact1.city = None
        contact1.zip_code = "44444"
        contact1.save()

        entity2, contact2 = self._make_contact("EFGH", None, "44444")
        contact2.city = city1
        contact2.zip_code = ""
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-has_city_and_zip-_-0": 1 if has_address else 0}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        if has_address:
            self.assertNotContains(response, entity1.name)
            self.assertNotContains(response, contact1.lastname)

            self.assertNotContains(response, entity2.name)
            self.assertNotContains(response, contact2.lastname)
        else:
            self.assertContains(response, entity1.name)
            self.assertContains(response, contact1.lastname)

            self.assertContains(response, entity2.name)
            self.assertContains(response, contact2.lastname)

    def test_has_no_address_entity(self):
        """has no address: entities"""
        self.test_has_address_entity(False)

    def test_has_no_address_contact(self):
        """has no address contacts"""
        self.test_has_address_contact(False)

    def test_has_no_address_mix(self):
        """has no address contacts and entites"""
        self.test_has_address_mix(False)


class HasAddressTest(BaseTestCase):
    """test has address"""

    def _make_contact(self, name, city, zip_code, address=''):
        """make a contact"""
        entity = mommy.make(models.Entity, address=address, city=city, zip_code=zip_code)
        contact = entity.default_contact
        contact.lastname = name
        contact.main_contact = True
        contact.has_left = False
        contact.save()
        return entity, contact

    def test_has_address_entity(self, has_address=True):
        """has address on entity"""

        city1 = mommy.make(models.City, name="ZooPark")
        mommy.make(models.City, name="VodooPark")

        entity1, contact1 = self._make_contact("ABCD", city1, "44444", '123 something street')

        contact5 = mommy.make(models.Contact, entity=entity1, lastname="QRST")

        entity2, contact2 = self._make_contact("EFGH", city1, "44444")
        contact2.address = '124 something street'
        contact2.save()

        entity3, contact3 = self._make_contact("IJKL", city1, "44444", '')

        entity4, contact4 = self._make_contact("MNOP", None, "", '')

        response = self.client.post(
            reverse('search'),
            data={"gr0-_-has_address-_-0": 1 if has_address else 0}
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, len(BeautifulSoup(response.content).select('.field-error')))

        if has_address:
            self.assertContains(response, entity1.name)
            self.assertContains(response, contact1.lastname)
            self.assertContains(response, contact5.lastname)

            self.assertNotContains(response, entity2.name)
            self.assertNotContains(response, contact2.lastname)

            self.assertNotContains(response, entity3.name)
            self.assertNotContains(response, contact3.lastname)

            self.assertNotContains(response, entity4.name)
            self.assertNotContains(response, contact4.lastname)
        else:
            self.assertNotContains(response, entity1.name)
            self.assertNotContains(response, contact1.lastname)
            self.assertNotContains(response, contact5.lastname)

            self.assertContains(response, entity2.name)
            self.assertContains(response, contact2.lastname)

            self.assertContains(response, entity3.name)
            self.assertContains(response, contact3.lastname)

            self.assertContains(response, entity4.name)
            self.assertContains(response, contact4.lastname)

    def test_has_address_contact(self, has_address=True):
        """has address on contacts"""

        city1 = mommy.make(models.City, name="ZooPark")
        mommy.make(models.City, name="VodooPark")

        entity1, contact1 = self._make_contact("ABCD", None, "")
        contact1.city = city1
        contact1.zip_code = "44444"
        contact1.address = "123 something street"
        contact1.save()

        contact5 = mommy.make(models.Contact, entity=entity1, lastname="QRST")

        entity2, contact2 = self._make_contact("EFGH", None, "")
        contact2.city = city1
        contact2.zip_code = "4444"
        contact2.save()

        entity3, contact3 = self._make_contact("IJKL", None, "44444")
        contact3.city = city1
        contact3.zip_code = "44444"
        contact3.save()

        entity4, contact4 = self._make_contact("MNOP", None, "")
        contact4.city = None
        contact4.zip_code = ""
        contact4.save()

        response = self.client.post(
            reverse('search'),
            data={"gr0-_-has_address-_-0": 1 if has_address else 0}
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, len(BeautifulSoup(response.content).select('.field-error')))

    def test_has_address_mix(self, has_address=True):
        """has address contacts and entities"""

        city1 = mommy.make(models.City, name="ZooPark")
        mommy.make(models.City, name="VodooPark")

        entity1, contact1 = self._make_contact("ABCD", city1, "44444")
        contact1.city = None
        contact1.address = "123 something street"
        contact1.save()

        entity2, contact2 = self._make_contact("EFGH", None, "", '123 something street')
        contact2.city = city1
        contact2.zip_code = ""
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-has_address-_-0": 1 if has_address else 0}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        if has_address:
            self.assertNotContains(response, entity1.name)
            self.assertNotContains(response, contact1.lastname)

            self.assertNotContains(response, entity2.name)
            self.assertNotContains(response, contact2.lastname)
        else:
            self.assertContains(response, entity1.name)
            self.assertContains(response, contact1.lastname)

            self.assertContains(response, entity2.name)
            self.assertContains(response, contact2.lastname)

    def test_has_no_address_entity(self):
        """has no address: entities"""
        self.test_has_address_entity(False)

    def test_has_no_address_contact(self):
        """has no address contacts"""
        self.test_has_address_contact(False)

    def test_has_no_address_mix(self):
        """has no address contacts and entites"""
        self.test_has_address_mix(False)


class HasEntitySearchTest(BaseTestCase):
    """Search has entity"""

    @skipIf(not crm_settings.ALLOW_SINGLE_CONTACT, "ALLOW_SINGLE_CONTACT disabled")
    def test_contact_has_entity(self):
        """contact has entity"""
        entity1 = mommy.make(models.Entity, is_single_contact=False)
        entity2 = mommy.make(models.Entity, is_single_contact=True)

        contact1 = entity1.default_contact
        contact1.lastname = "AZERTYUIOP"
        contact1.save()

        contact2 = entity2.default_contact
        contact2.lastname = "QWERTYUIOP"
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-has_entity-_-0": 1}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)

    @skipIf(not crm_settings.ALLOW_SINGLE_CONTACT, "ALLOW_SINGLE_CONTACT disabled")
    def test_contact_doesnt_have_entity(self):
        """contact doesn't have entity"""

        entity1 = mommy.make(models.Entity, is_single_contact=False)
        entity2 = mommy.make(models.Entity, is_single_contact=True)

        contact1 = entity1.default_contact
        contact1.lastname = "AZERTYUIOP"
        contact1.save()

        contact2 = entity2.default_contact
        contact2.lastname = "QWERTYUIOP"
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-has_entity-_-0": 0}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)


class LanguageSearchTest(BaseTestCase):
    """search by language"""

    def test_contact_language(self):
        """search language is set"""

        contact1 = mommy.make(models.Contact, lastname="ABCD", favorite_language="")
        contact2 = mommy.make(models.Contact, lastname="Azerty", favorite_language="fr")
        contact3 = mommy.make(models.Contact, lastname="Qwerty", favorite_language="en")

        response = self.client.post(
            reverse('search'),
            data={"gr0-_-contact_lang-_-0": 'fr'}
        )
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)

    def test_contact_no_language(self):
        """search language is not set"""

        contact1 = mommy.make(models.Contact, lastname="ABCD", favorite_language="")
        contact2 = mommy.make(models.Contact, lastname="Azerty", favorite_language="fr")
        contact3 = mommy.make(models.Contact, lastname="Qwerty", favorite_language="en")

        response = self.client.post(
            reverse('search'),
            data={"gr0-_-contact_lang-_-0": ''}
        )
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)


class HasSameAsTest(BaseTestCase):
    """Search has same-as"""

    def test_search_without_same_as(self):
        """contact ithout same-as"""
        same_as = models.SameAs.objects.create()

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False,
            same_as=same_as, same_as_priority=1
        )

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False,
            same_as=same_as, same_as_priority=2
        )

        contact3 = mommy.make(
            models.Contact, lastname=u"IJKL", email="contact3@email3.fr", main_contact=True, has_left=False,
        )

        url = reverse('search')

        data = {"gr0-_-has_same_as-_-0": '0'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)
        self.assertContains(response, contact3.email)

    def test_search_with_same_as_only_prio1(self):
        """contact ithout same-as"""
        same_as = models.SameAs.objects.create()

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False,
            same_as=same_as, same_as_priority=1
        )

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False,
            same_as=same_as, same_as_priority=2
        )

        contact3 = mommy.make(
            models.Contact, lastname=u"IJKL", email="contact3@email3.fr", main_contact=True, has_left=False,
        )

        url = reverse('search')

        data = {"gr0-_-has_same_as-_-0": '1'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)
        self.assertNotContains(response, contact3.email)

    def test_search_with_same_as_all(self):
        """contact ithout same-as"""
        same_as = models.SameAs.objects.create()

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False,
            same_as=same_as, same_as_priority=1
        )

        contact2 = mommy.make(
            models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False,
            same_as=same_as, same_as_priority=2
        )

        contact3 = mommy.make(
            models.Contact, lastname=u"IJKL", email="contact3@email3.fr", main_contact=True, has_left=False,
        )

        url = reverse('search')

        data = {"gr0-_-has_same_as-_-0": '2'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.email)
        self.assertContains(response, contact2.email)
        self.assertNotContains(response, contact3.email)


class SameEmailTest(BaseTestCase):
    """Search same-email"""

    def test_search_email_only_duplicate(self):
        """same as not allowed: search on entity group"""

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCDEFG", email=u"contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"EFGHIJK", email=u"contact1@email1.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"IJKLMNO", main_contact=True, has_left=False
        )
        contact3.entity.email = u'contact1@email1.fr'
        contact3.entity.default_contact.delete()
        contact3.entity.save()

        contact4 = mommy.make(
            models.Contact, lastname=u"MNOPQRS", email=u"contact4@email1.fr",  main_contact=True, has_left=False
        )
        contact4.entity.default_contact.delete()
        contact4.entity.save()

        group = mommy.make(models.Group, name=u"GROUP1")
        group.entities.add(contact1.entity)
        group.entities.add(contact2.entity)
        group.entities.add(contact3.entity)
        group.entities.add(contact4.entity)
        group.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_email-_-1": '1'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        in_response_count = 0
        for contact in (contact1, contact2, contact3):
            try:
                self.assertContains(response, contact.lastname)
                in_response_count += 1
            # pylint: disable=broad-except
            except Exception:
                pass

        self.assertEqual(2, in_response_count)  # 2 contacts on 3 are found
        self.assertNotContains(response, contact4.lastname)

    def test_search_email_exclude_duplicate(self):
        """same email allowed: search on entity group"""

        contact1 = mommy.make(
            models.Contact, lastname=u"ABCDEFG123456#", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()

        contact2 = mommy.make(
            models.Contact, lastname=u"EFGHIJK456789?", email="contact1@email1.fr", main_contact=True, has_left=False
        )
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()

        contact3 = mommy.make(
            models.Contact, lastname=u"IJKLMNO789012$", main_contact=True, has_left=False
        )
        contact3.entity.email = 'contact1@email1.fr'
        contact3.entity.default_contact.delete()
        contact3.entity.save()

        contact4 = mommy.make(
            models.Contact, lastname=u"MNOPQRS135791@", email="contact4@email1.fr",  main_contact=True, has_left=False
        )
        contact4.entity.default_contact.delete()
        contact4.entity.save()

        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(contact1.entity)
        group.entities.add(contact2.entity)
        group.entities.add(contact3.entity)
        group.entities.add(contact4.entity)
        group.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_email-_-1": '0'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        in_response_count = 0
        for contact in (contact1, contact2, contact3):
            try:
                self.assertContains(response, contact.lastname)
                in_response_count += 1
            # pylint: disable=broad-except
            except Exception:
                pass

        self.assertEqual(1, in_response_count)  # 2 contacts on 3 are found
        self.assertContains(response, contact4.lastname)
