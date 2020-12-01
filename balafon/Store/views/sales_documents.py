# -*- coding: utf-8 -*-
"""a simple store"""

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.views.generic import TemplateView


from balafon.permissions import can_access
from balafon.settings import get_pdf_view_base_class
from balafon.utils import Utf8JSONRenderer
from balafon.Crm.models import Action
from balafon.Crm.serializers import ActionSerializer
from balafon.Store.models import Discount, Sale, SaleItem, VatRate, StoreManagementActionType
from balafon.Store.settings import get_commercial_document_pdf_options
from balafon.Store.api.serializers import (
    DiscountSerializer, SaleItemSerializer, SaleSerializer, VatRateSerializer, VatTotalSerializer
)


class SalesDocumentViewMixin(object):
    """display sales document: to be inherited in TemplateView and PdfTemplateView"""
    action = None
    is_public = False
    is_pdf = False
    template_name = "Store/commercial_document.html"

    def dispatch(self, *args, **kwargs):
        if not self.is_public:
            if not self.request.user.is_authenticated:
                return HttpResponseRedirect(reverse('login'))
        return super(SalesDocumentViewMixin, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        """return customized template of exists"""
        action = self.get_action()
        try:
            store_action_type = StoreManagementActionType.objects.get(action_type=action.type)
            if store_action_type.template_name:
                return store_action_type.template_name
        except StoreManagementActionType.DoesNotExist:
            pass
        return super(SalesDocumentViewMixin, self).get_template_names()

    def get_context_data(self, **kwargs):
        """get context data"""
        context = super(SalesDocumentViewMixin, self).get_context_data(**kwargs)

        if not self.is_public and not can_access(self.request.user):
            raise PermissionDenied

        action = self.get_action()

        sale = self.get_sale(action)

        if self.is_public:
            is_read_only = True
        else:
            if action.frozen:
                is_read_only = True
            else:
                if action.type:
                    is_read_only = action.status in action.type.storemanagementactiontype.readonly_status.all()
                else:
                    is_read_only = False

        action_serializer = ActionSerializer(self.get_action())
        action_data = Utf8JSONRenderer().render(action_serializer.data)

        sale_serializer = SaleSerializer(sale)
        sale_data = Utf8JSONRenderer().render(sale_serializer.data)

        vat_total_serializer = VatTotalSerializer(sale.vat_total_amounts(), many=True)
        vat_total_data = Utf8JSONRenderer().render(vat_total_serializer.data)

        sale_items_serializer = SaleItemSerializer(self.get_sale_items(), many=True)
        sale_items_data = Utf8JSONRenderer().render(sale_items_serializer.data)

        vat_rates_serializer = VatRateSerializer(VatRate.objects.all(), many=True)
        vat_rates_data = Utf8JSONRenderer().render(vat_rates_serializer.data)

        discounts_serializer = DiscountSerializer(Discount.objects.filter(active=True), many=True)
        discounts_data = Utf8JSONRenderer().render(discounts_serializer.data)

        context['action'] = action
        context['is_read_only'] = is_read_only
        context['is_pdf'] = self.is_pdf
        context["references_text"] = sale.get_references_text()

        context['DJANGO_APP'] = """
        var DJANGO_APP = {{
            action: {0},
            sale_items: {1},
            sale: {2},
            vat_rates: {3},
            isPdf: {4},
            isPublic: {5},
            isReadOnly: {6},
            discounts: {7},
            vat_totals: {8},
            showPercentage: {9},
        }};""".format(
            action_data,
            sale_items_data,
            sale_data,
            vat_rates_data,
            'true' if self.is_pdf else 'false',
            'true' if self.is_public else 'false',
            'true' if is_read_only else 'false',
            discounts_data,
            vat_total_data,
            'true' if getattr(settings, 'BALAFON_STORE_SHOW_PERCENTAGE', False) else 'false'
        )
        return context

    def get_action(self):
        """get the associated action"""
        if self.action is None:
            if self.is_public:
                action_uuid = self.kwargs.get('action_uuid', '')
                if not action_uuid:
                    raise Http404
                self.action = get_object_or_404(Action, uuid=action_uuid)
            else:
                action_id = self.kwargs.get('action_id', 0)
                self.action = get_object_or_404(Action, id=action_id)
        return self.action

    def get_sale(self, action):
        try:
            return action.sale
        except Sale.DoesNotExist:
            raise Http404

    def get_sale_items(self):
        """get the sales items"""
        return SaleItem.objects.filter(sale__action=self.get_action()).order_by('order_index')


class SalesDocumentView(SalesDocumentViewMixin, TemplateView):
    """display sales document as html"""
    is_pdf = False


class SalesDocumentPdfView(SalesDocumentViewMixin, get_pdf_view_base_class()):
    """display sales document as pdf"""
    is_pdf = True
    cmd_options = {
        'javascript-delay': 1000,
        'margin-top': 0,
        'margin-bottom': 0,
        'margin-left': 0,
        'margin-right': 0,
    }
    
    def __init__(self, *args, **kwargs):
        options = get_commercial_document_pdf_options()
        if options is not None:
            self.cmd_options = options
        super(SalesDocumentPdfView, self).__init__(*args, **kwargs)

    def _get_template_for_document(self, footer):
        """return customized template of exists"""
        action = self.get_action()
        try:
            store_action_type = StoreManagementActionType.objects.get(action_type=action.type)
            if store_action_type.template_name:
                if footer:
                    return store_action_type.footer_template_name or None
                else:
                    return store_action_type.header_template_name or None
        except StoreManagementActionType.DoesNotExist:
            pass
        return None

    @property
    def header_template(self):
        return self._get_template_for_document(False)

    @property
    def footer_template(self):
        return self._get_template_for_document(True)

    def get_filename(self):
        action = self.get_action()
        return '{0}.pdf'.format(slugify(action.type.name) if action.type else 'document')

    def get_context_data(self, **kwargs):
        """get context data"""
        context = super(SalesDocumentPdfView, self).get_context_data(**kwargs)

        # Make sure that the action is in readonly status
        action = self.get_action()
        default_readonly_status = action.type.storemanagementactiontype.default_readonly_status
        if default_readonly_status:
            read_only_status = action.type.storemanagementactiontype.readonly_status.all()
            if action.status not in read_only_status:
                action.status = default_readonly_status
                action.save()

        if settings.DEBUG:
            port = self.request.META.get('SERVER_PORT', 8000)
            context["DOMAIN"] = 'http://127.0.0.1:{0}'.format(port)
        else:
            try:
                site = Site.objects.get_current()
                context["DOMAIN"] = 'http://{0}'.format(site.domain)
            except Site.DoesNotExist:
                pass

        return context


class SalesDocumentPublicView(SalesDocumentViewMixin, TemplateView):
    """display sales document as pdf"""
    is_pdf = False
    is_public = True
    cmd_options = {
        'javascript-delay': 1000,
        'margin-top': 0,
        'margin-bottom': 0,
        'margin-left': 0,
        'margin-right': 0,
    }


class SalesDocumentPublicPdfView(SalesDocumentPdfView):
    """display sales document as pdf"""
    is_public = True
