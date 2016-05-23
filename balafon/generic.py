# -*- coding: utf-8 -*-
"""Balafon : your django CRM"""


from datetime import date, datetime
import xlwt

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.dateformat import DateFormat
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.generic.edit import FormView

from colorbox.decorators import popup_redirect

from balafon.permissions import can_access


class StaffPopupFormView(FormView):
    """A base class for Popup form view"""

    @method_decorator(user_passes_test(can_access))
    @method_decorator(popup_redirect)
    def dispatch(self, *args, **kwargs):
        return super(StaffPopupFormView, self).dispatch(*args, **kwargs)


class XlsExportView(View):
    only_staff = True
    doc_name = 'balafon.xls'
    _col_widths = None
    _line_heights = None

    def dispatch(self, *args, **kwargs):
        if self.only_staff and not can_access(self.request.user):
            raise PermissionDenied()
        return super(XlsExportView, self).dispatch(*args, **kwargs)

    def get_default_style(self):
        """

        * Colour index
        8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta,
        7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown),
        20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on... sty

        * Borders
        borders.left, borders.right, borders.top, borders.bottom
        May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED,
        THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED,
        SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.

        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        borders.left_colour = 0x00
        borders.right_colour = 0x00
        borders.top_colour = 0x00
        borders.bottom_colour = 0x00
        style.borders = borders

        * Fonts
        style.font = xlwt.Font()
        style.font.height = 8 * 20
        style.font.colour_index = 22

        * Alignment
        style.alignment = xlwt.Alignment()
        style.alignment.horz = xlwt.Alignment.HORZ_LEFT
        style.alignment.vert = xlwt.Alignment.VERT_CENTER

        * Pattern
        May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12

        style.pattern = xlwt.Pattern()
        style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        style.pattern.pattern_fore_colour = 23

        """

        style = xlwt.XFStyle()
        return style

    def _calculate_size(self, ws, line, column, value):

        col_widths = [len(value_lines) for value_lines in unicode(value).split("\n")]
        line_height = (len(col_widths) * 240) if len(col_widths) > 1 else 0
        width = 1500 + max(col_widths) * 220

        if width > self._col_widths.get(column, 0):
            self._col_widths[column] = width
            ws.col(column).width = width
        if line_height > self._line_heights.get(line, 0):
            self._line_heights[line] = line_height
            ws.row(line).height_mismatch = True
            ws.row(line).height = line_height

    def get_value(self, value):
        if isinstance(value, date):
            date_format = DateFormat(value)
            return date_format.format("d/m/y").capitalize()
        elif isinstance(value, datetime):
            date_format = DateFormat(value)
            return date_format.format("d/m/y H:M").capitalize()
        return value

    def write_cell(self, sheet, line, column, value, *args, **kwargs):
        value = self.get_value(value)
        style = kwargs.pop('style', None) or self.get_default_style()
        ret = sheet.write(line, column, value, style, *args, **kwargs)
        self._calculate_size(sheet, line, column, value)
        return ret

    def write_merge(self, sheet, line1, line2, column1, column2, value, *args, **kwargs):
        value = self.get_value(value)
        style = kwargs.pop('style', None) or self.get_default_style()
        ret = sheet.write_merge(line1, line2, column1, column2, value, style, *args, **kwargs)
        self._calculate_size(sheet, line1, column1, value)
        return ret

    def do_fill_workbook(self, workbook):
        """implement it in base class"""
        pass

    def get(self, *args, **kwargs):
        workbook = xlwt.Workbook()
        self._col_widths = {}
        self._line_heights = {}
        self.do_fill_workbook(workbook)

        response = HttpResponse(content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename={0}'.format(self.doc_name)
        workbook.save(response)
        return response