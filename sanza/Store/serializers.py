# -*- coding: utf-8 -*-
"""a simple store"""

from rest_framework import serializers

from sanza.Store.models import Sale, StoreItem, StoreItemCategory, StoreItemSale, VatRate


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
        fields = ('id', 'rate', 'name')
        

class StoreItemSerializer(serializers.ModelSerializer):
    pre_tax_price = serializers.FloatField()
    vat_rate = VatRateSerializer()
    category = StoreItemCategorySerializer()

    class Meta:
        model = StoreItem
        fields = ('name', 'category', 'vat_rate', 'pre_tax_price')


class StoreItemSaleSerializer(serializers.ModelSerializer):
    """Serialize a contact"""
    sale = SaleSerializer()
    quantity = serializers.FloatField()
    pre_tax_price = serializers.FloatField()
    vat_rate = VatRateSerializer()

    class Meta:
        model = StoreItemSale
        fields = (
            'id', 'sale', 'quantity', 'vat_rate', 'pre_tax_price', 'text'
        )

