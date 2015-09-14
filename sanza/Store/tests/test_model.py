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
        soup = BeautifulSoup(item.stock_threshold_alert(), "html.parser")
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
        soup = BeautifulSoup(item.stock_threshold_alert(), "html.parser")
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


class CategoryNameTest(TestCase):
    """Test that category name can not be duplicated"""

    def test_strip_name(self):
        """it should strip name"""
        category = mommy.make(models.StoreItemCategory, name=' Abc ')
        self.assertEqual(category.name, 'Abc')

    def test_merge_duplicates_articles(self):
        """it should merge articles in only 1 category"""
        category_name = "Abc"
        category1 = mommy.make(models.StoreItemCategory, name=category_name)
        article1 = mommy.make(models.StoreItem, category=category1)
        article2 = mommy.make(models.StoreItem, category=category1)

        category2 = mommy.make(models.StoreItemCategory, name=category_name)

        category = models.StoreItemCategory.objects.get(name=category_name)
        self.assertEqual(category.id, category2.id)
        self.assertEqual(category.storeitem_set.count(), 2)
        self.assertTrue(article1 in category.storeitem_set.all())
        self.assertTrue(article2 in category.storeitem_set.all())

        self.assertEqual(models.StoreItemCategory.objects.filter(id=category1.id).count(), 0)

    def test_merge_duplicates_subcategories(self):
        """it should merge subcategories in only 1 category"""
        category_name = "Abc"
        category1 = mommy.make(models.StoreItemCategory, name=category_name)
        sub_category1 = mommy.make(models.StoreItemCategory, name='Def', parent=category1)
        sub_category2 = mommy.make(models.StoreItemCategory, name='Ghi', parent=category1)

        category2 = mommy.make(models.StoreItemCategory, name=category_name)

        category = models.StoreItemCategory.objects.get(name=category_name)
        self.assertEqual(category.id, category2.id)
        self.assertEqual(category.subcategories_set.count(), 2)
        self.assertTrue(sub_category1 in category.subcategories_set.all())
        self.assertTrue(sub_category2 in category.subcategories_set.all())

        self.assertEqual(models.StoreItemCategory.objects.filter(id=category1.id).count(), 0)

    def test_path_name(self):
        """it should show full name"""
        category_name = "Abc"
        category1 = mommy.make(models.StoreItemCategory, name=category_name)
        sub_category1 = mommy.make(models.StoreItemCategory, name='Def', parent=category1)

        self.assertEqual(category1.get_path_name(), category1.name)
        self.assertEqual(sub_category1.get_path_name(), u'{0} > {1}'.format(category1.name, sub_category1.name))


