# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from rest_framework import viewsets, permissions

from sanza.Store.models import SaleItem, StoreItem, StoreItemCategory, StoreItemTag
from sanza.Store import serializers, settings


def get_public_api_permissions():
    """get public api permissions"""
    if settings.is_public_api_allowed():
        return [permissions.IsAuthenticatedOrReadOnly]
    else:
        return [permissions.IsAuthenticated]


class SaleItemViewSet(viewsets.ModelViewSet):
    """returns sales items"""
    queryset = SaleItem.objects.all()
    serializer_class = serializers.SaleItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ('PUT', 'POST'):
            return serializers.UpdateSaleItemSerializer
        else:
            return super(SaleItemViewSet, self).get_serializer_class(*args, **kwargs)

    def get_queryset(self):
        """returns objects"""
        action_id = self.kwargs['action_id']
        return self.queryset.filter(sale__action__id=action_id)


class StoreItemViewSet(viewsets.ModelViewSet):
    """returns sales items"""
    queryset = StoreItem.objects.all()
    serializer_class = serializers.StoreItemSerializer
    permission_classes = get_public_api_permissions()

    def get_queryset(self):
        """returns objects"""
        name = self.request.GET.get('name', None)
        if name:
            return self.queryset.filter(name__icontains=name)[:20]

        category = self.request.GET.get('category', None)
        if category:
            return self.queryset.filter(category=category)

        return self.queryset


class StoreItemCategoryViewSet(viewsets.ModelViewSet):
    """returns categories"""
    queryset = StoreItemCategory.objects.all()
    serializer_class = serializers.StoreItemCategorySerializer
    permission_classes = get_public_api_permissions()


class StoreItemTagViewSet(viewsets.ModelViewSet):
    """returns tags"""
    queryset = StoreItemTag.objects.all()
    serializer_class = serializers.StoreItemTagSerializer
    permission_classes = get_public_api_permissions()
