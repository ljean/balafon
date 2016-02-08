# -*- coding: utf-8 -*-
"""test we can search contact by zones"""

from bs4 import BeautifulSoup as BeautifulSoup4
from unittest import skipIf

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm import settings as crm_settings
from balafon.Crm.utils import get_default_country

from balafon.Search.tests import BaseTestCase


class ZoneSearchTest(BaseTestCase):
    """Search by zone city, area, country ..."""

    def test_view_search(self):
        """view search form"""
        city1 = mommy.make(models.City)
        city2 = mommy.make(models.City)

        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        entity2 = mommy.make(models.Entity)
        contact2 = entity2.default_contact
        contact2.lastname = "EFGH"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.city = city1
        contact2.save()

        entity3 = mommy.make(models.Entity)
        contact3 = entity3.default_contact
        contact3.lastname = "IJKL"
        contact3.main_contact = True
        contact3.has_left = False
        contact3.city = city2
        contact3.save()

        entity4 = mommy.make(models.Entity)
        contact4 = entity4.default_contact
        contact4.lastname = "MNOP"
        contact4.main_contact = True
        contact4.has_left = False
        contact4.save()

        url = reverse("search_cities", args=[city1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact4.lastname)

    def test_search_zipcode(self):
        """search zipcode"""
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.city = city1
        contact1.zip_code = "42810"
        contact1.save()

        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity)
        contact2 = entity2.default_contact
        contact2.lastname = "DEFG"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.city = city2
        contact2.zip_code = "26100"
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-zip_code-_-0": "42"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_zipcode_entity(self):
        """search zipcode of entity"""
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity, city=city1, zip_code="42810")
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        contact3 = mommy.make(
            models.Contact, entity=entity1, lastname=u"IJKL",
            main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity, city=city2, zip_code="26100")
        contact2 = entity2.default_contact
        contact2.lastname = "DEFG"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-zip_code-_-0": "42"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_zipcode_entity_contact_mix(self):
        """zipcode entity and contact"""
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity, city=city1, zip_code="42810")
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        contact3 = mommy.make(
            models.Contact, city=None, entity=entity1, lastname=u"IJKL",
            main_contact=True, has_left=False
        )
        contact4 = mommy.make(
            models.Contact, city=city2, zip_code="26100", entity=entity1,
            lastname=u"MNOP", main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity)
        contact2 = entity2.default_contact
        contact2.lastname = "DEFG"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.city = city2
        contact2.zip_code = "26100"
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-zip_code-_-0": "42"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_entity_zipcode(self):
        """another zipcode search"""
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity, city=city1, zip_code="42810")
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        contact3 = mommy.make(
            models.Contact, city=None, entity=entity1, lastname=u"IJKL",
            main_contact=True, has_left=False
        )
        contact4 = mommy.make(
            models.Contact, city=city2, zip_code="26100", entity=entity1,
            lastname=u"MNOP", main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity, city=city2, zip_code="26100")
        contact2 = entity2.default_contact
        contact2.lastname = "DEFG"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.save()

        url = reverse('search')

        data = {"gr0-_-entity_zip_code-_-0": "42"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertContains(response, contact4.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_city(self, cities=None, data=None):
        """search by city"""
        if cities:
            city1 = cities[0]
            city2 = cities[1]
        else:
            city1 = mommy.make(models.City, name="ZooPark")
            city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.city = city1
        contact1.save()

        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity)
        contact2 = entity2.default_contact
        contact2.lastname = "DEFG"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.city = city2
        contact2.save()

        url = reverse('search')

        data = data or {"gr0-_-city-_-0": city1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_city_entity(self, cities=None, data=None):
        """search by city of the entity"""
        if cities:
            city1 = cities[0]
            city2 = cities[1]
        else:
            city1 = mommy.make(models.City, name="ZooPark")
            city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, city=city2)
        contact2 = entity2.default_contact
        contact2.lastname = "DEFG"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.save()

        url = reverse('search')

        data = data or {"gr0-_-city-_-0": city1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def test_search_city_entity_contact_mix(self, cities=None, data=None):
        """search by city for entity and contact"""
        if cities:
            city1 = cities[0]
            city2 = cities[1]
        else:
            city1 = mommy.make(models.City, name="ZooPark")
            city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        contact3 = mommy.make(
            models.Contact, city=None, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False
        )
        contact4 = mommy.make(
            models.Contact, city=city2, entity=entity1, lastname=u"MNOP", main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity)
        contact2 = entity2.default_contact
        contact2.lastname = "DEFG"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.city = city2
        contact2.save()

        url = reverse('search')

        data = data or {"gr0-_-city-_-0": city1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact4.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def _test_search_multi_zones(self, cities=None, data=None, entity_search=False):
        """search by zone"""
        city1 = cities[0]
        city2 = cities[1]
        city3 = mommy.make(models.City, name="BlablaPark")

        entity1 = mommy.make(models.Entity, city=city1 if entity_search else None)
        contact1a = entity1.default_contact
        contact1a.lastname = "ABCD"
        contact1a.main_contact = True
        contact1a.has_left = False
        contact1a.city = city1
        contact1a.save()

        contact1b = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, city=city2 if entity_search else None)
        contact2 = entity2.default_contact
        contact2.lastname = "DEFG"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.city = None if entity_search else city2
        contact2.save()

        entity3 = mommy.make(models.Entity)
        contact3 = entity3.default_contact
        contact3.lastname = "MNOP"
        contact3.main_contact = True
        contact3.has_left = False
        contact3.city = city3
        contact3.save()

        url = reverse('search')

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual([], soup.select('.field-error'))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1a.lastname)
        if entity_search:
            self.assertContains(response, contact1b.lastname)
        else:
            self.assertNotContains(response, contact1b.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact3.lastname)

    def test_search_entity_city(self, cities=None, data=None):
        """another city serach for entity"""
        if cities:
            city1 = cities[0]
            city2 = cities[1]
        else:
            city1 = mommy.make(models.City, name="ZooPark")
            city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        contact3 = mommy.make(
            models.Contact, city=None, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False
        )
        contact4 = mommy.make(
            models.Contact, city=city2, entity=entity1, lastname=u"MNOP", main_contact=True, has_left=False
        )

        entity2 = mommy.make(models.Entity, city=city2)
        contact2 = entity2.default_contact
        contact2.lastname = "DEFG"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.save()

        url = reverse('search')

        data = data or {"gr0-_-entity_city-_-0": city1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertContains(response, contact4.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

    def _get_departements_data(self, form_name="department"):
        """get departemenst"""
        default_country = get_default_country()
        region_type = mommy.make(models.ZoneType, type="region")
        region = mommy.make(models.Zone, parent=default_country, type=region_type)
        departement_type = mommy.make(models.ZoneType, type="department")
        departement1 = mommy.make(models.Zone, parent=region, type=departement_type)
        departement2 = mommy.make(models.Zone, parent=region, type=departement_type)

        city1 = mommy.make(models.City, name="ZooPark", parent=departement1)
        city2 = mommy.make(models.City, name="VodooPark", parent=departement2)

        data = {"gr0-_-{0}-_-0".format(form_name): departement1.id}

        return (city1, city2), data

    def test_search_multi_departements(self):
        """search by several departements"""
        cities, data = self._get_departements_data()
        city1 = cities[0]
        city2 = cities[1]
        data = {"gr0-_-department-_-0": [city1.parent.id, city2.parent.id]}
        self._test_search_multi_zones(cities, data)

    def test_search_multi_departements_entity(self):
        """search by several entity departements"""
        cities, data = self._get_departements_data()
        city1 = cities[0]
        city2 = cities[1]
        data = {"gr0-_-entity_department-_-0": [city1.parent.id, city2.parent.id]}
        self._test_search_multi_zones(cities, data, True)

    def test_search_departement(self):
        """search by departement"""
        self.test_search_city(*self._get_departements_data())

    def test_search_departement_entity(self):
        """search by entity departements"""
        self.test_search_city_entity(*self._get_departements_data())

    def test_search_departement_entity_contact(self):
        """search by departements of contacts and entities"""
        self.test_search_city_entity_contact_mix(*self._get_departements_data())

    def test_search_entity_departement(self):
        """search by entity departements"""
        self.test_search_entity_city(*self._get_departements_data("entity_department"))

    def _get_regions_data(self, form_name="region"):
        """get region data"""
        default_country = get_default_country()
        region_type = mommy.make(models.ZoneType, type="region")
        region1 = mommy.make(models.Zone, parent=default_country, type=region_type)
        region2 = mommy.make(models.Zone, parent=default_country, type=region_type)
        departement_type = mommy.make(models.ZoneType, type="department")
        departement1 = mommy.make(models.Zone, parent=region1, type=departement_type)
        departement2 = mommy.make(models.Zone, parent=region2, type=departement_type)

        city1 = mommy.make(models.City, name="ZooPark", parent=departement1)
        city2 = mommy.make(models.City, name="VodooPark", parent=departement2)

        data = {"gr0-_-{0}-_-0".format(form_name): region1.id}

        return (city1, city2), data

    def test_search_region(self):
        """search by region"""
        self.test_search_city(*self._get_regions_data())

    def test_search_multi_regions(self):
        """search by several regions"""
        cities, data = self._get_regions_data()
        city1 = cities[0]
        city2 = cities[1]
        data = {"gr0-_-region-_-0": [city1.parent.parent.id, city2.parent.parent.id]}
        self._test_search_multi_zones(cities, data)

    def test_search_region_entity(self):
        """search by region entity"""
        self.test_search_city_entity(*self._get_regions_data())

    def test_search_region_entity_contact_mix(self):
        """search by region contacts and entities"""
        self.test_search_city_entity_contact_mix(*self._get_regions_data())

    def test_search_entity_region(self):
        """search by entity region"""
        self.test_search_entity_city(*self._get_regions_data("entity_region"))

    def _get_countries_data(self, form_name="country"):
        """get countries data"""
        country_type = mommy.make(models.ZoneType, type="country")
        country1 = mommy.make(models.Zone, type=country_type)
        country2 = mommy.make(models.Zone, type=country_type)

        city1 = mommy.make(models.City, name="ZooPark", parent=country1)
        city2 = mommy.make(models.City, name="VodooPark", parent=country2)

        data = {"gr0-_-{0}-_-0".format(form_name): country1.id}

        return (city1, city2), data

    def test_search_country(self):
        """search by country"""
        self.test_search_city(*self._get_countries_data())

    def test_search_country_entity(self):
        """search by country entity"""
        self.test_search_city_entity(*self._get_countries_data())

    def test_search_multi_country(self):
        """search by several countries"""
        cities, data = self._get_countries_data()
        city1 = cities[0]
        city2 = cities[1]
        data = {"gr0-_-country-_-0": [city1.parent.id, city2.parent.id]}
        self._test_search_multi_zones(cities, data)

    def test_search_country_entity_contact_mix(self):
        """search by contact and entity country"""
        self.test_search_city_entity_contact_mix(*self._get_countries_data())

    def test_search_entity_country(self):
        """search by entity country"""
        self.test_search_entity_city(*self._get_countries_data("entity_country"))

    def _get_countries_mix_data(self, form_name="country"):
        """get date with full hierarchy"""
        country_type = mommy.make(models.ZoneType, type="country")
        country1 = default_country = get_default_country()
        country2 = mommy.make(models.Zone, type=country_type, parent=None)
        region_type = mommy.make(models.ZoneType, type="region")
        region1 = mommy.make(models.Zone, parent=default_country, type=region_type)
        departement_type = mommy.make(models.ZoneType, type="department")
        departement1 = mommy.make(models.Zone, parent=region1, type=departement_type)

        city1 = mommy.make(models.City, name="ZooPark", parent=departement1)
        city2 = mommy.make(models.City, name="VodooPark", parent=country2)

        data = {"gr0-_-{0}-_-0".format(form_name): country1.id}

        return (city1, city2), data

    def test_search_country2(self):
        """search by country full hierarchy"""
        self.test_search_city(*self._get_countries_mix_data())

    def test_search_country_entity2(self):
        """search by entity country full hierarchy"""
        self.test_search_city_entity(*self._get_countries_mix_data())

    def test_search_country_entity_contact_mi2x(self):
        """search by entity and contact country full hierarchy"""
        self.test_search_city_entity_contact_mix(*self._get_countries_mix_data())

    def test_search_entity_country2(self):
        """again search by entity country full hierarchy"""
        self.test_search_entity_city(*self._get_countries_mix_data("entity_country"))

    def _get_zonegroup_data(self, form_name="zone_group"):
        """get zonegroup data"""
        default_country = get_default_country()

        region_type = mommy.make(models.ZoneType, type="region")
        region1 = mommy.make(models.Zone, parent=default_country, type=region_type)
        region2 = mommy.make(models.Zone, parent=default_country, type=region_type)
        departement_type = mommy.make(models.ZoneType, type="department")
        departement1 = mommy.make(models.Zone, parent=region1, type=departement_type)
        departement2 = mommy.make(models.Zone, parent=region2, type=departement_type)

        city1 = mommy.make(models.City, name="ZooPark", parent=departement1)
        city2 = mommy.make(models.City, name="VodooPark", parent=departement2)

        zone_group_type = mommy.make(models.ZoneType, type="zone_group")
        zone_group = mommy.make(models.Zone, parent=None, type=zone_group_type)

        city1.groups.add(zone_group)
        city1.save()

        data = {"gr0-_-{0}-_-0".format(form_name): zone_group.id}

        return (city1, city2), data

    @skipIf(not crm_settings.ZONE_GROUP_SEARCH, "ZONE_GROUP_SEARCH disabled")
    def test_search_zonegroup(self):
        """search by contact zone group"""
        self.test_search_city(*self._get_zonegroup_data())

    @skipIf(not crm_settings.ZONE_GROUP_SEARCH, "ZONE_GROUP_SEARCH disabled")
    def test_search_zonegroup_entity(self):
        """search by entity zone group"""
        self.test_search_city_entity(*self._get_zonegroup_data())

    @skipIf(not crm_settings.ZONE_GROUP_SEARCH, "ZONE_GROUP_SEARCH disabled")
    def test_search_zonegroup_entity_contact_mix(self):
        """search by contact and entity zone group"""
        self.test_search_city_entity_contact_mix(*self._get_zonegroup_data())


class CitySearchTest(BaseTestCase):
    """Another city search test"""

    def test_search_city(self):
        """search by city"""
        city = mommy.make(models.City)
        entity1 = mommy.make(models.Entity, name=u"My tiny corp", city=city)
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", email="toto1@toto.fr")
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL")

        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", city=city)

        entity3 = mommy.make(models.Entity, name=u"The big Org", email="toto2@toto.fr")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC")

        url = reverse('search')

        data = {"gr0-_-city-_-0": city.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)


class AddressSearchTest(BaseTestCase):
    """search by address"""

    def test_search_address(self):
        """search by city"""
        city = mommy.make(models.City)
        entity1 = mommy.make(models.Entity, name=u"My tiny corp", city=city, address="rue Paul Mc Cartney")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", email="toto1@toto.fr")
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL")

        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(
            models.Contact, entity=entity2, lastname=u"WXYZ", city=city, address="rue Jean-Paul Belmondo"
        )

        entity3 = mommy.make(models.Entity, name=u"The big Org", email="toto2@toto.fr")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC")

        entity5 = mommy.make(models.Entity, is_single_contact=True)
        contact5 = entity5.default_contact
        contact5.lastname = "QWERTYUIOP"
        contact5.address = "lot appaulou"
        contact5.city = city
        contact5.save()

        url = reverse('search')

        data = {"gr0-_-address-_-0": 'Paul'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

        self.assertContains(response, contact5.lastname)