# -*- coding: utf-8 -*-

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

import logging
import os.path

from django.contrib.auth.models import User
from django.test import TestCase


class BaseTestCase(TestCase):
    """Base class for test cases"""

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.save()
        self._login()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def _get_file(self, file_name='unittest1.txt'):
        full_name = os.path.normpath(os.path.dirname(__file__) + '/fixtures/' + file_name)
        return open(full_name, 'rb')

    def _login(self):
        self.client.login(username="toto", password="abc")