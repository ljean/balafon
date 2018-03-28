# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from __future__ import unicode_literals

from decimal import Decimal
from datetime import date, datetime, time, timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404


from rest_framework.response import Response
from rest_framework.views import APIView

from balafon.Store.models import (
    SaleItem, StoreItem, StoreItemCategory, StoreItemTag, SaleAnalysisCode
)
from balafon.Store.api import get_staff_api_permissions, serializers


class SalesStatisticsBaseView(APIView):
    """get sales by category"""
    permission_classes = get_staff_api_permissions()

    def get_month_limits(self, the_date):
        """return the date limits of the given month"""
        date_from = datetime.combine(date(the_date.year, the_date.month, 1), time.min)

        next_month = date_from + timedelta(31)
        date_to = datetime.combine(date(next_month.year, next_month.month, 1), time.min)

        return date_from, date_to

    def get_sales_amount(self, sale_items_queryset):
        """returns the sum of sales for the given queryset"""
        total_amount = Decimal(0)
        for sales_item in sale_items_queryset:
            total_amount += sales_item.pre_tax_total_price()
        return total_amount

    def get_date_range(self, **kwargs):
        """date range from args"""
        from_month = int(kwargs['from_month'])
        from_year = int(kwargs['from_year'])
        to_month = int(kwargs['to_month'])
        to_year = int(kwargs['to_year'])

        first_date = datetime.combine(date(from_year, from_month, 1), time.min)
        last_date = datetime.combine(date(to_year, to_month, 1), time.min)
        return first_date, last_date

    def get_objects(self, **kwargs):
        """return list of objects (a line of the statistic array)"""
        return []

    def get_object_sale_items(self, obj, date_from, date_to):
        """return sales for an objects for the given period (a cell of the statistic array)"""
        return SaleItem.objects.filter(
            sale__action__planned_date__gte=date_from,
            sale__action__planned_date__lt=date_to,
        ).exclude(sale__analysis_code__isnull=True)

    def get_object_name(self, obj):
        """return object name"""
        return obj.name

    def get_object_icon(self, obj):
        """return object name"""
        return obj.icon

    def get(self, request, **kwargs):
        """return a list with monthly amount by categories"""

        first_date, last_date = self.get_date_range(**kwargs)

        date_from, date_to = self.get_month_limits(first_date)

        objects = self.get_objects(**kwargs)

        objects_data = [
            {'id': obj.id, 'name': self.get_object_name(obj), 'icon': self.get_object_icon(obj), 'values': []}
            for obj in objects
        ]
        months = []
        while date_from <= last_date:
            months.append(date_from)

            for index, obj in enumerate(objects):
                sales_items = self.get_object_sale_items(obj, date_from, date_to)
                amount = self.get_sales_amount(sales_items)
                objects_data[index]['values'].append({'value': amount})

            next_date = date_to + timedelta(days=1)
            date_from, date_to = self.get_month_limits(next_date)

        stat_serializer = serializers.SalesStatisticSerializer(objects_data, many=True)
        months_serializer = serializers.DateSerializer(
            [{'date': _datetime} for _datetime in months], many=True
        )
        return Response({'months': months_serializer.data, 'data': stat_serializer.data})


class SalesByCategoryView(SalesStatisticsBaseView):
    """sales statistics by category"""

    def get_objects(self, **kwargs):
        """return list of objects (a line of the statistic array)"""
        return list(StoreItemCategory.objects.filter(parent__isnull=False))

    def get_object_sale_items(self, obj, date_from, date_to):
        """return sales for an objects for the given period (a cell of the statistic array)"""
        return super(SalesByCategoryView, self).get_object_sale_items(
            obj, date_from, date_to
        ).filter(item__category=obj)


class SalesByFamilyView(SalesStatisticsBaseView):
    """sales statistics by family"""

    def get_objects(self, **kwargs):
        """return list of objects (a line of the statistic array)"""
        return list(StoreItemCategory.objects.filter(parent__isnull=True))

    def get_object_sale_items(self, obj, date_from, date_to):
        """return sales for an objects for the given period (a cell of the statistic array)"""
        return super(SalesByFamilyView, self).get_object_sale_items(
            obj, date_from, date_to
        ).filter(Q(item__category__parent=obj) | Q(item__category=obj))


class SalesByTagView(SalesStatisticsBaseView):
    """sales statistics by tags"""

    def get_objects(self, **kwargs):
        """return list of objects (a line of the statistic array)"""
        return list(StoreItemTag.objects.all())

    def get_object_sale_items(self, obj, date_from, date_to):
        """return sales for an objects for the given period (a cell of the statistic array)"""
        return super(SalesByTagView, self).get_object_sale_items(
            obj, date_from, date_to
        ).filter(item__tags=obj)


class SalesByItemOfFamilyView(SalesStatisticsBaseView):
    """get sales by items of category"""

    def get_objects(self, **kwargs):
        """return list of objects (a line of the statistic array)"""
        category = get_object_or_404(StoreItemCategory, id=kwargs['category_id'])
        return list(StoreItemCategory.objects.filter(parent=category))

    def get_object_sale_items(self, obj, date_from, date_to):
        """return sales for an objects for the given period (a cell of the statistic array)"""
        return super(SalesByItemOfFamilyView, self).get_object_sale_items(
            obj, date_from, date_to
        ).filter(item__category=obj)


class SalesByItemOfCategoryView(SalesStatisticsBaseView):
    """get sales by items of category"""

    def get_objects(self, **kwargs):
        """return list of objects (a line of the statistic array)"""
        category = get_object_or_404(StoreItemCategory, id=kwargs['category_id'])
        return list(StoreItem.objects.filter(category=category))

    def get_object_sale_items(self, obj, date_from, date_to):
        """return sales for an objects for the given period (a cell of the statistic array)"""
        return super(SalesByItemOfCategoryView, self).get_object_sale_items(
            obj, date_from, date_to
        ).filter(item=obj)

    def get_object_icon(self, obj):
        """return object name"""
        return obj.category.icon if obj.category else ''


class SalesByItemOfTagView(SalesStatisticsBaseView):
    """get sales by items of tag"""

    def get_objects(self, **kwargs):
        """return list of objects (a line of the statistic array)"""
        tag = get_object_or_404(StoreItemTag, id=kwargs['tag_id'])
        return list(StoreItem.objects.filter(tags=tag))

    def get_object_sale_items(self, obj, date_from, date_to):
        """return sales for an objects for the given period (a cell of the statistic array)"""
        return super(SalesByItemOfTagView, self).get_object_sale_items(
            obj, date_from, date_to
        ).filter(item=obj)

    def get_object_icon(self, obj):
        """return object name"""
        return obj.category.icon if obj.category else ''


class TotalSalesView(SalesStatisticsBaseView):
    """get sales by items of tag"""

    def get_objects(self, **kwargs):
        """return list of objects (a line of the statistic array)"""
        return SaleAnalysisCode.objects.all()

    def get_object_icon(self, obj):
        """return object name"""
        return 'piggy-bank'

    def get_object_sale_items(self, obj, date_from, date_to):
        """return sales for an objects for the given period (a cell of the statistic array)"""

        return super(TotalSalesView, self).get_object_sale_items(
            obj, date_from, date_to
        ).filter(sale__analysis_code=obj)


