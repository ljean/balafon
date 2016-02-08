# -*- coding: utf-8 -*-
"""search test package"""

from django.contrib.auth.models import User
from django.test import TestCase

from coop_cms.utils import RequestManager


class BaseTestCase(TestCase):
    """Base class for search tests"""

    def setUp(self):
        """before"""
        RequestManager().clean()
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.is_staff = True
        self.user.save()
        self._login()

    def _login(self):
        """login"""
        is_logged = self.client.login(username="toto", password="abc")
        if not is_logged:
            raise Exception("login failed")
