# -*- coding: utf-8 -*-
"""a simple store"""

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from rest_framework.renderers import JSONRenderer

from sanza.permissions import can_access
from sanza.Crm.models import Action
from sanza.Crm.serializers import ActionSerializer
from sanza.Store.models import Sale, SaleItem, VatRate, StoreManagementActionType
from sanza.Store.serializers import SaleItemSerializer, SaleSerializer, VatRateSerializer


class Utf8JSONRenderer(JSONRenderer):
    """Utf-8 support"""
    ensure_ascii = False


class SalesDocumentView(TemplateView):
    """display sales document"""
    template_name = "Store/commercial_document.html"
    action = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SalesDocumentView, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        """return customized template of exists"""
        action = self.get_action()
        try:
            store_action_type = StoreManagementActionType.objects.get(action_type=action.type)
            if store_action_type.template_name:
                return store_action_type.template_name
        except StoreManagementActionType.DoesNotExist:
            pass
        return super(SalesDocumentView, self).get_template_names()

    def get_context_data(self, **kwargs):
        """get context data"""
        context = super(SalesDocumentView, self).get_context_data(**kwargs)

        if not can_access(self.request.user):
            raise PermissionDenied

        action = self.get_action()

        try:
            sale = action.sale
        except Sale.DoesNotExist:
            raise Http404

        action_serializer = ActionSerializer(self.get_action())
        action_data = Utf8JSONRenderer().render(action_serializer.data)

        sale_serializer = SaleSerializer(sale)
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
