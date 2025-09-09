# -*- coding: utf-8 -*-
"""Balafon : your django CRM"""

import floppyforms as forms


class HidableModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    hidden_widget = forms.HiddenInput
