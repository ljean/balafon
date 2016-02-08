# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User

from coop_cms.utils import RequestManager


class BaseTestCase(TestCase):

    def setUp(self):
        RequestManager().clean()
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.is_staff = True
        self.user.save()
        self._login()

    def _login(self):
        return self.client.login(username="toto", password="abc")