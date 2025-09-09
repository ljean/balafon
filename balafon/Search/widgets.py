# -*- coding: utf-8 -*-

import floppyforms as forms


class DatespanInput(forms.TextInput):
    """widget with two dates"""
    template_name = 'Search/_datespan_widget.html'
