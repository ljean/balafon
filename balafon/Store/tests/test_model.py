# -*- coding: utf-8 -*-
"""unit testing"""

from bs4 import BeautifulSoup
from decimal import Decimal

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from model_mommy import mommy

from balafon.Crm.models import Action, ActionMenu, ActionType, Contact
from balafon.Store import models


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

    def test_sale_no_vat(self):
        """Vat should be 0"""
        sale = mommy.make(models.Sale)
        item = mommy.make(models.SaleItem, quantity=Decimal(2), pre_tax_price=Decimal("10"), vat_rate=None, sale=sale)

        self.assertEqual(item.vat_price(), Decimal(0))
        self.assertEqual(item.total_vat_price(), Decimal(0))
        self.assertEqual(item.vat_incl_price(), Decimal("10"))
        self.assertEqual(item.vat_incl_total_price(), Decimal("20"))

    def test_sale_with_vat(self):
        """Vat should not be 0"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("10.0"))
        sale = mommy.make(models.Sale)
        item = mommy.make(models.SaleItem, quantity=Decimal(2), pre_tax_price=Decimal("11"), vat_rate=vat_rate, sale=sale)

        self.assertEqual(item.vat_price(), Decimal("1.1"))
        self.assertEqual(item.total_vat_price(), Decimal("2.2"))
        self.assertEqual(item.vat_incl_price(), Decimal("12.1"))
        self.assertEqual(item.vat_incl_total_price(), Decimal("24.2"))


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

    def test_amount_no_vat(self):
        """It should return list with no vat value"""
        sale = mommy.make(models.Sale)
        mommy.make(models.SaleItem, quantity=1, pre_tax_price="10", vat_rate=None, sale=sale)
        vat_totals = sale.vat_total_amounts()
        self.assertEqual(len(vat_totals), 0)


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


class BlankLineTest(TestCase):
    """It should calculate price with VAT"""

    def test_blank_lines(self):
        """it should return all lines and calculate price properly"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("10.0"))
        sale = mommy.make(models.Sale)
        mommy.make(models.SaleItem, quantity=2, pre_tax_price="10", vat_rate=vat_rate, sale=sale)
        item2 = mommy.make(models.SaleItem, quantity=1, pre_tax_price="1", vat_rate=None, sale=sale, is_blank=True)
        mommy.make(models.SaleItem, quantity=1, pre_tax_price="15", vat_rate=vat_rate, sale=sale)

        self.assertEqual(sale.saleitem_set.count(), 3)
        self.assertEqual(item2.quantity, 0)
        self.assertEqual(item2.pre_tax_price, 0)

        self.assertEqual(Decimal("38.5"), sale.vat_incl_total_price())


