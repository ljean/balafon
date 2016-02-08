# -*- coding: utf-8 -*-
"""test quick search"""

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models

from balafon.Search.tests import BaseTestCase


class QuickSearchTest(BaseTestCase):
    """Quick search"""

    def test_quick_search_city_start(self):
        """quick search on city: start with text"""
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        url = reverse("quick_search")
        data = {"text": "Zoo"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, city1.name)
        self.assertNotContains(response, city2.name)

    def test_quick_search_city_contains_1(self):
        """quick search on city: contains text only 1"""
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        url = reverse("quick_search")
        data = {"text": "oo"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, city1.name)
        self.assertNotContains(response, city2.name)

    def test_quick_search_city_contains_2(self):
        """quick search on city: contains text all"""
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")

        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()

        entity3 = mommy.make(models.Entity)
        contact3 = entity3.default_contact
        contact3.lastname = "IJKL"
        contact3.main_contact = True
        contact3.has_left = False
        contact3.city = city2
        contact3.save()

        url = reverse("quick_search")
        data = {"text": "oo"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, city1.name)
        self.assertContains(response, city2.name)

    def test_contact_by_name(self):
        """quick search by name"""
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Benjamin", lastname="Doe")
        star_wars_company = mommy.make(models.Entity)
        luke = mommy.make(models.Contact, firstname="Luuukeeee", lastname="Skywalker", entity=star_wars_company)

        url = reverse('quick_search')

        data = {"text": u"Skywalker"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, anakin.firstname)
        self.assertNotContains(response, obi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)

    def test_quick_search_anonymous(self):
        """quick search without login in"""

        mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")

        url = reverse('quick_search')

        data = {"text": u"Skywalker"}

        self.client.logout()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

    def test_quick_search_non_staff(self):
        """quick search without being staff member"""

        mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")

        url = reverse('quick_search')

        data = {"text": u"Skywalker"}

        self.user.is_staff = False
        self.user.save()

        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

    def test_has_left_contact_by_name(self):
        """quick search by name for contact who left"""
        start_wars_company = mommy.make(models.Entity)
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=start_wars_company)
        anakin = mommy.make(
            models.Contact, firstname="Anakin", lastname="Skywalker", entity=start_wars_company, has_left=True
        )

        url = reverse('quick_search')

        data = {"text": u"Skywalker"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, anakin.firstname)
        self.assertContains(response, luke.firstname)

    def test_has_left_contact_by_entity_name(self):
        """quick search by company name with contacts who left"""
        star_wars_company = mommy.make(models.Entity, name="Star-Wars", is_single_contact=False)
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=star_wars_company)
        anakin = mommy.make(
            models.Contact, firstname="Anakin", lastname="Skywalker", entity=star_wars_company, has_left=True
        )
        leia = mommy.make(models.Contact, firstname="Leia", lastname="Skywalker", entity=star_wars_company)
        shmi = mommy.make(
            models.Contact, firstname="Shmi", lastname="Skywalker", entity=star_wars_company, main_contact=False
        )

        url = reverse('quick_search')

        data = {"text": u"Star-Wars"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, anakin.firstname)
        self.assertNotContains(response, shmi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertContains(response, leia.firstname)

    def test_contact_by_entity_name(self):
        """quick search by entity name"""
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        star_wars_company = mommy.make(models.Entity, name="Starwars")
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=star_wars_company)
        star_trek_company = mommy.make(models.Entity, name="StarTrek")
        piccard = mommy.make(models.Contact, firstname="Jean-Luc", lastname="Piccard", entity=star_trek_company)
        dark_side_company = mommy.make(models.Entity, name="DarkSide")
        palpatine = mommy.make(models.Contact, firstname="Senateur", lastname="Palpatine", entity=dark_side_company)

        url = reverse('quick_search')

        data = {"text": u"Star"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, piccard.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)
        self.assertNotContains(response, palpatine.firstname)

    def test_contact_by_phone(self):
        """quick search by phone"""
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", phone="04.99.99.99.99")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi", mobile="04.99.00.00.00")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", phone="03.33.33.33.33")
        star_wars_company = mommy.make(models.Entity, phone="04.99.11.22.33")
        mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=star_wars_company)

        url = reverse('quick_search')

        data = {"text": u"04.99"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, anakin.phone)
        self.assertContains(response, obi.mobile)
        self.assertContains(response, star_wars_company.phone)
        self.assertNotContains(response, doe.phone)

        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, star_wars_company.name)
        self.assertNotContains(response, doe.firstname)

    def test_contact_by_phone_has_left(self):
        """quick search by phone with contacts who left"""
        anakin = mommy.make(
            models.Contact, firstname="Anakin", lastname="Skywalker", phone="04.99.99.99.99", has_left=True
        )
        obi = mommy.make(
            models.Contact, firstname="Obi-Wan", lastname="Kenobi", mobile="04.99.00.00.00", has_left=True
        )
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", phone="03.33.33.33.33")
        star_wars_company = mommy.make(models.Entity, phone="04.99.11.22.33")
        mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=star_wars_company, has_left=True)

        url = reverse('quick_search')

        data = {"text": u"04.99"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, anakin.phone)
        self.assertContains(response, obi.mobile)
        self.assertContains(response, star_wars_company.phone)
        self.assertNotContains(response, doe.phone)

        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, star_wars_company.name)
        self.assertNotContains(response, doe.firstname)

    def test_contact_by_email(self):
        """quick search by email"""
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", email="anakin@starwars.com")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi", email="obiwan@starwars.com")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", email="john.doe@toto.fr")
        star_wars_company = mommy.make(models.Entity, email="contact@starwars.com")
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=star_wars_company)
        sidious = mommy.make(
            models.Contact, firstname="Dark", lastname="Sidious", entity=star_wars_company, email="sidious@darkside.com"
        )

        url = reverse('quick_search')

        data = {"text": u"@starwars.com"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, anakin.email)
        self.assertContains(response, obi.email)
        self.assertContains(response, star_wars_company.email)
        self.assertNotContains(response, doe.email)
        self.assertNotContains(response, sidious.email)

        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)
        self.assertNotContains(response, sidious.firstname)

    def test_contact_by_email_has_left(self):
        """quick search by contacts who left"""
        anakin = mommy.make(
            models.Contact, firstname="Anakin", lastname="Skywalker", email="anakin@starwars.com", has_left=True
        )
        obi = mommy.make(
            models.Contact, firstname="Obi-Wan", lastname="Kenobi", email="obiwan@starwars.com", has_left=True
        )
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", email="john.doe@toto.fr")
        star_wars_company = mommy.make(models.Entity, email="contact@starwars.com")
        luke = mommy.make(
            models.Contact, firstname="Luke", lastname="Skywalker", entity=star_wars_company, has_left=True
        )
        sidious = mommy.make(
            models.Contact, firstname="Dark", lastname="Sidious", entity=star_wars_company, email="sidious@darkside.com"
        )

        url = reverse('quick_search')

        data = {"text": u"@starwars.com"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, anakin.email)
        self.assertContains(response, obi.email)
        self.assertContains(response, star_wars_company.email)
        self.assertNotContains(response, doe.email)
        self.assertNotContains(response, sidious.email)

        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)
        self.assertNotContains(response, sidious.firstname)

    def test_contact_by_email_no_at(self):
        """quick search by email: no @ in text"""
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", email="anakin@starwars.com")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi", email="obiwan@starwars.com")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", email="john.doe@toto.fr")
        star_wars_company = mommy.make(models.Entity, email="contact@starwars.com")
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=star_wars_company)
        sidious = mommy.make(
            models.Contact, firstname="Dark", lastname="Sidious", entity=star_wars_company, email="sidious@darkside.com"
        )

        url = reverse('quick_search')

        data = {"text": u"starwars.com"}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, anakin.email)
        self.assertContains(response, obi.email)
        self.assertContains(response, star_wars_company.email)
        self.assertNotContains(response, doe.email)
        self.assertNotContains(response, sidious.email)

        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)
        self.assertNotContains(response, sidious.firstname)
