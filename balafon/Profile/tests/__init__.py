# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os.path

from django.contrib.auth.models import User

from balafon.unit_tests import TestCase


class BaseTestCase(TestCase):
    """Base class for test cases"""

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.save()
        self._login()

    def tearDown(self):
        super(BaseTestCase, self).tearDown()

    def _get_file(self, file_name='unittest1.txt'):
        full_name = os.path.normpath(os.path.dirname(__file__) + '/fixtures/' + file_name)
        return open(full_name, 'rb')

    def _login(self):
        self.client.login(username="toto", password="abc")
