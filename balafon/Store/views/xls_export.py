# -*- coding: utf-8 -*-
"""a simple store"""

import xlwt

from django.utils.translation import ugettext as _

from balafon.generic import XlsExportView
from balafon.Store.models import StoreItem


class StockXlsView(XlsExportView):
    doc_name = 'export-stock.xls'

    def do_fill_workbook(self, workbook):
        """export to excel all articles tin stock"""

        sheet = workbook.add_sheet(_(u"Stock"))

        line = 0

        for line, item in enumerate(StoreItem.objects.filter(stock_count__isnull=False).order_by('name')):
            sheet.write(line, 0, item.name)
            sheet.write(line, 1, unicode(item.category) if item.category else '')
            sheet.write(line, 2, item.purchase_price if item.purchase_price else 0)
            sheet.write(line, 3, item.stock_count)
            sheet.write(line, 4, item.stock_threshold)
            sheet.write(line, 5, xlwt.Formula('C{0}*D{0})'.format(line+1)))

        sheet.write(line+2, 5, xlwt.Formula('SUM(F1:F{0})'.format(line+1)))


class StockAlertXlsView(XlsExportView):
    doc_name = 'export-stock-alert.xls'

    def do_fill_workbook(self, workbook):
        """export to excel all articles that must be purchased"""

        sheet = workbook.add_sheet(_(u"Stock"))

        line = 0
        for item in StoreItem.objects.filter(stock_count__isnull=False).order_by('name'):
            if item.has_stock_threshold_alert():
                sheet.write(line, 0, item.name)
                sheet.write(line, 1, unicode(item.category) if item.category else '')
                sheet.write(line, 2, item.purchase_price if item.purchase_price else 0)
                sheet.write(line, 3, item.stock_count)
                sheet.write(line, 4, item.stock_threshold)
                sheet.write(line, 5, xlwt.Formula('C{0}*D{0})'.format(line+1)))
                line += 1

        sheet.write(line+2, 5, xlwt.Formula('SUM(F1:F{0})'.format(line+1)))


class StoreXlsCatalogueView(XlsExportView):
    doc_name = 'catalogue.xls'

    def get_header_style(self):
        style = xlwt.XFStyle()
        style.pattern = xlwt.Pattern()
        style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        style.pattern.pattern_fore_colour = 22
        return style

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
            _(u'Name'), _(u'Category'), _(u'Brand'), _(u"VAT inclusive price"), _(u'Reference'), _(u'certificates'),
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
