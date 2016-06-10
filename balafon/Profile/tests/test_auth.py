# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.test import TestCase

from django.test.utils import override_settings

from model_mommy import mommy

TEST_AUTHENTICATION_BACKENDS = (
    'balafon.Profile.backends.ArticleCategoryPermissionBackend',
    'balafon.Profile.backends.EmailModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)


class BaseTest(TestCase):
    """Base class for TestCase"""

    def _make(self, klass, **kwargs):
        """Make an object"""
        password = None
        if klass == User:
            password = kwargs.pop('password', None)
        obj = mommy.make(klass, **kwargs)
        if password:
            obj.set_password(password)
            obj.save()
        return obj


@override_settings(AUTHENTICATION_BACKENDS=TEST_AUTHENTICATION_BACKENDS)
class EmailAuthBackendTest(BaseTest):
    """Email auth test case"""

    def test_email_login(self):
        """Test user can login with email"""
        user = self._make(User, is_active=True, password="password", email="toto@toto.fr", username="toto")
        login_ok = self.client.login(email=user.email, password="password")
        self.assertEqual(login_ok, True)

    def test_email_login_inactve(self):
        """Test user can not login if inactive"""
        user = self._make(User, is_active=False, password="password", email="toto@toto.fr", username="toto")
        login_ok = self.client.login(email=user.email, password="password")
        self.assertEqual(login_ok, False)

    def test_email_login_not_exists(self):
        """Test can not login if email does'nt exist"""
        login_ok = self.client.login(email="titi@titi.fr", password="password")
        self.assertEqual(login_ok, False)

    def test_email_login_several(self):
        """test can login if several user with same email"""
        user1 = self._make(User, is_active=True, password="password1", email="toto@toto.fr", username="toto1")
        user2 = self._make(User, is_active=True, password="password2", email="toto@toto.fr", username="toto2")
        login_ok = self.client.login(email=user1.email, password="password1")
        self.assertEqual(login_ok, True)
        self.client.logout()
        login_ok = self.client.login(email=user2.email, password="password2")
        self.assertEqual(login_ok, True)

    def test_email_login_several_one_inactive(self):
        """test user can login if several user with email and one is inactive"""
        user1 = self._make(User, is_active=False, password="password1", email="toto@toto.fr", username="toto1")
        user2 = self._make(User, is_active=False, password="password2", email="toto@toto.fr", username="toto2")
        login_ok = self.client.login(email=user1.email, password="password1")
        self.assertEqual(login_ok, False)
        self.client.logout()
        login_ok = self.client.login(email=user2.email, password="password2")
        self.assertEqual(login_ok, False)

    def test_email_login_several_all_inactive(self):
        """test user can not login if several user with email but all are inactive"""
        user1 = self._make(User, is_active=False, password="password1", email="toto@toto.fr", username="toto1")
        user2 = self._make(User, is_active=True, password="password2", email="toto@toto.fr", username="toto2")
        login_ok = self.client.login(email=user1.email, password="password1")
        self.assertEqual(login_ok, False)
        self.client.logout()
        login_ok = self.client.login(email=user2.email, password="password2")
        self.assertEqual(login_ok, True)

    def test_email_login_wrong_password(self):
        """test user can not login if wrong password"""
        user = self._make(User, is_active=True, password="password", email="toto@toto.fr", username="toto")
        login_ok = self.client.login(email=user.email, password="toto")
        self.assertEqual(login_ok, False)