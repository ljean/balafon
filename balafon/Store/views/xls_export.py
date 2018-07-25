# -*- coding: utf-8 -*-
"""a simple store"""

from __future__ import unicode_literals

from datetime import datetime, date, time
import xlrd
import xlwt

from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import FormView

from balafon.generic import XlsExportView, StaffPopupFormView
from balafon.Crm.models import ActionType
from balafon.Store.forms import StockImportForm
from balafon.Store.models import StoreItem
from balafon.Store.utils import to_decimal

from ..forms import DateRangeForm


class XlsBaseView(XlsExportView):

    def get_header_style(self):
        """style of header"""
        style = xlwt.XFStyle()
        style.pattern = xlwt.Pattern()
        style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        style.pattern.pattern_fore_colour = 22
        return style


class StockXlsView(XlsBaseView):
    doc_name = 'export-stock.xls'

    def get_store_items(self):
        """returns objects to export"""
        return StoreItem.objects.all().order_by('category__name', 'name')

    def do_fill_workbook(self, workbook):
        """export to excel all articles tin stock"""

        sheet = workbook.add_sheet(_("Stock"))

        line = 0

        columns = [
            _('Id'), _('Name'), _('Category'), _('Purchase price'), _("Stock count"), _('Stock threshold'),
            _('Value'),
        ]

        for col, label in enumerate(columns):
            self.write_cell(sheet, 0, col, label, style=self.get_header_style())

        for line, item in enumerate(self.get_store_items()):
            sheet.write(line + 1, 0, item.id)
            sheet.write(line + 1, 1, item.name)
            sheet.write(line + 1, 2, '{0}'.format(item.category) if item.category else '')
            sheet.write(line + 1, 3, item.purchase_price if item.purchase_price else 0)
            sheet.write(line + 1, 4, '' if item.stock_count is None else item.stock_count)
            sheet.write(line + 1, 5, '' if item.stock_count is None else item.stock_threshold)
            sheet.write(line + 1, 6, xlwt.Formula('D{0}*E{0})'.format(line + 2)))

        sheet.write(line + 3, 6, xlwt.Formula('SUM(G1:G{0})'.format(line + 2)))


class StockAlertXlsView(StockXlsView):
    doc_name = 'export-stock-alert.xls'

    def get_store_items(self):
        """returns objects to export"""
        for item in StoreItem.objects.filter(stock_count__isnull=False):
            if item.has_stock_threshold_alert():
                yield item


class StoreXlsCatalogueView(XlsBaseView):
    doc_name = 'catalogue.xls'

    def do_fill_workbook(self, workbook):
        """implement it in base class"""

        sheet = workbook.add_sheet(_('Catalogue'))

        try:
            category_id = int(self.kwargs.get('category_id', 0))
        except ValueError:
            category_id = 0

        queryset = StoreItem.objects.filter(available=True)
        if category_id:
            queryset = queryset.filter(category=category_id)

        columns = [
            _('Name'), _('Category'), _('Brand'), _("VAT inclusive price"), _('Reference'),
            _('certificates'),
        ]

        for col, label in enumerate(columns):
            self.write_cell(sheet, 0, col, label, style=self.get_header_style())

        for line, store_item in enumerate(queryset):
            self.write_cell(sheet, line + 1, 0, store_item.fullname())
            self.write_cell(sheet, line + 1, 1, store_item.category.name if store_item.category else '')
            self.write_cell(sheet, line + 1, 2, store_item.brand.name if store_item.brand else '')
            self.write_cell(sheet, line + 1, 3, store_item.vat_incl_price())
            self.write_cell(sheet, line + 1, 4, store_item.reference)
            self.write_cell(
                sheet, line + 1, 5, ','.join(
                    [certificate.name for certificate in store_item.certificates.all()]
                )
            )


class StoreItemXlsView(XlsBaseView):
    doc_name = 'articles.xls'

    def do_fill_workbook(self, workbook):
        """implement it in base class"""

        sheet = workbook.add_sheet(_('Articles'))

        try:
            category_id = int(self.kwargs.get('category_id', 0))
        except ValueError:
            category_id = 0

        try:
            supplier_id = int(self.kwargs.get('supplier_id', 0))
        except ValueError:
            supplier_id = 0

        queryset = StoreItem.objects.all()
        if category_id:
            queryset = queryset.filter(category=category_id)

        if supplier_id:
            queryset = queryset.filter(supplier=supplier_id)

        columns = [
            _('Name'), _('Famille'), _('Category'), _('Brand'), _("TTC"), _("HT"), _('TVA'), _("Available"),
            _('Supplier'), _('Reference'), _('certificates'),
        ]

        for col, label in enumerate(columns):
            self.write_cell(sheet, 0, col, label, style=self.get_header_style())

        for line, store_item in enumerate(queryset):
            root_category = store_item.root_category()
            self.write_cell(sheet, line + 1, 0, store_item.fullname())
            self.write_cell(sheet, line + 1, 1, root_category.name if root_category else '')
            self.write_cell(sheet, line + 1, 2, store_item.category.name if store_item.category else '')
            self.write_cell(sheet, line + 1, 3, store_item.brand.name if store_item.brand else '')
            self.write_cell(sheet, line + 1, 4, store_item.vat_incl_price())
            self.write_cell(sheet, line + 1, 5, store_item.pre_tax_price)
            self.write_cell(sheet, line + 1, 6, str(store_item.vat_rate) if store_item.vat_rate else '')
            self.write_cell(sheet, line + 1, 7, _('Yes') if store_item.available else _('No'))
            self.write_cell(sheet, line + 1, 8, store_item.supplier.name if store_item.supplier else '')
            self.write_cell(sheet, line + 1, 9, store_item.reference)
            self.write_cell(
                sheet, line + 1, 10, ','.join(
                    [certificate.name for certificate in store_item.certificates.all()]
                )
            )


