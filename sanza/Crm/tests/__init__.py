# -*- coding: utf-8 -*-
"""unit testing"""
from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

import logging

from django.test import TestCase
from django.contrib.auth.models import User


class BaseTestCase(TestCase):
    """Base class for tests"""

    def setUp(self):
        """before each test"""
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="toto", is_staff=True)
        self.user.set_password("abc")
        self.user.save()
        self._login()

    def tearDown(self):
        """after each test"""
        logging.disable(logging.NOTSET)

    def _login(self):
        """login"""
        self.client.login(username="toto", password="abc")
