# -*- coding: utf-8 -*-
"""unit testing"""

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from bs4 import BeautifulSoup
from decimal import Decimal

from django.test import TestCase

from model_mommy import mommy

from sanza.Crm.models import ActionMenu, ActionType
from sanza.Store import models


class StockThresholdTest(TestCase):
    """It should display a warning sign when stock is below threshold"""

    def test_above_threshold(self):
        """It should not show a warning sign"""
        item = mommy.make(models.StoreItem, stock_count=40, stock_threshold=30)
        soup = BeautifulSoup(item.stock_threshold_alert())
        self.assertEqual(0, len(soup.select("img")))

    def test_threshold_not_defined(self):
        """It should not show a warning sign"""
        item = mommy.make(models.StoreItem, stock_count=40, stock_threshold=None)
        self.assertEqual("", item.stock_threshold_alert())

    def test_stock_not_defined(self):
        """It should not show a warning sign"""
        item = mommy.make(models.StoreItem, stock_count=None, stock_threshold=None)
        self.assertEqual("", item.stock_threshold_alert())

    def test_below_threshold(self):
        """It should show a warning sign"""
        item = mommy.make(models.StoreItem, stock_count=20, stock_threshold=30)
        soup = BeautifulSoup(item.stock_threshold_alert())
        self.assertEqual(1, len(soup.select("img")))


class VatInclusivePriceTest(TestCase):
    """It should calculate price with VAT"""

    def test_price(self):
        """it should be right"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("10.0"))
        item = mommy.make(models.StoreItem, pre_tax_price=Decimal("20.0"), vat_rate=vat_rate)
        self.assertEqual(Decimal("22.0"), item.vat_incl_price())


class StoreManagementActionTypeTest(TestCase):
    """It should create actions menus"""

    def test_create_store_action_type(self):
        """It should create the menu"""
        self.assertEqual(0, ActionMenu.objects.count())
        action_type = mommy.make(ActionType)
        mommy.make(models.StoreManagementActionType, action_type=action_type)
        self.assertEqual(1, ActionMenu.objects.count())
        menu = ActionMenu.objects.all()[0]
        self.assertEqual(menu.view_name, 'store_view_sales_document')

    def test_create_store_action_type_and_save(self):
        """It should create only 1 menu"""
        self.assertEqual(0, ActionMenu.objects.count())
        action_type = mommy.make(ActionType)
        store_action_type = mommy.make(models.StoreManagementActionType, action_type=action_type)
        self.assertEqual(1, ActionMenu.objects.count())
        menu = ActionMenu.objects.all()[0]
        self.assertEqual(menu.view_name, 'store_view_sales_document')
        store_action_type.save()
        self.assertEqual(1, ActionMenu.objects.count())
