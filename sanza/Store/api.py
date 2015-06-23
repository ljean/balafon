# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from rest_framework import viewsets

from sanza.Store.models import StoreItemSale, StoreItem
from sanza.Store import serializers


class StoreItemSaleViewSet(viewsets.ModelViewSet):
    """returns sales items"""
    queryset = StoreItemSale.objects.all()
    serializer_class = serializers.StoreItemSaleSerializer

    def get_queryset(self):
        """returns objects"""
        action_id = self.kwargs['action_id']
        return self.queryset.filter(sale__action__id=action_id)


class StoreItemViewSet(viewsets.ModelViewSet):
    """returns sales items"""
    queryset = StoreItem.objects.all()
    serializer_class = serializers.StoreItemSerializer

    def get_queryset(self):
        """returns objects"""
        name = self.request.GET.get('name', None)
        if name:
            return self.queryset.filter(name__icontains=name)[:20]
        return self.queryset
