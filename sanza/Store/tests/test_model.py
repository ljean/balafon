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

from sanza.Crm.models import Action, ActionMenu, ActionType
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


class UpdateActionItemTest(TestCase):
    """It should keep Action amount up-to-date"""

    def test_amount_on_add(self):
        """It should set action amount correctly"""
        action_type = mommy.make(ActionType)
        mommy.make(
            models.StoreManagementActionType,
            action_type=action_type,
            show_amount_as_pre_tax=True
        )

        action = mommy.make(Action, type=action_type)

        self.assertNotEqual(action.sale, None)
        vat_rate = mommy.make(models.VatRate, rate="20.0")

        mommy.make(models.SaleItem, quantity=1, pre_tax_price="12.6", vat_rate=vat_rate, sale=action.sale)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("12.6"))

    def test_amount_on_update_quantity(self):
        """It should set action amount correctly"""
        action_type = mommy.make(ActionType)
        mommy.make(
            models.StoreManagementActionType,
            action_type=action_type,
            show_amount_as_pre_tax=True
        )

        action = mommy.make(Action, type=action_type)

        self.assertNotEqual(action.sale, None)
        vat_rate = mommy.make(models.VatRate, rate="20.0")

        mommy.make(models.SaleItem, quantity=1, pre_tax_price="12.6", vat_rate=vat_rate, sale=action.sale)
        sale_item2 = mommy.make(models.SaleItem, quantity=2, pre_tax_price="4", vat_rate=vat_rate, sale=action.sale)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("20.6"))

        sale_item2.quantity = 3
        sale_item2.save()

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("24.6"))

    def test_amount_on_update_price(self):
        """It should set action amount correctly"""
        action_type = mommy.make(ActionType)
        mommy.make(
            models.StoreManagementActionType,
            action_type=action_type,
            show_amount_as_pre_tax=True
        )

        action = mommy.make(Action, type=action_type)

        self.assertNotEqual(action.sale, None)
        vat_rate = mommy.make(models.VatRate, rate="20.0")

        mommy.make(models.SaleItem, quantity=1, pre_tax_price="12.6", vat_rate=vat_rate, sale=action.sale)
        sale_item2 = mommy.make(models.SaleItem, quantity=2, pre_tax_price="4", vat_rate=vat_rate, sale=action.sale)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("20.6"))

        sale_item2.pre_tax_price = 2
        sale_item2.save()

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("16.6"))

    def test_amount_on_delete_sale(self):
        """It should set action amount correctly"""
        action_type = mommy.make(ActionType)
        mommy.make(
            models.StoreManagementActionType,
            action_type=action_type,
            show_amount_as_pre_tax=True
        )

        action = mommy.make(Action, type=action_type)

        self.assertNotEqual(action.sale, None)
        vat_rate = mommy.make(models.VatRate, rate="20.0")

        mommy.make(models.SaleItem, quantity=1, pre_tax_price="12.6", vat_rate=vat_rate, sale=action.sale)
        sale_item2 = mommy.make(models.SaleItem, quantity=2, pre_tax_price="4", vat_rate=vat_rate, sale=action.sale)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("20.6"))

        sale_item2.delete()

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("12.6"))

    def test_amount_on_vat(self):
        """It should set action amount correctly"""
        action_type = mommy.make(ActionType)
        mommy.make(
            models.StoreManagementActionType,
            action_type=action_type,
            show_amount_as_pre_tax=False
        )

        action = mommy.make(Action, type=action_type)

        self.assertNotEqual(action.sale, None)
        vat_rate1 = mommy.make(models.VatRate, rate="20.0")
        vat_rate2 = mommy.make(models.VatRate, rate="10.0")

        mommy.make(models.SaleItem, quantity=1, pre_tax_price="10", vat_rate=vat_rate1, sale=action.sale)
        mommy.make(models.SaleItem, quantity=2, pre_tax_price="1", vat_rate=vat_rate2, sale=action.sale)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("14.2"))

    def test_amount_on_update_vat(self):
        """It should set action amount correctly"""
        action_type = mommy.make(ActionType)
        mommy.make(
            models.StoreManagementActionType,
            action_type=action_type,
            show_amount_as_pre_tax=False
        )

        action = mommy.make(Action, type=action_type)

        self.assertNotEqual(action.sale, None)
        vat_rate1 = mommy.make(models.VatRate, rate="20.0")
        vat_rate2 = mommy.make(models.VatRate, rate="10.0")

        mommy.make(models.SaleItem, quantity=1, pre_tax_price="10", vat_rate=vat_rate1, sale=action.sale)
        sale_item2 = mommy.make(models.SaleItem, quantity=2, pre_tax_price="1", vat_rate=vat_rate2, sale=action.sale)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("14.2"))

        sale_item2.vat_rate = vat_rate1
        sale_item2.save()

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.amount, Decimal("14.4"))


class SaleTotalTest(TestCase):
    """test that the total amount of a sale is calculated correctly"""

    def test_amount_empty_cart(self):
        """It should return 0"""
        sale = mommy.make(models.Sale)
        self.assertEqual(Decimal(0), sale.vat_incl_total_price())

    def test_amount_cart(self):
        """It should return sum"""
        sale = mommy.make(models.Sale)
        vat_rate_20 = mommy.make(models.VatRate, rate="20.0")
        vat_rate_10 = mommy.make(models.VatRate, rate="10.0")

        mommy.make(models.SaleItem, quantity=1, pre_tax_price="10", vat_rate=vat_rate_20, sale=sale)
        mommy.make(models.SaleItem, quantity=2, pre_tax_price="1", vat_rate=vat_rate_10, sale=sale)
        mommy.make(models.SaleItem, quantity=1, pre_tax_price="5", vat_rate=vat_rate_10, sale=sale)

        self.assertEqual(Decimal("19.7"), sale.vat_incl_total_price())

    def test_vat_amount_empty_cart(self):
        """It should return empty list"""
        sale = mommy.make(models.Sale)
        self.assertEqual([], sale.vat_total_amounts())

    def test_vat_amount_cart(self):
        """It should return list with dictionary with total amount of vat per rate"""
        sale = mommy.make(models.Sale)
        vat_rate_20 = mommy.make(models.VatRate, rate="20.0")
        vat_rate_10 = mommy.make(models.VatRate, rate="10.0")

        mommy.make(models.SaleItem, quantity=1, pre_tax_price="10", vat_rate=vat_rate_20, sale=sale)
        mommy.make(models.SaleItem, quantity=2, pre_tax_price="1", vat_rate=vat_rate_10, sale=sale)
        mommy.make(models.SaleItem, quantity=1, pre_tax_price="5", vat_rate=vat_rate_10, sale=sale)

        vat_totals = sale.vat_total_amounts()
        self.assertEqual(len(vat_totals), 2)
        self.assertEqual(vat_totals[0]['vat_rate'], vat_rate_10)
        self.assertEqual(vat_totals[0]['amount'], Decimal("0.7"))
        self.assertEqual(vat_totals[1]['vat_rate'], vat_rate_20)
        self.assertEqual(vat_totals[1]['amount'], Decimal("2"))


