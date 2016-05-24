# -*- coding: utf-8 -*-

"""a simple store"""

from datetime import datetime, date, time
from decimal import Decimal

from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView

from balafon.generic import StaffPopupFormView
from balafon.Crm.models import Action
from balafon.Store.forms import AddExtraSaleForm
from balafon.Store.models import Sale, SaleItem


class StaticticsIndexView(TemplateView):
    template_name = "Store/statistics_index.html"

    def get_context_data(self, **kwargs):
        context_data = super(StaticticsIndexView, self).get_context_data(**kwargs)

        first_sale = Sale.objects.all().order_by('action__planned_date')[0]

        context_data['from_year'] = first_sale.action.planned_date.year

        return context_data


class AddExtraSaleView(StaffPopupFormView):
    """This view makes possible to add other sales data than the one from the Internet site"""
    template_name = "Store/add_extra_sale.html"
    form_class = AddExtraSaleForm
    success_url = reverse_lazy('store_statistics_index')

    def form_valid(self, form):
        """create a new sale"""
        analysis_code = form.cleaned_data['analysis_code']
        planned_date = datetime.combine(form.cleaned_data['date'], time.min)
        amount = form.cleaned_data['amount']
        vat_rate = form.cleaned_data['vat_rate']

        action = Action.objects.create(type=analysis_code.action_type, planned_date=planned_date)

        if action.sale:
            action.sale.analysis_code = analysis_code
            action.sale.save()
            SaleItem.objects.create(
                sale=action.sale, pre_tax_price=amount, text=analysis_code.name, vat_rate=vat_rate, quantity=Decimal(1)
            )

        return super(AddExtraSaleView, self).form_valid(form)