class PricePolicyTest(TestCase):
    """Test that price is calculated properly"""

    def test_article_no_policy(self):
        """it should not change the price"""
        add_20_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.2")

        category1 = mommy.make(models.StoreItemCategory, price_policy=add_20_percent)

        article = mommy.make(
            models.StoreItem,
            category=category1,
            price_policy=None,
            purchase_price=Decimal("1"),
            pre_tax_price=Decimal("2")
        )

        self.assertEqual(article.pre_tax_price, Decimal("2"))

    def test_category_no_policy(self):
        """it should not change the price"""
        from_category = mommy.make(models.PricePolicy, policy='from_category', parameters='')

        category1 = mommy.make(models.StoreItemCategory, price_policy=None)

        article = mommy.make(
            models.StoreItem,
            category=category1,
            price_policy=from_category,
            purchase_price=Decimal("1"),
            pre_tax_price=Decimal("2")
        )

        self.assertEqual(article.pre_tax_price, Decimal("2"))

    def test_article_ratio_policy(self):
        """it should change the price"""
        add_20_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.2")
        add_50_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.5")

        category1 = mommy.make(models.StoreItemCategory, price_policy=add_50_percent)

        article = mommy.make(
            models.StoreItem,
            category=category1,
            price_policy=add_20_percent,
            purchase_price=Decimal("1"),
            pre_tax_price=Decimal("2")
        )

        self.assertEqual(article.pre_tax_price, Decimal("1.2"))

    def test_category_ratio_policy(self):
        """it should change the price"""
        from_category = mommy.make(models.PricePolicy, policy='from_category', parameters='')
        add_50_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.5")

        category1 = mommy.make(models.StoreItemCategory, price_policy=add_50_percent)

        article = mommy.make(
            models.StoreItem,
            category=category1,
            price_policy=from_category,
            purchase_price=Decimal("1"),
            pre_tax_price=Decimal("2")
        )

        self.assertEqual(article.pre_tax_price, Decimal("1.5"))

    def test_parent_category_ratio_policy(self):
        """it should change the price"""
        from_category = mommy.make(models.PricePolicy, policy='from_category', parameters='')
        add_20_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.2")

        category1 = mommy.make(models.StoreItemCategory, price_policy=add_20_percent)
        category2 = mommy.make(models.StoreItemCategory, price_policy=from_category, parent=category1)

        article = mommy.make(
            models.StoreItem,
            category=category2,
            price_policy=from_category,
            purchase_price=Decimal("1"),
            pre_tax_price=Decimal("2")
        )

        self.assertEqual(article.pre_tax_price, Decimal("1.2"))

    def test_change_category_policy_update_price(self):
        """it should change the price"""
        from_category = mommy.make(models.PricePolicy, policy='from_category', parameters='')
        add_20_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.2")
        add_50_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.5")

        category1 = mommy.make(models.StoreItemCategory, price_policy=add_20_percent)
        category2 = mommy.make(models.StoreItemCategory, price_policy=from_category, parent=category1)

        article = mommy.make(
            models.StoreItem,
            category=category2,
            price_policy=from_category,
            purchase_price=Decimal("1"),
            pre_tax_price=Decimal("2")
        )

        self.assertEqual(article.pre_tax_price, Decimal("1.2"))

        category2.price_policy = add_50_percent
        category2.save()

        article = models.StoreItem.objects.get(id=article.id)
        self.assertEqual(article.pre_tax_price, Decimal("1.5"))

    def test_change_category_parent_policy_update_price(self):
        """it should change the price"""
        from_category = mommy.make(models.PricePolicy, policy='from_category', parameters='')
        add_20_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.2")
        add_50_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.5")

        category1 = mommy.make(models.StoreItemCategory, price_policy=add_20_percent)
        category2 = mommy.make(models.StoreItemCategory, price_policy=from_category, parent=category1)

        article = mommy.make(
            models.StoreItem,
            category=category2,
            price_policy=from_category,
            purchase_price=Decimal("1"),
            pre_tax_price=Decimal("2")
        )

        self.assertEqual(article.pre_tax_price, Decimal("1.2"))

        category1.price_policy = add_50_percent
        category1.save()

        article = models.StoreItem.objects.get(id=article.id)
        self.assertEqual(article.pre_tax_price, Decimal("1.5"))

    def test_category_parent_policy_not_set(self):
        """it should change the price"""
        from_category = mommy.make(models.PricePolicy, policy='from_category', parameters='')

        category1 = mommy.make(models.StoreItemCategory, price_policy=None)
        category2 = mommy.make(models.StoreItemCategory, price_policy=from_category, parent=category1)

        article = mommy.make(
            models.StoreItem,
            category=category2,
            price_policy=from_category,
            purchase_price=Decimal("1"),
            pre_tax_price=Decimal("2")
        )

        self.assertEqual(article.pre_tax_price, Decimal("2"))

    def test_category_invalid_purchase_prise(self):
        """it should not change the price"""
        from_category = mommy.make(models.PricePolicy, policy='from_category', parameters='')
        add_20_percent = mommy.make(models.PricePolicy, policy='multiply_purchase_by_ratio', parameters="1.2")

        category1 = mommy.make(models.StoreItemCategory, price_policy=None)
        category2 = mommy.make(models.StoreItemCategory, price_policy=from_category, parent=category1)

        article = mommy.make(
            models.StoreItem,
            category=category2,
            price_policy=add_20_percent,
            purchase_price=None,
            pre_tax_price=Decimal("2")
        )

        self.assertEqual(article.pre_tax_price, Decimal("2"))
