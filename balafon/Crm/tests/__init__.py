# -*- coding: utf-8 -*-
"""unit testing"""

from __future__ import unicode_literals

from django.contrib.auth.models import User

from balafon.unit_tests import TestCase


class BaseTestCase(TestCase):
    """Base class for tests"""

    def setUp(self):
        """before each test"""
        super(BaseTestCase, self).setUp()

        self.user = User.objects.create(username="toto", is_staff=True)
        self.user.set_password("abc")
        self.user.save()
        self._login()

    def _login(self):
        """login"""
        self.client.login(username="toto", password="abc")
