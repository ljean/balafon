# -*- coding: utf-8 -*-
"""Balafon : your django CRM"""

from __future__ import unicode_literals

import floppyforms.__future__ as forms


class HidableModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    hidden_widget = forms.HiddenInput
