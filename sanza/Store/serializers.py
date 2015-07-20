# -*- coding: utf-8 -*-
"""a simple store"""

from rest_framework import serializers

from sanza.Store.models import Sale, StoreItem, StoreItemCategory, StoreItemTag, SaleItem, VatRate


class SaleSerializer(serializers.ModelSerializer):
    """json serializer"""

    class Meta:
        model = Sale
        fields = ('id', )


class StoreItemCategorySerializer(serializers.ModelSerializer):
    """json serializer"""

    class Meta:
        model = StoreItemCategory
        fields = ('id', 'name')


class VatRateSerializer(serializers.ModelSerializer):
    """json serializer"""

    rate = serializers.FloatField()
    name = serializers.CharField(read_only=True)

    class Meta:
        model = VatRate
        fields = ('id', 'rate', 'name', 'is_default')
        

class StoreItemSerializer(serializers.ModelSerializer):
    """json serializer"""

    pre_tax_price = serializers.FloatField()
    vat_rate = VatRateSerializer()
    category = StoreItemCategorySerializer()
    vat_incl_price = serializers.FloatField(read_only=True)

    class Meta:
        model = StoreItem
        fields = ('id', 'name', 'category', 'vat_rate', 'pre_tax_price', 'vat_incl_price')


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
    quantity = serializers.DecimalField(max_digits=9, decimal_places=2)
    pre_tax_price = serializers.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        model = SaleItem
        fields = (
            'id', 'quantity', 'vat_rate', 'pre_tax_price', 'text', 'item', 'order_index', 'sale',
        )


class StoreItemTagSerializer(serializers.ModelSerializer):
    """tags"""
    class Meta:
        model = StoreItemTag
        fields = (
            'id', 'name',
        )
