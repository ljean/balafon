# -*- coding: utf-8 -*-
"""unit testing"""

from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.unit_tests import response_as_json
from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


class CitiesSuggestListTestCase(BaseTestCase):

    def setUp(self):
        super(CitiesSuggestListTestCase, self).setUp()
        self.default_country = mommy.make(models.Zone, name=settings.BALAFON_DEFAULT_COUNTRY, parent=None)
        self.foreign_country = mommy.make(models.Zone, name="BB", parent=None)
        self.parent = mommy.make(models.Zone, name="AA", code="42", parent=self.default_country)

    def test_cities_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('crm_get_cities')+'?term=c')
        self.assertEqual(200, response.status_code)

    def test_get_city_id(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        city2 = mommy.make(models.City, name="abce", parent=self.parent)
        city_in_other_country = mommy.make(models.City, name="abcd", parent=self.foreign_country)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+city.name+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, city.id)
        self.assertNotContains(response, city2.id)

    def test_get_city_id_case_insensitive(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        city2 = mommy.make(models.City, name="abce", parent=self.parent)
        city_in_other_country = mommy.make(models.City, name="abcd", parent=self.foreign_country)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+"ABCD"+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, city.id)
        self.assertNotContains(response, city2.id)

    def test_get_city_id_unicode(self):
        response = self.client.get("{0}?name=Mérignac".format(reverse('crm_get_city_id')))
        self.assertEqual(200, response.status_code)
        data = response_as_json(response)
        self.assertEqual(data["id"], "Mérignac")

    def test_get_city_id_case_insensitive_twice(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        city2 = mommy.make(models.City, name="ABCD", parent=self.parent)
        city_in_other_country = mommy.make(models.City, name="abcd", parent=self.foreign_country)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+"ABCD"+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "ABCD")

    def test_get_city_id_same_name(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        parent2 = mommy.make(models.Zone, name="AB", code="43", parent=self.default_country)
        city2 = mommy.make(models.City, name=city.name, parent=parent2)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+city.name+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, city.name)
        self.assertNotContains(response, city.id)
        self.assertNotContains(response, city2.id)

    def test_get_foreign_city(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        city2 = mommy.make(models.City, name="abce", parent=self.parent)
        city_in_other_country = mommy.make(models.City, name="abcd", parent=self.foreign_country)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+city.name+"&country="+str(self.foreign_country.id))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, city_in_other_country.id)
        self.assertNotContains(response, city.id)
        self.assertNotContains(response, city2.id)

    def test_get_city_unknown(self):
        name = "abcd"
        response = self.client.get(reverse('crm_get_city_id')+"?name="+name+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, name)

    def test_city_in_default_country(self):
        c1 = mommy.make(models.City, name="ABC", parent=self.parent)
        c2 = mommy.make(models.City, name="ABD", parent=self.parent)
        c3 = mommy.make(models.City, name="XYZ", parent=self.parent)
        c4 = mommy.make(models.City, name="ABE", parent=self.foreign_country)

        response = self.client.get(reverse('crm_get_cities')+'?term=a&country=0')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, c1.name)
        self.assertContains(response, c2.name)
        self.assertNotContains(response, c3.name)
        self.assertNotContains(response, c4.name)

    def test_city_in_foreign_country(self):
        c1 = mommy.make(models.City, name="ABC", parent=self.parent)
        c2 = mommy.make(models.City, name="ABD", parent=self.parent)
        c3 = mommy.make(models.City, name="XYZ", parent=self.parent)
        c4 = mommy.make(models.City, name="ABE", parent=self.foreign_country)

        response = self.client.get(reverse('crm_get_cities')+'?term=a&country={0}'.format(
            self.foreign_country.id))
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, c1.name)
        self.assertNotContains(response, c2.name)
        self.assertNotContains(response, c3.name)
        self.assertContains(response, c4.name)
