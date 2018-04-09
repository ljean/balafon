# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User

from balafon.unit_tests import TestCase


class BaseTestCase(TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.is_staff = True
        self.user.save()
        self._login()

    def _login(self):
        return self.client.login(username="toto", password="abc")