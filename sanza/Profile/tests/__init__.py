# -*- coding: utf-8 -*-

import logging
import os.path

from django.contrib.auth.models import User
from django.test import TestCase

from coop_cms.utils import RequestManager


class BaseTestCase(TestCase):
    """Base class for test cases"""

    def setUp(self):
        logging.disable(logging.CRITICAL)
        RequestManager().clean()
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