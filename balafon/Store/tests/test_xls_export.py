# -*- coding: utf-8 -*-
"""unit testing"""

import xlrd

from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Store import models
from balafon.Store.admin import StockThresholdFilter, StoreItemAdmin


class CatalogueTest(TestCase):
    """It should export """

    def setUp(self):
        """before each test"""
        user = mommy.make(User, is_active=True, is_staff=True, is_superuser=False)
        user.set_password('abc')
        user.save()
        self.client.login(username=user.username, password='abc')
        self.user = user

    def test_export_all(self):
        """It should export all in xls"""
        mommy.make(models.StoreItem, available=True)
        mommy.make(models.StoreItem, available=True)

        response = self.client.get(reverse('store_xls_catalogue', args=[0]))

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 1 + 2) # header + 2 lines

    def test_export_all_available(self):
        """It should export only available items"""
        item1 = mommy.make(models.StoreItem, available=True)
        mommy.make(models.StoreItem, available=False)

        response = self.client.get(reverse('store_xls_catalogue', args=[0]))

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 1 + 1)
        self.assertEqual(sheet.cell(1, 0).value, item1.fullname())

    def test_export_anonymous(self):
        """It should raise 403"""
        self.client.logout()

        item1 = mommy.make(models.StoreItem, available=True)
        mommy.make(models.StoreItem, available=False)

        response = self.client.get(reverse('store_xls_catalogue', args=[0]))

        self.assertEqual(response.status_code, 403)

    def test_export_category(self):
        """It should export only items of category"""
        category1 = mommy.make(models.StoreItemCategory)
        category2 = mommy.make(models.StoreItemCategory)

        item1 = mommy.make(models.StoreItem, available=True, category=category1)
        mommy.make(models.StoreItem, available=True, category=category2)

        response = self.client.get(reverse('store_xls_catalogue', args=[category1.id]))

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 1 + 1)
        self.assertEqual(sheet.cell(1, 0).value, item1.fullname())
