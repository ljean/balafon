# -*- coding: utf-8 -*-
"""a simple store"""

import xlwt

from django.utils.translation import ugettext as _

from balafon.generic import XlsExportView
from balafon.Store.models import StoreItem


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

        sheet = workbook.add_sheet(_(u"Stock"))

        line = 0

        columns = [
            _(u'Id'), _(u'Name'), _(u'Category'), _(u'Purchase price'), _(u"Stock count"), _(u'Stock threshold'),
            _(u'Value'),
        ]

        for col, label in enumerate(columns):
            self.write_cell(sheet, 0, col, label, style=self.get_header_style())

        for line, item in enumerate(self.get_store_items()):
            sheet.write(line + 1, 0, item.id)
            sheet.write(line + 1, 1, item.name)
            sheet.write(line + 1, 2, u'{0}'.format(item.category) if item.category else '')
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

        sheet = workbook.add_sheet(_(u'Catalogue'))

        try:
            category_id = int(self.kwargs.get('category_id', 0))
        except ValueError:
            category_id = 0

        queryset = StoreItem.objects.filter(available=True)
        if category_id:
            queryset = queryset.filter(category=category_id)

        columns = [
            _(u'Name'), _(u'Category'), _(u'Brand'), _(u"VAT inclusive price"), _(u'Reference'),
            _(u'certificates'),
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
                sheet, line + 1, 5, u','.join(
                    [certificate.name for certificate in store_item.certificates.all()]
                )
            )
