# -*- coding: utf-8 -*-
"""unit testing"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches

from django.contrib.auth.models import User
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
