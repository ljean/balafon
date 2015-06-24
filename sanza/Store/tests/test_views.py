# -*- coding: utf-8 -*-
"""unit testing"""

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from sanza.Crm.models import Action, ActionType
from sanza.Store import models

CUSTOM_STYLE = '''<style>
    body {
      background: #000;
    }
</style>'''


class ViewCommercialDocumentTest(TestCase):
    """It should display commercial document"""

    def setUp(self):
        """before each test"""
        user = mommy.make(User, is_active=True, is_staff=True, is_superuser=False)
        user.set_password('abc')
        user.save()
        self.client.login(username=user.username, password='abc')
        self.user = user

    def tearDown(self):
        """after each test"""
        self.client.logout()

    def test_view_no_sale_action_type(self):
        """It should display standard document"""

        action = mommy.make(Action, type=None)
        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, CUSTOM_STYLE)

    def test_view_no_custom_template(self):
        """It should display standard document"""

        action_type = mommy.make(ActionType)
        action = mommy.make(Action, type=action_type)
        mommy.make(models.StoreManagementActionType, action_type=action_type, template_name='')

        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, CUSTOM_STYLE)

    def test_view_custom_template(self):
        """It should display custom document"""

        action_type = mommy.make(ActionType)
        action = mommy.make(Action, type=action_type)
        mommy.make(models.StoreManagementActionType, action_type=action_type, template_name='Store/tests/bill.html')

        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, CUSTOM_STYLE)
        self.assertContains(response, 'big head')
        self.assertContains(response, 'big foot')

    def test_view_no_sales(self):
        """It should display page not found"""
        action = mommy.make(Action, type=None)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_view_admin_only(self):
        """It should display permission denied"""
        self.user.is_staff = False
        self.user.save()

        action = mommy.make(Action, type=None)
        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_view_anonymous(self):
        """It should redirect to login page"""
        self.client.logout()

        action = mommy.make(Action, type=None)
        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse('django.contrib.auth.views.login')
        self.assertEqual(response['Location'], 'http://testserver{0}?next={1}'.format(login_url, url))

    def test_view_values(self):
        """It should display item text"""

        action = mommy.make(Action, type=None)
        sale = mommy.make(models.Sale, action=action)

        item = mommy.make(models.SaleItem, sale=sale, text=u'Promo été')

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertContains(response, item.text)
