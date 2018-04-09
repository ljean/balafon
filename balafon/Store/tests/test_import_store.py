# -*- coding: utf-8 -*-
"""unit testing"""

from __future__ import unicode_literals

from datetime import date
from decimal import Decimal
import os.path

from django.core.files.base import ContentFile
from django.utils.translation import ugettext

from model_mommy import mommy

from balafon.Crm.tests import BaseTestCase
from balafon.Store import models


class ImportStoreTest(BaseTestCase):
    """Import test"""

    @staticmethod
    def _get_file(file_name):
        """open a csv file for test"""
        full_name = os.path.normpath(os.path.dirname(__file__) + '/import_files/' + file_name)
        with open(full_name, 'rb') as f:
            return ContentFile(f.read(), name=file_name)

    def test_import_store_fields(self):
        """it should create items properly"""
        data_file = self._get_file('import_store_fields.xls')

        # by default fields are name,brand,reference,category,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            _create_files=True
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.pre_tax_price, item.purchase_price)
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))

    def test_import_store_fields_no_header(self):
        """it should create items properly: no header in file"""
        data_file = self._get_file('import_store_fields_no_header.xls')

        # by default fields are name,brand,reference,category,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            ignore_first_line=False
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.pre_tax_price, item.purchase_price)
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))

    def test_import_store_fields_no_purchase_price(self):
        """it should create items properly: price"""
        data_file = self._get_file('import_store_fields.xls')

        # by default fields are name,brand,reference,category,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            margin_rate=Decimal("1.2")
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.pre_tax_price, item.purchase_price * Decimal('1.2'))
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))

    def test_import_store_fields_no_vat(self):
        """it should create items properly: default VAT"""
        data_file = self._get_file('import_store_fields_no_vat.xls')

        vat_rate = mommy.make(models.VatRate, rate=Decimal('20'), is_default=True)

        # by default fields are name,brand,reference,category,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='name,brand,reference,category,pre_tax_price'
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, None)
            self.assertEqual(item.pre_tax_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.vat_rate, vat_rate)

    def test_import_store_fields_only_1_without_vat(self):
        """it should create items properly: default VAT if no value"""
        data_file = self._get_file('import_store_fields_no_vat_only_1.xls')

        vat_rate = mommy.make(models.VatRate, rate=Decimal('20'), is_default=True)

        # by default fields are name,brand,reference,category,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='name,brand,reference,category,pre_tax_price,vat_rate'
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, None)
            self.assertEqual(item.pre_tax_price, Decimal('{0}.50'.format(index)))
            if index == 1:
                self.assertEqual(item.vat_rate, vat_rate)
            else:
                self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))

    def test_import_store_fields_no_category(self):
        """it should create items properly: default categorie"""
        data_file = self._get_file('import_store_fields_no_category.xls')

        # by default fields are name,brand,reference,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='name,brand,reference,pre_tax_price,vat_rate'
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, ugettext('Uncategorized'))
            self.assertEqual(item.purchase_price, None)
            self.assertEqual(item.pre_tax_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))

    def test_import_store_fields_no_category_only_1(self):
        """it should create items properly: default category"""
        data_file = self._get_file('import_store_fields_no_category_only_1.xls')

        # by default fields are name,brand,reference,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='name,brand,reference,category,pre_tax_price,vat_rate'
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            if index == 1:
                self.assertEqual(item.category.name, ugettext('Uncategorized'))
            else:
                self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, None)
            self.assertEqual(item.pre_tax_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))

    def test_import_store_fields_no_brand_and_ref(self):
        """it should create items properly: default categorie"""
        data_file = self._get_file('import_store_fields_no_brand_and_ref.xls')

        # by default fields are name,brand,reference,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='name,category,pre_tax_price,vat_rate'
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand, None)
            self.assertEqual(item.reference, '')
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, None)
            self.assertEqual(item.pre_tax_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))

    def test_import_store_fields_no_brand_and_ref_only_1(self):
        """it should create items properly: default categorie"""
        data_file = self._get_file('import_store_fields_no_brand_and_ref_only_1.xls')

        # by default fields are name,brand,reference,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='name,brand,reference,category,pre_tax_price,vat_rate'
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            if index == 1:
                self.assertEqual(item.brand, None)
                self.assertEqual(item.reference, '')
            else:
                self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
                self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, None)
            self.assertEqual(item.pre_tax_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))

    def test_import_error(self):
        """it should create items properly: default categorie"""
        data_file = self._get_file('import_store_fields_no_brand_and_ref_only_1.xls')

        # by default fields are name,brand,reference,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='pre_tax_price,vat_rate'
        )

        store_import.import_data()

        self.assertNotEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, False)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 0)

    def test_import_store_fields_property(self):
        """it should create items properly: property"""
        data_file = self._get_file('import_store_fields_property.xls')

        # by default fields are name,brand,reference,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='name,brand,reference,category,pre_tax_price,vat_rate,dlc'
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, None)
            self.assertEqual(item.pre_tax_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))
            self.assertEqual(item.get_property('dlc'), 'A{0}'.format(index))

    def test_import_store_fields_property_existing(self):
        """it should create items properly: property already existing"""
        data_file = self._get_file('import_store_fields_property.xls')

        mommy.make(models.StoreItemProperty, name='dlc')

        # by default fields are name,brand,reference,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='name,brand,reference,category,pre_tax_price,vat_rate,dlc'
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, None)
            self.assertEqual(item.pre_tax_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))
            self.assertEqual(item.get_property('dlc'), 'A{0}'.format(index))

    def test_import_store_fields_property_1_missing(self):
        """it should create items properly: missing value for 1 property"""
        data_file = self._get_file('import_store_fields_property_missing_1.xls')

        # by default fields are name,brand,reference,purchase_price,vat_rate
        store_import = mommy.make(
            models.StoreItemImport,
            data=data_file,
            fields='name,brand,reference,category,pre_tax_price,vat_rate,dlc'
        )

        store_import.import_data()

        self.assertEqual(store_import.import_error, '')
        self.assertEqual(store_import.is_successful, True)
        self.assertEqual(store_import.last_import_date.date(), date.today())

        self.assertEqual(models.StoreItem.objects.count(), 3)

        for index, item in enumerate(models.StoreItem.objects.all()):

            self.assertEqual(item.name, 'Item {0}'.format(index))
            self.assertEqual(item.brand.name, 'Brand {0}'.format(index))
            self.assertEqual(item.reference, 'Reference {0}'.format(index))
            self.assertEqual(item.category.name, 'Category {0}'.format(index))
            self.assertEqual(item.purchase_price, None)
            self.assertEqual(item.pre_tax_price, Decimal('{0}.50'.format(index)))
            self.assertEqual(item.vat_rate.rate, Decimal('1{0}.00'.format(index)))
            if index == 1:
                self.assertEqual(item.get_property('dlc'), '')
            else:
                self.assertEqual(item.get_property('dlc'), 'A{0}'.format(index))

    def test_set_property(self):
        """it should set and get property"""
        item = mommy.make(models.StoreItem)
        self.assertEqual(item.get_property('dlc'), '')
        item.set_property('dlc', 'abc')
        self.assertEqual(item.get_property('dlc'), 'abc')
        item.set_property('dlc', 'def')
        self.assertEqual(item.get_property('dlc'), 'def')
        item.set_property('dlc', '')
        self.assertEqual(item.get_property('dlc'), '')