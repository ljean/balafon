# -*- coding: utf-8 -*-
"""a simple store"""

from rest_framework import serializers

from sanza.Store.models import Sale, StoreItem, StoreItemCategory, SaleItem, VatRate


class SaleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sale
        fields = ('id', )


class StoreItemCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreItemCategory
        fields = ('id', 'name')


class VatRateSerializer(serializers.ModelSerializer):
    rate = serializers.FloatField()
    name = serializers.CharField(read_only=True)

    class Meta:
        model = VatRate
        fields = ('id', 'rate', 'name', 'is_default')
        

class StoreItemSerializer(serializers.ModelSerializer):
    pre_tax_price = serializers.FloatField()
    vat_rate = VatRateSerializer()
    category = StoreItemCategorySerializer()

    class Meta:
        model = StoreItem
        fields = ('id', 'name', 'category', 'vat_rate', 'pre_tax_price')


class SaleItemSerializer(serializers.ModelSerializer):
    """Serialize a sales item"""
    sale = SaleSerializer(read_only=True)
    quantity = serializers.FloatField()
    pre_tax_price = serializers.FloatField()
    vat_rate = VatRateSerializer()

    class Meta:
        model = SaleItem
        fields = (
            'id', 'sale', 'quantity', 'vat_rate', 'pre_tax_price', 'text', 'item', 'order_index',
        )


class UpdateSaleItemSerializer(serializers.ModelSerializer):
    """Serialize a sale item for update"""
    quantity = serializers.FloatField()
    pre_tax_price = serializers.FloatField()

    class Meta:
        model = SaleItem
        fields = (
            'id', 'quantity', 'vat_rate', 'pre_tax_price', 'text', 'item', 'order_index', 'sale',
        )
