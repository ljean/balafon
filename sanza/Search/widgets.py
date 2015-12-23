# -*- coding: utf-8 -*-

from floppyforms.widgets import TextInput


class DatespanInput(TextInput):
    """widget with two dates"""
    template_name = 'Search/_datespan_widget.html'
