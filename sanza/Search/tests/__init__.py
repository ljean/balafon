# -*- coding: utf-8 -*-
"""search test package"""

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.contrib.auth.models import User
from django.test import TestCase


class BaseTestCase(TestCase):
    """Base class for search tests"""

    def setUp(self):
        """before"""
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