class StockImportView(FormView):
    """Import purchase price, stock and threshold of store items from Excel file"""
    form_class = StockImportForm
    template_name = "Store/import_stock.html"
    success_url = reverse_lazy('admin:Store_storeitem_changelist')

    def _get_value(self, value):
        if value is None or value == '':
            return None
        return to_decimal(value)

    def form_valid(self, form):
        """Process the file"""

        xls_file = form.cleaned_data['xls_file']

        workbook = xlrd.open_workbook(file_contents=xls_file.read())

        worksheet = workbook.sheet_by_index(0)

        for row in range(1, worksheet.nrows):
            item_id = worksheet.cell(rowx=row, colx=0).value
            if item_id:
                try:
                    store_item = StoreItem.objects.get(id=int(item_id))
                except (StoreItem.DoesNotExist, ValueError):
                    store_item = None

                if store_item:
                    store_item.purchase_price = self._get_value(worksheet.cell(rowx=row, colx=3).value)
                    store_item.stock_count = self._get_value(worksheet.cell(rowx=row, colx=4).value)
                    store_item.stock_threshold = self._get_value(worksheet.cell(rowx=row, colx=5).value)
                    store_item.save()

        return super(StockImportView, self).form_valid(form)


class ActionSummaryFormView(StaffPopupFormView):
    template_name = 'Store/popup_actions_summary.html'
    form_class = DateRangeForm
    action_type = None

    def get_header_style(self):
        """style of header"""
        style = xlwt.XFStyle()
        style.pattern = xlwt.Pattern()
        style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        style.pattern.pattern_fore_colour = 22
        return style

    def get_action_type(self):
        if self.action_type is None:
            self.action_type = get_object_or_404(ActionType, id=self.kwargs['action_type_id'])
        return self.action_type

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_type'] = self.get_action_type()
        return context

    def form_valid(self, form):
        """returns objects to export"""
        action_type = self.get_action_type()
        start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
        end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
        url = reverse('store_actions_summary_xls', args=[action_type.id, start_date, end_date])
        return HttpResponseRedirect(url)


class ActionSummaryXlsView(XlsBaseView):
    doc_name = 'action-summary.xlsx'
    template_name = 'Store/popup_actions_summary.html'
    form_class = DateRangeForm
    only_staff = True
    action_type = None

    def get_action_type(self):
        if self.action_type is None:
            self.action_type = get_object_or_404(ActionType, id=self.kwargs['action_type_id'])
        return self.action_type

    def get_actions(self, action_type, start_date, end_date):
        """returns objects to export"""
        start_date = date(*[int(elt) for elt in start_date.split('-')])
        end_date = date(*[int(elt) for elt in end_date.split('-')])

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        return action_type.action_set.filter(
            planned_date__gte=start_datetime, planned_date__lte=end_datetime
        ).order_by('number')

    def do_fill_workbook(self, workbook):
        """export to excel all actions of this type"""

        action_type = self.get_action_type()
        start_date = self.kwargs['start_date']
        end_date = self.kwargs['end_date']

        name = action_type.name
        sheet = workbook.add_sheet(name)
        self.doc_name = "{0}_{1}_{2}.xlsx".format(name.lower().replace(' ', '-'), start_date, end_date)

        columns = [
            _('Number'), _('Client'), _('Date') + ' ' * 6, _('State'), _('Accounting code'), _('Pre-tax amount'), _('VAT amount'),
            _('Tax incl Amount'),
        ]

        sheet.col(2).width = 256 * 20

        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/mm/yyyy'

        for col, label in enumerate(columns):
            self.write_cell(sheet, 0, col, label, style=self.get_header_style())

        actions = self.get_actions(action_type, start_date, end_date)
        line = 0
        for action in actions:

            for accounting_elt in action.sale.accounting_code_amounts():
                line += 1

                sheet.write(line, 0, action.number)
                sheet.write(line, 1, action.get_recipients(False))
                sheet.write(line, 2, action.planned_date, style=date_format)
                sheet.write(line, 3, action.status.name if action.status else '')
                sheet.write(line, 4, accounting_elt['accounting_code'])
                sheet.write(line, 5, accounting_elt['pre_tax_total'])
                sheet.write(line, 6, accounting_elt['vat_total'])
                sheet.write(line, 7, accounting_elt['vat_incl_total'])

        if line:
            sheet.write(line + 2, 5, xlwt.Formula('SUM(F2:F{0})'.format(line + 1)), style=self.get_header_style())
            sheet.write(line + 2, 6, xlwt.Formula('SUM(G2:G{0})'.format(line + 1)), style=self.get_header_style())
            sheet.write(line + 2, 7, xlwt.Formula('SUM(H3:H{0})'.format(line + 1)), style=self.get_header_style())