class SaleDiscountTest(TestCase):
    """It should take discount into account when calculating price"""

    def test_calculate_discount(self):
        """It should have a discount"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("20.0"))

        tag = mommy.make(models.StoreItemTag, name="vrac")

        discount = mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=True
        )
        discount.tags.add(tag)
        discount.save()

        item = mommy.make(models.StoreItem, pre_tax_price=Decimal("10"), vat_rate=vat_rate)
        item.tags.add(tag)
        item.save()

        sale = mommy.make(models.Sale)
        sale_item = mommy.make(
            models.SaleItem, quantity=2, item=item, pre_tax_price=item.pre_tax_price, vat_rate=item.vat_rate, sale=sale
        )
        sale.save()

        self.assertEqual(sale.saleitem_set.count(), 1)
        self.assertEqual(Decimal("18"), sale.pre_tax_total_price())
        self.assertEqual(Decimal("21.6"), sale.vat_incl_total_price())

        sale_item = models.SaleItem.objects.get(id=sale_item.id)
        self.assertEqual(sale_item.discount, discount)
        self.assertEqual(sale_item.unit_price(), Decimal('9'))
        self.assertEqual(sale_item.vat_incl_price(), Decimal('10.8'))
        self.assertEqual(sale_item.vat_price(), Decimal('1.8'))
        self.assertEqual(sale_item.total_vat_price(), Decimal('3.6'))

    def test_calculate_discount_price_class(self):
        """It should have a discount"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("20.0"))

        discount = mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=True
        )
        price_class = mommy.make(models.PriceClass)
        price_class.discounts.add(discount)
        price_class.save()

        item = mommy.make(models.StoreItem, pre_tax_price=Decimal("10"), vat_rate=vat_rate, price_class=price_class)

        sale = mommy.make(models.Sale)
        sale_item = mommy.make(
            models.SaleItem, quantity=2, item=item, pre_tax_price=item.pre_tax_price, vat_rate=item.vat_rate, sale=sale
        )
        sale.save()

        self.assertEqual(sale.saleitem_set.count(), 1)
        self.assertEqual(Decimal("18"), sale.pre_tax_total_price())
        self.assertEqual(Decimal("21.6"), sale.vat_incl_total_price())

        sale_item = models.SaleItem.objects.get(id=sale_item.id)
        self.assertEqual(sale_item.discount, discount)
        self.assertEqual(sale_item.unit_price(), Decimal('9'))
        self.assertEqual(sale_item.vat_incl_price(), Decimal('10.8'))
        self.assertEqual(sale_item.vat_price(), Decimal('1.8'))
        self.assertEqual(sale_item.total_vat_price(), Decimal('3.6'))

    def test_calculate_discount_disabled(self):
        """It should not have a discount"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("20.0"))

        tag = mommy.make(models.StoreItemTag, name="vrac")

        discount = mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=False
        )
        discount.tags.add(tag)
        discount.save()

        item = mommy.make(models.StoreItem, pre_tax_price=Decimal("10"), vat_rate=vat_rate)
        item.tags.add(tag)
        item.save()

        sale = mommy.make(models.Sale)
        sale_item = mommy.make(
            models.SaleItem, quantity=2, item=item, pre_tax_price=item.pre_tax_price, vat_rate=item.vat_rate, sale=sale
        )
        sale.save()

        self.assertEqual(sale.saleitem_set.count(), 1)
        self.assertEqual(Decimal("20"), sale.pre_tax_total_price())
        self.assertEqual(Decimal("24"), sale.vat_incl_total_price())

        sale_item = models.SaleItem.objects.get(id=sale_item.id)
        self.assertEqual(sale_item.discount, None)
        self.assertEqual(sale_item.unit_price(), Decimal('10'))
        self.assertEqual(sale_item.vat_incl_price(), Decimal('12'))
        self.assertEqual(sale_item.vat_price(), Decimal('2'))
        self.assertEqual(sale_item.total_vat_price(), Decimal('4'))

    def test_calculate_discount_quantity_zero(self):
        """It should not have a discount"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("20.0"))

        tag = mommy.make(models.StoreItemTag, name="vrac")

        discount = mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=False
        )
        discount.tags.add(tag)
        discount.save()

        item = mommy.make(models.StoreItem, pre_tax_price=Decimal("10"), vat_rate=vat_rate)
        item.tags.add(tag)
        item.save()

        sale = mommy.make(models.Sale)
        sale_item = mommy.make(
            models.SaleItem, quantity=0, item=item, pre_tax_price=item.pre_tax_price, vat_rate=item.vat_rate, sale=sale
        )
        sale.save()

        self.assertEqual(sale.saleitem_set.count(), 1)
        self.assertEqual(Decimal(0), sale.pre_tax_total_price())
        self.assertEqual(Decimal(0), sale.vat_incl_total_price())

        sale_item = models.SaleItem.objects.get(id=sale_item.id)
        self.assertEqual(sale_item.discount, None)
        self.assertEqual(sale_item.unit_price(), Decimal("10"))
        self.assertEqual(sale_item.vat_incl_price(), Decimal("12"))
        self.assertEqual(sale_item.vat_price(), Decimal("2"))
        self.assertEqual(sale_item.total_vat_price(), Decimal(0))

    def test_several_discount(self):
        """It should have only 1 discount"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("20.0"))

        tag = mommy.make(models.StoreItemTag, name="vrac")

        discount = mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=True
        )
        discount.tags.add(tag)
        discount.save()

        discount2 = mommy.make(
            models.Discount, name=u'-20% à partir de 2 Kg', rate=Decimal("20"), quantity=Decimal("3"), active=True
        )
        discount2.tags.add(tag)
        discount2.save()

        item = mommy.make(models.StoreItem, pre_tax_price=Decimal("10"), vat_rate=vat_rate)
        item.tags.add(tag)
        item.save()

        sale = mommy.make(models.Sale)
        sale_item = mommy.make(
            models.SaleItem, quantity=2, item=item, pre_tax_price=item.pre_tax_price, vat_rate=item.vat_rate, sale=sale
        )
        sale.save()

        self.assertEqual(sale.saleitem_set.count(), 1)
        self.assertEqual(Decimal("18"), sale.pre_tax_total_price())
        self.assertEqual(Decimal("21.6"), sale.vat_incl_total_price())

        sale_item = models.SaleItem.objects.get(id=sale_item.id)
        self.assertEqual(sale_item.discount, discount)
        self.assertEqual(sale_item.unit_price(), Decimal('9'))
        self.assertEqual(sale_item.vat_incl_price(), Decimal('10.8'))
        self.assertEqual(sale_item.vat_price(), Decimal('1.8'))
        self.assertEqual(sale_item.total_vat_price(), Decimal('3.6'))

    def test_several_discount_right_quantity(self):
        """It should have only 1 discount"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("20.0"))

        tag = mommy.make(models.StoreItemTag, name="vrac")

        discount = mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=True
        )
        discount.tags.add(tag)
        discount.save()

        discount2 = mommy.make(
            models.Discount, name=u'-20% à partir de 3 Kg', rate=Decimal("20"), quantity=Decimal("3"), active=True
        )
        discount2.tags.add(tag)
        discount2.save()

        item = mommy.make(models.StoreItem, pre_tax_price=Decimal("10"), vat_rate=vat_rate)
        item.tags.add(tag)
        item.save()

        sale = mommy.make(models.Sale)
        sale_item = mommy.make(
            models.SaleItem, quantity=3, item=item, pre_tax_price=item.pre_tax_price, vat_rate=item.vat_rate, sale=sale
        )
        sale.save()

        self.assertEqual(sale.saleitem_set.count(), 1)
        self.assertEqual(Decimal("24"), sale.pre_tax_total_price())
        self.assertEqual(Decimal("28.8"), sale.vat_incl_total_price())

        sale_item = models.SaleItem.objects.get(id=sale_item.id)
        self.assertEqual(sale_item.discount, discount2)
        self.assertEqual(sale_item.unit_price(), Decimal('8'))
        self.assertEqual(sale_item.vat_incl_price(), Decimal('9.6'))
        self.assertEqual(sale_item.vat_price(), Decimal('1.6'))
        self.assertEqual(sale_item.total_vat_price(), Decimal('4.8'))

    def test_calculate_discount_on_item_saved(self):
        """It should recalculate discount when item is saved"""
        vat_rate = mommy.make(models.VatRate, rate=Decimal("20.0"))

        tag = mommy.make(models.StoreItemTag, name="vrac")

        discount = mommy.make(
            models.Discount, name=u'-10% à partir de 3 Kg', rate=Decimal("10"), quantity=Decimal("3"), active=True
        )
        discount.tags.add(tag)
        discount.save()

        item1 = mommy.make(models.StoreItem, pre_tax_price=Decimal("10"), vat_rate=vat_rate)
        item1.tags.add(tag)
        item1.save()

        item2 = mommy.make(models.StoreItem, pre_tax_price=Decimal("10"), vat_rate=vat_rate)
        item2.tags.add(tag)
        item2.save()

        sale = mommy.make(models.Sale)

        sale_item1 = mommy.make(
            models.SaleItem, quantity=3, item=item1, pre_tax_price=item1.pre_tax_price, vat_rate=item1.vat_rate,
            sale=sale
        )

        self.assertEqual(sale.saleitem_set.count(), 1)
        self.assertEqual(Decimal("27"), sale.pre_tax_total_price())
        self.assertEqual(Decimal("32.4"), sale.vat_incl_total_price())

        sale_item1 = models.SaleItem.objects.get(id=sale_item1.id)
        self.assertEqual(sale_item1.discount, discount)
        self.assertEqual(sale_item1.unit_price(), Decimal('9'))
        self.assertEqual(sale_item1.vat_incl_price(), Decimal('10.8'))
        self.assertEqual(sale_item1.vat_price(), Decimal('1.8'))
        self.assertEqual(sale_item1.total_vat_price(), Decimal('5.4'))

        sale_item2 = mommy.make(
            models.SaleItem, quantity=1, item=item1, pre_tax_price=item2.pre_tax_price, vat_rate=item2.vat_rate,
            sale=sale
        )

        self.assertEqual(sale.saleitem_set.count(), 2)
        self.assertEqual(Decimal("37"), sale.pre_tax_total_price())
        self.assertEqual(Decimal("44.4"), sale.vat_incl_total_price())

        sale_item2 = models.SaleItem.objects.get(id=sale_item2.id)
        self.assertEqual(sale_item2.discount, None)
        self.assertEqual(sale_item2.unit_price(), Decimal('10'))
        self.assertEqual(sale_item2.vat_incl_price(), Decimal('12'))
        self.assertEqual(sale_item2.vat_price(), Decimal('2'))
        self.assertEqual(sale_item2.total_vat_price(), Decimal('2'))

        sale_item2.quantity = 3
        sale_item2.save()
        sale_item2 = models.SaleItem.objects.get(id=sale_item2.id)
        self.assertEqual(sale_item2.discount, discount)
        self.assertEqual(sale_item2.unit_price(), Decimal('9'))
        self.assertEqual(sale_item2.vat_incl_price(), Decimal('10.8'))
        self.assertEqual(sale_item2.vat_price(), Decimal('1.8'))
        self.assertEqual(sale_item2.total_vat_price(), Decimal('5.4'))

        sale = models.Sale.objects.get(id=sale.id)
        self.assertEqual(sale.saleitem_set.count(), 2)
        self.assertEqual(Decimal("54"), sale.pre_tax_total_price())
        self.assertEqual(Decimal("64.8"), sale.vat_incl_total_price())


