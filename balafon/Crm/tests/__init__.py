# -*- coding: utf-8 -*-
"""unit testing"""

import logging
import os.path
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from coop_cms.utils import RequestManager


default_media_root = settings.MEDIA_ROOT


@override_settings(MEDIA_ROOT=os.path.join(default_media_root, '_unit_tests'))
class BaseTestCase(TestCase):
    """Base class for tests"""

    def _clean_files(self):
        if default_media_root != settings.MEDIA_ROOT:
            try:
                shutil.rmtree(settings.MEDIA_ROOT)
            except OSError:
                pass
        else:
            raise Exception("Warning! wrong media root for unittesting")

    def setUp(self):
        """before each test"""
        RequestManager().clean()
        logging.disable(logging.CRITICAL)
        self._clean_files()

        self.user = User.objects.create(username="toto", is_staff=True)
        self.user.set_password("abc")
        self.user.save()
        self._login()

    def tearDown(self):
        """after each test"""
        logging.disable(logging.NOTSET)
        self._clean_files()

    def _login(self):
        """login"""
        self.client.login(username="toto", password="abc")
