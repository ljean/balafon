# -*- coding: utf-8 -*-
"""a simple store"""

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from rest_framework.renderers import JSONRenderer

from sanza.Crm.models import Action
from sanza.Crm.serializers import ActionSerializer
from sanza.Store.models import SaleItem, VatRate
from sanza.Store.serializers import SaleItemSerializer, SaleSerializer, VatRateSerializer


class Utf8JSONRenderer(JSONRenderer):
    """Utf-8 support"""
    ensure_ascii = False


class SalesDocumentView(TemplateView):
    """display sales document"""
    template_name = "Store/commercial_document.html"
    action = None

    def get_context_data(self, **kwargs):
        """get context data"""
        context = super(SalesDocumentView, self).get_context_data(**kwargs)

        action = self.get_action()

        action_serializer = ActionSerializer(self.get_action())
        action_data = Utf8JSONRenderer().render(action_serializer.data)

        sale_serializer = SaleSerializer(action.sale)
        sale_data = Utf8JSONRenderer().render(sale_serializer.data)

        sale_items_serializer = SaleItemSerializer(self.get_sale_items(), many=True)
        sale_items_data = Utf8JSONRenderer().render(sale_items_serializer.data)

        vat_rates_serializer = VatRateSerializer(VatRate.objects.all(), many=True)
        vat_rates_data = Utf8JSONRenderer().render(vat_rates_serializer.data)

        context['DJANGO_APP'] = """
        var DJANGO_APP = {{
            action: {0},
            sale_items: {1},
            sale: {2},
            vat_rates: {3}
        }};""".format(
            action_data, sale_items_data, sale_data, vat_rates_data
        )
        return context

    def get_action(self):
        """get the associated action"""
        if self.action is None:
            action_id = self.kwargs.get('action_id', 0)
            self.action = get_object_or_404(Action, id=action_id)
        return self.action

    def get_sale_items(self):
        """get the sales items"""
        return SaleItem.objects.filter(sale__action=self.get_action())