class StoreItemDiscountTest(TestCase):
    """It should return the list of discounts associated with an item"""

    def test_view_discounts(self):
        """if several tags are associated"""

        tag1 = mommy.make(models.StoreItemTag, name="vrac")
        tag2 = mommy.make(models.StoreItemTag, name="promo")
        tag3 = mommy.make(models.StoreItemTag, name="soldes")
        tag4 = mommy.make(models.StoreItemTag, name="super-promos")

        discount = mommy.make(
            models.Discount, name=u'-50% à partir de 4 Kg', rate=Decimal("50"), quantity=Decimal("4"), active=True
        )
        discount.tags.add(tag1)
        discount.tags.add(tag2)
        discount.save()

        discount2 = mommy.make(
            models.Discount, name=u'-20% à partir de 3 Kg', rate=Decimal("20"), quantity=Decimal("3"), active=True
        )
        discount2.tags.add(tag1)
        discount2.save()

        discount3 = mommy.make(
            models.Discount, name=u'-80% à partir de 3 Kg', rate=Decimal("80"), quantity=Decimal("3"), active=True
        )

        item = mommy.make(models.StoreItem)
        item.tags.add(tag1)
        item.tags.add(tag2)
        item.save()

        self.assertEqual(list(item.discounts), [discount2, discount])

    def test_view_discounts_price_class(self):
        """if several tags are associated"""

        discount = mommy.make(
            models.Discount, name=u'-50% à partir de 4 Kg', rate=Decimal("50"), quantity=Decimal("4"), active=True
        )

        price_class = mommy.make(models.PriceClass)
        price_class.discounts.add(discount)
        price_class.save()

        item = mommy.make(models.StoreItem, price_class=price_class)

        self.assertEqual(list(item.discounts), [discount])

    def test_view_discounts_tag_and_price_class(self):
        """if tags and price classes are associated"""
        tag1 = mommy.make(models.StoreItemTag, name="vrac")
        tag2 = mommy.make(models.StoreItemTag, name="promo")

        discount = mommy.make(
            models.Discount, name=u'-20% à partir de 4 Kg', rate=Decimal("20"), quantity=Decimal("4"), active=True
        )
        discount.tags.add(tag1)
        discount.tags.add(tag2)
        discount.save()

        discount2 = mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=True
        )
        discount2.tags.add(tag1)
        discount2.save()

        price_class = mommy.make(models.PriceClass)
        price_class.discounts.add(discount)
        price_class.save()

        item = mommy.make(models.StoreItem, price_class=price_class)
        item.tags.add(tag1)
        item.tags.add(tag2)
        item.save()

        discounts = list(item.discounts)
        self.assertEqual(discounts, [discount2, discount])

    def test_view_discounts_tag_and_price_class2(self):
        """if tags and price classes are associated"""
        tag1 = mommy.make(models.StoreItemTag, name="vrac")

        discount = mommy.make(
            models.Discount, name=u'-20% à partir de 4 Kg', rate=Decimal("20"), quantity=Decimal("4"), active=True
        )
        discount.tags.add(tag1)
        discount.save()

        discount2 = mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=True
        )

        price_class = mommy.make(models.PriceClass)
        price_class.discounts.add(discount2)
        price_class.save()

        item = mommy.make(models.StoreItem, price_class=price_class)
        item.tags.add(tag1)
        item.save()

        self.assertEqual(list(item.discounts), [discount2, discount])

    def test_view_price_class_several_discounts(self):
        """if several price classes are associated"""
        discount = mommy.make(
            models.Discount, name=u'-20% à partir de 4 Kg', rate=Decimal("20"), quantity=Decimal("4"), active=True
        )

        discount2 = mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=True
        )

        price_class = mommy.make(models.PriceClass)
        price_class.discounts.add(discount)
        price_class.discounts.add(discount2)
        price_class.save()

        item = mommy.make(models.StoreItem, price_class=price_class)
        self.assertEqual(list(item.discounts), [discount2, discount])

    def test_view_price_class_no_discounts(self):
        """if no price classes are associated"""
        discount = mommy.make(
            models.Discount, name=u'-20% à partir de 4 Kg', rate=Decimal("20"), quantity=Decimal("4"), active=False
        )

        mommy.make(
            models.Discount, name=u'-10% à partir de 2 Kg', rate=Decimal("10"), quantity=Decimal("2"), active=True
        )

        price_class = mommy.make(models.PriceClass)
        price_class.discounts.add(discount)
        price_class.save()

        item = mommy.make(models.StoreItem, price_class=price_class)
        self.assertEqual(list(item.discounts), [])

    def test_view_discounts_inactive(self):
        """If only 1 tag"""

        tag1 = mommy.make(models.StoreItemTag, name="vrac")
        tag2 = mommy.make(models.StoreItemTag, name="promo")
        tag3 = mommy.make(models.StoreItemTag, name="soldes")

        discount = mommy.make(
            models.Discount, name=u'-50% à partir de 4 Kg', rate=Decimal("50"), quantity=Decimal("4"), active=False
        )
        discount.tags.add(tag1)
        discount.tags.add(tag2)
        discount.save()

        discount2 = mommy.make(
            models.Discount, name=u'-20% à partir de 3 Kg', rate=Decimal("20"), quantity=Decimal("3"), active=True
        )
        discount2.tags.add(tag1)
        discount2.save()

        discount3 = mommy.make(
            models.Discount, name=u'-80% à partir de 3 Kg', rate=Decimal("80"), quantity=Decimal("3"), active=True
        )

        item = mommy.make(models.StoreItem)
        item.tags.add(tag1)
        item.tags.add(tag2)
        item.save()

        self.assertEqual(list(item.discounts), [discount2])

    def test_view_discounts_none(self):
        """if no tag"""

        tag1 = mommy.make(models.StoreItemTag, name="vrac")
        tag2 = mommy.make(models.StoreItemTag, name="promo")

        discount = mommy.make(
            models.Discount, name=u'-50% à partir de 4 Kg', rate=Decimal("50"), quantity=Decimal("4"), active=False
        )
        discount.tags.add(tag1)
        discount.tags.add(tag2)
        discount.save()

        item = mommy.make(models.StoreItem)

        self.assertEqual(list(item.discounts), [])


