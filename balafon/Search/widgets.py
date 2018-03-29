# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import floppyforms.__future__ as forms


class DatespanInput(forms.TextInput):
    """widget with two dates"""
    template_name = 'Search/_datespan_widget.html'
