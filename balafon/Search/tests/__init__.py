# -*- coding: utf-8 -*-
"""search test package"""

from __future__ import unicode_literals

from django.contrib.auth.models import User

from coop_cms.utils import RequestManager

from balafon.unit_tests import TestCase


class BaseTestCase(TestCase):
    """Base class for search tests"""

    def setUp(self):
        """before"""
        super(BaseTestCase, self).setUp()
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