class MailtoActionTest(TestCase):
    """mailtto"""

    def test_mailto_to_action_body(self):

        action_type = mommy.make(ActionType, mail_to_subject='', generate_uuid=True, name='Doc')
        mommy.make(models.StoreManagementActionType, action_type=action_type)

        action = mommy.make(Action, type=action_type, subject=u'Test')

        contact = mommy.make(Contact, email='toto@toto.fr', lastname='Doe', firstname='John')
        action.contacts.add(contact)
        action.save()

        self.assertNotEqual(action.uuid, '')
        url = reverse('store_view_sales_document_public', args=[action.uuid])

        body = _(u"Here is a link to your {0}: {1}{2}").format(
            action_type.name,
            "http://" + Site.objects.get_current().domain,
            url
        )

        self.assertEqual(
            action.mail_to,
            u'mailto:"John Doe" <toto@toto.fr>?subject=Test&body={0}'.format(body)
        )

    def test_mailto_to_action_body_no_sale(self):

        action_type = mommy.make(ActionType, mail_to_subject='', generate_uuid=True, name='Doc')

        action = mommy.make(Action, type=action_type, subject=u'Test')

        contact = mommy.make(Contact, email='toto@toto.fr', lastname='Doe', firstname='John')
        action.contacts.add(contact)
        action.save()

        self.assertNotEqual(action.uuid, '')

        self.assertEqual(
            action.mail_to,
            u'mailto:"John Doe" <toto@toto.fr>?subject=Test&body='
        )

    def test_mailto_to_action_body_no_uuid(self):

        action_type = mommy.make(ActionType, mail_to_subject='', generate_uuid=False, name='Doc')
        mommy.make(models.StoreManagementActionType, action_type=action_type)

        action = mommy.make(Action, type=action_type, subject=u'Test')

        contact = mommy.make(Contact, email='toto@toto.fr', lastname='Doe', firstname='John')
        action.contacts.add(contact)
        action.save()

        self.assertEqual(action.uuid, '')

        self.assertEqual(
            action.mail_to,
            u'mailto:"John Doe" <toto@toto.fr>?subject=Test&body='
        )

    def test_mailto_to_action_subject(self):

        action_type = mommy.make(ActionType, mail_to_subject='Another subject', generate_uuid=True, name='Doc')
        mommy.make(models.StoreManagementActionType, action_type=action_type)

        action = mommy.make(Action, type=action_type, subject=u'Test')

        contact = mommy.make(Contact, email='toto@toto.fr', lastname='Doe', firstname='John')
        action.contacts.add(contact)
        action.save()

        self.assertNotEqual(action.uuid, '')
        url = reverse('store_view_sales_document_public', args=[action.uuid])

        body = _(u"Here is a link to your {0}: {1}{2}").format(
            action_type.name,
            "http://" + Site.objects.get_current().domain,
            url
        )

        self.assertEqual(
            action.mail_to,
            u'mailto:"John Doe" <toto@toto.fr>?subject=Another subject&body={0}'.format(body)
        )


