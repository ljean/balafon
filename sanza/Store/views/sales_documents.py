# -*- coding: utf-8 -*-
"""a simple store"""

from django.core import serializers

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404, render_to_response, get_list_or_404
from django.template import RequestContext
from django.utils.functional import curry
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_close
from rest_framework.renderers import JSONRenderer

from coop_cms.generic_views import EditableFormsetView

from sanza.Crm.models import Action
from sanza.Crm.serializers import ActionSerializer
from sanza.Store.models import StoreItemSale, VatRate
from sanza.Store.serializers import StoreItemSaleSerializer, SaleSerializer, VatRateSerializer
from sanza.Store.forms import StoreItemSaleForm, ChooseStoreItemForm


@login_required
@popup_close
def choose_item(request):
    """edit fragments of the current template"""

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = ChooseStoreItemForm(request.POST)
        if form.is_valid():
            #popup_close decorator will close and refresh
            return None
    else:
        form = ChooseStoreItemForm()

    context_dict = {
        'form': form,
        'title': _(u"Select Item?"),
    }

    return render_to_response(
        'Store/popup_choose_item.html',
        context_dict,
        context_instance=RequestContext(request)
    )


class SalesDocumentView(TemplateView):
    template_name = "Store/commercial_document.html"
    action = None

    def get_context_data(self, **kwargs):
        context = super(SalesDocumentView, self).get_context_data(**kwargs)

        action = self.get_action()

        action_serializer = ActionSerializer(self.get_action())
        action_data = JSONRenderer().render(action_serializer.data)

        sales_serializer = SaleSerializer(action.sale_set.all(), many=True)
        sales_data = JSONRenderer().render(sales_serializer.data)

        sale_items_serializer = StoreItemSaleSerializer(self.get_sale_items(), many=True)
        sale_items_data = JSONRenderer().render(sale_items_serializer.data)

        vat_rates_serializer = VatRateSerializer(VatRate.objects.all(), many=True)
        vat_rates_data = JSONRenderer().render(vat_rates_serializer.data)

        context['DJANGO_APP'] = u"""
        var DJANGO_APP = {{
            action: {0},
            sale_items: {1},
            sales: {2},
            vat_rates: {3}
        }};""".format(
            action_data, sale_items_data, sales_data, vat_rates_data
        )
        return context

    def get_action(self):
        """get the associated action"""
        if self.action is None:
            action_id = self.kwargs.get('action_id', 0)
            self.action = get_object_or_404(Action, id=action_id)
        return self.action

    def get_sale_items(self):
        """get the associated action"""
        return StoreItemSale.objects.filter(sale__action=self.get_action())




# class SalesDocumentView(EditableFormsetView):
#     """
#     Edit a sales document: bill, proposition...
#     Make possible to change the StoreItemSale formset
#     """
#     model = StoreItemSale
#     form_class = StoreItemSaleForm
#     extra = 1
#     action = None
#
#     def get_action(self):
#         """get the associated action"""
#         if self.action is None:
#             action_id = self.kwargs.get('action_id', 0)
#             self.action = get_object_or_404(Action, id=action_id)
#         return self.action
#
#     def get_edit_url(self):
#         """get edit url: where to go for edition"""
#         return reverse('store_edit_sales_document', args=[self.get_action().id])
#
#     def get_template(self):
#         """get the template to use"""
#         return self.get_action().type.default_template
#
#     def get_success_url(self):
#         """get success url : where to go after successful edition"""
#         return reverse('store_view_sales_document', args=[self.get_action().id])
#
#     def get_formset_class(self):
#         """formset class"""
#         sale = self.get_action().sale_set.all()[0]
#         form_class = self.get_form_class()
#         formset = modelformset_factory(self.model, form_class, extra=self.extra, can_delete=True)
#         formset.form = staticmethod(curry(form_class, sale=sale))
#         return formset
#
#     def get_queryset(self):
#         """returns objects to edit"""
#         queryset = super(SalesDocumentView, self).get_queryset()
#         return queryset.filter(sale__action=self.get_action())
#
#     def get_empty_object_kwargs(self):
#         """get argument to use for creating an empty object"""
#         sale = self.get_action().sale_set.all()[0]
#         return {'sale': sale, 'id': None}
#
#     def get_context_data(self, *args, **kwargs):
#         """get context"""
#         context = super(SalesDocumentView, self).get_context_data(*args, **kwargs)
#         context['action'] = self.get_action()
#         return context
