# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from rest_framework.response import Response
from rest_framework.views import APIView

from balafon.Store.models import Sale
from balafon.Store.api import get_staff_api_permissions, serializers


class SaleVatTotalsView(APIView):
    """get sales by category"""
    permission_classes = get_staff_api_permissions()

    def get_sale(self, sale_id):
        """return sales for an objects for the given period (a cell of the statistic array)"""
        return Sale.objects.get(id=sale_id)

    def get(self, request, **kwargs):
        """return a list with monthly amount by categories"""

        sale = self.get_sale(kwargs['sale_id'])

        vat_total_serializer = serializers.VatTotalSerializer(sale.vat_total_amounts(), many=True)
        return Response({'vat_totals': vat_total_serializer.data})

