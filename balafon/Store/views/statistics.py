# -*- coding: utf-8 -*-

"""a simple store"""

from django.views.generic import TemplateView

from balafon.Store.models import Sale


class StaticticsIndexView(TemplateView):
    template_name = "Store/statistics_index.html"

    def get_context_data(self, **kwargs):
        context_data = super(StaticticsIndexView, self).get_context_data(**kwargs)

        first_sale = Sale.objects.all().order_by('action__planned_date')[0]

        context_data['from_year'] = first_sale.action.planned_date.year

        return context_data