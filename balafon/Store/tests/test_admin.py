# -*- coding: utf-8 -*-
"""unit testing"""

from django.test import TestCase

from model_mommy import mommy

from balafon.Store import models
from balafon.Store.admin import StockThresholdFilter, StoreItemAdmin


class StockThresholdListFilterTest(TestCase):
    """It should filter items according to threshold level"""

    def test_below_threshold(self):
        """It should display items below threshold"""
        item1 = mommy.make(models.StoreItem, stock_count=20, stock_threshold=30)
        mommy.make(models.StoreItem, stock_count=40, stock_threshold=30)
        item3 = mommy.make(models.StoreItem, stock_count=0, stock_threshold=30)
        mommy.make(models.StoreItem, stock_count=40, stock_threshold=None)
        mommy.make(models.StoreItem, stock_count=None, stock_threshold=None)

        list_filter = StockThresholdFilter(
            None,
            {StockThresholdFilter.parameter_name: StockThresholdFilter.THRESHOLD_ALERT},
            models.StoreItem,
            StoreItemAdmin
        )
        filtered_items = list_filter.queryset(None, models.StoreItem.objects.all())
        self.assertEqual(
            sorted([item1, item3], key=lambda x: x.id),
            sorted(filtered_items.all(), key=lambda x: x.id)
        )

    def test_above_threshold(self):
        """It should filter display items above threshold"""
        mommy.make(models.StoreItem, stock_count=20, stock_threshold=30)
        item2 = mommy.make(models.StoreItem, stock_count=40, stock_threshold=30)
        mommy.make(models.StoreItem, stock_count=0, stock_threshold=30)
        mommy.make(models.StoreItem, stock_count=40, stock_threshold=None)
        mommy.make(models.StoreItem, stock_count=None, stock_threshold=None)

        list_filter = StockThresholdFilter(
            None,
            {StockThresholdFilter.parameter_name: StockThresholdFilter.THRESHOLD_OK},
            models.StoreItem,
            StoreItemAdmin
        )
        filtered_items = list_filter.queryset(None, models.StoreItem.objects.all())
        self.assertEqual(sorted([item2]), sorted(filtered_items.all()))

    def test_no_threshold(self):
        """It should filter items without threshold"""
        mommy.make(models.StoreItem, stock_count=20, stock_threshold=30)
        mommy.make(models.StoreItem, stock_count=40, stock_threshold=30)
        mommy.make(models.StoreItem, stock_count=0, stock_threshold=30)
        item4 = mommy.make(models.StoreItem, stock_count=40, stock_threshold=None)
        item5 = mommy.make(models.StoreItem, stock_count=None, stock_threshold=None)

        list_filter = StockThresholdFilter(
            None,
            {StockThresholdFilter.parameter_name: StockThresholdFilter.THRESHOLD_NONE},
            models.StoreItem,
            StoreItemAdmin
        )
        filtered_items = list_filter.queryset(None, models.StoreItem.objects.all())
        self.assertEqual(
            sorted([item4, item5], key=lambda x: x.id),
            sorted(filtered_items.all(), key=lambda x: x.id)
        )

    def test_view_all(self):
        """It should return all"""
        item1 = mommy.make(models.StoreItem, stock_count=20, stock_threshold=30)
        item2 = mommy.make(models.StoreItem, stock_count=40, stock_threshold=30)
        item3 = mommy.make(models.StoreItem, stock_count=0, stock_threshold=30)
        item4 = mommy.make(models.StoreItem, stock_count=40, stock_threshold=None)
        item5 = mommy.make(models.StoreItem, stock_count=None, stock_threshold=None)

        list_filter = StockThresholdFilter(
            None,
            {},
            models.StoreItem,
            StoreItemAdmin
        )
        filtered_items = list_filter.queryset(None, models.StoreItem.objects.all())
        self.assertEqual(
            sorted([item1, item2, item3, item4, item5], key=lambda x: x.id),
            sorted(filtered_items.all(), key=lambda x: x.id)
        )

    def test_warning_threshold_empty(self):
        """It should return empty list"""
        list_filter = StockThresholdFilter(
            None,
            {StockThresholdFilter.parameter_name: StockThresholdFilter.THRESHOLD_ALERT},
            models.StoreItem,
            StoreItemAdmin
        )
        filtered_items = list_filter.queryset(None, models.StoreItem.objects.all())
        self.assertEqual(0, filtered_items.count())

    def test_ok_threshold_empty(self):
        """It should return empty list"""
        list_filter = StockThresholdFilter(
            None,
            {StockThresholdFilter.parameter_name: StockThresholdFilter.THRESHOLD_OK},
            models.StoreItem,
            StoreItemAdmin
        )
        filtered_items = list_filter.queryset(None, models.StoreItem.objects.all())
        self.assertEqual(0, filtered_items.count())

    def test_no_threshold_empty(self):
        """It should return empty list"""
        list_filter = StockThresholdFilter(
            None,
            {StockThresholdFilter.parameter_name: StockThresholdFilter.THRESHOLD_NONE},
            models.StoreItem,
            StoreItemAdmin
        )
        filtered_items = list_filter.queryset(None, models.StoreItem.objects.all())
        self.assertEqual(0, filtered_items.count())

