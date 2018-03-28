# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from floppyforms.widgets import TextInput


class DatespanInput(TextInput):
    """widget with two dates"""
    template_name = 'Search/_datespan_widget.html'
