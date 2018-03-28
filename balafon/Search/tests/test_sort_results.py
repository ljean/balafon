# -*- coding: utf-8 -*-
"""test we can sort results"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm.utils import get_default_country
from balafon.Search.tests import BaseTestCase


class SortTest(BaseTestCase):
    """Sort results"""

    def _make_contact(self, lastname, firstname, entity=""):
        """make a contact"""
        contact1 = mommy.make(models.Contact, lastname=lastname, firstname=firstname, main_contact=True, has_left=False)
        contact1.entity.name = entity or "????"
        contact1.entity.is_single_contact = not bool(entity)
        contact1.entity.default_contact.delete()
        contact1.entity.save()
        return contact1

    def _contacts(self):
        """create contacts"""
        contact1 = self._make_contact('Martin', 'Georges', 'apple')
        contact2 = self._make_contact('Dupond', 'Pierre', 'Abcdef')
        contact3 = self._make_contact('Martin', 'Alain', 'Petitmo')
        contact4 = self._make_contact('Bernard', 'Jacques', '')
        contact5 = self._make_contact('Xylo', 'Henri', 'Balafon')
        contact6 = self._make_contact('Poulet', 'Andre', 'Maitre Coq')
        return contact1, contact2, contact3, contact4, contact5, contact6

    def _groups(self, *args):
        """create groups"""
        contact1, contact2, contact3, contact4, contact5, contact6 = args
        group1 = mommy.make(models.Group, name="GROUP1")
        for contact in (contact1, contact2, contact3,):
            group1.contacts.add(contact)
        group1.save()

        group2 = mommy.make(models.Group, name="GROUP2")
        for contact in (contact4, contact5, contact6,):
            group2.contacts.add(contact)
        group2.save()

        return group1, group2

    def _post_and_check(self, data, expected_order):
        """post and check"""
        url = reverse('search')
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        content = '{0}'.format(response.content.decode("iso-8859-15"))

        self.assertContains(response, "<!-- ut: contacts_display -->")

        for contact in expected_order:
            self.assertContains(response, contact.firstname)
        pos = [content.find(contact.firstname) for contact in expected_order]
        self.assertEqual(pos, sorted(pos))

    def test_sort_by_name(self):
        """sort by name"""
        contact1, contact2, contact3, contact4, contact5, contact6 = self._contacts()
        group1, group2 = self._groups(contact1, contact2, contact3, contact4, contact5, contact6)
        expected_order = (contact2, contact1, contact5, contact4, contact6, contact3)
        data = {
            "gr0-_-group-_-0": group1.id,
            "gr0-_-sort-_-1": 'name',
            "gr1-_-group-_-0": group2.id,
        }
        self._post_and_check(data, expected_order)

    def test_sort_by_entity(self):
        """sort by entity"""
        contact1, contact2, contact3, contact4, contact5, contact6 = self._contacts()
        group1, group2 = self._groups(contact1, contact2, contact3, contact4, contact5, contact6)
        expected_order = (contact2, contact1, contact5, contact6, contact3, contact4)
        data = {
            "gr0-_-group-_-0": group1.id,
            "gr0-_-sort-_-1": 'entity',
            "gr1-_-group-_-0": group2.id,
        }
        self._post_and_check(data, expected_order)

    def test_sort_by_contact(self):
        """sort by contact"""
        contact1, contact2, contact3, contact4, contact5, contact6 = self._contacts()
        group1, group2 = self._groups(contact1, contact2, contact3, contact4, contact5, contact6)
        expected_order = (contact4, contact2, contact3, contact1, contact6, contact5)
        data = {
            "gr0-_-group-_-0": group1.id,
            "gr0-_-sort-_-1": 'contact',
            "gr1-_-group-_-0": group2.id,
        }
        self._post_and_check(data, expected_order)

    def test_sort_by_zipcode(self):
        """sort by zipcode"""
        contact1, contact2, contact3, contact4, contact5, contact6 = self._contacts()
        group1, group2 = self._groups(contact1, contact2, contact3, contact4, contact5, contact6)

        contact1.zip_code = "42100"
        contact1.city = mommy.make(models.City, parent=get_default_country(), name="Ville1")
        contact1.save()

        contact2.entity.zip_code = "42100"
        contact2.entity.city = mommy.make(models.City, parent=get_default_country(), name="City2")
        contact2.entity.save()

        contact3.entity.zip_code = "42000"
        contact3.entity.city = contact2.entity.city
        contact3.entity.save()

        contact4.zip_code = ""
        contact4.city = mommy.make(
            models.City,
            parent=mommy.make(models.Zone, name="ABC", type=get_default_country().type),
            name="City3"
        )
        contact4.save()

        contact5.zip_code = "42000"
        contact5.city = contact2.entity.city
        contact5.save()

        contact6.zip_code = "42100"
        contact6.city = mommy.make(
            models.City,
            parent=mommy.make(models.Zone, name="DEF", type=get_default_country().type),
            name="Ville4"
        )
        contact6.save()

        expected_order = (contact5, contact3, contact2, contact1, contact4, contact6)
        data = {
            "gr0-_-group-_-0": group1.id,
            "gr0-_-sort-_-1": 'zipcode',
            "gr1-_-group-_-0": group2.id,
        }
        self._post_and_check(data, expected_order)

    def test_sort_by_zipcode2(self):
        """sort by zipcode again"""
        contact1, contact2, contact3, contact4, contact5, contact6 = self._contacts()
        group1, group2 = self._groups(contact1, contact2, contact3, contact4, contact5, contact6)

        country1 = get_default_country()
        country2 = mommy.make(models.Zone, name="ABC", type=country1.type)
        country3 = mommy.make(models.Zone, name="DEF", type=country1.type)

        contact1.zip_code = "42100"
        contact1.city = mommy.make(models.City, parent=country1, name="Ville1")
        contact1.save()

        contact3.entity.zip_code = "01000"
        contact3.entity.city = mommy.make(models.City, parent=country1, name="City2")
        contact3.entity.save()

        contact4.zip_code = ""
        contact4.city = mommy.make(models.City, parent=country2, name="City3")
        contact4.save()

        contact5.zip_code = "42000"
        contact5.city = contact1.city
        contact5.save()

        contact6.zip_code = "42100"
        contact6.city = mommy.make(models.City, parent=country3, name="Ville4")
        contact6.save()

        expected_order = (contact3, contact5, contact1, contact4, contact6, contact2)
        data = {
            "gr0-_-group-_-0": group1.id,
            "gr0-_-sort-_-1": 'zipcode',
            "gr1-_-group-_-0": group2.id,
        }
        self._post_and_check(data, expected_order)

    def test_sort_by_zipcode3(self):
        """sort by zipcode again and again"""
        contact1, contact2, contact3, contact4, contact5, contact6 = self._contacts()
        group1, group2 = self._groups(contact1, contact2, contact3, contact4, contact5, contact6)

        contact1.zip_code = "42100"
        contact1.city = mommy.make(models.City, parent=get_default_country(), name="Ville1")
        contact1.save()

        contact3.entity.zip_code = "01000"
        contact3.entity.city = mommy.make(models.City, parent=None, name="City2")
        contact3.entity.save()

        contact4.zip_code = ""
        contact4.city = mommy.make(
            models.City,
            parent=mommy.make(models.Zone, name="ABC", type=get_default_country().type),
            name="City3"
        )
        contact4.save()

        contact5.zip_code = "42000"
        contact5.city = contact1.city
        contact5.save()

        contact6.zip_code = "42100"
        contact6.city = mommy.make(
            models.City,
            parent=mommy.make(models.Zone, name="DEF", type=get_default_country().type),
            name="Ville4"
        )
        contact6.save()

        expected_order = (contact3, contact5, contact1, contact4, contact6, contact2)
        data = {
            "gr0-_-group-_-0": group1.id,
            "gr0-_-sort-_-1": 'zipcode',
            "gr1-_-group-_-0": group2.id,
        }
        self._post_and_check(data, expected_order)