class SaleItemOrderTest(TestCase):
    """It should increment the order correctly"""

    def test_default(self):
        """It should be 1"""
        sale = mommy.make(models.Sale)
        item = mommy.make(models.SaleItem, sale=sale, pre_tax_price="10")
        self.assertEqual(1, item.order_index)

    def test_zero(self):
        """It should be 1"""
        sale = mommy.make(models.Sale)
        item = mommy.make(models.SaleItem, sale=sale, order_index=0, pre_tax_price="10")
        self.assertEqual(1, item.order_index)

    def test_max(self):
        """It should be max + 1"""
        sale = mommy.make(models.Sale)
        mommy.make(models.SaleItem, sale=sale, order_index=10, pre_tax_price="10")
        item = mommy.make(models.SaleItem, sale=sale, pre_tax_price="10")
        self.assertEqual(11, item.order_index)

    def test_value(self):
        """It should be the given value"""
        sale = mommy.make(models.Sale)
        item = mommy.make(models.SaleItem, sale=sale, order_index=5, pre_tax_price="10")
        self.assertEqual(5, item.order_index)

    def test_max_other(self):
        """It should be 1 (max of the sale)"""
        sale = mommy.make(models.Sale)
        other_sale = mommy.make(models.Sale)
        mommy.make(models.SaleItem, sale=other_sale, order_index=10, pre_tax_price="10")
        item = mommy.make(models.SaleItem, sale=sale, pre_tax_price="10")
        self.assertEqual(1, item.order_index)


class SaleReferenceText(TestCase):
    """It should increment the order correctly"""

    def test_empty(self):
        """It should be empty"""
        action_type = mommy.make(ActionType)
        mommy.make(models.StoreManagementActionType, action_type=action_type)

        action = mommy.make(Action, type=action_type)

        self.assertNotEqual(action.sale, None)
        self.assertEqual(action.sale.get_references_text(), "")

    def test_value(self):
        """It should be empty"""
        action_type = mommy.make(ActionType)
        references_text = "<p>Hello</p>"
        mommy.make(models.StoreManagementActionType, action_type=action_type, references_text=references_text)

        action = mommy.make(Action, type=action_type)

        self.assertNotEqual(action.sale, None)
        self.assertEqual(action.sale.get_references_text(), references_text)
