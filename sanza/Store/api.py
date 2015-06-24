# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from rest_framework import viewsets, permissions

from sanza.Store.models import SaleItem, StoreItem
from sanza.Store import serializers


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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """returns objects"""
        name = self.request.GET.get('name', None)
        if name:
            return self.queryset.filter(name__icontains=name)[:20]
        return self.queryset
