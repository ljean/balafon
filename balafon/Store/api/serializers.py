# -*- coding: utf-8 -*-
"""a simple store"""

from rest_framework import serializers

from balafon.Store.models import (
    Brand, Certificate, Discount, PriceClass, Sale, StoreItem, StoreItemCategory, StoreItemTag, SaleItem, Unit, VatRate
)


class SaleSerializer(serializers.ModelSerializer):
    """json serializer"""

    class Meta:
        model = Sale
        fields = ('id', )


class StoreItemCategorySerializer(serializers.ModelSerializer):
    """json serializer"""
    get_path_name = serializers.CharField(read_only=True)
    get_articles_count = serializers.IntegerField(read_only=True)
    get_children_count = serializers.IntegerField(read_only=True)

    #parent = serializers.CharField(read_only=True)

    class Meta:
        model = StoreItemCategory
        fields = ('id', 'name', "icon", "get_path_name", "parent", "get_articles_count", "get_children_count")


class VatRateSerializer(serializers.ModelSerializer):
    """json serializer"""

    rate = serializers.FloatField()
    name = serializers.CharField(read_only=True)

    class Meta:
        model = VatRate
        fields = ('id', 'rate', 'name', 'is_default')
        

class BrandSerializer(serializers.ModelSerializer):
    """json serializer"""
    class Meta:
        model = Brand
        fields = ('id', 'name',)


class StoreItemTagSerializer(serializers.ModelSerializer):
    """tags"""
    class Meta:
        model = StoreItemTag
        fields = (
            'id', 'name', "icon", "show_always"
        )


class UnitSerializer(serializers.ModelSerializer):
    """unit"""
    class Meta:
        model = Unit
        fields = (
            'id', 'name'
        )


class DiscountSerializer(serializers.ModelSerializer):
    """json serializer"""
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Discount
        fields = ('id', 'name', 'quantity', 'rate', 'display_name')


class PriceClassSerializer(serializers.ModelSerializer):
    """json serializer"""

    class Meta:
        model = PriceClass
        fields = ('name', )


class CertificateSerializer(serializers.ModelSerializer):
    """json serializer"""

    class Meta:
        model = Certificate
        fields = ('name', 'image',)


class StoreItemSerializer(serializers.ModelSerializer):
    """json serializer"""

    pre_tax_price = serializers.FloatField()
    vat_rate = VatRateSerializer()
    category = StoreItemCategorySerializer()
    vat_incl_price = serializers.FloatField(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = StoreItemTagSerializer(read_only=True, many=True)
    available = serializers.BooleanField(read_only=True)
    unit = UnitSerializer(read_only=True)
    public_properties = serializers.DictField(read_only=True)
    discounts = DiscountSerializer(many=True, read_only=True)
    price_class = PriceClassSerializer(read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)

    class Meta:
        model = StoreItem
        fields = (
            'id', 'name', 'category', 'vat_rate', 'pre_tax_price', 'vat_incl_price', 'brand', 'reference', 'tags',
            'available', 'unit', 'public_properties', 'discounts', 'price_class', 'certificates',
        )


class SaleItemSerializer(serializers.ModelSerializer):
    """Serialize a sales item"""
    sale = SaleSerializer(read_only=True)
    quantity = serializers.FloatField()
    pre_tax_price = serializers.FloatField()
    unit_price = serializers.FloatField()
    discount = DiscountSerializer()
    vat_rate = VatRateSerializer()

    class Meta:
        model = SaleItem
        fields = (
            'id', 'sale', 'quantity', 'vat_rate', 'pre_tax_price', 'text', 'item', 'order_index', 'is_blank',
            'discount', 'unit_price'
        )


class UpdateSaleItemSerializer(serializers.ModelSerializer):
    """Serialize a sale item for update"""
    quantity = serializers.DecimalField(max_digits=9, decimal_places=2)
    pre_tax_price = serializers.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        model = SaleItem
        fields = (
            'id', 'quantity', 'vat_rate', 'pre_tax_price', 'text', 'item', 'order_index', 'sale', 'is_blank',
            'discount',
        )


class CartItemSerializer(serializers.Serializer):
    """Serialize a sales item"""
    id = serializers.IntegerField()
    quantity = serializers.FloatField()


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    purchase_datetime = serializers.DateTimeField()
    delivery_point = serializers.IntegerField()
    notes = serializers.CharField(max_length=3000, required=False)


class FavoriteItemSerializer(serializers.Serializer):
    """Serialize"""
    id = serializers.IntegerField()


class FavoriteSerializer(serializers.Serializer):
    items = FavoriteItemSerializer(many=True)


class ValueSerializer(serializers.Serializer):
    """a value"""
    value = serializers.DecimalField(max_digits=9, decimal_places=2)


class SalesStatisticSerializer(serializers.Serializer):
    """Serialize"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    icon = serializers.CharField(required=False)
    values = ValueSerializer(many=True)


class DateSerializer(serializers.Serializer):
    """a value"""
    date = serializers.DateTimeField()