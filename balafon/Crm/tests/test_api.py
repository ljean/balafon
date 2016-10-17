# -*- coding: utf-8 -*-
"""unit testing"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse

from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from balafon.Crm import models


class AboutMeTest(APITestCase):
    """It should return actions"""

    def setUp(self):
        self.client = APIClient()

    def test_get_about_me_staff(self):
        """It should return info about user"""
        user = mommy.make(User, username='joe', is_active=True, is_staff=True)
        user.set_password('pass')
        user.save()

        self.client.login(username=user.username, password='pass')

        url = reverse('crm_api_about_me')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertEqual(user.last_name, response.data[0]['last_name'])
        self.assertEqual(user.first_name, response.data[0]['first_name'])
        self.assertEqual(None, response.data[0].get('password'))

    def test_get_about_me_team_member(self):
        """It should return info about user"""
        user = mommy.make(User, username='joe', is_active=True, is_staff=False)
        user.set_password('pass')
        user.save()

        mommy.make(models.TeamMember, user=user)

        self.client.login(username=user.username, password='pass')

        url = reverse('crm_api_about_me')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertEqual(user.last_name, response.data[0]['last_name'])
        self.assertEqual(user.first_name, response.data[0]['first_name'])
        self.assertEqual(None, response.data[0].get('password'))

    def test_get_about_me_anynone(self):
        """It should return info about user"""
        user = mommy.make(User, username='joe', is_active=True, is_staff=False)
        user.set_password('pass')
        user.save()

        self.client.login(username=user.username, password='pass')

        url = reverse('crm_api_about_me')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertEqual(user.last_name, response.data[0]['last_name'])
        self.assertEqual(user.first_name, response.data[0]['first_name'])
        self.assertEqual(None, response.data[0].get('password'))

    def test_get_about_me_anonymous(self):
        """It should return error"""
        url = reverse('crm_api_about_me')

        response = self.client.get(url, format='json')
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_get_about_me_inactive(self):
        """It should return info about user"""
        user = mommy.make(User, username='joe', is_active=True, is_staff=False)
        user.set_password('pass')
        user.save()

        self.client.login(username=user.username, password='pass')

        user.is_active = False
        user.save()

        url = reverse('crm_api_about_me')

        response = self.client.get(url, format='json')
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


class ContactOrEntityTest(APITestCase):
    """test search contacts or entities"""

    def _login(self):
        user = mommy.make(User, username='joe', is_active=True, is_staff=True)
        user.set_password('pass')
        user.save()

        self.client.login(username=user.username, password='pass')

        return user

    def test_api_not_logged(self):
        """can't access"""
        url = reverse('crm_api_contacts_or_entities') + "?name=A"
        response = self.client.get(url)
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_api_not_admin(self):
        """can't access"""
        user = self._login()
        user.is_staff = False
        user.save()
        url = reverse('crm_api_contacts_or_entities') + "?name=A"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_empty(self):
        """returns empty list"""
        self._login()
        url = reverse('crm_api_contacts_or_entities') + "?name=A"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_api_both(self):
        """returns list of contacts and entities"""

        contact_type = ContentType.objects.get_for_model(models.Contact)
        entity_type = ContentType.objects.get_for_model(models.Entity)

        entity1 = mommy.make(models.Entity, name='Alpha', is_single_contact=False)
        entity2 = mommy.make(models.Entity, name='Beta', is_single_contact=False)

        entity3 = mommy.make(models.Entity, name='ALLARD', is_single_contact=True)
        contact1 = mommy.make(models.Contact, lastname='Allard', entity=entity3)

        entity4 = mommy.make(models.Entity, name='Zardo', is_single_contact=False)
        contact2 = mommy.make(models.Contact, lastname='Bernard')

        self._login()

        url = reverse('crm_api_contacts_or_entities') + "?name=A"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {'id': contact1.id, 'name': u'Allard', 'type': contact_type.id, 'city': u''},
            {'id': entity1.id, 'name': u'Alpha', 'type': entity_type.id, 'city': u''},
        ])

    def test_api_cities(self):
        """returns list of contacts and entities"""

        contact_type = ContentType.objects.get_for_model(models.Contact)
        entity_type = ContentType.objects.get_for_model(models.Entity)

        default_country = mommy.make(models.Zone, name=settings.BALAFON_DEFAULT_COUNTRY, parent=None)
        foreign_country = mommy.make(models.Zone, name="BB", parent=None)
        parent = mommy.make(models.Zone, name="AA", code="42", parent=default_country)

        city1 = mommy.make(models.City, name="abcd", parent=parent)
        city2 = mommy.make(models.City, name="efgh", parent=parent)
        city3 = mommy.make(models.City, name="ijkl", parent=foreign_country)

        entity1 = mommy.make(models.Entity, name='Alpha', is_single_contact=False, city=city1)

        entity2 = mommy.make(models.Entity, name='ENTITY2', is_single_contact=False, city=city2)
        contact2 = mommy.make(models.Contact, lastname='Allard', entity=entity2)

        entity3 = mommy.make(models.Entity, name='ENTITY3', is_single_contact=False, city=city2)
        contact3 = mommy.make(models.Contact, lastname='Azerty', entity=entity3, city=city3)

        self._login()

        url = reverse('crm_api_contacts_or_entities') + "?name=A"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {'id': contact2.id,'name': u'Allard', 'type': contact_type.id, 'city': city2.get_friendly_name()},
            {'id': entity1.id, 'name': u'Alpha', 'type': entity_type.id, 'city': city1.get_friendly_name()},
            {'id': contact3.id, 'name': u'Azerty', 'type': contact_type.id, 'city': city3.get_friendly_name()},
        ])

    def test_api_limit(self):
        """returns list of contacts and entities"""
        for i in range(20):
            mommy.make(models.Entity, name='Alpha', is_single_contact=False)
            mommy.make(models.Entity, name='Beta', is_single_contact=False)

        entity = mommy.make(models.Entity, name='ZZ', is_single_contact=True)
        for i in range(20):
            mommy.make(models.Contact, lastname='Allard', entity=entity)
            mommy.make(models.Contact, lastname='Bernard', entity=entity)

        self._login()

        url = reverse('crm_api_contacts_or_entities') + "?name=A"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        for elt in response.data:
            self.assertEqual(elt['name'][0], 'A')
