# -*- coding: utf-8 -*-
"""unit testing"""

from __future__ import unicode_literals

from datetime import date, datetime
from decimal import Decimal
import xlrd

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from colorbox.utils import assert_popup_redirects
from model_mommy import mommy

from balafon.unit_tests import TestCase
from balafon.Crm.models import ActionType, Action, Contact, Entity, ActionStatus
from balafon.Store import models


class CatalogueTest(TestCase):
    """It should export """

    def setUp(self):
        """before each test"""
        super(CatalogueTest, self).setUp()
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

        self.assertEqual(sheet.nrows, 1 + 2)  # header + 2 lines

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


class ActionSummaryTest(TestCase):
    """It should export """

    def setUp(self):
        """before each test"""
        super(ActionSummaryTest, self).setUp()
        user = mommy.make(User, is_active=True, is_staff=True, is_superuser=False)
        user.set_password('abc')
        user.save()
        self.client.login(username=user.username, password='abc')
        self.user = user

    def test_view_export(self):
        """It should export all in xls"""
        action_type = mommy.make(ActionType, name="Bills of Month")

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        action = mommy.make(Action, type=action_type, planned_date=date.today())
        vat_rate = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item = mommy.make(models.SaleItem, sale=action.sale, vat_rate=vat_rate, pre_tax_price=Decimal(10))

        url = reverse('store_actions_summary', args=[action_type.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')

    def test_view_export_anonymous(self):
        """It should export all in xls"""
        self.client.logout()
        action_type = mommy.make(ActionType, name="Bills of Month")

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        action = mommy.make(Action, type=action_type, planned_date=date.today())
        vat_rate = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item = mommy.make(models.SaleItem, sale=action.sale, vat_rate=vat_rate, pre_tax_price=Decimal(10))

        url = reverse('store_actions_summary', args=[action_type.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_export_redirect(self):
        """It should export all in xls"""
        action_type = mommy.make(ActionType, name="Bills of Month")

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        action = mommy.make(Action, type=action_type, planned_date=datetime(2018, 6, 21))
        vat_rate = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item = mommy.make(models.SaleItem, sale=action.sale, vat_rate=vat_rate, pre_tax_price=Decimal(10))

        data = {
            'start_date': date(2018, 6, 1),
            'end_date': date(2018, 6, 30),
        }

        url = reverse('store_actions_summary', args=[action_type.id])
        response = self.client.post(url, data)

        redirect_url = reverse('store_actions_summary_xls', args=[action_type.id, '2018-06-01', '2018-06-30'])

        assert_popup_redirects(response, redirect_url)

    def test_export_anonymous(self):
        """It should export all in xls"""

        self.client.logout()
        action_type = mommy.make(ActionType, name="Bills of Month", number_auto_generated=1)
        action_status = mommy.make(ActionStatus, name="Created")
        action_status = mommy.make(ActionStatus, name="Paid")

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        contact = mommy.make(Contact, firstname="Pierre", lastname="Dupond")

        planned_date = datetime(2018, 6, 21)
        action = mommy.make(Action, type=action_type, planned_date=planned_date, status=action_status)
        action.contacts.add(contact)
        action.save()

        vat_rate = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate, pre_tax_price=Decimal(10), quantity=1
        )

        url = reverse('store_actions_summary_xls', args=[action_type.id, '2018-06-01', '2018-06-30'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_export_one_for_contact(self):
        """It should export all in xls"""
        action_type = mommy.make(ActionType, name="Bills of Month", number_auto_generated=1)
        action_status = mommy.make(ActionStatus, name="Created")
        action_status = mommy.make(ActionStatus, name="Paid")

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        contact = mommy.make(Contact, firstname="Pierre", lastname="Dupond")

        planned_date = datetime(2018, 6, 21)
        action = mommy.make(Action, type=action_type, planned_date=planned_date, status=action_status)
        action.contacts.add(contact)
        action.save()

        vat_rate = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate, pre_tax_price=Decimal(10), quantity=1
        )

        url = reverse('store_actions_summary_xls', args=[action_type.id, '2018-06-01', '2018-06-30'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 2 + 2)

        values = [sheet.cell(1, col).value for col in range(sheet.ncols)]
        self.assertEqual(values[0], 1)
        self.assertEqual(values[1], "Pierre Dupond")
        self.assertEqual(datetime(*xlrd.xldate_as_tuple(values[2], workbook.datemode)).date(), planned_date.date())
        self.assertEqual(values[3], action_status.name)
        self.assertEqual(values[4], '')
        self.assertEqual(values[5], Decimal(10))
        self.assertEqual(values[6], Decimal(1))
        self.assertEqual(values[7], Decimal(11))

    def test_export_one_for_contact_before_start(self):
        """It should export all in xls"""
        action_type = mommy.make(ActionType, name="Bills of Month", number_auto_generated=1)
        action_status = mommy.make(ActionStatus, name="Created")
        action_status = mommy.make(ActionStatus, name="Paid")

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        contact = mommy.make(Contact, firstname="Pierre", lastname="Dupond")

        planned_date = datetime(2018, 5, 31)
        action = mommy.make(Action, type=action_type, planned_date=planned_date, status=action_status)
        action.contacts.add(contact)
        action.save()

        vat_rate = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate, pre_tax_price=Decimal(10), quantity=1
        )

        url = reverse('store_actions_summary_xls', args=[action_type.id, '2018-06-01', '2018-06-30'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 1)

        # Check emptiness
        for row in range(1, sheet.nrows):
            values = [sheet.cell(row, col).value for col in range(sheet.ncols)]
            self.assertEqual([""] * sheet.ncols, values)

    def test_export_one_for_contact_after_end(self):
        """It should export all in xls"""
        action_type = mommy.make(ActionType, name="Bills of Month", number_auto_generated=1)
        action_status = mommy.make(ActionStatus, name="Created")
        action_status = mommy.make(ActionStatus, name="Paid")

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        contact = mommy.make(Contact, firstname="Pierre", lastname="Dupond")

        planned_date = datetime(2018, 7, 1)
        action = mommy.make(Action, type=action_type, planned_date=planned_date, status=action_status)
        action.contacts.add(contact)
        action.save()

        vat_rate = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate, pre_tax_price=Decimal(10), quantity=1
        )

        url = reverse('store_actions_summary_xls', args=[action_type.id, '2018-06-01', '2018-06-30'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 1)

        # Check emptiness
        for row in range(1, sheet.nrows):
            values = [sheet.cell(row, col).value for col in range(sheet.ncols)]
            self.assertEqual([""] * sheet.ncols, values)

    def test_export_one_for_contact_other_type(self):
        """It should export all in xls"""
        action_type1 = mommy.make(ActionType, name="Bills of Month", number_auto_generated=1)
        action_type2 = mommy.make(ActionType, name="Bills of Month", number_auto_generated=1)
        action_status = mommy.make(ActionStatus, name="Created")
        action_status = mommy.make(ActionStatus, name="Paid")

        mommy.make(models.StoreManagementActionType, action_type=action_type2)

        contact = mommy.make(Contact, firstname="Pierre", lastname="Dupond")

        planned_date = datetime(2018, 6, 21)
        action = mommy.make(Action, type=action_type2, planned_date=planned_date, status=action_status)
        action.contacts.add(contact)
        action.save()

        vat_rate = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate, pre_tax_price=Decimal(10), quantity=1
        )

        url = reverse('store_actions_summary_xls', args=[action_type1.id, '2018-06-01', '2018-06-30'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 1)

        # Check emptiness
        for row in range(1, sheet.nrows):
            values = [sheet.cell(row, col).value for col in range(sheet.ncols)]
            self.assertEqual([""] * sheet.ncols, values)

    def test_export_several_for_contacts(self):
        """It should export all in xls"""
        action_type = mommy.make(ActionType, name="Bills of Month", number_auto_generated=1)
        action_status1 = mommy.make(ActionStatus, name="Created")
        action_status2 = mommy.make(ActionStatus, name="Paid")

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        contact1 = mommy.make(Contact, firstname="Pierre", lastname="Dupond")
        contact2 = mommy.make(Contact, firstname="Paul", lastname="Dupuis")

        planned_date1 = datetime(2018, 6, 1)
        action1 = mommy.make(Action, type=action_type, planned_date=planned_date1, status=action_status1)
        action1.contacts.add(contact1)
        action1.save()

        planned_date2 = datetime(2018, 6, 30, 18, 0)
        action2 = mommy.make(Action, type=action_type, planned_date=planned_date2, status=action_status2)
        action2.contacts.add(contact2)
        action2.save()

        vat_rate1 = mommy.make(models.VatRate, rate=Decimal(10))
        vat_rate2 = mommy.make(models.VatRate, rate=Decimal("5.5"))
        mommy.make(
            models.SaleItem, sale=action1.sale, vat_rate=vat_rate1, pre_tax_price=Decimal(10), quantity=1
        )
        mommy.make(
            models.SaleItem, sale=action1.sale, vat_rate=vat_rate2, pre_tax_price=Decimal(20), quantity=10
        )
        mommy.make(
            models.SaleItem, sale=action2.sale, vat_rate=vat_rate2, pre_tax_price=Decimal(100), quantity=1
        )

        url = reverse('store_actions_summary_xls', args=[action_type.id, '2018-06-01', '2018-06-30'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 3 + 2)

        values = [sheet.cell(1, col).value for col in range(sheet.ncols)]
        self.assertEqual(values[0], 1)
        self.assertEqual(values[1], "Pierre Dupond")
        self.assertEqual(datetime(*xlrd.xldate_as_tuple(values[2], workbook.datemode)).date(), planned_date1.date())
        self.assertEqual(values[3], action_status1.name)
        self.assertEqual(values[4], '')
        self.assertEqual(values[5], Decimal(210))
        self.assertEqual(values[6], Decimal("12"))
        self.assertEqual(values[7], Decimal("222"))

        values = [sheet.cell(2, col).value for col in range(sheet.ncols)]
        self.assertEqual(values[0], 2)
        self.assertEqual(values[1], "Paul Dupuis")
        self.assertEqual(datetime(*xlrd.xldate_as_tuple(values[2], workbook.datemode)).date(), planned_date2.date())
        self.assertEqual(values[3], action_status2.name)
        self.assertEqual(values[4], '')
        self.assertEqual(values[5], Decimal(100))
        self.assertEqual(values[6], Decimal("5.5"))
        self.assertEqual(values[7], Decimal("105.5"))

    def test_export_one_for_entity(self):
        """It should export all in xls"""
        action_type = mommy.make(ActionType, name="Bills of Month", number_auto_generated=1)
        action_status = mommy.make(ActionStatus, name="Created")
        action_status = mommy.make(ActionStatus, name="Paid")

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        entity = mommy.make(Entity, name="Horse&Co")

        planned_date = datetime(2018, 6, 21)
        action = mommy.make(Action, type=action_type, planned_date=planned_date, status=action_status)
        action.entities.add(entity)
        action.save()

        vat_rate = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate, pre_tax_price=Decimal(10), quantity=1
        )

        url = reverse('store_actions_summary_xls', args=[action_type.id, '2018-06-01', '2018-06-30'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 2 + 2)

        values = [sheet.cell(1, col).value for col in range(sheet.ncols)]
        self.assertEqual(values[0], 1)
        self.assertEqual(values[1], "Horse&Co")
        self.assertEqual(datetime(*xlrd.xldate_as_tuple(values[2], workbook.datemode)).date(), planned_date.date())
        self.assertEqual(values[3], action_status.name)
        self.assertEqual(values[4], '')
        self.assertEqual(values[5], Decimal(10))
        self.assertEqual(values[6], Decimal(1))
        self.assertEqual(values[7], Decimal(11))

    def test_export_accounting(self):
        """It should export all in xls"""
        action_type = mommy.make(ActionType, name="Bills of Month", number_auto_generated=1)
        action_status = mommy.make(ActionStatus, name="Created")
        action_status = mommy.make(ActionStatus, name="Paid")

        cat1 = mommy.make(models.StoreItemCategory, accounting_code="code1")
        cat2 = mommy.make(models.StoreItemCategory, accounting_code="code2")
        item1 = mommy.make(models.StoreItem, item_accounting_code="code1")
        item2 = mommy.make(models.StoreItem, item_accounting_code="", category=cat1)
        item3 = mommy.make(models.StoreItem, item_accounting_code="", category=cat2)
        item4 = mommy.make(models.StoreItem, item_accounting_code="code1", category=cat2)

        mommy.make(models.StoreManagementActionType, action_type=action_type)

        entity = mommy.make(Entity, name="Horse&Co")

        planned_date = datetime(2018, 6, 21)
        action = mommy.make(Action, type=action_type, planned_date=planned_date, status=action_status)
        action.entities.add(entity)
        action.save()

        vat_rate1 = mommy.make(models.VatRate, rate=Decimal(10))
        sale_item1 = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate1, pre_tax_price=Decimal(10), quantity=1, item=item1
        )  # code1

        vat_rate2 = mommy.make(models.VatRate, rate=Decimal(20))
        sale_item2 = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate2, pre_tax_price=Decimal(20), quantity=2, item=item2
        )  # code1
        sale_item3 = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate2, pre_tax_price=Decimal(20), quantity=1, item=item3
        )  # code2
        sale_item4 = mommy.make(
            models.SaleItem, sale=action.sale, vat_rate=vat_rate2, pre_tax_price=Decimal(10), quantity=1, item=item4
        )  # code1

        url = reverse('store_actions_summary_xls', args=[action_type.id, '2018-06-01', '2018-06-30'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        workbook = xlrd.open_workbook(file_contents=response.content, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        self.assertEqual(sheet.nrows, 3 + 2)

        values = [sheet.cell(1, col).value for col in range(sheet.ncols)]
        self.assertEqual(values[0], 1)
        self.assertEqual(values[1], "Horse&Co")
        self.assertEqual(datetime(*xlrd.xldate_as_tuple(values[2], workbook.datemode)).date(), planned_date.date())
        self.assertEqual(values[3], action_status.name)
        self.assertEqual(values[4], 'code1')
        self.assertEqual(values[5], Decimal(60))
        self.assertEqual(values[6], Decimal(11))
        self.assertEqual(values[7], Decimal(71))

        values = [sheet.cell(2, col).value for col in range(sheet.ncols)]
        self.assertEqual(values[0], 1)
        self.assertEqual(values[1], "Horse&Co")
        self.assertEqual(datetime(*xlrd.xldate_as_tuple(values[2], workbook.datemode)).date(), planned_date.date())
        self.assertEqual(values[3], action_status.name)
        self.assertEqual(values[4], 'code2')
        self.assertEqual(values[5], Decimal(20))
        self.assertEqual(values[6], Decimal(4))
        self.assertEqual(values[7], Decimal(24))


